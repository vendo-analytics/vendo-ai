import os
from datetime import date
from typing import Union, List, Optional, Iterable

from google.adk.agents import Agent
from .prompt import (
    GRAPH_VISUALIZATION_INSTRUCTION
)
from .tools import build_chart
from google.genai.types import GenerateContentConfig
import google.genai.types as types 
from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv
load_dotenv()


# Graph Visualization Agent - Creates interactive charts and graphs from data
data_visualization_agent = Agent(
    name="data_visualization_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Creates interactive charts and graphs from data using Recharts JSX components for Next.js frontend rendering.",
    instruction=GRAPH_VISUALIZATION_INSTRUCTION,
    tools=[build_chart],
    generate_content_config=types.GenerateContentConfig(temperature=0.1)
) 