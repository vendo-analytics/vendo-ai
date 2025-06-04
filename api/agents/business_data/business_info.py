"""Client information and configuration."""

from typing import Dict, Any, Optional
from datetime import date
from zoneinfo import ZoneInfo

from ...firestore_instance import firestore_session_service
from ...state_manager import get_current_connection_id
from ...mixpanel_client import MixpanelClient
from fastapi.responses import JSONResponse

# Fallback client information dictionary
FALLBACK_CLIENT_INFO: Dict[str, Any] = {
    "name": "Yalcin Kaya",
    "preferred_name": "Yalcin", 
    "user_id": "test_user",
    "company_name": "Growth Analytics Marketing",
    "company_short": "GAM",
    "origin_country": "AU",
    "countries_served": "Global",
    "timezone": "Australia/Sydney",
    "currency": "AUD", 
    "annual_target": "$1.2M",
    "current_date": date.today().strftime("%Y-%m-%d"),
    "dataset_id":"12345678",
    
}


def get_info(connection_id: str = None):
    """
    Get the client information dictionary from Firebase with fallback to hardcoded values.
    Uses the provided connection_id or falls back to current connection_id from global state.
    
    Args:
        connection_id (str, optional): The connection ID to use. If None, uses global state.
        
    Returns:
        Dict[str, Any]: Client information including name, company, timezone, etc.
    """
    # Use provided connection_id or get from state_manager
    if connection_id is None:
        connection_id = get_current_connection_id()
    print(f"[DEBUG] Using connection_id: {connection_id}", flush=True)
    
    # # Try to get from cached state first
    # cached_context = get_business_context_from_state()
    # print(f"[DEBUG] Cached context: {cached_context}", flush=True)
    # cached_annotations = get_annotations_in_state()
    mixpanel_annotations = get_annotations_from_mixpanel(connection_id)
    

    # if cached_annotations:
    #     annotations = cached_annotations
    if mixpanel_annotations:
         annotations = mixpanel_annotations
    else:
         annotations = None
    print(f"[DEBUG] Annotations: {annotations}", flush=True)
    
    # if cached_context:
    #     return cached_context, annotations

    firestore_business_context = firestore_session_service.get_business_context_from_firebase(connection_id)
    print(f"[DEBUG] Firestore business context: {firestore_business_context}", flush=True)
    #firestore_business_context = None
    if firestore_business_context:
        print(f"[DEBUG] Business context for {connection_id}: {firestore_business_context}")
    else:
        print(f"[DEBUG] No business context found for {connection_id}")
    if firestore_business_context:
        # Merge with fallback values to ensure all required fields are present
        merged_info = FALLBACK_CLIENT_INFO.copy()
        merged_info.update(firestore_business_context)
        
        # Ensure current_date is always up to date
        merged_info["current_date"] = date.today().strftime("%Y-%m-%d")
        
        print(f"[DEBUG] Using Firebase business_context for user {connection_id}", flush=True)
        return merged_info, annotations
    else:
        # Use fallback values
        fallback_info = FALLBACK_CLIENT_INFO.copy()
        fallback_info["current_date"] = date.today().strftime("%Y-%m-%d")
        
        print(f"[DEBUG] Using fallback client_info for user {connection_id}", flush=True)
        return fallback_info, annotations




def get_client_timezone() -> ZoneInfo:
    """
    Get the client's timezone as a ZoneInfo object.
    
    Returns:
        ZoneInfo: The client's timezone.
    """
    return ZoneInfo(FALLBACK_CLIENT_INFO["timezone"])


def get_current_date() -> date:
    """
    Get the current date as configured for the client.
    
    Returns:
        date: The current date for the client context.
    """
    return date.today()


def get_annotations_from_mixpanel(connection_id: str):
    
    # Call your Mixpanel annotations fetcher
    mixpanel_client = MixpanelClient(connection_id)
    df = mixpanel_client.get_mixpanel_annotations_data()
    records = df.to_dict(orient="records")
    annotations = [
        {
            "id": str(row.get("id", "")),
            "date": row.get("date", ""),
            "description": row.get("description", ""),
            "user": f"{row.get('user_first_name', '')} {row.get('user_last_name', '')}".strip(),
        }
        for row in records
    ]
    print(f"[DEBUG] Annotations: {annotations}", flush=True)
    return JSONResponse(content=annotations)