"""Client information and configuration."""

from typing import Dict, Any, Optional
from datetime import date
from zoneinfo import ZoneInfo

from ...firestore_instance import firestore_session_service
from ...state_manager import get_business_context_from_state


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
    "dataset_id":"12345678"
}


def get_info(user_id: str):
    """
    Get the client information dictionary from Firebase with fallback to hardcoded values.
    
    Args:
        user_id (str): The user ID to fetch business context for
        
    Returns:
        Dict[str, Any]: Client information including name, company, timezone, etc.
    """
    # Try to get from Firebase first
    cached = get_business_context_from_state(user_id)
    if cached:
        return cached
    

    firestore_business_context = firestore_session_service.get_client_info_from_firebase(user_id)
    #firestore_business_context = None
    if firestore_business_context:
        print(f"[DEBUG] Business context for {user_id}: {firestore_business_context}")
    else:
        print(f"[DEBUG] No business context found for {user_id}")
    if firestore_business_context:
        # Merge with fallback values to ensure all required fields are present
        merged_info = FALLBACK_CLIENT_INFO.copy()
        merged_info.update(firestore_business_context)
        
        # Ensure current_date is always up to date
        merged_info["current_date"] = date.today().strftime("%Y-%m-%d")
        
        print(f"[DEBUG] Using Firebase business_context for user {user_id}", flush=True)
        return merged_info
    else:
        # Use fallback values
        fallback_info = FALLBACK_CLIENT_INFO.copy()
        fallback_info["current_date"] = date.today().strftime("%Y-%m-%d")
        
        print(f"[DEBUG] Using fallback client_info for user {user_id}", flush=True)
        return fallback_info




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