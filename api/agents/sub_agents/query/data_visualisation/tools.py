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


from google.cloud import bigquery
from google.oauth2 import service_account


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
    print(f"▶️ Building {chart_type} chart with {len(x)} data points")
    
    # Validate inputs
    if not x or not y:
        return "❌ Error: Both x and y data are required to build a chart."
    
    if len(x) != len(y):
        return f"❌ Error: x and y data must have the same length. Got x={len(x)}, y={len(y)}."
    
    # Validate chart type
    valid_types = ["line", "bar", "scatter"]
    if chart_type not in valid_types:
        chart_type = "line"  # Default fallback
    
    try:
        # Combine x and y into data points
        if chart_type == "scatter":
            # For scatter plots, try to convert x values to float for numeric axis
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
        title_component = f"<h2 style={{textAlign: 'center', marginBottom: '20px'}}>{title}</h2>" if title else ""
        
        # Generate chart-specific JSX with improved styling
        if chart_type == "line":
            jsx = f"""{title_component}
<div style={{width: '100%', height: '400px', display: 'flex', justifyContent: 'center'}}>
  <LineChart width={{600}} height={{350}} data={data_json} margin={{top: 20, right: 30, left: 20, bottom: 20}}>
    <XAxis dataKey="x" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Line type="monotone" dataKey="y" stroke="#2563eb" strokeWidth={{2}} dot={{fill: '#2563eb', strokeWidth: 2, r: 4}} />
  </LineChart>
</div>"""
        
        elif chart_type == "bar":
            jsx = f"""{title_component}
<div style={{width: '100%', height: '400px', display: 'flex', justifyContent: 'center'}}>
  <BarChart width={{600}} height={{350}} data={data_json} margin={{top: 20, right: 30, left: 20, bottom: 20}}>
    <XAxis dataKey="x" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Bar dataKey="y" fill="#2563eb" />
  </BarChart>
</div>"""
        
        elif chart_type == "scatter":
            # For scatter charts, determine if x-axis should be numeric or categorical
            x_axis_type = "number" if chart_type == "scatter" and all(str(val).replace('.', '').replace('-', '').isdigit() for val in x[:3]) else "category"
            jsx = f"""{title_component}
<div style={{width: '100%', height: '400px', display: 'flex', justifyContent: 'center'}}>
  <ScatterChart width={{600}} height={{350}} data={data_json} margin={{top: 20, right: 30, left: 20, bottom: 20}}>
    <XAxis dataKey="x" type="{x_axis_type}" />
    <YAxis dataKey="y" type="number" />
    <Tooltip />
    <Legend />
    <Scatter data={data_json} fill="#2563eb" />
  </ScatterChart>
</div>"""

        print(f"✅ Successfully generated {chart_type} chart JSX")
        return jsx
        
    except Exception as e:
        error_msg = f"❌ Error building chart: {str(e)}"
        print(error_msg)
        return error_msg 