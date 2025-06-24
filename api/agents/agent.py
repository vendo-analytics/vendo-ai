import os
import json
import requests
import gzip
import io
from typing import Union, List, Optional, Iterable
from datetime import date
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext # Or ToolContext
from google.genai import types


#Prompts
from .prompt import root_agent_prompt, google_search_agent_prompt
from .global_instructions import global_instructions_prompt

#Agents and Tools
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search, load_artifacts, FunctionTool
from .tools.notify_vendo import notify_vendo
from .sub_agents.data_retrieval.agent import data_retrieval
from .sub_agents.data_planner.agent import data_planner
from .sub_agents.analyst.agent import analyst_agent

#Environment Variables
from dotenv import load_dotenv
load_dotenv()

# Import Business information
from .firestore_instance import firestore_session_service
from .state_manager import get_current_connection_id, get_current_session_id,  get_debug_mode ## don't work on debugger

## Below are reading from the Business Data Folder. There is some overlap between what .state_manager and .business_data.business_info.py does
from .business_data.business_info import get_business_context
from .business_data.annotation import get_annotations  ## don't work on debugger
from .business_data.schemas_v2 import get_user_properties, get_events  ## don't work on debugger


## Define Variables 
current_date = date.today()
debug = get_debug_mode()  # True = on, False = off
connection_id = get_current_connection_id()
session_id = get_current_session_id()
business_context = get_business_context(connection_id)
business_documents =firestore_session_service.get_all_general_context(get_current_connection_id())
chat_history = firestore_session_service.get_chat_messages(connection_id=get_current_connection_id(),session_id=get_current_session_id)
user_property_schema = get_user_properties()
event_schema = get_events()

# ────────────────────────────────────────────────────────────────────────────
# Bring business context to the agent
# ────────────────────────────────────────────────────────────────────────────
def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""
    callback_context.state["annotations"] = get_annotations() #getting from .business.data not app
    callback_context.state["business_context"] = business_context
    callback_context.state["business_documents"] = business_documents
    callback_context.state["chat_history"] = chat_history 
    callback_context.state["current_date"] = current_date
    callback_context.state["debug_mode"] = debug
    callback_context.state["event_dataset"] = f"gam-dwh.{business_context['dataset_id']}.mixpanel_all_data_export"
    callback_context.state["user_property_dataset"] = f"gam-dwh.{business_context['dataset_id']}.mixpanel_user_data"
    callback_context.state["user_property_schema"] = user_property_schema
    callback_context.state["event_schema"] = event_schema


# ────────────────────────────────────────────────────────────────────────────
# Google Search agent
# ────────────────────────────────────────────────────────────────────────────
google_search_agent = Agent(
    model=os.getenv("MODEL_GEMINI"),
    name='google_search',
    description="You are the `google_search` agent, a specialist in retrieving and synthesizing up-to-date, factual, and external information using Google Search. Your primary responsibility is to supplement internal analytics with authoritative, relevant, and timely information from the web.",
    instruction=google_search_agent_prompt(debug),
    tools=[google_search]
)

# ────────────────────────────────────────────────────────────────────────────
# Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="root_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="You are the root agent in a multi-agent analytics assistant system designed to be fast, efficient, and user-friendly. You coordinate a team of specialized agents and tools, each designed for specific analytics or data-related tasks.",
    instruction=root_agent_prompt(debug),
    global_instruction=global_instructions_prompt(),
    sub_agents=[
        data_retrieval,
        data_planner,
        #analyst_agent
    ],
    tools=[
        AgentTool(agent=google_search_agent),
        notify_vendo,
    ],
    before_agent_callback=setup_before_agent_call, #Add client context, schemas
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
    )
)