import os
import json
import base64
import logging
import asyncio
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
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
from .tts_service import router as tts_router
from google.adk.sessions import InMemorySessionService
# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Firebase session setup
APP_NAME = "ADK Non-Streaming"
firestore_session_service = FirestoreSessionService(collection_name="vendo_ai_memory")
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

def get_context(user_id: str):
    try:
        messages = firestore_session_service.get_all_messages(user_id)
        if not messages:
            return []
        contents = [msg["content"] for msg in messages if msg.get("content")]
        return contents
    except Exception as e:
        logger.error(f"[context] Error: {e}")
        return []

def get_top_k_context(user_query: str, user_id: str, k=3, min_similarity=0.0):
    try:
        query_vec = np.array(embed_text(user_query)).reshape(1, -1)
        messages = session_service.get_all_messages(user_id)
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
async def websocket_endpoint(websocket: WebSocket, session_id: int, user_id: str = Query(...)):
    await websocket.accept()
    print(f"[CONNECTED] #{session_id} User: {user_id}")

    #session = session_service.create_session(APP_NAME, user_id, str(session_id))
    session = session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=str(session_id))
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)
    run_config = RunConfig(response_modalities=["text"])

    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            content = data.get("data", "")

            if not content:
                continue

            with tracer.start_as_current_span("user_message") as span:
                span_ctx = span.get_span_context()
                active_contexts[user_id] = span_ctx
                #session_service.append_message(str(user_id), "user", content)

            context = get_context(user_id)

            full_input = "\n\n".join(context + [content])
            content_obj = Content(role="user", parts=[Part.from_text(text=full_input)])

            result = runner.run_async(session_id=str(session_id), user_id=user_id, new_message=content_obj)

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
                    break

            #session_service.append_message(str(user_id), "assistant", result_text)
            await websocket.send_text(json.dumps({
                "mime_type": "text/plain",
                "data": result_text,
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
async def get_chat_history(user_id: str = Query(...)):
    try:
        messages = session_service.get_messages(str(user_id))
        return messages
    except Exception as e:
        logger.error(f"[GET /chat/history] {e}")
        return {"error": str(e)}, 500


@app.get("/api/context/requirements")
async def get_all_requirements(user_id: str = Query(...)):
    try:
        mixpanel_dataset_id = firestore_session_service.get_user_mixpanel_dataset_id(str(user_id))
        if mixpanel_dataset_id:
            print(f"[INFO] Mixpanel Dataset ID for {user_id}: {mixpanel_dataset_id}")
        messages = firestore_session_service.get_all_requirements(str(user_id), message_type="requirements")
        return messages or []
    except Exception as e:
        logger.error(f"[GET /context/requirements] {e}")
        return {"error": str(e)}, 500


@app.post("/api/context/add")
async def add_knowledge_requirement(request: dict):
    try:
        user_id = request.get("user_id")
        content = request.get("content")
        message_type = request.get("message_type", "requirements")

        if not user_id or not content:
            return {"error": "user_id and content are required"}, 400

        firestore_session_service.append_message(
            str(user_id),
            "user",
            content,
            message_type=message_type,
            include_embedding=True
        )
        return {"success": True, "message": "Content added successfully"}
    except Exception as e:
        logger.error(f"[POST /context/add] {e}")
        return {"error": str(e)}, 500


@app.put("/api/context/update")
async def update_knowledge_requirement(request: dict):
    try:
        user_id = request.get("user_id")
        index = request.get("index")
        new_content = request.get("new_content")
        message_type = request.get("message_type", "requirements")

        if not user_id or index is None or not new_content:
            return {"error": "user_id, index, and new_content are required"}, 400

        success = firestore_session_service.update_requirement_by_index(
            str(user_id),
            int(index),
            new_content,
            message_type=message_type
        )
        if success:
            return {"success": True, "message": "Content updated successfully"}
        else:
            return {"error": "Invalid index or update failed"}, 404

    except Exception as e:
        logger.error(f"[PUT /context/update] {e}")
        return {"error": str(e)}, 500


@app.delete("/api/context/delete")
async def delete_knowledge_requirement(request: dict):
    try:
        user_id = request.get("user_id")
        index = request.get("index")
        message_type = request.get("message_type", "requirements")

        if not user_id or index is None:
            return {"error": "user_id and index are required"}, 400

        success = firestore_session_service.delete_requirement_by_index(
            str(user_id),
            int(index),
            message_type=message_type
        )
        if success:
            return {"success": True, "message": "Content deleted successfully"}
        else:
            return {"error": "Invalid index or delete failed"}, 404

    except Exception as e:
        logger.error(f"[DELETE /context/delete] {e}")
        return {"error": str(e)}, 500
