import os
from datetime import date
from typing import Union, List, Optional, Iterable
from google.adk.agents.callback_context import CallbackContext # Or ToolContext

from .tools import (
    query_bigquery,
    build_chart,
)

from google.adk.agents import Agent

from .prompt import data_retrieval_prompt
debug = False  # True = on, False = off

from dotenv import load_dotenv
load_dotenv()


# Data Query Agent - Runs the queries in BQ to bring the right data set based on users request
data_retrieval = Agent(
    name="data_retrieval",
    model=os.getenv("MODEL_GEMINI"),
    description="Plans and conducts data extraction from the clients database",
    instruction=data_retrieval_prompt(debug),
    tools=[
        query_bigquery,
        build_chart,
    ]
)