import os
import json
import base64
import logging
import asyncio
import numpy as np
from pathlib import Path
from datetime import date, datetime
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.genai.types import Content, Part
from .agents.firebase_client import FirestoreSessionService, embed_text
from .agents.agent import root_agent
from .agents.business_data.business_info import FALLBACK_CLIENT_INFO
from .tts_service import router as tts_router
from google.adk.sessions import InMemorySessionService
from .agents.firestore_instance import firestore_session_service
from google.adk.agents.callback_context import CallbackContext
from .agents.state_manager import set_current_connection_id, get_current_connection_id, set_debug_mode, get_debug_mode, set_current_session_id, get_current_session_id
from google.cloud import bigquery
from fastapi.responses import JSONResponse
from .agents.mixpanel_client import MixpanelClient
from langfuse import Langfuse
import secrets
from fastapi import HTTPException
from typing import Optional

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Firebase session setup
APP_NAME = "ADK Non-Streaming"
session_service = InMemorySessionService()
# Tracing setup
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()
OTEL_ENDPOINT = "https://us.cloud.langfuse.com/api/public/otel/v1/traces"
OTEL_HEADERS = { "Authorization": f"Basic {LANGFUSE_AUTH}" }

provider = TracerProvider(resource=Resource.create({
    "service.name": "agent_router", "service.version": "1.0.0"
}))

class LoggingExporter(OTLPSpanExporter):
    def export(self, spans):
        logger.debug("Exporting %d spans", len(spans))
        return super().export(spans)

provider.add_span_processor(BatchSpanProcessor(
    LoggingExporter(endpoint=OTEL_ENDPOINT, headers=OTEL_HEADERS, timeout=30)
))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent_router", "1.0.0")

# FastAPI setup
app = FastAPI()
app.include_router(tts_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

active_contexts = {}


langfuse = Langfuse(public_key=os.getenv("LANGFUSE_PUBLIC_KEY"), secret_key=os.getenv("LANGFUSE_SECRET_KEY"))

def get_all_general_context_into_firebase(connection_id: str):
    try:
        messages = firestore_session_service.get_all_general_context(connection_id)
        print(f"[DEBUG] Messages: {messages}", flush=True)
        if not messages:
            return []
        contents = [msg["content"] for msg in messages if msg.get("content")]
        return contents
    except Exception as e:
        logger.error(f"[context] Error: {e}")
        return []

def get_top_k_context(user_query: str, connection_id: str, k=3, min_similarity=0.0):
    try:
        query_vec = np.array(embed_text(user_query)).reshape(1, -1)
        messages = firestore_session_service.get_all_general_context(connection_id)
        if not messages:
            return []
        scored = []
        for msg in messages:
            emb = msg.get("embedding")
            if not emb:
                continue
            score = cosine_similarity(query_vec, np.array(emb).reshape(1, -1))[0][0]
            if score >= min_similarity:
                scored.append((msg, score))
        top_k = sorted(scored, key=lambda x: x[1], reverse=True)[:k]
        return [msg["content"] for msg, _ in top_k]
    except Exception as e:
        logger.warning(f"[context] Embedding failure: {e}")
        return []


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, connection_id: str = Query(...)):
    print(f"[INIT] /ws/{session_id}?connection_id={connection_id}")
    await websocket.accept()
    print(f"[ACCEPTED] WebSocket accepted")
    
    
    print(f"[CONNECTED] #{session_id} User: {connection_id}")

    # Create session with the provided session ID
    session = session_service.create_session(
        app_name=APP_NAME, 
        user_id=connection_id, 
        session_id=session_id  # Use the session_id from frontend
    )

    # Set the current connection_id for the agent to use
    set_current_connection_id(connection_id)
    set_current_session_id(session_id)



    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)
    run_config = RunConfig(response_modalities=["text"])
    organization_id = firestore_session_service.get_connection_info(connection_id).get("organization_id")
    source_id = firestore_session_service.get_connection_info(connection_id).get("source_id")
    mixpanel_details = firestore_session_service.get_mixpanel_details(organization_id, source_id)

    try:
        while True:
            
            print("[WAITING] for client message")
            msg = await websocket.receive_text()
            print(f"[RECEIVED] {msg}")
            data = json.loads(msg)

            # # Skip pings and other non-data messages
            if data.get("type") == "ping":
                continue

            content = data.get("data", "")
            print(f"[CONTENT] {content}")

            if not content:
                continue
                   
            with tracer.start_as_current_span("user_message") as span:
                

                content_obj = Content(role="user", parts=[Part.from_text(text=content)])
           

                # Store user message in Firebase chat history
                firestore_session_service.store_chat_message(
                    connection_id=connection_id,
                    session_id=session_id,
                    role="user",
                    content=content  # Including embedding for potential semantic search later
                )

                
                
                # Get debug mode from state manager
                debug_mode = get_debug_mode()
                print(f"[DEBUG MODE] {debug_mode}")
                
                # Configure agent with debug mode
                run_config = RunConfig(
                    response_modalities=["text"] # Pass debug mode to agent
                )
                
                result = runner.run_async(
                    session_id=session_id, 
                    user_id=connection_id, 
                    new_message=content_obj,
                    run_config=run_config
                )
                
                span.set_attribute("input", content)
                span.set_attribute("user_id", connection_id)
                span.set_attribute("organization_id", organization_id)
                span.set_attribute("message_type", "user")
                input_token_count = len(content) // 4
                span.set_attribute("gen_ai.usage.prompt_tokens", input_token_count)
                span.set_attribute("gen_ai.response.model", "gemini-2.0-flash")

                result_text = ""
                
                async for event in result:
                    print(f"[EVENT] {event.content}")
                    # Handle audio events as before
                    is_audio = event.content and event.content.parts and event.content.parts[0].inline_data and event.content.parts[0].inline_data.mime_type.startswith("audio/pcm")
                    
                    if is_audio:
                        audio_data = event.content.parts[0].inline_data.data
                        if audio_data:
                            message = {
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_data).decode("ascii")
                            }
                            await websocket.send_text(json.dumps(message))
                            print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                            continue
                        
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            result_text = event.content.parts[0].text
                            
                            # Store assistant response in Firebase chat history
                            firestore_session_service.store_chat_message(
                                connection_id=connection_id,
                                session_id=session_id,
                                role="assistant",
                                content=result_text # Including embedding for potential semantic search later
                            )
                            
                            span.set_attribute("output", result_text)
                            span.set_attribute("user_id", connection_id)
                            span.set_attribute("organization_id", organization_id)
                            span.set_attribute("message_type", "assistant")
                            output_token_count = len(result_text) // 4
                            span.set_attribute("gen_ai.usage.completion_tokens", output_token_count)
                            span.set_attribute("gen_ai.usage.total_tokens", output_token_count)
                            span.set_attribute("gen_ai.response.model", "gemini-2.0-flash")
                            print(f"[DEBUG] {result_text}", flush=True)

                            # Create Langfuse trace for this assistant message
                            # trace = langfuse.trace(
                            #     name="assistant_message",
                            #     user_id=connection_id,
                            #     metadata={
                            #         "session_id": str(session_id),
                            #         "organization_id": organization_id,
                            #     },
                            # )
                            trace_id = format(span.get_span_context().trace_id, '032x')
                            print(f"Trace ID: {trace_id}")

                trace_id = format(span.get_span_context().trace_id, '032x')
                print(f"Trace ID: {trace_id}")

                await websocket.send_text(json.dumps({
                    "mime_type": "text/plain",
                    "data": result_text,
                    "traceId": trace_id if 'trace_id' in locals() else None,
                    "turn_complete": True,
                    "is_speech": True,
                    "session_id": session_id  # Send the session ID back to client
                }))
                
    except WebSocketDisconnect:
        print(f"[DISCONNECTED] #{session_id}")
    except Exception as e:
        print(f"[ERROR] WebSocket failure: {e}")
        await websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": f"Error: {str(e)}",
            "error": True
        }))

@app.get("/api/chat/history")
async def get_chat_history(connection_id: str = Query(...)):
    try:
        print(f"[DEBUG] Getting chat history for {connection_id}")
        # Get the chat_history document
        chat_ref = firestore_session_service.collection.document(connection_id)\
            .collection('chat_history')\
            .document('messages')
        
        doc = chat_ref.get()
        if not doc.exists:
            return []
            
        sessions_data = doc.to_dict()
        
        all_chats = []
        for session_id, messages in sessions_data.items():
            if messages:  # If session has messages
                # Use the first message for preview and timestamp
                first_message = messages[0]
                all_chats.append({
                    'session_id': session_id,
                    'timestamp': first_message.get('timestamp'),
                    'content': first_message.get('content', ''),
                    'message_count': len(messages)
                })
        
        # Sort by timestamp descending (newest first)
        all_chats.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_chats
    except Exception as e:
        logger.error(f"[GET /chat/history] {e}")
        return {"error": str(e)}, 500


@app.get("/api/general-context")
async def get_all_general_context(connection_id: str = Query(...)):
    try:
        mixpanel_dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
        if mixpanel_dataset_id:
            print(f"[INFO] Mixpanel Dataset ID for {connection_id}: {mixpanel_dataset_id}")
        messages = firestore_session_service.get_all_general_context(str(connection_id), message_type="general_context")
        return messages or []
    except Exception as e:
        logger.error(f"[GET /context/general-context] {e}")
        return {"error": str(e)}, 500


@app.post("/api/general-context/add")
async def add_general_context(request: dict):
    try:
        connection_id = request.get("connection_id")
        content = request.get("content")
        title = request.get("title")
        author = request.get("author")
        created_at = request.get("created_at")
        updated_at = request.get("updated_at")
        message_type = request.get("message_type", "general_context")

        if not connection_id or not content:
            return {"error": "connection_id and content are required"}, 400

        firestore_session_service.append_message(
            str(connection_id),
            "user",
            content,
            message_type=message_type,
            include_embedding=True,
            title=title,
            author=author,
            created_at=created_at,
            updated_at=updated_at
        )
        return {"success": True, "message": "Content added successfully"}
    except Exception as e:
        logger.error(f"[POST /general-context/add] {e}")
        return {"error": str(e)}, 500


@app.put("/api/general-context/update")
async def update_general_context(request: dict):
    try:
        connection_id = request.get("connection_id")
        index = request.get("index")
        new_content = request.get("new_content")
        new_title = request.get("new_title")
        message_type = request.get("message_type", "general-context")

        if not connection_id or index is None or not new_content:
            return {"error": "connection_id, index, and new_content are required"}, 400

        success = firestore_session_service.update_general_context_by_index(
            connection_id,
            int(index),
            new_content,
            message_type=message_type,
            new_title=new_title
        )
        if success:
            return {"success": True, "message": "Content updated successfully"}
        else:
            return {"error": "Invalid index or update failed"}, 404

    except Exception as e:
        logger.error(f"[PUT /general-context/update] {e}")
        return {"error": str(e)}, 500


@app.delete("/api/general-context/delete")
async def delete_general_context(request: dict):
    try:
        connection_id = request.get("connection_id")
        index = request.get("index")
        message_type = request.get("message_type", "general_context")

        if not connection_id or index is None:
            return {"error": "connection_id and index are required"}, 400

        success = firestore_session_service.delete_general_context_by_index(
            connection_id,
            int(index),
            message_type=message_type
        )
        if success:
            return {"success": True, "message": "Content deleted successfully"}
        else:
            return {"error": "Invalid index or delete failed"}, 404

    except Exception as e:
        logger.error(f"[DELETE /general-context/delete] {e}")
        return {"error": str(e)}, 500


@app.get("/api/business-context")
async def get_business_context(connection_id: str = Query(...)):
    try:
        business_context = firestore_session_service.get_business_context_from_firebase(connection_id)
        if business_context:
            return business_context
        else:
            # Return empty object instead of error for auto-context updating
            return {}
    except Exception as e:
        logger.error(f"[GET /business_context] {e}")
        return {"error": str(e)}, 500


@app.put("/api/business-context")
async def update_business_context(request: dict):
    try:
        connection_id = request.get("connection_id")
        business_context = request.get("business_context")
        #print(f"[DEBUG] NEW Business context: {business_context}", flush=True)

        if not connection_id or not business_context:
            return {"error": "connection_id and business_context are required"}, 400

        # Update business context in Firebase
        firestore_session_service.collection.document(connection_id).set({
            "business_context": business_context
        }, merge=True)

        #update_business_context_in_state(connection_id, business_context)
        
        return {"success": True, "message": "Business context updated successfully"}
    except Exception as e:
        logger.error(f"[PUT /business_context] {e}")
        return {"error": str(e)}, 500

@app.post("/api/set-current-connection")
async def set_current_connection(request: dict):
    try:
        connection_id = request.get("connection_id")
        
        if not connection_id:
            return {"error": "connection_id is required"}, 400

        # Set the current connection_id in the backend state
        set_current_connection_id(connection_id)
        
        return {"success": True, "message": f"Current connection_id set to {connection_id}"}
    except Exception as e:
        logger.error(f"[POST /set-current-connection] {e}")
        return {"error": str(e)}, 500

@app.get("/api/current-connection")
async def get_current_connection():
    try:
        current_id = get_current_connection_id()
        return {"connection_id": current_id}
    except Exception as e:
        logger.error(f"[GET /current-connection] {e}")
        return {"error": str(e)}, 500

@app.get("/api/events-data")
async def get_events_data(connection_id: str = Query(...)):
    client = bigquery.Client()
    dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
    query = f"""
        SELECT id, name, description, source, status, count, change, first_seen, last_seen
        FROM `{dataset_id}.events_data`
        where name != '$user'
    """
    results = client.query(query).result()
    events = []
    for row in results:
        events.append({
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "source": row.source,
            "status": row.status,
            "count": row.count,
            "change": row.change,
            "first_seen": row.first_seen,
            "last_seen": row.last_seen,
        })
    #print(f"[DEBUG] Events: {events}", flush=True)
    return events

@app.get("/api/event-properties")
async def get_event_details(connection_id: str = Query(...), event_id: str = None):
    client = bigquery.Client()
    dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
    if event_id:
        query = f"""
            SELECT event_name, name, CASE WHEN type = 'nan' THEN 'Unknown' ELSE type END as type, CASE WHEN description = 'nan' THEN 'No description available' ELSE description END as description
            FROM `{dataset_id}.event_properties_data`
            WHERE event_name = @event_id
            ORDER BY event_name ASC
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("event_id", "STRING", event_id)
            ]
        )
        results = client.query(query, job_config=job_config).result()
    else:
        query = f"""
            SELECT event_name, name, type, description
            FROM `{dataset_id}.event_details`
            ORDER BY event_name ASC
        """
        results = client.query(query).result()

    properties = []
    for row in results:
        properties.append({
            "event_name": row.event_name,
            "name": row.name,
            "type": row.type,
            "description": row.description,
        })
    #print(f"[DEBUG] Properties: {properties}", flush=True)
    return properties

@app.get("/api/annotations")
async def get_annotations(connection_id: str = Query(...)):
    # Create MixpanelClient with the provided connection_id
    client = MixpanelClient(connection_id)
    df = client.get_mixpanel_annotations_data()
    records = df.to_dict(orient="records")
    annotations = [
        {
            "id": str(row.get("id", "")),
            "date": row.get("date", ""),
            "description": row.get("description", ""),
            "user": f"{row.get('user_first_name', '')} {row.get('user_last_name', '')}".strip(),
        }
        for row in records
    ]
    print(f"[DEBUG] Annotations: {annotations}", flush=True)
    return JSONResponse(content=annotations)

@app.patch("/api/annotations/{annotation_id}")
async def patch_annotation(annotation_id: str, data: dict = Body(...), connection_id: str = Query(...)):
    client = MixpanelClient(connection_id)
    result = client.update_annotation(annotation_id, data)
    #update_annotations_in_state(connection_id, result)
    return result

@app.delete("/api/annotations/{annotation_id}")
async def delete_annotation(annotation_id: str, connection_id: str = Query(...)):
    client = MixpanelClient(connection_id)
    result = client.delete_annotation(annotation_id)
    #update_annotations_in_state(connection_id, result)
    return result

@app.post("/api/annotations")
async def create_annotation(data: dict = Body(...)):
    # Get connection_id from the request body instead of query parameter for POST
    connection_id = data.get("connection_id", "001")  # Fallback to "001" if not provided
    client = MixpanelClient(connection_id)
    description = data.get("description")
    date = data.get("date")
    result = client.create_annotation(description, date)
    return result

@app.post("/api/feedback")
async def post_feedback(request: Request):
    data = await request.json()
    trace_id = data.get("traceId")
    value = data.get("value")  # 1 for up, 0 for down

    if not trace_id or value is None:
        return {"success": False, "error": "Missing traceId or value"}

    try:
        langfuse.score(
            trace_id=trace_id,
            name="user_feedback",
            value=value,
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/user-properties")
async def get_user_properties(connection_id: str = Query(...)):
    client = bigquery.Client()
    dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
    if dataset_id:
        query = f"""
            SELECT event_name, name, CASE WHEN type = 'nan' THEN 'Unknown' ELSE type END as type, CASE WHEN description = 'nan' THEN 'No description available' ELSE description END as description
            FROM `{dataset_id}.event_properties_data`
            WHERE event_name = '$user'
            ORDER BY name ASC
        """
        results = client.query(query).result()

    properties = []
    for row in results:
        properties.append({
            "event_name": row.event_name,
            "name": row.name,
            "type": row.type,
            "description": row.description,
        })
    #print(f"[DEBUG] User Properties: {properties}", flush=True)
    return properties

@app.get("/api/chat/messages")
async def get_chat_messages(
    connection_id: str = Query(...),
    session_id: str = Query(...)
):
    try:
        messages = firestore_session_service.get_chat_messages(
            connection_id=connection_id,
            session_id=session_id
        )
        print(f"[DEBUG] Messages: {messages}")
        return messages
    except Exception as e:
        logger.error(f"[GET /chat/messages] {e}")
        return {"error": str(e)}, 500

@app.get("/api/debug-mode")
async def get_debug_mode_endpoint():
    try:
        return {"debug_mode": get_debug_mode()}
    except Exception as e:
        logger.error(f"[GET /debug-mode] {e}")
        return {"error": str(e)}, 500

@app.post("/api/debug-mode")
async def set_debug_mode_endpoint(request: dict):
    try:
        debug_mode = request.get("debug_mode")
        print(f"[DEBUG] Debug mode: {debug_mode}")
        
        if debug_mode is None:
            return {"error": "debug_mode is required"}, 400

        set_debug_mode(debug_mode)
        return {"success": True, "message": f"Debug mode set to {debug_mode}"}
    except Exception as e:
        logger.error(f"[POST /debug-mode] {e}")
        return {"error": str(e)}, 500


@app.get("/api/vendo-schema")
async def get_data_dictionary(connection_id: str = "001"):
    """
    Get data dictionary from Firebase for a specific connection.
    Events and their properties are sorted alphabetically.
    
    Args:
        connection_id (str): The connection ID to fetch data dictionary for
        
    Returns:
        dict: Sorted data dictionary from Firebase
    """
    try:
        data_dictionary = firestore_session_service.get_data_dictionary_from_firebase(connection_id)
        if data_dictionary is None:
            raise HTTPException(status_code=404, detail="Data dictionary not found")
        
        # Sort events alphabetically
        sorted_events = {}
        for event_name in sorted(data_dictionary.get("events", {}).keys()):
            event_data = data_dictionary["events"][event_name]
            
            # Sort properties alphabetically if they exist
            if "properties" in event_data:
                sorted_properties = {}
                for prop_name in sorted(event_data["properties"].keys()):
                    sorted_properties[prop_name] = event_data["properties"][prop_name]
                event_data["properties"] = sorted_properties
            
            sorted_events[event_name] = event_data
        
        # Create new dictionary with sorted events and preserve summary
        sorted_data_dictionary = {
            "summary": data_dictionary.get("summary", {}),
            "events": sorted_events
        }
        
        print(f"[DEBUG] Sorted data dictionary: {sorted_data_dictionary}", flush=True)
        return sorted_data_dictionary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/vendo-schema/update")
async def update_schema(
    connection_id: str,
    event_name: str,
    property_name: Optional[str] = None,
    description: Optional[str] = None,
    data_type: Optional[str] = None
):
    try:
        # Get the current data dictionary
        current_dict = firestore_session_service.get_data_dictionary_from_firebase(connection_id)
        if current_dict is None:
            current_dict = {"events": {}}
        
        # Ensure events dictionary exists
        if "events" not in current_dict:
            current_dict["events"] = {}
        
        # If property_name is provided, update property description/type
        if property_name:
            if event_name not in current_dict["events"]:
                current_dict["events"][event_name] = {"properties": {}}
            if "properties" not in current_dict["events"][event_name]:
                current_dict["events"][event_name]["properties"] = {}
                
            if property_name not in current_dict["events"][event_name]["properties"]:
                current_dict["events"][event_name]["properties"][property_name] = {}
                
            if description is not None:
                current_dict["events"][event_name]["properties"][property_name]["description"] = description
            if data_type is not None:
                current_dict["events"][event_name]["properties"][property_name]["data_type"] = data_type
        # Otherwise, update event description
        else:
            if event_name not in current_dict["events"]:
                current_dict["events"][event_name] = {"properties": {}}
            if description is not None:
                current_dict["events"][event_name]["description"] = description
        
        # Update the entire data dictionary in Firebase
        success = firestore_session_service.update_data_dictionary(connection_id, current_dict)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update data dictionary")
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 