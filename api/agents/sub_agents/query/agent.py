import os
from datetime import date
from typing import Union, List, Optional, Iterable

from google.adk.agents import Agent
from .prompt import (
    QUERY_INSTRUCTION
)
from .tools import query_bigquery, build_chart
from dotenv import load_dotenv
load_dotenv()

# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
query_agent = Agent(
    name="query_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Plans and conducts data extraction from BigQuery",
    instruction=QUERY_INSTRUCTION,
    tools=[query_bigquery, build_chart]
)

