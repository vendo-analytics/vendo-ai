import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import httpx

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api/slack-text")

logging.basicConfig(level=logging.INFO)

app = App(token=SLACK_BOT_TOKEN)

@app.event("assistant_thread_started")
def handle_thread_started(event, client, logger):
    print(event)
    context = event.get("context", {})
    channel_id = context.get("channel_id")
    thread_ts = event.get("thread_ts")
    logger.info(f"assistant_thread_started: context={context}")
    # Optionally check channel access
    try:
        client.conversations_info(channel=channel_id)
    except Exception as e:
        logger.error(f"conversations_info failed: {e}")
    # Set status or suggest prompts
    try:
        client.assistant_threads_setStatus(
            channel_id=channel_id,
            thread_ts=thread_ts,
            status="Ready to help! Ask me anything about your data."
        )
        client.assistant_threads_setSuggestedPrompts(
            channel=channel_id,
            prompts=[
                {"text": "Summarize last week's activity"},
                {"text": "What are my top performing products?"},
                {"text": "Give me a quick business update"},
            ],
        )
    except Exception as e:
        logger.error(f"Failed to set status or prompts: {e}")

@app.event("message")
def handle_message(event, client, logger):
    # Only handle direct messages (IMs)
    if event.get("channel_type") != "im":
        return
    text = event.get("text")
    thread_ts = event.get("thread_ts")
    channel = event.get("channel")
    logger.info(f"message: text={text}, channel={channel}, thread_ts={thread_ts}")
    # Set status indicator
    try:
        client.assistant_threads_setStatus(
            channel_id=channel,
            thread_ts=thread_ts,
            status="Thinking..."
        )
    except Exception as e:
        logger.error(f"Failed to set status: {e}")
    # Call backend for text response
    try:
        with httpx.Client() as http:
            resp = http.post(
                os.environ.get("BACKEND_URL", "http://localhost:8000/api/slack-text"),
                json={"prompt": text, "connection_id": f"slack_{channel}"},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            response_text = data.get("text")
    except Exception as e:
        logger.error(f"Backend call failed: {e}")
        response_text = "Sorry, I couldn't generate a response."
    # Post message in thread
    try:
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=response_text or "Here's your answer:",
        )
    except Exception as e:
        logger.error(f"Failed to post message: {e}")
    # Clear status
    try:
        client.assistant_threads_setStatus(
            channel_id=channel,
            thread_ts=thread_ts,
            status=""
        )
    except Exception as e:
        logger.error(f"Failed to clear status: {e}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start() 