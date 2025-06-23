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
    model="gemini-2.5-pro-preview-06-05",
    description="You are the data planner agent in a multi-agent analytics assistant system. Your job is to design event tracking schemas, but in debug mode you must be more verbose, explain your reasoning, and ask clarifying questions if anything is ambiguous.",
    instruction=data_planner_prompt(debug)
)
