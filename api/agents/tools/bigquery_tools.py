from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime, date
import pandas as pd
import os
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
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

def query_bigquery(query: str):
    print("▶️ get_event_data()")
    
    # Get the path to the service key file in the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', '..')
    service_key_path = os.path.join(project_root, 'service_key.json')
    
    credentials = service_account.Credentials.from_service_account_file(
            service_key_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    try:
        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        event_data_df = client.query(query, job_config=job_config).to_dataframe()
        
        print(event_data_df)
        result_data = event_data_df.to_dict(orient='records')
        
        # Convert date objects to strings for JSON serialization
        result_data = convert_dates_to_strings(result_data)
        
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

def get_bigquery_schema():
    credentials = service_account.Credentials.from_service_account_file(
            'adk_cred.json',
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    client = bigquery.Client()

    table_ref = "gam-dwh.mixpanel_data_3266709.mixpanel_all_data_export_20250509"
    table = client.get_table(table_ref)

    schema = []
    for field in table.schema:
        schema.append({
            "name": field.name,
            "type": field.field_type,
            "mode": field.mode,
            "description": field.description or ""
        })

    #print(schema)
    return schema

get_bigquery_schema()