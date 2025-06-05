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
from .tools.notify_vendo import notify_vendo

from .prompt import (return_root_agent_prompt, google_search_agent_prompt)

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
from .business_data.annotation import get_annotations
from .state_manager import get_current_connection_id


date_today = date.today()

debug = os.getenv("DEBUG_MODE", "false").lower() == "false"


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""

    # Get the current connection_id from state_manager (set by WebSocket endpoint)
    #connection_id = get_current_connection_id()
    connection_id = "gb1uauyn0Khjcs4Fgxh8"
    print(f"[DEBUG] Using connection_id from state_manager: {connection_id}", flush=True)
    
    # Load client information into session state 
    business_context = get_info(connection_id)  #TODO add back the annotation 

    print(f"[DEBUG] Business context: {business_context}", flush=True)
    #business_context = None
    callback_context.state["business_context"] = business_context
    callback_context.state["connection_id"] = connection_id
    callback_context.state["dataset_id"] = business_context["dataset_id"]
    #callback_context.state["annotations"] = annotations
    print(f"[DEBUG] Loaded business context for user {connection_id}", flush=True)
    
    #TODO: make these dynamic
    user_table = f"gam-dwh.{business_context['dataset_id']}.mixpanel_user_data"
    event_table = f"gam-dwh.{business_context['dataset_id']}.mixpanel_all_data_export"

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
    instruction=google_search_agent_prompt(debug),
    tools=[google_search]
)


# ────────────────────────────────────────────────────────────────────────────
# Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="root_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Job is to route the user's request to the right sub-agent.",
    instruction=return_root_agent_prompt(debug),
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
        notify_vendo,
        #load_artifacts, 
    ],
    before_agent_callback=setup_before_agent_call, #Add client context, schemas
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)