import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

from .tools import (
    query_bigquery,
    build_chart,
)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""
    
    user_table = "gam-dwh.piri_red.engage"
    event_table = "gam-dwh.piri_red.export"

    callback_context.state["user_table"] = user_table
    callback_context.state["event_table"] = event_table


from google.adk.agents import Agent
from .prompt import (
    QUERY_INSTRUCTION
)

from dotenv import load_dotenv
load_dotenv()

# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
data_retrieval = Agent(
    name="data_retrieval",
    model=os.getenv("MODEL_GEMINI"),
    description="Plans and conducts data extraction from the clients database",
    instruction=QUERY_INSTRUCTION,
    tools=[
        query_bigquery,
        build_chart,
    ],
    before_agent_callback=setup_before_agent_call, #Add client context, schemas
)