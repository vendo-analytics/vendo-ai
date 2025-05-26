import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents import Agent
from google.adk.tools import google_search
from .prompt import (
    GOOGLE_SEARCH_INSTRUCTION
)

from dotenv import load_dotenv
load_dotenv()

date_today = date.today()
# google search agent
google_search = Agent(
    model=os.getenv("MODEL_GEMINI"),
    name='google_search',
    description="Google search agent",
    instruction=GOOGLE_SEARCH_INSTRUCTION,
    tools=[google_search]
)

