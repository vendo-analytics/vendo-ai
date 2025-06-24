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
from pydantic import BaseModel

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

@app.get("/")
async def root():
    """Root endpoint for ADK Web Server"""
    return {
        "message": "ADK Web Server is running",
        "status": "active",
        "websocket_endpoint": "/ws/{session_id}?connection_id={connection_id}",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "available_endpoints": [
            "/api/chat/history",
            "/api/general-context", 
            "/api/business-context",
            "/api/events-data",
            "/api/annotations",
            "/api/user-properties",
            "/api/debug-mode",
            "/api/mixpanel-event-schema"
        ]
    }

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
    is_first_message = True

    try:
        while True:
            print("[WAITING] for client message")
            msg = await websocket.receive_text()
            print(f"[RECEIVED] {msg}")
            data = json.loads(msg)

            # Skip pings and other non-data messages
            if data.get("type") == "ping":
                continue

            content = data.get("data", "")
            print(f"[CONTENT] {content}")

            if not content:
                continue
                   
            with tracer.start_as_current_span("user_message") as span:
                # Store user message in Firebase chat history
                firestore_session_service.store_chat_message(
                    connection_id=connection_id,
                    session_id=session_id,
                    role="user",
                    content=content
                )

                # Generate summary for first message
                if is_first_message:
                    # Create a separate session for summary generation
                    summary_session = session_service.create_session(
                        app_name=APP_NAME,
                        user_id=connection_id,
                        session_id=f"{session_id}_summary"
                    )
                    
                    summary_prompt = f"""You are a summarization assistant. Your task is to summarize the user's message by identifying their intent, topic, and any specific questions they're asking. DO NOT answer their question - only summarize what they're asking about. Restrict to 30 charactrers max

                            For example:
                            User: "What's the weather like in New York?"
                            Summary: "Current weather conditions in New York City"

                            User: "Can you help me fix my broken laptop screen?"
                            Summary: "Assistance with laptop screen repair"

                            Now, please summarize this user message:
                            {content}

                            Summary:"""
                    
                    summary_content = Content(role="user", parts=[Part.from_text(text=summary_prompt)])
                    summary_result = runner.run_async(
                        session_id=f"{session_id}_summary",  # Use separate session for summary
                        user_id=connection_id,
                        new_message=summary_content,
                        run_config=run_config
                    )
                    
                    summary_text = ""
                    async for event in summary_result:
                        if event.is_final_response():
                            if event.content and event.content.parts:
                                summary_text = event.content.parts[0].text
                                print(f"[DEBUG] Message Summary: {summary_text}", flush=True)
                                # Store summary in Firebase
                                firestore_session_service.store_chat_message(
                                    connection_id=connection_id,
                                    session_id=session_id,
                                    role="summary",
                                    content=f"Message Summary: {summary_text}"
                                )
                    is_first_message = False
                
                # Get debug mode from state manager
                debug_mode = get_debug_mode()
                print(f"[DEBUG MODE] {debug_mode}")
                
                # Configure agent with debug mode
                run_config = RunConfig(
                    response_modalities=["text"]
                )
                
                # Create content object for the actual response
                content_obj = Content(role="user", parts=[Part.from_text(text=content)])
                
                # Get the actual response using the main session
                result = runner.run_async(
                    session_id=session_id,  # Use main session for actual response
                    user_id=connection_id, 
                    new_message=content_obj,
                    run_config=run_config
                )
                
                

                result_text = ""
                
                async for event in result:
                    
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
                            if event.usage_metadata:
                                input_token_count = event.usage_metadata.prompt_token_count
                                output_token_count = event.usage_metadata.candidates_token_count
                            else:
                                input_token_count = len(content) // 4
                                output_token_count = len(result_text) // 4
                            
                            # Store assistant response in Firebase chat history
                            firestore_session_service.store_chat_message(
                                connection_id=connection_id,
                                session_id=session_id,
                                role="assistant",
                                content=result_text
                            )
                            span.set_attribute("input", content)
                            span.set_attribute("user_id", connection_id)
                            span.set_attribute("organization_id", organization_id)
                            span.set_attribute("gen_ai.usage.prompt_tokens", input_token_count)
                            span.set_attribute("gen_ai.response.model", "gemini-2.0-flash")
                            span.set_attribute("output", result_text)
                            span.set_attribute("gen_ai.usage.completion_tokens", output_token_count)
                            span.set_attribute("gen_ai.usage.total_tokens", input_token_count + output_token_count)
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
                    "session_id": session_id
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
                # Find the summary message
                summary = None
                first_message = None
                for msg in messages:
                    if msg.get('role') == 'summary':
                        summary = msg.get('content', '').replace('Message Summary: ', '')
                    elif not first_message:
                        first_message = msg
                
                # Use summary as title if available, otherwise use first message
                title = summary if summary else first_message.get('content', '')
                
                all_chats.append({
                    'session_id': session_id,
                    'timestamp': first_message.get('timestamp'),
                    'content': title,
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
    print(f"[DEBUG] Events: {events}", flush=True)
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
        """
        results = client.query(query).result()

#     properties = []
#     for row in results:
#         properties.append({
#             "event_name": row.event_name,
#             "name": row.name,
#             "type": row.type,
#             "description": row.description,
#         })
#     #print(f"[DEBUG] Properties: {properties}", flush=True)
#     return properties

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
    connection_id = data.get("connection_id", "gb1uauyn0Khjcs4Fgxh8")  # Fallback to "001" if not provided
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

@app.put("/api/user-properties/update")
async def update_user_property(
    connection_id: str = Query(...),
    property_name: str = Query(...),
    description: str = Query(...),
    type: str = Query(...)
):
    try:
        print(f"[DEBUG] Updating user property: {property_name} for connection {connection_id}")
        print(f"[DEBUG] New values - description: {description}, type: {type}")
        
        # Load or initialize user_edits
        user_properties_edits = firestore_session_service.get_mixpanel_user_properties_edits(connection_id)
        print(f"[DEBUG] Current user edits: {user_properties_edits}")
        
        if user_properties_edits is None:
            print("[DEBUG] No existing edits found, initializing empty dict")
            user_properties_edits = {}
        
        # Update property description and type
        user_properties_edits[property_name] = {
            "description": description,
            "type": type
        }
        print(f"[DEBUG] Updated user edits: {user_properties_edits}")
        
        # Save user edits
        success = firestore_session_service.update_mixpanel_user_properties_edits(connection_id, user_properties_edits)
        if not success:
            print("[ERROR] Failed to update user edits in Firebase")
            raise HTTPException(status_code=500, detail="Failed to update user edits in Firebase")
        
        print("[DEBUG] Successfully updated user property")
        return {"success": True}
    
    except Exception as e:
        print(f"[ERROR] Failed to update user property: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-properties")
async def get_user_properties(connection_id: str = Query(...)):
    try:
        client = bigquery.Client()
        dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
        if not dataset_id:
            raise HTTPException(status_code=404, detail="Dataset not found for connection")

        # Load raw user properties from BigQuery
        query = f"""
            SELECT event_name, name, 
                   CASE WHEN type = 'nan' THEN 'Unknown' ELSE type END as type,
                   CASE WHEN description = 'nan' THEN 'No description available' ELSE description END as description,
                   sample_value
            FROM `{dataset_id}.event_properties_data`
            WHERE event_name = '$user'
            ORDER BY name ASC
        """
        results = client.query(query).result()

        # Load user edits from Firebase
        user_properties_edits = firestore_session_service.get_mixpanel_user_properties_edits(connection_id) or {}

        # Merge edits with raw
        properties = []
        for row in results:
                prop_name = row.name
                merged = {
                "event_name": row.event_name,
                    "name": prop_name,
                    "type": user_properties_edits.get(prop_name, {}).get("type", row.type),
                    "description": user_properties_edits.get(prop_name, {}).get("description", row.description),
                    "sample_value": row.sample_value
                }
                properties.append(merged)

        
        return properties

    except Exception as e:
        print(f"[ERROR] Failed to get user properties: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))


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

        # Filter out summary messages
        filtered_messages = [msg for msg in messages if msg.get('role') != 'summary']
        print(f"[DEBUG] Filtered Messages: {filtered_messages}")
        return filtered_messages
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


@app.get("/api/mixpanel-event-schema")
async def get_mixpanel_event_schema(connection_id: str = "gb1uauyn0Khjcs4Fgxh8"):
    """
    Get merged Mixpanel Event Schema (raw + user edits) from Firebase for a specific connection.
    Events and their properties are sorted alphabetically.
    
    Args:
        connection_id (str): The connection ID to fetch Mixpanel Event Schema for
        
    Returns:
        dict: Merged and sorted Mixpanel Event Schema
    """
    try:
        raw_schema = firestore_session_service.get_mixpanel_event_schema(connection_id) or {"events": {}}
        user_edits = firestore_session_service.get_mixpanel_event_schema_edits(connection_id) or {"events": {}}
        
        # Merge schemas
        merged_schema = {"events": {}}
        for event_name, event_data in raw_schema.get("events", {}).items():
            merged_event = dict(event_data)  # shallow copy
            user_event = user_edits.get("events", {}).get(event_name, {})

            # Override event-level description if edited
            if "description" in user_event:
                merged_event["description"] = user_event["description"]

            # Merge properties
            merged_event["properties"] = {}
            for prop_name, prop_data in event_data.get("properties", {}).items():
                merged_prop = dict(prop_data)
                user_prop = user_event.get("properties", {}).get(prop_name, {})

                if "description" in user_prop:
                    merged_prop["description"] = user_prop["description"]
                if "data_type" in user_prop:
                    merged_prop["data_type"] = user_prop["data_type"]

                merged_event["properties"][prop_name] = merged_prop

            merged_schema["events"][event_name] = merged_event

        # Optional: bring over summary if needed
        if "summary" in raw_schema:
            merged_schema["summary"] = raw_schema["summary"]

        # Sort the events and their properties alphabetically
        sorted_events = {}
        for event_name in sorted(merged_schema.get("events", {})):
            event_data = merged_schema["events"][event_name]
            if "properties" in event_data:
                event_data["properties"] = {
                    k: event_data["properties"][k]
                    for k in sorted(event_data["properties"].keys())
                }
            sorted_events[event_name] = event_data

        sorted_schema = {
            "summary": merged_schema.get("summary", {}),
            "events": sorted_events
        }

        print(f"[DEBUG] Merged & Sorted Schema: {sorted_schema}", flush=True)
        return sorted_schema

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
@app.put("/api/mixpanel-event-schema/update")
async def update_mixpanel_event_schema(
    connection_id: str,
    event_name: str,
    property_name: Optional[str] = None,
    description: Optional[str] = None,
    data_type: Optional[str] = None
):
    try:
        # Load or initialize user_edits
        mixpanel_event_schema_edits = firestore_session_service.get_mixpanel_event_schema_edits(connection_id)
        if mixpanel_event_schema_edits is None:
            mixpanel_event_schema_edits = {"events": {}}
        
        # Ensure event structure exists
        event = mixpanel_event_schema_edits["events"].setdefault(event_name, {"properties": {}})
        
        # If editing a property description/type
        if property_name:
            prop = event["properties"].setdefault(property_name, {})
            if description is not None:
                prop["description"] = description
            if data_type is not None:
                prop["data_type"] = data_type
        # If editing event description
        else:
            if description is not None:
                event["description"] = description
        
        # Save user edits only
        success = firestore_session_service.update_mixpanel_event_schema_edits(connection_id, mixpanel_event_schema_edits)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user edits")
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 



@app.get("/api/mixpanel-events/query")
async def query_mixpanel_events(connection_id: str = Query(...)):
    """
    Query the Mixpanel Event Schema to return all events, descriptions, and properties
    in a structured format suitable for analysis.
    
    Args:
        connection_id (str): The connection ID to fetch data for
        
    Returns:
        dict: Structured event schema with events, descriptions, and properties
    """
    try:
        from .agents.sub_agents.data_retrieval.tools import query_mixpanel_event_schema
        result = query_mixpanel_event_schema(connection_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mixpanel-events/event/{event_name}")
async def get_mixpanel_event_by_name(event_name: str, connection_id: str = Query(...)):
    """
    Get a specific event by name from the schema.
    
    Args:
        event_name (str): The name of the event to retrieve
        connection_id (str): The connection ID to fetch data for
        
    Returns:
        dict: Event information or 404 if not found
    """
    try:
        from .agents.sub_agents.data_retrieval.tools import get_event_by_name
        result = get_event_by_name(event_name, connection_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Event '{event_name}' not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mixpanel-events/property/{property_name}")
async def get_mixpanel_events_by_property(property_name: str, connection_id: str = Query(...)):
    """
    Get all events that contain a specific property.
    
    Args:
        property_name (str): The name of the property to search for
        connection_id (str): The connection ID to fetch data for
        
    Returns:
        list: List of events that contain the specified property
    """
    try:
        from .agents.sub_agents.data_retrieval.tools import get_events_by_property
        result = get_events_by_property(property_name, connection_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mixpanel-events/search")
async def search_mixpanel_events_by_description(search_term: str = Query(...), connection_id: str = Query(...)):
    """
    Search for events by description content.
    
    Args:
        search_term (str): The term to search for in event descriptions
        connection_id (str): The connection ID to fetch data for
        
    Returns:
        list: List of events whose descriptions contain the search term
    """
    try:
        from .agents.sub_agents.data_retrieval.tools import search_events_by_description
        result = search_events_by_description(search_term, connection_id)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


class SlackTextRequest(BaseModel):
    prompt: str
    connection_id: str = "slack_user"
    session_id: str = None

@app.post("/api/slack-text")
async def slack_text_endpoint(request: SlackTextRequest):
    """
    Accepts a prompt from Slack, runs the root_agent, and returns a plain text response.
    """
    # Use a unique session_id if not provided
    session_id = request.session_id or f"slack_{int(datetime.now().timestamp())}"
    connection_id = request.connection_id or "slack_user"
    # Create session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=connection_id,
        session_id=session_id
    )
    set_current_connection_id(connection_id)
    set_current_session_id(session_id)
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)
    run_config = RunConfig(response_modalities=["text"])
    content_obj = Content(role="user", parts=[Part.from_text(text=request.prompt)])
    result_text = ""
    try:
        result = runner.run_async(
            session_id=session_id,
            user_id=connection_id,
            new_message=content_obj,
            run_config=run_config
        )
        async for event in result:
            if event.is_final_response():
                if event.content and event.content.parts:
                    result_text = event.content.parts[0].text
                    break
    except Exception as e:
        result_text = f"Error: {str(e)}"
    return {"text": result_text} 

@app.get("/api/companies")
async def get_companies():
    try:
        companies = firestore_session_service.list_companies()
        print(f"[DEBUG] Companies: {companies}", flush=True)
        # Filter companies for only "Piri Red"
        filtered_companies = [company for company in companies if company.get('name') == 'Piri']
        print(f"[DEBUG] Filtered Companies: {filtered_companies}", flush=True)
        return filtered_companies
    except Exception as e:
        logger.error(f"[GET /api/companies] {e}")
        raise HTTPException(status_code=500, detail=str(e))