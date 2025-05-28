import os
from datetime import date
from typing import Union, List, Optional, Iterable

from google.adk.agents import Agent
from .prompt import (
    QUERY_EXECUTION_INSTRUCTION
)
from .tools import query_bigquery
from google.genai.types import GenerateContentConfig
import google.genai.types as types 
from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv
load_dotenv()


# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
query_execution_agent = Agent(
    name="query_execution_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Executes pre-approved SQL queries from BigQuery with user confirmation and safe formatting.",
    instruction=QUERY_EXECUTION_INSTRUCTION,
    tools=[query_bigquery],
    generate_content_config=types.GenerateContentConfig(temperature=0.01)
)