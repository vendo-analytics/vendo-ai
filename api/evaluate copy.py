import pandas as pd
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import langfuse
from datetime import datetime

from google.genai.types import (
    Part,
    Content,
)

from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from firebase_client import FirestoreSessionService
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import base64
import time
from google.adk.agents import LiveRequestQueue
import asyncio
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Langfuse client
langfuse = langfuse.Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host="https://us.cloud.langfuse.com"  # US region
)

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
        "service.name": "agent_evaluator",
        "service.version": "1.0.0",
    })
)

class LoggingExporter(OTLPSpanExporter):
    def export(self, spans):
        #print(f"[DEBUG] Exporting spans: {spans}", flush=True)
        #logger.debug("Attempting to export %d spans", len(spans))
        try:
            result = super().export(spans)
            #logger.debug("Export result: %s", result)
            return result
        except Exception as e:
            #logger.error("Failed to export spans: %s", str(e))
            raise

# Configure the OTLP exporter
exporter = LoggingExporter(
    endpoint=OTEL_ENDPOINT,
    headers=OTEL_HEADERS,
    timeout=30
)

provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("agent_evaluator", "1.0.0")

from opentelemetry.trace import format_trace_id
from agents.agents import root_agent

# Setup evaluation environment
APP_NAME = "Vendo Evaluation"

async def _evaluate_async(question, expected_answer, trace, user_id):
    from google.genai.types import Content, Part
    from google.adk.runners import Runner
    from google.adk.agents.run_config import RunConfig
    from google.adk.agents import LiveRequestQueue
    from firebase_client import FirestoreSessionService

    session_service = FirestoreSessionService(collection_name="vendo_ai_memory")
    session_id = f"eval_{int(time.time())}"

    span = trace.span(
        name="question_evaluation",
        input={"question": question, "expected": expected_answer}
    )

    try:
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

        # Send content to agent
        content = Content(role="user", parts=[Part(text=question)])
        live_request_queue.send_content(content)

        # Await live agent response
        buffer = ""
        async for event in live_events:
            part = event.content.parts[0] if event.content and event.content.parts else None
            if part and part.text:
                buffer += part.text

            if getattr(event, 'is_final_response', lambda: False)():
                break

        if not buffer:
            buffer = "No answer received"

        span.end(
            output={"answer": buffer},
            metadata={
                "model": "gemini-2.0-flash-live-001",
                "app": APP_NAME
            }
        )
        return buffer

    except Exception as e:
        span.end(
            output={"error": str(e)},
            metadata={"status": "error"}
        )
        return f"[ERROR] {str(e)}"

def create_evaluation_dataset(questions_data, dataset_name=None):
    """Create a Langfuse dataset from evaluation data."""
    if dataset_name is None:
        dataset_name = f"vendo_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create the dataset
    langfuse.create_dataset(
        name=dataset_name,
        description="Vendo evaluation dataset",
        metadata={
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "evaluation"
        }
    )
    
    # Add items to dataset
    for idx, item in enumerate(questions_data):
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input={"text": item["question"]},
            expected_output={"text": item["expected_answer"]},
            metadata={"source_index": idx}
        )
    print(f"[EVAL] Dataset created: {dataset_name}")
    return dataset_name

def run_evaluation(questions_data, dataset_name=None):
    """Run evaluation using Langfuse dataset tracking."""
    # Create dataset if name not provided
    dataset_name = create_evaluation_dataset(questions_data)
    
    # Get dataset
    dataset = langfuse.get_dataset(dataset_name)
    
    # Create a single trace for the entire evaluation run
    trace = langfuse.trace(
        name="vendo_evaluation_run",
        metadata={
            "dataset": dataset_name,
            "model": "gemini-2.0-flash-live-001",
            "app": APP_NAME
        }
    )
    
    results = []
    
    # Run evaluation for each item
    for item in dataset.items:
        question = item.input["text"]
        expected = item.expected_output["text"]
        print(f"\n[EVAL] Question: {question}")
        print(f"[EVAL] Expected: {expected}")
        
        # Run evaluation
        answer = asyncio.run(_evaluate_async(question, expected, trace, user_id))(question, expected, trace)
        print(f"[EVAL] Answer: {answer}", flush=True)
        
        # Link trace to dataset item
        item.link(
            trace.id,
            run_name="vendo_evaluation_run",
            run_metadata={
                "model": "gemini-2.0-flash-live-001",
                "app": APP_NAME
            }
        )
        
        # Score the result
        exact_match = answer.lower().strip() == expected.lower().strip()
        trace.score(
            name="exact_match",
            value=1.0 if exact_match else 0.0,
            comment=f"Answer: {answer}"
        )
        
        print(f"[EVAL] Answer: {answer}")
        print(f"[EVAL] Exact Match: {exact_match}")
        
        results.append({
            "question": question,
            "expected": expected,
            "answer": answer,
            "trace_id": trace.id,
            "exact_match": exact_match
        })
    
    # Ensure all telemetry is sent
    langfuse.flush()
    return results

if __name__ == "__main__":
    # Example evaluation data
    evaluation_data = [
        {
            "question": "What is 2+2?",
            "expected_answer": "4"
        },
        {
            "question": "What is the capital of France?",
            "expected_answer": "Paris"
        }
    ]
    
    # Run evaluation with dataset tracking
    dataset_name = "vendo_evaluation_example"
    results = run_evaluation(evaluation_data, dataset_name)
    print("\nEvaluation Complete!")
    print(f"Dataset: {dataset_name}")
    print(f"Total evaluations: {len(results)}")
    print(f"Exact matches: {sum(r['exact_match'] for r in results)}")

