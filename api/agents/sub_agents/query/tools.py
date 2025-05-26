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
    """Execute a BigQuery SQL query and return formatted results."""
    print("▶️ Executing BigQuery...")
    credentials = service_account.Credentials.from_service_account_file(
            'service_key.json',
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    try:
        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        event_data_df = client.query(query, job_config=job_config).to_dataframe()
        
        print(f"Query returned {len(event_data_df)} rows")
        result_data = event_data_df.to_dict(orient='records')
        
        if len(result_data) == 0:
            return "✅ Query executed successfully, but no rows were returned."
        else:
            # Format all rows as a readable table
            message = "✅ Query Results:\n\n"
            # Get column names from first row
            columns = list(result_data[0].keys())
            # Add header
            message += "| " + " | ".join(columns) + " |\n"
            message += "|" + "|".join(["---" for _ in columns]) + "|\n"
            # Add rows (limit to first 100 rows for readability)
            display_rows = result_data[:100]
            for row in display_rows:
                formatted_values = []
                for col in columns:
                    value = row[col]
                    # Format decimal values to 2 decimal places for readability
                    if hasattr(value, 'quantize'):  # Decimal type
                        formatted_values.append(f"{float(value):.2f}")
                    else:
                        formatted_values.append(str(value))
                message += "| " + " | ".join(formatted_values) + " |\n"
            
            if len(result_data) > 100:
                message += f"\n... and {len(result_data) - 100} more rows (showing first 100)"
            
            message += f"\n\n**Total rows returned:** {len(result_data)}"
            return message
            
    except Exception as e:
        error_msg = f"❌ Error executing BigQuery: {str(e)}"
        print(error_msg)
        return error_msg

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