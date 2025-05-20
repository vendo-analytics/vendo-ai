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
from .firebase_client import FirestoreSessionService
from .firebase_client import FirestoreMemoryService
from fastapi import FastAPI, WebSocket, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import WebSocketDisconnect

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
        buffer = ""  # Buffer to accumulate assistant's response
        response_count = 0  # Track number of responses
        last_response_time = None  # Track time of last response
        
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
                        await asyncio.sleep(0.5)
                        
                        # If no new responses have come in after waiting, this is truly the final one
                        if current_time == last_response_time:
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

async def client_to_agent_messaging(websocket, user_id):
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            mime_type = data.get("mime_type", "")
            content = data.get("data", "")
            history = data.get("history", [])
            is_recording = data.get("is_recording", None)

            # Handle audio recording state changes
            if mime_type == "audio/state":
                if is_recording is not None:
                    print(f"[Audio] Recording state changed to: {is_recording}", flush=True)
                continue

            # All text messages (whether from direct text input or transcribed audio)
            # go through the same path
            if mime_type == "text/plain" and content:
                print(f"[Agent] Received text message: {content}", flush=True)
                
                # Create run config with only allowed parameters
                run_config = RunConfig(
                    response_modalities=["text"]  # Only include valid parameters
                )

                # Run the agent with the text input - pass run_config as a kwarg
                agent = root_agent
                async for event in agent.run_live(content, config=run_config):
                    await agent_to_client_messaging(websocket, [event], user_id)

    except WebSocketDisconnect:
        print(f"[WebSocket] Client #{user_id} disconnected", flush=True)
    except Exception as e:
        print(f"[WebSocket] Error in client_to_agent_messaging: {str(e)}", flush=True)
        traceback.print_exc()

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
        client_to_agent_task = asyncio.create_task(client_to_agent_messaging(websocket, user_id))
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
