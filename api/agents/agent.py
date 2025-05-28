import os
from datetime import date
import json
import requests
import gzip
import io
from typing import Union, List, Optional, Iterable

import google.genai.types as types
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search, FunctionTool  # Import the tool
from google.adk.agents.callback_context import CallbackContext # Or ToolContext
from google.adk.tools import google_search, load_artifacts

from .prompt import (ROOT_AGENT_INSTRUCTION, GOOGLE_SEARCH_INSTRUCTION)

from .sub_agents.data_retrieval.agent import data_retrieval
from .sub_agents.data_planner.agent import data_planner
from .sub_agents.analyst.agent import analyst_agent

from dotenv import load_dotenv
load_dotenv()

# Import client information
from .business_data.business_info import get_info
from .business_data.schemas import (
    get_user_table_schema,
    get_event_table_schema,
    get_event_names,
    get_ad_data_properties,
    get_order_received_properties,
    get_products_object_schema,
    get_product_events,
    format_user_table_schema_for_prompt,
    format_event_table_schema_for_prompt,
    format_event_names_for_prompt,
    format_all_schemas_for_prompt
)

date_today = date.today()
business_context = get_info()

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""

    # Load client information into session state 
    if "business_context" not in callback_context.state:
        callback_context.state["business_context"] = business_context
    
    user_table = "gam-dwh.piri_red.engage"
    event_table = "gam-dwh.piri_red.export"

    callback_context.state["user_table"] = user_table
    callback_context.state["event_table"] = event_table
    
    # Add individual schema components to the state
    callback_context.state["user_table_schema"] = get_user_table_schema()
    callback_context.state["event_table_schema"] = get_event_table_schema()
    callback_context.state["event_names"] = get_event_names()
    callback_context.state["ad_data_properties"] = get_ad_data_properties()
    callback_context.state["order_received_properties"] = get_order_received_properties()
    callback_context.state["products_object_schema"] = get_products_object_schema()
    callback_context.state["product_events"] = get_product_events()
    
    # Add formatted schemas to the state
    callback_context.state["schemas"] = format_all_schemas_for_prompt(user_table, event_table)


# google search agent
google_search_agent = Agent(
    model=os.getenv("MODEL_GEMINI"),
    name='google_search',
    description="Google search agent",
    instruction=GOOGLE_SEARCH_INSTRUCTION,
    tools=[google_search]
)


# ────────────────────────────────────────────────────────────────────────────
# Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="root_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Job is to route the user's request to the right sub-agent.",
    instruction=ROOT_AGENT_INSTRUCTION,
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Today's date: {date_today}
        """
    ),
    sub_agents=[
        data_retrieval,
        data_planner,
        analyst_agent
    ],
    tools=[
        AgentTool(agent=google_search_agent),
        #load_artifacts, 
    ],
    before_agent_callback=setup_before_agent_call, #Add client context, schemas
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)