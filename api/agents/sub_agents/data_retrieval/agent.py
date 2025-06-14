import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents.callback_context import CallbackContext # Or ToolContext
from google.adk.agents import Agent

from ...firestore_instance import firestore_session_service
from ...state_manager import get_current_connection_id, get_debug_mode
from .prompt import data_retrieval_prompt

from dotenv import load_dotenv
load_dotenv()

from .tools import (
    query_bigquery, 
    build_chart,
    query_mixpanel_event_schema,
    get_event_by_name,
    get_events_by_property,
    search_events_by_description,
    debug_connection_info
)

# Variables 
connection_id = get_current_connection_id()
debug = get_debug_mode()  # True = on, False = off

#Schemas
# from .business_data.schemas_v2 import get_user_properties,  get_events ## 
#callback_context.state["event_schema"] = get_events() ## reads from .business_data.schemas_v2
#callback_context.state["user_property_schema"] = get_user_properties() ## reads from .business_data.schemas_v2

# Schema query functions are available as tools for the agent to use dynamically

# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
data_retrieval = Agent(
    name="data_retrieval",
    model=os.getenv("MODEL_GEMINI"),
    description="Plans and conducts data extraction from the clients database",
    instruction=data_retrieval_prompt(debug),
    tools=[
        query_bigquery,
        build_chart,
        query_mixpanel_event_schema,
        get_event_by_name,
        get_events_by_property,
        search_events_by_description,
        debug_connection_info
    ]
)