import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search  # Import the tool
from typing import Union, List, Optional, Iterable
import os
import json
import gzip

import io

# ────────────────────────────────────────────────────────────────────────────
# 1. Tools
# ────────────────────────────────────────────────────────────────────────────
# moved Mixpanel tool to its own file
#from google.adk.tools import Tool


#moved prompts to a separate file
from .prompts import (
 
    ROOT_AGENT_INSTRUCTION,
    GOOGLE_SEARCH_AGENT_INSTRUCTION,
    BIGQUERY_QUERY_RUNNER_AGENT_INSTRUCTION,
    GET_BIGQUERY_QUERY_AGENT_INSTRUCTION,
)



# ────────────────────────────────────────────────────────────────────────────
# 3. Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────

root_agent = Agent(
    name="agent_router",
    model="gemini-2.0-flash-live-001",
    description="Professional analytics assistant that can answer questions using both web search and event data analysis.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[
        google_search,  # Direct tool for web searche
    ]
)

