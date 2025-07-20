import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents import Agent

from ...firestore_instance import firestore_session_service
from ...state_manager import get_current_connection_id, get_debug_mode
from ...mixpanel_client import MixpanelClient
from .prompt import mixpanel_mcp_prompt
from .tools import (
    initialize_mixpanel_mcp_tools,
    query_events_mcp,
    get_user_profiles_mcp,
    create_funnel_mcp,
    get_cohorts_mcp,
    get_insights_mcp,
    get_retention_analysis_mcp,
    get_schema_mcp
)

from dotenv import load_dotenv
load_dotenv()

# Variables 
connection_id = get_current_connection_id()
debug = get_debug_mode()  # True = on, False = off

# Get Mixpanel credentials from your existing MixpanelClient
mixpanel_client = MixpanelClient(connection_id)

# Initialize MCP tools with Mixpanel credentials
initialize_mixpanel_mcp_tools(mixpanel_client)

# Mixpanel MCP Agent - Connects to Mixpanel's MCP server for advanced analytics
mixpanel_mcp_agent = Agent(
    name="mixpanel_mcp",
    model=os.getenv("MODEL_GEMINI"),
    description="Connects to Mixpanel's MCP server to access advanced analytics capabilities including real-time data access, funnel analysis, cohort management, and extended Mixpanel features not available through standard API",
    instruction=mixpanel_mcp_prompt(debug),
    tools=[
        query_events_mcp,
        get_user_profiles_mcp,
        create_funnel_mcp,
        get_cohorts_mcp,
        get_insights_mcp,
        get_retention_analysis_mcp,
        get_schema_mcp
    ],
)

# Alias for system compatibility - some systems might look for 'root_agent'
root_agent = mixpanel_mcp_agent