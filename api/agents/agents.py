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
from .tools.bigquery_tools import query_bigquery


#moved prompts to a separate file
from .prompts import (
 
    ROOT_AGENT_INSTRUCTION,
    GOOGLE_SEARCH_AGENT_INSTRUCTION,
    BIGQUERY_QUERY_RUNNER_AGENT_INSTRUCTION,
    GET_BIGQUERY_QUERY_AGENT_INSTRUCTION,
)


bigquery_query_runner_agent = Agent(
    name="bigquery_query_runner_agent",
    model="gemini-2.0-flash",
    description="Builds & executes the BigQuery query, returns raw rows.",
    instruction=BIGQUERY_QUERY_RUNNER_AGENT_INSTRUCTION,
    tools=[query_bigquery],
    output_key="bigquery_data"
)



get_bigquery_query_agent = Agent(
    name="get_bigquery_query_agent",
    model="gemini-2.0-flash",
    description="Returns the BigQuery SQL query to use with bigquery_query_runner_agent which queries the table.",
    instruction=GET_BIGQUERY_QUERY_AGENT_INSTRUCTION,
    tools=[AgentTool(agent=bigquery_query_runner_agent)],
    output_key="bigquery_query"
)


# google search agent
google_search_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='google_search_agent',
    instruction=GOOGLE_SEARCH_AGENT_INSTRUCTION,
    tools=[google_search]
)

# ────────────────────────────────────────────────────────────────────────────
# 3. Root orchestration agent
# ────────────────────────────────────────────────────────────────────────────

root_agent_x = Agent(
    name="agent_router",
    model="gemini-2.0-flash",
    description="Job is to route the user's request to the right sub-agent.",
    instruction=ROOT_AGENT_INSTRUCTION,
    sub_agents=[
        get_bigquery_query_agent,
    ],
    tools=[
        AgentTool(agent=google_search), 
    ]
)
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LiveRequestQueue
from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool
from google.genai import Client
from google.genai import types as genai_types

async def monitor_stock_price(stock_symbol: str) -> AsyncGenerator[str, None]:
  """This function will monitor the price for the given stock_symbol in a continuous, streaming and asynchronously way."""
  print(f"Start monitor stock price for {stock_symbol}!")

  # Let's mock stock price change.
  await asyncio.sleep(4)
  price_alert1 = f"the price for {stock_symbol} is 300"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(4)
  price_alert1 = f"the price for {stock_symbol} is 400"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"the price for {stock_symbol} is 900"
  yield price_alert1
  print(price_alert1)

  await asyncio.sleep(20)
  price_alert1 = f"the price for {stock_symbol} is 500"
  yield price_alert1
  print(price_alert1)


# for video streaming, `input_stream: LiveRequestQueue` is required and reserved key parameter for ADK to pass the video streams in.
async def monitor_video_stream(
    input_stream: LiveRequestQueue,
) -> AsyncGenerator[str, None]:
  """Monitor how many people are in the video streams."""
  print("start monitor_video_stream!")
  client = Client(vertexai=False)
  prompt_text = (
      "Count the number of people in this image. Just respond with a numeric"
      " number."
  )
  last_count = None
  while True:
    last_valid_req = None
    print("Start monitoring loop")

    # use this loop to pull the latest images and discard the old ones
    while input_stream._queue.qsize() != 0:
      live_req = await input_stream.get()

      if live_req.blob is not None and live_req.blob.mime_type == "image/jpeg":
        last_valid_req = live_req

    # If we found a valid image, process it
    if last_valid_req is not None:
      print("Processing the most recent frame from the queue")

      # Create an image part using the blob's data and mime type
      image_part = genai_types.Part.from_bytes(
          data=last_valid_req.blob.data, mime_type=last_valid_req.blob.mime_type
      )

      contents = genai_types.Content(
          role="user",
          parts=[image_part, genai_types.Part.from_text(prompt_text)],
      )

      # Call the model to generate content based on the provided image and prompt
      response = client.models.generate_content(
          model="gemini-2.0-flash-exp",
          contents=contents,
          config=genai_types.GenerateContentConfig(
              system_instruction=(
                  "You are a helpful video analysis assistant. You can count"
                  " the number of people in this image or video. Just respond"
                  " with a numeric number."
              )
          ),
      )
      if not last_count:
        last_count = response.candidates[0].content.parts[0].text
      elif last_count != response.candidates[0].content.parts[0].text:
        last_count = response.candidates[0].content.parts[0].text
        yield response
        print("response:", response)

    # Wait before checking for new images
    await asyncio.sleep(0.5)


# Use this exact function to help ADK stop your streaming tools when requested.
# for example, if we want to stop `monitor_stock_price`, then the agent will
# invoke this function with stop_streaming(function_name=monitor_stock_price).
def stop_streaming(function_name: str):
  """Stop the streaming

  Args:
    function_name: The name of the streaming function to stop.
  """
  pass

root_agent = Agent(
    name="agent_router",
    model="gemini-2.0-flash-live-001",
    description="Job is to route the user's request to the right sub-agent.",
    instruction="""You are a monitoring agent. You can do video monitoring and stock price monitoring
      using the provided tools/functions.
      When users want to monitor a video stream,
      You can use monitor_video_stream function to do that. When monitor_video_stream
      returns the alert, you should tell the users.
      When users want to monitor a stock price, you can use monitor_stock_price.
      Don't ask too many questions. Don't be too talkative.""",
    tools=[google_search,
         query_bigquery
    ], # Enable tool output formatting
)

