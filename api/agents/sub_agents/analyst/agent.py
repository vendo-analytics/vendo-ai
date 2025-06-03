import os
from datetime import date
from typing import Union, List, Optional, Iterable

from google.adk.agents import Agent
from .prompt import (
    analyst_prompt
)

from .tools import (
    query_bigquery,
    build_chart,
    analyze_dataset,
    generate_insights,
    create_visualization,
    calculate_statistics,
    detect_outliers,
    perform_correlation_analysis,
    segment_data,
    time_series_analysis,
    geographic_analysis
)
from dotenv import load_dotenv
load_dotenv()

debug = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Data Analyst Agent - Analyzes data and provides insights, recommendations, and visualizations
analyst_agent = Agent(
    name="analyst_agent",
    model=os.getenv("MODEL_GEMINI"),
    description="Analyzes datasets, provides insights, generates visualizations, and suggests advanced analyses",
    instruction=analyst_prompt(debug),
    tools=[
        query_bigquery,
        build_chart,
        analyze_dataset,
        generate_insights,
        create_visualization,
        calculate_statistics,
        detect_outliers,
        perform_correlation_analysis,
        segment_data,
        time_series_analysis,
        geographic_analysis
    ]
)
