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

date_today = date.today()

# Import client information
from .business_context.client_info import get_client_info

def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""
    
    # Load client information into session state 
    if "client_info" not in callback_context.state:
        client_info = get_client_info()
        callback_context.state["client_info"] = client_info


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
        #analyst_agent
    ],
    tools=[
        AgentTool(agent=google_search_agent),
        #load_artifacts, 
    ],
    before_agent_callback=setup_before_agent_call, #Add client context, schemas
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)