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

from .prompt import (
    return_root_agent_prompt, 
    google_search_agent_prompt
    )

from .sub_agents.data_retrieval.agent import data_retrieval
from .sub_agents.data_planner.agent import data_planner
from .sub_agents.analyst.agent import analyst_agent

from .global_instructions import (
    get_annotation_context,
    get_routing_escalation_rules,
    get_today_date,
)

from dotenv import load_dotenv
load_dotenv()

# Import client information
from .business_data.business_info import get_info
from .business_data.schemas_v2 import (
    get_user_properties,
    get_events
)
from .business_data.annotation import get_annotations  ## don't work on debugger
from .state_manager import (
    get_current_connection_id, 
    get_current_session_id,
    get_debug_mode
)  ## don't work on debugger
from .firestore_instance import firestore_session_service

## debug mode
debug = get_debug_mode()  # True = on, False = off

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""

    # Get the current connection_id and session_id from state_manager
    connection_id = get_current_connection_id()
    session_id = get_current_session_id()

    chat_history = firestore_session_service.get_chat_messages(connection_id=get_current_connection_id(),session_id=get_current_session_id)
    general_context =firestore_session_service.get_all_general_context(get_current_connection_id())

    callback_context.state["chat_history"] = chat_history
    callback_context.state["general_context"] = general_context
    
    data_dictionary = firestore_session_service.get_data_dictionary_from_firebase(connection_id)
    callback_context.state["data_dictionary"] = data_dictionary
    
    callback_context.state["connection_id"] = connection_id
    callback_context.state["session_id"] = session_id

    # Get debug mode from state manager
    debug_mode = get_debug_mode()
    callback_context.state["debug_mode"] = debug_mode

    # Load client information into session state 
    business_context = get_info(connection_id)
    callback_context.state["business_context"] = business_context
    callback_context.state["dataset_id"] = business_context["dataset_id"]

    # Load annotations into session state
    callback_context.state["annotations"] = get_annotations()

    # Load data set addresses and schemas into session state
    callback_context.state["user_property_dataset"] = f"gam-dwh.{business_context['dataset_id']}.mixpanel_user_data"
    callback_context.state["user_property_schema"] = get_user_properties()
    callback_context.state["event_schema"] = get_events()
    callback_context.state["event_dataset"] = f"gam-dwh.{business_context['dataset_id']}.mixpanel_all_data_export"
    #TODO: Add more Context Tables


# Google Search agent
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
        - Today's date: {get_today_date()}\n    
        - Always assume the context in the business context information is correct and do not confirm with the customer. i.e currency, business name, data set id, etc.
        """  
        #  How to use annotations: {get_annotation_context()}

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