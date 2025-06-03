import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents import Agent

from .prompt import (
    data_planner_prompt
)

from dotenv import load_dotenv
load_dotenv()

debug = os.getenv("DEBUG_MODE", "false").lower() == "true"

# data planner agent
data_planner = Agent(
    name="data_planner",
    model=os.getenv("MODEL_GEMINI"),
    description="Creates tracking requirements for new events based on customer requests",
    instruction=data_planner_prompt(debug)
)
