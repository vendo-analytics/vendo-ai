import os
from datetime import date
from typing import Union, List, Optional, Iterable

from google.adk.agents import Agent
from .data_visualisation.agent import data_visualization_agent
from .prompt import (
    QUERY_INSTRUCTION_V2
)
from google.adk.tools.agent_tool import AgentTool

from .query_execution.tools import query_bigquery, build_chart
from google.genai.types import GenerateContentConfig
import google.genai.types as types 
from dotenv import load_dotenv
load_dotenv()


# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
query_agent = Agent(
    name="query_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Plans and conducts data extraction from BigQuery",
    instruction=QUERY_INSTRUCTION_V2,
    tools=[query_bigquery, AgentTool(agent=data_visualization_agent)],
    generate_content_config=types.GenerateContentConfig(temperature=0.01)
)

