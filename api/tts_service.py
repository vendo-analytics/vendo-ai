import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import google.cloud.texttospeech as tts
from dotenv import load_dotenv

load_dotenv()

class TTSRequest(BaseModel):
    text: str

router = APIRouter()

@router.options("/speak")
async def options_speak():
    return {}

@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    client = tts.TextToSpeechClient()
    synthesis_input = tts.SynthesisInput(text=request.text)

    voice = tts.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-F",
        ssml_gender=tts.SsmlVoiceGender.FEMALE
    )

    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Create an in-memory bytes buffer
    audio_content = io.BytesIO(response.audio_content)
    audio_content.seek(0)

    return StreamingResponse(
        audio_content,
        media_type="audio/mpeg",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )