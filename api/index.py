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
from .firebase_client import FirestoreSessionService
from .firebase_client import FirestoreMemoryService
from fastapi import FastAPI, WebSocket, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .agents.agents import root_agent

# Load environment variables
load_dotenv()

APP_NAME = "ADK Streaming example"
session_service = FirestoreSessionService(collection_name="vendo_ai_memory")
def start_agent_session(session_id, user_id, is_audio=False):
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
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])
    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events, user_id):
    try:
        async for event in live_events:
            try:
                if event.turn_complete or event.interrupted:
                    await websocket.send_text(json.dumps({
                        "turn_complete": event.turn_complete,
                        "interrupted": event.interrupted
                    }))
                    continue
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
                    # Only save assistant message if this is the final response for the turn
                    if getattr(event, 'is_final_response', lambda: False)() or getattr(event, 'turn_complete', False):
                        session_service.append_message(str(user_id), "assistant", part.text)
                    print(f"[DEBUG] Sending assistant message: {part.text}", flush=True)
                    await websocket.send_text(json.dumps({
                        "mime_type": "text/plain",
                        "data": part.text,
                        "is_speech": True
                    }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "mime_type": "text/plain",
                    "data": f"Error: {str(e)}",
                    "error": True
                }))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": f"Fatal error: {str(e)}",
            "error": True
        }))
        await websocket.send_text(json.dumps({"turn_complete": True}))

async def client_to_agent_messaging(websocket, live_request_queue, user_id):
    try:
        while True:
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            mime_type = message.get("mime_type")
            data = message.get("data", "")
            is_partial = message.get("is_partial", False)
            if mime_type == "text/plain" and not is_partial and data.strip():
                print(f"[DEBUG] Received user message: {data}", flush=True)
                # Retrieve history for context
                history = session_service.get_messages(str(user_id))
                print(f"[DEBUG] About to send to agent: {data}", flush=True)
                live_request_queue.send_content(Content(role="user", parts=[Part.from_text(text=data)]))
                print(f"[DEBUG] Sent to agent: {data}", flush=True)
            elif mime_type == "audio/pcm":
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": f"Fatal error: {str(e)}",
            "error": True
        }))
        await websocket.send_text(json.dumps({"turn_complete": True}))

app = FastAPI()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    user_id: str = Query(...),
    is_audio: str = Query("false")
):
    try:
        await websocket.accept()
        print(f"Client #{session_id} connected (User: {user_id}, Audio: {is_audio})", flush=True)
        live_events, live_request_queue = start_agent_session(
            session_id=str(session_id),
            user_id=user_id,
            is_audio=is_audio == "true"
        )
        agent_to_client_task = asyncio.create_task(agent_to_client_messaging(websocket, live_events, user_id))
        client_to_agent_task = asyncio.create_task(client_to_agent_messaging(websocket, live_request_queue, user_id))
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
