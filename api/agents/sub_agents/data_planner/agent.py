import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents import Agent


from .prompt import (
    DATA_PLANNER_INSTRUCTION
)

from dotenv import load_dotenv
load_dotenv()

# data planner agent
data_planner = Agent(
    name="data_planner",
    model=os.getenv("MODEL_GEMINI"),
    description="Creates tracking requirements for new events based on customer requests",
    instruction=DATA_PLANNER_INSTRUCTION
)
