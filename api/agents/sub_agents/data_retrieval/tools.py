from typing import Dict, List, Optional, TypedDict, Any
from datetime import datetime, date
from decimal import Decimal
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
import os
from ...firestore_instance import firestore_session_service
from ...state_manager import get_current_connection_id


def convert_to_json_serializable(obj):
    """
    Recursively convert non-JSON-serializable objects (dates, decimals) to serializable types.
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..', '..')
        service_key_path = os.path.join(project_root, 'service_key.json')
        credentials = service_account.Credentials.from_service_account_file(
            service_key_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)

        # Block until done (with timeout)
        df = query_job.result(timeout=60).to_dataframe()
        result_data = df.to_dict(orient="records")
        
        # Convert non-JSON-serializable objects to serializable types
        result_data = convert_to_json_serializable(result_data)

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

def query_mixpanel_event_schema(connection_id: Optional[str] = None):
    """
    Query the combined Mixpanel Event Schema to return all events, descriptions, and properties
    in a structured format suitable for analysis and querying.
    
    Use this tool to:
    - Get an overview of all available events and their properties
    - Understand what data is available for analysis
    - Find event names and property names for building queries
    
    Args:
        connection_id (Optional[str]): The connection ID to fetch data for. 
                                     If not provided, uses current connection.
        
    Returns:
        dict: Structured event schema with events, descriptions, and properties
        
    Example usage:
        schema = query_mixpanel_event_schema()
        print(f"Found {schema['total_events']} events")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] query_mixpanel_event_schema using connection_id: {connection_id}", flush=True)
        
    try:
        # Get base schema (left table)
        base_schema = firestore_session_service.get_mixpanel_event_schema(connection_id) or {"events": {}}
        print(f"[DEBUG] Base schema has {len(base_schema.get('events', {}))} events", flush=True)
        
        # Get user edits (right table for join)
        user_edits = firestore_session_service.get_mixpanel_event_schema_edits(connection_id) or {"events": {}}
        print(f"[DEBUG] User edits has {len(user_edits.get('events', {}))} events", flush=True)
        
        # Structure to return
        result = {
            "events": [],
            "total_events": 0,
            "total_properties": 0
        }
        
        # Combine base schema with user edits
        for event_name, event_data in base_schema.get("events", {}).items():
            combined_event = {
                "event_name": event_name,
                "description": event_data.get("description", ""),
                "first_seen": event_data.get("first_seen"),
                "last_seen": event_data.get("last_seen"),
                "last_30_day_count": event_data.get("last_30_day_count", 0),
                "status": event_data.get("status", "unknown"),
                "properties": []
            }
            
            # Apply user edits to event description if available
            if event_name in user_edits.get("events", {}):
                user_event_edits = user_edits["events"][event_name]
                if user_event_edits.get("description"):
                    combined_event["description"] = user_event_edits["description"]
            
            # Process properties
            for prop_name, prop_data in event_data.get("properties", {}).items():
                combined_property = {
                    "property_name": prop_name,
                    "description": prop_data.get("description", ""),
                    "data_type": prop_data.get("data_type", "unknown"),
                    "sample_values": prop_data.get("sample_values", []),
                    "is_required": prop_data.get("is_required", False)
                }
                
                # Apply user edits to property if available
                if (event_name in user_edits.get("events", {}) and 
                    prop_name in user_edits["events"][event_name].get("properties", {})):
                    user_prop_edits = user_edits["events"][event_name]["properties"][prop_name]
                    if user_prop_edits.get("description"):
                        combined_property["description"] = user_prop_edits["description"]
                    if user_prop_edits.get("data_type"):
                        combined_property["data_type"] = user_prop_edits["data_type"]
                
                combined_event["properties"].append(combined_property)
            
            result["events"].append(combined_event)
            result["total_properties"] += len(combined_event["properties"])
        
        result["total_events"] = len(result["events"])
        print(f"[DEBUG] Final result: {result['total_events']} events, {result['total_properties']} properties", flush=True)
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed to query event schema: {str(e)}", flush=True)
        return {"events": [], "total_events": 0, "total_properties": 0, "error": str(e)}

def get_event_by_name(event_name: str, connection_id: Optional[str] = None):
    """
    Get detailed information about a specific event by name from the schema.
    
    Use this tool to:
    - Get details about a specific event (description, properties, etc.)
    - Understand what properties are available for a specific event
    - Validate if an event exists before building queries
    
    Args:
        event_name (str): The name of the event to retrieve (e.g., "Order Received", "Page Viewed")
        connection_id (Optional[str]): The connection ID to fetch data for.
                                     If not provided, uses current connection.
        
    Returns:
        dict: Event details including properties, or None if not found
        
    Example usage:
        event = get_event_by_name("Order Received")
        if event:
            print(f"Event has {len(event['properties'])} properties")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] get_event_by_name searching for '{event_name}' using connection_id: {connection_id}", flush=True)
        
    schema = query_mixpanel_event_schema(connection_id)
    
    for event in schema.get("events", []):
        if event["event_name"].lower() == event_name.lower():
            print(f"[DEBUG] Found event: {event['event_name']}", flush=True)
            return event
    
    print(f"[DEBUG] Event '{event_name}' not found", flush=True)
    return None

def get_events_by_property(property_name: str, connection_id: Optional[str] = None):
    """
    Find all events that contain a specific property name.
    
    Use this tool to:
    - Find which events contain a specific property (e.g., "order_id", "product_id")
    - Understand data relationships across events
    - Validate property availability before building queries
    
    Args:
        property_name (str): The name of the property to search for (e.g., "order_id", "product_id")
        connection_id (Optional[str]): The connection ID to fetch data for.
                                     If not provided, uses current connection.
        
    Returns:
        list: Events that contain the specified property
        
    Example usage:
        events = get_events_by_property("order_id")
        print(f"Found {len(events)} events with 'order_id' property")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] get_events_by_property searching for property '{property_name}' using connection_id: {connection_id}", flush=True)
        
    schema = query_mixpanel_event_schema(connection_id)
    matching_events = []
    
    for event in schema.get("events", []):
        for prop in event.get("properties", []):
            if prop["property_name"].lower() == property_name.lower():
                matching_events.append(event)
                break
    
    print(f"[DEBUG] Found {len(matching_events)} events with property '{property_name}'", flush=True)
    return matching_events

def search_events_by_description(search_term: str, connection_id: Optional[str] = None):
    """
    Search for events by keywords in their descriptions.
    
    Use this tool to:
    - Find events related to specific business processes (e.g., "checkout", "payment")
    - Discover relevant events when building queries
    - Explore available events by functionality
    
    Args:
        search_term (str): Keywords to search for in event descriptions (e.g., "checkout", "payment")
        connection_id (Optional[str]): The connection ID to fetch data for.
                                     If not provided, uses current connection.
        
    Returns:
        list: Events whose descriptions contain the search term
        
    Example usage:
        events = search_events_by_description("checkout")
        print(f"Found {len(events)} events related to checkout")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] search_events_by_description searching for '{search_term}' using connection_id: {connection_id}", flush=True)
        
    schema = query_mixpanel_event_schema(connection_id)
    matching_events = []
    
    search_term_lower = search_term.lower()
    
    for event in schema.get("events", []):
        description = event.get("description") or ""
        if search_term_lower in description.lower():
            matching_events.append(event)
    
    print(f"[DEBUG] Found {len(matching_events)} events with description containing '{search_term}'", flush=True)
    return matching_events 

def query_mixpanel_user_schema(connection_id: Optional[str] = None):
    """
    Query the combined Mixpanel User Schema to return all user properties and their details
    in a structured format suitable for analysis and querying.
    
    Use this tool to:
    - Get an overview of all available user properties
    - Understand what user data is available for analysis
    - Find user property names for building queries
    
    Args:
        connection_id (Optional[str]): The connection ID to fetch data for. 
                                     If not provided, uses current connection.
        
    Returns:
        dict: Structured user schema with properties and details
        
    Example usage:
        schema = query_mixpanel_user_schema()
        print(f"Found {schema['total_properties']} user properties")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] query_mixpanel_user_schema using connection_id: {connection_id}", flush=True)
        
    try:
        # Get raw user properties from BigQuery
        raw_properties = firestore_session_service.get_mixpanel_user_properties_raw(connection_id) or []
        print(f"[DEBUG] Raw user properties has {len(raw_properties)} properties", flush=True)
        
        # Get user edits (Firebase edits)
        user_edits = firestore_session_service.get_mixpanel_user_properties_edits(connection_id) or {}
        print(f"[DEBUG] User edits has {len(user_edits)} properties", flush=True)
        
        # Structure to return
        result = {
            "properties": [],
            "total_properties": 0
        }
        
        # Combine raw properties with user edits
        for raw_prop in raw_properties:
            property_name = raw_prop.get("name")
            combined_property = {
                "property_name": property_name,
                "description": raw_prop.get("description", ""),
                "data_type": raw_prop.get("type", "unknown"),
                "sample_values": [raw_prop.get("sample_value")] if raw_prop.get("sample_value") else [],
                "is_required": False,  # Not available in raw data
                "first_seen": None,    # Not available in raw data
                "last_seen": None,     # Not available in raw data
                "status": "active"     # Default status
            }
            
            # Apply user edits to property if available
            if property_name in user_edits:
                user_property_edits = user_edits[property_name]
                if user_property_edits.get("description"):
                    combined_property["description"] = user_property_edits["description"]
                if user_property_edits.get("type"):
                    combined_property["data_type"] = user_property_edits["type"]
            
            result["properties"].append(combined_property)
        
        result["total_properties"] = len(result["properties"])
        print(f"[DEBUG] Final result: {result['total_properties']} user properties", flush=True)
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed to query user schema: {str(e)}", flush=True)
        return {"properties": [], "total_properties": 0, "error": str(e)}

def get_user_property_by_name(property_name: str, connection_id: Optional[str] = None):
    """
    Get detailed information about a specific user property by name from the schema.
    
    Use this tool to:
    - Get details about a specific user property (description, data type, etc.)
    - Validate if a user property exists before building queries
    - Understand what values are available for a specific user property
    
    Args:
        property_name (str): The name of the user property to retrieve (e.g., "total_spent", "city")
        connection_id (Optional[str]): The connection ID to fetch data for.
                                     If not provided, uses current connection.
        
    Returns:
        dict: User property details, or None if not found
        
    Example usage:
        property = get_user_property_by_name("total_spent")
        if property:
            print(f"Property type: {property['data_type']}")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] get_user_property_by_name searching for '{property_name}' using connection_id: {connection_id}", flush=True)
        
    schema = query_mixpanel_user_schema(connection_id)
    
    for prop in schema.get("properties", []):
        if prop["property_name"].lower() == property_name.lower():
            print(f"[DEBUG] Found user property: {prop['property_name']}", flush=True)
            return prop
    
    print(f"[DEBUG] User property '{property_name}' not found", flush=True)
    return None

def search_user_properties_by_description(search_term: str, connection_id: Optional[str] = None):
    """
    Search for user properties by keywords in their descriptions.
    
    Use this tool to:
    - Find user properties related to specific attributes (e.g., "marketing", "location")
    - Discover relevant user properties when building queries
    - Explore available user properties by functionality
    
    Args:
        search_term (str): Keywords to search for in property descriptions (e.g., "marketing", "location")
        connection_id (Optional[str]): The connection ID to fetch data for.
                                     If not provided, uses current connection.
        
    Returns:
        list: User properties whose descriptions contain the search term
        
    Example usage:
        properties = search_user_properties_by_description("marketing")
        print(f"Found {len(properties)} user properties related to marketing")
    """
    if connection_id is None:
        connection_id = get_current_connection_id()
    
    print(f"[DEBUG] search_user_properties_by_description searching for '{search_term}' using connection_id: {connection_id}", flush=True)
        
    schema = query_mixpanel_user_schema(connection_id)
    matching_properties = []
    
    search_term_lower = search_term.lower()
    
    for prop in schema.get("properties", []):
        description = prop.get("description") or ""
        if search_term_lower in description.lower():
            matching_properties.append(prop)
    
    print(f"[DEBUG] Found {len(matching_properties)} user properties with description containing '{search_term}'", flush=True)
    return matching_properties 
