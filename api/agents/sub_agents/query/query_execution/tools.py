from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime
import pandas as pd
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Optional
import json



def query_bigquery(query: str):
    '''
    Executes a BigQuery SQL query and returns a structured response.

    Returns:
        - On success (with results): dict containing mime_type, data (Markdown), and raw_data.
        - On success (no results): dict with success message and empty raw_data.
        - On failure: error string starting with ❌
    '''
    from google.cloud import bigquery
    from google.oauth2 import service_account
    import pandas as pd

    print("▶️ Running query_bigquery()")

    credentials = service_account.Credentials.from_service_account_file(
        'service_key.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    try:
        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)
        event_data_df = query_job.result(timeout=60).to_dataframe()

        result_data = event_data_df.to_dict(orient='records')

        if len(result_data) == 0:
            message = "✅ Query executed successfully, but no rows were returned."
        else:
            columns = event_data_df.columns.tolist()
            message = "✅ Query Results:\n"
            message += "\n| " + " | ".join(columns) + " |"
            message += "\n|" + "|".join(["---"] * len(columns)) + "|"
            for row in result_data:
                message += "\n| " + " | ".join(str(row[col]) for col in columns) + " |"

        return {
            "mime_type": "text/plain",
            "data": message,
            "raw_data": result_data
        }

    except Exception as e:
        return f"❌ Error executing query: {str(e)}"

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