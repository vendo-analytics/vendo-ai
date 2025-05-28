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
from google.adk.tools import load_artifacts
import google.genai as genai

date_today = date.today()

from dotenv import load_dotenv
load_dotenv()

# Import client information
from .business_context.client_info import get_client_info

from .prompt import (
    ROOT_AGENT_INSTRUCTION
)

from .sub_agents.data_planner.agent import data_planner
from .sub_agents.query.agent import query_agent
from google import genai
from google.genai.types import (
    Content,
    LiveConnectConfig,
    HttpOptions,
    Modality,
    Part,
)


def setup_before_agent_call(callback_context: CallbackContext):
    """Setup the agent with client information."""
    
    # Load client information into session state 
    if "client_info" not in callback_context.state:
    #if 1==1:
        # Get user_id from session
        user_id = getattr(callback_context.session, 'user_id', '001')
        print(f"[DEBUG] Setting up agent for user_id: {user_id}", flush=True)
        
        # Get client info from Firebase with fallback
        client_info = get_client_info(user_id)
        callback_context.state["client_info"] = client_info
    
    # TODO: Loading Database Schema into Agent Instructions
client = genai.Client(http_options=HttpOptions(api_version="v1beta1"))
model_id = "gemini-2.0-flash-live-preview-04-09"
# ────────────────────────────────────────────────────────────────────────────
# Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────
root_agent = Agent(
    name="agent_router",
    model=os.getenv("MODEL_GEMINI"),
    description="Job is to route the user's request to the right sub-agent.",
    instruction=ROOT_AGENT_INSTRUCTION,
    global_instruction=(
        f"""
        You are a Data Science and Data Analytics Multi Agent System.
        Today's date: {date_today}
        When transferring to another agent, use default_api.transfer_to_agent(agent_name)
        """
    ),
    sub_agents=[
        query_agent,
        data_planner
    ],
    tools=[
        AgentTool(agent=google_search),
        #load_artifacts, 
    ],
    #before_agent_callback=setup_before_agent_call, #Add client context, schemas
    #generate_content_config=types.GenerateContentConfig(temperature=0.01),
)