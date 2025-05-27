# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import asyncio
import base64
import traceback
import logging
import time

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from .firebase_client import FirestoreSessionService, embed_text
from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import WebSocketDisconnect
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .agents.agent import root_agent
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from .tts_service import router as tts_router

from fastapi import Request
from fastapi.responses import PlainTextResponse
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from opentelemetry.trace import set_span_in_context, SpanContext, TraceFlags, INVALID_SPAN_CONTEXT
# Load environment variables
load_dotenv()
PUSH_CHAT_TO_FIREBASE = False


LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

# Configure OpenTelemetry with Langfuse endpoint
OTEL_ENDPOINT = "https://us.cloud.langfuse.com/api/public/otel/v1/traces"
OTEL_HEADERS = {
    "Authorization": f"Basic {LANGFUSE_AUTH}"
}

active_contexts = {}

# Sets the global default tracer provider
provider = TracerProvider(
    resource=Resource.create({
        "service.name": "agent_router",
        "service.version": "1.0.0",
    })
)

class LoggingExporter(OTLPSpanExporter):
    def export(self, spans):
        print(f"[DEBUG] Exporting spans: {spans}", flush=True)
        logger.debug("Attempting to export %d spans", len(spans))
        try:
            result = super().export(spans)
            logger.debug("Export result: %s", result)
            return result
        except Exception as e:
            logger.error("Failed to export spans: %s", str(e))
            raise

# Configure the OTLP exporter with the correct endpoint and headers
exporter = LoggingExporter(
    endpoint=OTEL_ENDPOINT,
    headers=OTEL_HEADERS,
    timeout=30
)
def is_final_answer(event):
    print(f"[DEBUG] Event type: {type(event)}", flush=True)
    print(f"[DEBUG] Event dir: {dir(event)}", flush=True)

    content = getattr(event, "content", None)
    if not content:
        print("[FAIL] missing content")
        return False

    role = getattr(content, "role", None)
    print(f"[DEBUG] role (from content): {role}", flush=True)

    if role != "model":
        print("[FAIL] role check failed")
        return False

    partial = getattr(event, "partial", None)
    print(f"[DEBUG] partial: {partial}", flush=True)

    if partial:
        print("[FAIL] partial check failed")
        return False

    parts = getattr(content, "parts", None)
    if not parts or not hasattr(parts[0], "text"):
        print("[FAIL] no parts or no text attribute in first part")
        return False

    text = parts[0].text
    print(f"[DEBUG] text: {repr(text)}", flush=True)

    if not text:
        print("[FAIL] text is empty or whitespace")
        #return False

    print("[PASS] Final answer detected")
    return True


# Add error handler for the exporter
def export_error_handler(error):
    logger.error("Error exporting spans: %s", error)

provider.add_span_processor(BatchSpanProcessor(
    exporter,
    schedule_delay_millis=5000,
    max_export_batch_size=512,
    export_timeout_millis=30000
))

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent_router", "1.0.0")

app = FastAPI()

# Add CORS middleware to the main app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(tts_router)

APP_NAME = "ADK Streaming example"
session_service = FirestoreSessionService(collection_name="vendo_ai_memory")

def start_agent_session(session_id, user_id):
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service
    )
    run_config = RunConfig(response_modalities=["text"])
    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


def get_context(user_query: str, user_id: str, k=3, min_similarity=0.0):
    try:
        print(f"[DEBUG] User query: {user_query}", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to process user query: {e}")
        return []

    messages = session_service.get_all_messages(user_id)  # Changed from get_all_message_embeddings
    if not messages:
        return []
    
    # Simply return the content from all messages, up to k messages
    contents = []
    for msg in messages:
        if msg.get("content"):
            contents.append(msg["content"])
    
    return contents[:k]  # Return only up to k messages

def get_top_k_context(user_query: str, user_id: str, k=3, min_similarity=0.0):
    try:
        print(f"[DEBUG] User query: {user_query}", flush=True)
        query_vec = np.array(embed_text(user_query))
        query_vec = query_vec.reshape(1, -1)  # Ensure 2D shape
    except ValueError as e:
        print(f"[ERROR] Failed to embed user query: {e}")
        return []

    messages = session_service.get_all_messages(user_id)
    if not messages:
        return []
    scored = []
    for msg in messages:
        emb = msg.get("embedding")
        if not emb:
            continue
        try:
            emb_vec = np.array(emb).reshape(1, -1)
            score = cosine_similarity(query_vec, emb_vec)[0][0]
            if score >= min_similarity:
                scored.append((msg, score))
        except Exception as e:
            print(f"[WARN] Failed similarity calc for message: {msg.get('content')}\nError: {e}")
            continue

    top_k = sorted(scored, key=lambda x: x[1], reverse=True)[:k]
    return [msg["content"] for msg, _ in top_k]


async def agent_to_client_messaging(websocket, live_events, user_id):
    try:
        buffer = ""  # Buffer to accumulate assistant's response

        async for event in live_events:
            try:
                print(f"[DEBUG] LIVE EVENT: {event}", flush=True)

                # Process text parts
                part = event.content.parts[0] if event.content and event.content.parts else None
                if not part:
                    continue

                # Handle audio data
                if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                    audio_data = part.inline_data.data
                    if audio_data:
                        await websocket.send_text(json.dumps({
                            "mime_type": "audio/pcm",
                            "data": base64.b64encode(audio_data).decode("ascii")
                        }))
                    continue

                # Accumulate text
                if part.text and part.text not in buffer:
                    buffer += part.text

                # Send when final response is received
                if event.is_final_response():
                    print("🎉 Final text part received")
                    
                    # Prepare tracing context
                    parent_span_context = active_contexts.get(user_id)
                    from opentelemetry.trace import NonRecordingSpan, set_span_in_context, INVALID_SPAN_CONTEXT
                    if parent_span_context:
                        parent_span = NonRecordingSpan(parent_span_context)
                        new_ctx = set_span_in_context(parent_span)
                    else:
                        new_ctx = set_span_in_context(NonRecordingSpan(INVALID_SPAN_CONTEXT))

                    # Send final message with OpenTelemetry span
                    with tracer.start_as_current_span("completion", context=new_ctx) as span:
                        cleaned_buffer = buffer.strip()
                        span.set_attribute("output", cleaned_buffer)
                        span.set_attribute("user_id", user_id)
                        span.set_attribute("message_type", "assistant")
                        output_token_count = len(cleaned_buffer) // 4
                        span.set_attribute("gen_ai.usage.completion_tokens", output_token_count)
                        span.set_attribute("gen_ai.usage.total_tokens", output_token_count)
                        span.set_attribute("gen_ai.response.model", "gemini-2.0-flash-live-001")

                        # Store in session service
                        session_service.append_message(str(user_id), "assistant", buffer, message_type="messages", include_embedding=False)

                        # Send to client
                        await websocket.send_text(json.dumps({
                            "mime_type": "text/plain",
                            "data": buffer,
                            "is_speech": True,
                            "turn_complete": True,
                            "interrupted": False
                        }))
                    
                    # Reset buffer
                    buffer = ""

            except Exception as e:
                logger.error(f"Processing stream event: {str(e)}")
                await websocket.send_text(json.dumps({
                    "mime_type": "text/plain",
                    "data": f"Error: {str(e)}",
                    "error": True
                }))

    except Exception as e:
        logger.error(f"Outer agent_to_client_messaging: {str(e)}")
        await websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": f"Fatal error: {str(e)}",
            "error": True
        }))
        await websocket.send_text(json.dumps({"turn_complete": True}))

async def client_to_agent_messaging(websocket, user_id, live_request_queue):
    try:
        while True:
            
            
            message = await websocket.receive_text()
            data = json.loads(message)
            content = data.get("data", "")
            
            if data.get("mime_type") == "text/plain":
                with tracer.start_as_current_span("user_message") as span:
                    span_context = span.get_span_context()  # ✅ This is correct
                    active_contexts[user_id] = span_context 
                    span.set_attribute("user_id", user_id)
                    span.set_attribute("message_type", "user")
                    # Set both attribute and event data
                    span.set_attribute("message_content", content)
                    span.set_attribute("input", content)
                    input_token_count = len(content) // 4
                    # Use proper OpenTelemetry Gen AI conventions
                    span.set_attribute("gen_ai.usage.prompt_tokens", int(input_token_count))
                    span.set_attribute("gen_ai.usage.total_tokens", int(input_token_count))
                    span.set_attribute("gen_ai.request.model", "gemini-2.0-flash-live-001")
                    
                    session_service.append_message(str(user_id), "user", content, message_type="messages", include_embedding=False)
                    context = get_context(content, user_id)
                    full_input = "\n\n".join(context + [content])
                    live_request_queue.send_content(Content(role="user", parts=[Part.from_text(text=full_input)]))
            elif data.get("mime_type") == "audio/state":
                span.set_attribute("audio_state", data.get('is_recording', False))
                logger.debug(f"Audio state change: is_recording={data.get('is_recording', False)}")
                        
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected")
    except Exception as e:
        logger.error(f"client_to_agent_messaging: {str(e)}")
        span = trace.get_current_span()
        if span:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))



@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    user_id: str = Query(...),
):
    
    try:
        await websocket.accept()
        print(f"Client #{session_id} connected (User: {user_id})", flush=True)
        
        # Create one session and runner for the entire WebSocket connection
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=str(session_id),
        )
        
        runner = Runner(
            app_name=APP_NAME,
            agent=root_agent,
            session_service=session_service
        )
        
        # Create initial run config
        run_config = RunConfig(response_modalities=["text"])
        
        print(f"[DEBUG] Created session and runner for WebSocket connection", flush=True)
        
        # Create a shared request queue
        live_request_queue = LiveRequestQueue()
        live_events = runner.run_live(
            session=session,
            live_request_queue=live_request_queue,
            run_config=run_config,
        )
        
        # Pass the shared session, runner, and request queue to the message handlers
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events, user_id)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, user_id, live_request_queue)
        )
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
    except Exception as e:
        print(f"Error in websocket endpoint: {e}", flush=True)
        await websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": f"Error in websocket endpoint: {str(e)}",
            "error": True
        }))
    finally:
        print(f"Client #{session_id} disconnected", flush=True)

@app.get("/api/chat/history")
async def get_chat_history(user_id: str = Query(...)):
    try:
        # Get messages for the user from Firebase
        messages = session_service.get_messages(str(user_id))
        return messages
    except Exception as e:
        print(f"[ERROR] Failed to get chat history: {str(e)}", flush=True)
        return {"error": str(e)}, 500

@app.get("/api/context/requirements")
async def get_all_requirements(user_id: str = Query(...)):
    try:
        print(f"[DEBUG] Getting all requirements for user: {user_id}", flush=True)
        
        # Get the user's mixpanel_dataset_id and print it
        mixpanel_dataset_id = session_service.get_user_mixpanel_dataset_id(str(user_id))
        if mixpanel_dataset_id:
            print(f"[INFO] User {user_id} Mixpanel Dataset ID: {mixpanel_dataset_id}", flush=True)
        
        # Get requirements/knowledge content for the user
        messages = session_service.get_all_requirements(str(user_id), message_type="requirements")
        return messages or []
    except Exception as e:
        print(f"[ERROR] Failed to get knowledge content: {str(e)}", flush=True)
        return {"error": str(e)}, 500

@app.post("/api/context/add")
async def add_knowledge_requirement(request: dict):
    try:
        user_id = request.get("user_id")
        content = request.get("content")
        message_type = request.get("message_type", "requirements")
        
        if not user_id or not content:
            return {"error": "user_id and content are required"}, 400
            
        session_service.append_message(
            str(user_id), 
            "user", 
            content, 
            message_type=message_type, 
            include_embedding=True
        )
        return {"success": True, "message": "Content added successfully"}
    except Exception as e:
        print(f"[ERROR] Failed to add knowledge content: {str(e)}", flush=True)
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
            
        success = session_service.update_requirement_by_index(
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
        print(f"[ERROR] Failed to update knowledge content: {str(e)}", flush=True)
        return {"error": str(e)}, 500

@app.delete("/api/context/delete")
async def delete_knowledge_requirement(request: dict):
    try:
        user_id = request.get("user_id")
        index = request.get("index")
        message_type = request.get("message_type", "requirements")
        
        if not user_id or index is None:
            return {"error": "user_id and index are required"}, 400
            
        success = session_service.delete_requirement_by_index(
            str(user_id), 
            int(index), 
            message_type=message_type
        )
        
        if success:
            return {"success": True, "message": "Content deleted successfully"}
        else:
            return {"error": "Invalid index or delete failed"}, 404
            
    except Exception as e:
        print(f"[ERROR] Failed to delete knowledge content: {str(e)}", flush=True)
        return {"error": str(e)}, 500
