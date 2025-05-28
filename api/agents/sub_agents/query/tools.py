from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime, date
import pandas as pd
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Optional
import json


from google.cloud import bigquery
from google.oauth2 import service_account

def convert_dates_to_strings(obj):
    """
    Recursively convert date/datetime objects to strings for JSON serialization.
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    else:
        return obj

def query_bigquery(query: str) -> dict:
    """
    Tool for ADK Agent: Executes a BigQuery SQL query and returns structured results.

    Args:
        query (str): The SQL query to run.

    Returns:
        dict: A structured response in agent-compatible format:
            {
                "mime_type": "text/plain",
                "data": "<Markdown table or message>",
                "raw_data": [<row dicts>]
            }

        If an error occurs, returns:
            {
                "mime_type": "text/plain",
                "data": "❌ Error executing query: <error message>",
                "raw_data": []
            }
    """
    print("▶️ Running query_bigquery()")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            "service_key.json",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)

        # Block until done (with timeout)
        df = query_job.result(timeout=60).to_dataframe()
        result_data = df.to_dict(orient="records")
        
        # Convert date objects to strings for JSON serialization
        result_data = convert_dates_to_strings(result_data)

        if not result_data:
            return {
                "mime_type": "text/plain",
                "data": "✅ Query executed successfully, but no rows were returned.",
                "raw_data": []
            }

        # Build markdown table
        columns = df.columns.tolist()
        message = "✅ Query Results:\n"
        message += "\n| " + " | ".join(columns) + " |"
        message += "\n|" + "|".join(["---"] * len(columns)) + "|"
        for row in result_data[:100]:  # limit to first 100 rows
            row_values = [str(row.get(col, "")) for col in columns]
            message += "\n| " + " | ".join(row_values) + " |"

        if len(result_data) > 100:
            message += f"\n\n... and {len(result_data) - 100} more rows (showing first 100)"

        message += f"\n\n**Total rows returned:** {len(result_data)}"

        return {
            "mime_type": "text/plain",
            "data": message,
            "raw_data": result_data
        }

    except Exception as e:
        return {
            "mime_type": "text/plain",
            "data": f"❌ Error executing query: {str(e)}",
            "raw_data": []
        }


