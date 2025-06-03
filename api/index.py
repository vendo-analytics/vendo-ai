import os
import json
import base64
import logging
import asyncio
import numpy as np
from pathlib import Path
from datetime import date
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
from .firebase_client import FirestoreSessionService, embed_text
from .agents.agent import root_agent
from .agents.business_data.business_info import FALLBACK_CLIENT_INFO
from .tts_service import router as tts_router
from google.adk.sessions import InMemorySessionService
from .firestore_instance import firestore_session_service
from google.adk.agents.callback_context import CallbackContext
from api.state_manager import update_business_context_in_state, update_annotations_in_state, get_annotations_in_state
from google.cloud import bigquery
from fastapi.responses import JSONResponse
from api.mixpanel_client import MixpanelClient
from langfuse import Langfuse

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
async def websocket_endpoint(websocket: WebSocket, session_id: int, connection_id: str = Query(...)):
    await websocket.accept()
    print(f"[CONNECTED] #{session_id} User: {connection_id}")

    

    #session = session_service.create_session(APP_NAME, user_id, str(session_id))
    session = session_service.create_session(app_name=APP_NAME, user_id=connection_id, session_id=str(session_id))
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)
    run_config = RunConfig(response_modalities=["text"])
    organization_id = firestore_session_service.get_connection_info(connection_id).get("organization_id")
    source_id = firestore_session_service.get_connection_info(connection_id).get("source_id")
    mixpanel_details = firestore_session_service.get_mixpanel_details(organization_id, source_id)
    print(f"[DEBUG] Organization ID: {organization_id}", flush=True)

    try:
        while True:
            msg = await websocket.receive_text()
            
            data = json.loads(msg)
            content = data.get("data", "")

            if not content:
                continue
                   
            with tracer.start_as_current_span("user_message") as span:
                
                
                #session_service.append_message(str(user_id), "user", content)

                context = get_all_general_context_into_firebase (connection_id)
                

                full_input = "\n\n".join(context + [content])
                content_obj = Content(role="user", parts=[Part.from_text(text=full_input)])

                result = runner.run_async(session_id=str(session_id), user_id=connection_id, new_message=content_obj)
                
                span.set_attribute("input", full_input)
                span.set_attribute("user_id", connection_id)
                span.set_attribute("organization_id", organization_id)
                span.set_attribute("message_type", "user")
                input_token_count = len(full_input) // 4
                span.set_attribute("gen_ai.usage.prompt_tokens", input_token_count)
                span.set_attribute("gen_ai.response.model", "gemini-2.0-flash")

                result_text = ""
                
                async for event in result:
                    # 🎤 Check if this event contains audio data
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

                #session_service.append_message(str(user_id), "assistant", result_text)
                await websocket.send_text(json.dumps({
                    "mime_type": "text/plain",
                    "data": result_text,
                    "traceId": trace_id if 'trace_id' in locals() else None,
                    "turn_complete": True,
                    "is_speech": True
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
        messages = session_service.get_messages(connection_id)
        return messages
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
        message_type = request.get("message_type", "general_context")

        if not connection_id or not content:
            return {"error": "connection_id and content are required"}, 400

        firestore_session_service.append_message(
            str(connection_id),
            "user",
            content,
            message_type=message_type,
            include_embedding=True
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
        message_type = request.get("message_type", "general-context")

        if not connection_id or index is None or not new_content:
            return {"error": "connection_id, index, and new_content are required"}, 400

        success = firestore_session_service.update_requirement_by_index(
            connection_id,
            int(index),
            new_content,
            message_type=message_type
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
            return {"error": "Business context not found"}, 404
    except Exception as e:
        logger.error(f"[GET /business_context] {e}")
        return {"error": str(e)}, 500


@app.put("/api/business-context")
async def update_business_context(request: dict):
    try:
        connection_id = request.get("connection_id")
        business_context = request.get("business_context")

        if not connection_id or not business_context:
            return {"error": "connection_id and business_context are required"}, 400

        # Update business context in Firebase
        firestore_session_service.collection.document(connection_id).set({
            "business_context": business_context
        }, merge=True)

        update_business_context_in_state(connection_id, business_context)
        
        return {"success": True, "message": "Business context updated successfully"}
    except Exception as e:
        logger.error(f"[PUT /business_context] {e}")
        return {"error": str(e)}, 500

@app.get("/api/events-data")
async def get_events_data(connection_id: str = Query(...)):
    client = bigquery.Client()
    dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
    query = f"""
        SELECT id, name, description, source, status, count, change, first_seen, last_seen
        FROM `{dataset_id}.events_data`
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

@app.get("/api/event-details")
async def get_event_details(connection_id: str = Query(...), event_id: str = None):
    client = bigquery.Client()
    dataset_id = firestore_session_service.get_mixpanel_dataset_id(connection_id)
    if event_id:
        query = f"""
            SELECT event_name, name, CASE WHEN type = 'nan' THEN 'Unknown' ELSE type END as type, CASE WHEN description = 'nan' THEN 'No description available' ELSE description END as description
            FROM `{dataset_id}.event_details`
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

    properties = []
    for row in results:
        properties.append({
            "event_name": row.event_name,
            "name": row.name,
            "type": row.type,
            "description": row.description,
        })
    print(f"[DEBUG] Properties: {properties}", flush=True)
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
    update_annotations_in_state(connection_id, result)
    return result

@app.delete("/api/annotations/{annotation_id}")
async def delete_annotation(annotation_id: str, connection_id: str = Query(...)):
    client = MixpanelClient(connection_id)
    result = client.delete_annotation(annotation_id)
    update_annotations_in_state(connection_id, result)
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


