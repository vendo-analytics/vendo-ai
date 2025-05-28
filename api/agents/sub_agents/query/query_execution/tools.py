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


def build_chart(
    x: List[str], 
    y: List[float], 
    title: Optional[str] = None, 
    chart_type: str = "line"
) -> str:
    """
    Generates JSX code for a Recharts chart using provided x/y values.
    Returns a JSX string to render a chart in a Next.js frontend.

    Args:
        x: List of strings (e.g. dates, categories, or numeric values as strings)
        y: List of numbers (e.g. sales, revenue, etc.)
        title: Optional title for the chart
        chart_type: Type of chart - "line", "bar", or "scatter" (default: "line")

    Returns:
        A string of JSX code for rendering the appropriate chart type with XAxis, YAxis, 
        Tooltip, and chart-specific components from Recharts
    """
    # Validate chart type
    valid_types = ["line", "bar", "scatter"]
    if chart_type not in valid_types:
        chart_type = "line"  # Default fallback
    
    # Combine x and y into data points
    if chart_type == "scatter":
        # For scatter plots, convert x values to float for numeric axis
        try:
            data_points = [{"x": float(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
        except ValueError:
            # If x values can't be converted to float, fall back to string
            data_points = [{"x": str(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
    else:
        # For line and bar charts, x can be string
        data_points = [{"x": str(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
    
    # Convert data points to a JSON string and ensure proper escaping for JSX
    data_json = json.dumps(data_points).replace('"', "'")
    
    # Build the JSX string with optional title
    title_component = f"<h2>{title}</h2>" if title else ""
    
    # Generate chart-specific JSX
    if chart_type == "line":
        jsx = f"""{title_component}
<LineChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" />
</LineChart>"""
    
    elif chart_type == "bar":
        jsx = f"""{title_component}
<BarChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="y" fill="#8884d8" />
</BarChart>"""
    
    elif chart_type == "scatter":
        # For scatter charts, determine if x-axis should be numeric or categorical
        x_axis_type = "number" if chart_type == "scatter" and all(str(val).replace('.', '').replace('-', '').isdigit() for val in x[:3]) else "category"
        jsx = f"""{title_component}
<ScatterChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" type="{x_axis_type}" />
  <YAxis dataKey="y" type="number" />
  <Tooltip />
  <Scatter data={data_json} fill="#8884d8" />
</ScatterChart>"""

    return jsx 