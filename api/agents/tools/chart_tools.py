from typing import List, Optional, Dict, Any
import json


def build_chart(
    x: List[str], 
    y: List[float], 
    title: Optional[str] = None, 
    chart_type: str = "line",
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates JSX code for a Recharts chart using provided x/y values.
    Returns a dict with a JSX string for the chart, embedding the caption and title directly in the JSX.

    Args:
        x: List of strings (e.g. dates, categories, or numeric values as strings)
        y: List of numbers (e.g. sales, revenue, etc.)
        title: Optional title for the chart
        chart_type: Type of chart - "line", "bar", or "scatter" (default: "line")
        caption: Optional descriptive caption to display with the chart

    Returns:
        Dict with key 'chart' (JSX string)
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
    
    # Build the JSX string with optional title and caption
    caption_component = f"<div style={{textAlign: 'center', color: '#666', marginBottom: '12px'}}>{caption}</div>" if caption else "No caption provided"
    title_component = f"<h2>{title}</h2>" if title else ""
    
    # Generate chart-specific JSX
    if chart_type == "line":
        jsx = f"""{caption_component}{title_component}
<LineChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" />
</LineChart>"""
    
    elif chart_type == "bar":
        jsx = f"""{caption_component}{title_component}
<BarChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="y" fill="#8884d8" />
</BarChart>"""
    
    elif chart_type == "scatter":
        # For scatter charts, determine if x-axis should be numeric or categorical
        x_axis_type = "number" if chart_type == "scatter" and all(str(val).replace('.', '').replace('-', '').isdigit() for val in x[:3]) else "category"
        jsx = f"""{caption_component}{title_component}
<ScatterChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" type="{x_axis_type}" />
  <YAxis dataKey="y" type="number" />
  <Tooltip />
  <Scatter data={data_json} fill="#8884d8" />
</ScatterChart>"""
        
    print("CHART",jsx, flush=True)

    return {"chart": jsx} 