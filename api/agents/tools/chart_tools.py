from typing import List, Optional
import json


def build_chart(x: List[str], y: List[float], title: Optional[str] = None) -> str:
    """
    Generates JSX code for a Recharts LineChart using provided x/y values.
    Returns a JSX string to render a chart in a Next.js frontend.

    Args:
        x: List of strings (e.g. dates or categories)
        y: List of numbers (e.g. sales, revenue, etc.)
        title: Optional title for the chart

    Returns:
        A string of JSX code for rendering a <LineChart> with XAxis, YAxis, Tooltip, 
        and Line components from Recharts
    """
    # Combine x and y into data points
    data_points = [{"x": str(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
    
    # Convert data points to a JSON string and ensure proper escaping for JSX
    data_json = json.dumps(data_points).replace('"', "'")
    
    # Build the JSX string with optional title
    title_component = f"<h2>{title}</h2>" if title else ""
    
    jsx = f"""{title_component}
<LineChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" />
</LineChart>"""

    return jsx 