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

# Load environment variables
load_dotenv()
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()
 
#OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("LANGFUSE_HOST") + "/api/public/otel"
OTEL_EXPORTER_OTLP_HEADERS = f"Authorization=Basic {LANGFUSE_AUTH}"
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

def get_top_k_context(user_query: str, user_id: str, k=3, min_similarity=0.7):
    try:
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
                    # Check if this text is already in the buffer to prevent duplication
                    if part.text not in buffer:
                        # Accumulate the text in buffer
                        buffer += part.text

                    # Add debug logging for each condition
                    is_final = getattr(event, 'is_final_response', lambda: False)()
                    is_turn_complete = getattr(event, 'turn_complete', False)
                    print(f"[DEBUG] Message conditions - is_final: {is_final}, turn_complete: {is_turn_complete}", flush=True)
                    print(f"[DEBUG] Current buffer content: {buffer}", flush=True)

                    # Send immediately for single events
                    if buffer:
                        # Store assistant message in Firebase
                        session_service.append_message(str(user_id), "assistant", buffer)
                        print(f"[DEBUG] Sending single event message", flush=True)
                        await websocket.send_text(json.dumps({
                            "mime_type": "text/plain",
                            "data": buffer,
                            "is_speech": True,
                            "turn_complete": True,
                            "interrupted": False
                        }))
                        buffer = ""  # Clear the buffer
                        print("[DEBUG] Buffer cleared", flush=True)

            except Exception as e:
                print(f"[ERROR] Processing single event: {str(e)}", flush=True)
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
                    # Check if this text is already in the buffer to prevent duplication
                    if part.text not in buffer:
                        # Accumulate the text in buffer
                        buffer += part.text

                    # Add debug logging for each condition
                    is_final = getattr(event, 'is_final_response', lambda: False)()
                    is_turn_complete = getattr(event, 'turn_complete', False)
                    print(f"[DEBUG] Message conditions - is_final: {is_final}, turn_complete: {is_turn_complete}", flush=True)
                    print(f"[DEBUG] Current buffer content: {buffer}", flush=True)

                    # Only send if this is truly the final response (no more coming)
                    current_time = asyncio.get_event_loop().time()
                    if is_final:
                        response_count += 1
                        last_response_time = current_time
                        # Wait a short time to see if more responses are coming
                        await asyncio.sleep(1)
                        
                        # If no new responses have come in after waiting, this is truly the final one
                        if current_time == last_response_time:
                            # Store assistant message in Firebase
                            session_service.append_message(str(user_id), "assistant", buffer)
                            print(f"[DEBUG] Sending complete assistant message after {response_count} responses", flush=True)
                            await websocket.send_text(json.dumps({
                                "mime_type": "text/plain",
                                "data": buffer,
                                "is_speech": True,
                                "turn_complete": True,
                                "interrupted": False
                            }))
                            buffer = ""  # Clear the buffer
                            response_count = 0  # Reset response count
                            print("[DEBUG] Buffer cleared", flush=True)

            except Exception as e:
                print(f"[ERROR] Inner agent_to_client_messaging: {str(e)}", flush=True)
                await websocket.send_text(json.dumps({
                    "mime_type": "text/plain",
                    "data": f"Error: {str(e)}",
                    "error": True
                }))

    except Exception as e:
        print(f"[ERROR] Outer agent_to_client_messaging: {str(e)}", flush=True)
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
                # Store user message in Firebase
                
                session_service.append_message(str(user_id), "user", content)
                context = get_top_k_context(content, user_id)
                full_input = "\n\n".join(context + [content])
                live_request_queue.send_content(Content(role="user", parts=[Part.from_text(text=full_input)]))
                #live_request_queue.send_content(Content(role="user", parts=[Part.from_text(text=content)]))
            elif data.get("mime_type") == "audio/state":
                # Handle audio state changes
                is_recording = data.get("is_recording", False)
                print(f"[DEBUG] Audio state change: is_recording={is_recording}", flush=True)
    except WebSocketDisconnect:
        print("[DEBUG] WebSocket disconnected", flush=True)
    except Exception as e:
        print(f"[ERROR] client_to_agent_messaging: {str(e)}", flush=True)

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
