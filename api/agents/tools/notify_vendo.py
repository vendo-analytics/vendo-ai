from typing import Any
import httpx
from pydantic import BaseModel, Field

WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/643883/2v8l2tq/"

class NotifyVendoInput(BaseModel):
    summary: str = Field(..., description="A concise summary of the thread or request to escalate.")
    business_context: dict = Field(..., description="Business context information relevant to the request.")
    chat_summary: str = Field(..., description="A summary of the chat or conversation thread.")

def notify_vendo(*, summary: str, business_context: dict, chat_summary: str) -> dict[str, Any]:
    """
    Escalate a request to the Vendo Team by posting a summary, business context, and chat summary to the Zapier webhook.
    Returns a dict with status and webhook response.
    """
    payload = {
        "summary": summary,
        "business_context": business_context,
        "chat_summary": chat_summary
    }
    try:
        response = httpx.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return {"status": "success", "webhook_status_code": response.status_code}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)} 