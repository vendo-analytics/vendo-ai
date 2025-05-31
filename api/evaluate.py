import os
import csv
import time
import logging
import asyncio
import base64
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict

import langfuse
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import format_trace_id

from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from api.agents.agent import root_agent_x

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_NAME = "Vendo Evaluation"
DATASET_NAME = f"vendo_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
session_service = InMemorySessionService()

# Langfuse setup
langfuse_client = langfuse.Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://us.cloud.langfuse.com"
)

# OpenTelemetry setup
LANGFUSE_AUTH = base64.b64encode(
    f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

provider = TracerProvider(resource=Resource.create({
    "service.name": "agent_evaluator",
    "service.version": "1.0.0",
}))
exporter = OTLPSpanExporter(
    endpoint="https://us.cloud.langfuse.com/api/public/otel/v1/traces",
    headers={"Authorization": f"Basic {LANGFUSE_AUTH}"}
)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent_evaluator", "1.0.0")


# --- Code Execution ---
def execute_code_string(code_str: str) -> str:
    try:
        import io
        import contextlib
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code_str, {}, {})
        return output.getvalue().strip()
    except Exception as e:
        return f"[ERROR executing code] {e}"


# --- Agent Execution ---
async def run_agent(question: str, connection_id: str) -> (str, str):
    session_id = f"eval_{int(time.time())}"
    session = session_service.create_session(app_name=APP_NAME, user_id=connection_id, session_id=session_id)
    runner = Runner(app_name=APP_NAME, agent=root_agent_x, session_service=session_service)
    request_queue = LiveRequestQueue()

    run_config = RunConfig(response_modalities=["text"])         # ✅ this tells Gemini it can call tools)
    events = runner.run_live(session=session, live_request_queue=request_queue, run_config=run_config)

    content = Content(role="user", parts=[Part(text=question)])
    request_queue.send_content(content)

    response = ""
    trace_id = None

    with tracer.start_as_current_span("run_agent") as span:
        span.set_attribute("input.question", question)
        span_context = span.get_span_context()
        trace_id = format_trace_id(span_context.trace_id)

        async for event in events:
            print(f"Event ID: {event.id}, Author: {event.author}")

            # --- Check for specific parts FIRST ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:  # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        print(
                            f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                        )
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        print(
                            f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                        )
                        has_specific_part = True
                    # Also print any text parts found in any event for debugging
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        # Do not set has_specific_part=True here, as we want the final response logic below

            # --- Check for final response AFTER specific parts ---
            # Only consider it final if it doesn't have the specific code parts we just handled
            if not has_specific_part and event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> Final Agent Response: {final_response_text}")
                    return final_response_text, trace_id
                else:
                    print("==> Final Agent Response: [No text content in final event]")

        return final_response_text, trace_id


# --- Evaluation ---
async def evaluate_dataset(data: List[Dict[str, str]], connection_id="eval_user"):
    results = []

    langfuse_client.create_dataset(
        name=DATASET_NAME,
        description="Gemini benchmark evaluation",
        metadata={"date": str(datetime.utcnow()), "type": "benchmark"}
    )

    for i, item in enumerate(data):
        langfuse_client.create_dataset_item(
            dataset_name=DATASET_NAME,
            input={"text": item["question"]},
            expected_output={"text": item["expected_answer"]},
            metadata={"source_index": i}
        )

    dataset = langfuse_client.get_dataset(DATASET_NAME)

    for item in dataset.items:
        question = item.input["text"]
        expected = item.expected_output["text"]
        print(f"Question: {question}", flush=True)
        print(f"Expected: {expected}", flush=True)

        try:
            answer, trace_id = await run_agent(question, connection_id)
            print(f"AnswerNEW: {answer}", flush=True)
            exact_match = expected.strip().lower() in  answer.strip().lower()

            if trace_id:
                trace_obj = langfuse_client.trace(id=trace_id, input=question, output=answer)
                trace_obj.score(
                    name="exact_match",
                    value=1.0 if exact_match else 0.0,
                    comment=f"Expected: {expected} | Got: {answer}"
                )
                item.link(trace_obj, run_name="eval_run", run_metadata={"model": "gemini-1.5-flash"})

            results.append({
                "question": question,
                "expected": expected,
                "answer": answer,
                "exact_match": exact_match
            })

        except Exception as e:
            logger.exception(f"❌ Error evaluating question '{question}': {str(e)}")
            results.append({
                "question": question,
                "expected": expected,
                "answer": f"[ERROR] {e}",
                "exact_match": False
            })

    langfuse_client.flush()
    return results


# --- Main ---
if __name__ == "__main__":

    sample_data = []
    with open('test_questions.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_data.append({
                "question": row["question"],
                "expected_answer": row["expected_answer"]
            })

    results = asyncio.run(evaluate_dataset(sample_data))

    print("\n📊 Evaluation Results:")
    for r in results:
        print(f"- Q: {r['question']}")
        print(f"  A: {r['answer']}")
        print(f"  ✅ Match: {r['exact_match']}\n")

    print(f"✔️ Done. Total: {len(results)} | Matches: {sum(1 for r in results if r['exact_match'])}")
