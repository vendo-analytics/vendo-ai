from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime
import pandas as pd
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from google.cloud import bigquery
from google.oauth2 import service_account


def query_bigquery(query: str):
    print("▶️ get_event_data()")
    credentials = service_account.Credentials.from_service_account_file(
            'service_key.json',
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    try:
        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        event_data_df = client.query(query, job_config=job_config).to_dataframe()
        
        print(event_data_df)
        result_data = event_data_df.to_dict(orient='records')
        if len(result_data) == 0:
            message = "✅ Query executed successfully, but no rows were returned."
        else:
            # Format all rows as a readable table
            message = "✅ Query Results:\n"
            # Get column names from first row
            columns = list(result_data[0].keys())
            # Add header
            message += "\n| " + " | ".join(columns) + " |"
            message += "\n|" + "|".join(["---" for _ in columns]) + "|"
            # Add rows
            for row in result_data:
                message += "\n| " + " | ".join(str(row[col]) for col in columns) + " |"

        return {
            "mime_type": "text/plain",
            "data": message,
            "raw_data": result_data  # Include the raw data for potential visualization
        }
    except Exception as e:
        error_msg = f"❌ Error fetching event data: {str(e)}"
        print(error_msg)
        return error_msg

