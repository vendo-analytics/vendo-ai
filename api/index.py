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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import WebSocketDisconnect
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .agents.agents import root_agent
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

# Sets the global default tracer provider
provider = TracerProvider(
    resource=Resource.create({
        "service.name": "agent_router",
        "service.version": "1.0.0",
    })
)

class LoggingExporter(OTLPSpanExporter):
    def export(self, spans):
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

def get_top_k_context(user_query: str, user_id: str, k=3, min_similarity=0.0):
    try:
        print(f"[DEBUG] User query: {user_query}", flush=True)
        query_vec = np.array(embed_text(user_query))
        query_vec = query_vec.reshape(1, -1)  # Ensure 2D shape
    except ValueError as e:
        print(f"[ERROR] Failed to embed user query: {e}")
        return []

    messages = session_service.get_all_message_embeddings(user_id)
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
        response_count = 0  # Track number of responses
        last_response_time = None  # Track time of last response
        
        with tracer.start_as_current_span("agent_response") as span:
            span.set_attribute("user_id", user_id)
            
            # If live_events is a list, handle single event
            if isinstance(live_events, list):
                event = live_events[0]
                try:
                    part: Part = event.content.parts[0] if event.content and event.content.parts else None
                    if not part:
                        return

                    if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                        audio_data = part.inline_data.data
                        if audio_data:
                            await websocket.send_text(json.dumps({
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_data).decode("ascii")
                            }))
                            return

                    if part.text:
                        if part.text not in buffer:
                            buffer += part.text

                        if buffer:
                            session_service.append_message(str(user_id), "assistant", buffer, message_type="messages", include_embedding=False)
                            await websocket.send_text(json.dumps({
                                "mime_type": "text/plain",
                                "data": buffer,
                                "is_speech": True,
                                "turn_complete": True,
                                "interrupted": False
                            }))
                            buffer = ""

                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    logger.error(f"Processing single event: {str(e)}")
                    await websocket.send_text(json.dumps({
                        "mime_type": "text/plain",
                        "data": f"Error: {str(e)}",
                        "error": True
                    }))
                return

            # Handle async iterator for live events
            async for event in live_events:
                try:
                    part: Part = event.content.parts[0] if event.content and event.content.parts else None
                    if not part:
                        continue

                    if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                        audio_data = part.inline_data.data
                        if audio_data:
                            await websocket.send_text(json.dumps({
                                "mime_type": "audio/pcm",
                                "data": base64.b64encode(audio_data).decode("ascii")
                            }))
                            continue

                    if part.text:
                        if part.text not in buffer:
                            buffer += part.text

                        is_final = getattr(event, 'is_final_response', lambda: False)()
                        current_time = asyncio.get_event_loop().time()
                        if is_final:
                            response_count += 1
                            last_response_time = current_time
                            await asyncio.sleep(1)
                            
                            if current_time == last_response_time:
                                session_service.append_message(str(user_id), "assistant", buffer, message_type="messages", include_embedding=False)
                                await websocket.send_text(json.dumps({
                                    "mime_type": "text/plain",
                                    "data": buffer,
                                    "is_speech": True,
                                    "turn_complete": True,
                                    "interrupted": False
                                }))
                                buffer = ""
                                response_count = 0

                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
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
            with tracer.start_as_current_span("user_message") as span:
                message = await websocket.receive_text()
                data = json.loads(message)
                content = data.get("data", "")
                
                if data.get("mime_type") == "text/plain":
                    session_service.append_message(str(user_id), "user", content, message_type="messages", include_embedding=False)
                    context = get_top_k_context(content, user_id)
                    full_input = "\n\n".join(context + [content])
                    live_request_queue.send_content(Content(role="user", parts=[Part.from_text(text=full_input)]))
                elif data.get("mime_type") == "audio/state":
                    logger.debug(f"Audio state change: is_recording={data.get('is_recording', False)}")
                    
    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected")
    except Exception as e:
        logger.error(f"client_to_agent_messaging: {str(e)}")
        span = trace.get_current_span()
        if span:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))

app = FastAPI()

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
