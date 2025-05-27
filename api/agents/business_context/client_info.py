"""Client information and configuration."""

from typing import Dict, Any, Optional
from datetime import date
from zoneinfo import ZoneInfo
import os

# Fallback client information dictionary
FALLBACK_CLIENT_INFO: Dict[str, Any] = {
    "name": "Suraj Kaya",
    "preferred_name": "Suraj", 
    "user_id": "test_user",
    "company_name": "Growth Analytics Marketing",
    "company_short": "GAM",
    "origin_country": "AU",
    "countries_served": "Global",
    "timezone": "Australia/Sydney",
    "currency": "AUD", 
    "annual_target": "$1.2M",
    "current_date": "2025-05-21"
}


def get_client_info_from_firebase(user_id: str = "001") -> Optional[Dict[str, Any]]:
    """
    Get client information from Firebase business_context object.
    
    Args:
        user_id (str): The user ID to fetch business context for
        
    Returns:
        Optional[Dict[str, Any]]: Client information from Firebase or None if not found
    """
    try:
        # Import here to avoid circular imports
        from ...firebase_client import FirestoreSessionService
        
        # Initialize Firebase client
        session_service = FirestoreSessionService(collection_name="vendo_ai_memory")
        
        # Get user document
        user_doc = session_service.collection.document(user_id).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            business_context = user_data.get("business_context")
            print(f"[DEBUG] Business context: {business_context}", flush=True)
            
            if business_context and isinstance(business_context, dict):
                print(f"[DEBUG] Successfully loaded business_context for user {user_id}", flush=True)
                return business_context
            else:
                print(f"[DEBUG] No business_context found for user {user_id}", flush=True)
                return None
        else:
            print(f"[DEBUG] User {user_id} not found in Firebase", flush=True)
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to get business_context from Firebase for user {user_id}: {str(e)}", flush=True)
        return None


def get_client_info(user_id: str = "001") -> Dict[str, Any]:
    """
    Get the client information dictionary from Firebase with fallback to hardcoded values.
    
    Args:
        user_id (str): The user ID to fetch business context for
        
    Returns:
        Dict[str, Any]: Client information including name, company, timezone, etc.
    """
    # Try to get from Firebase first
    firebase_client_info = get_client_info_from_firebase(user_id)
    
    if firebase_client_info:
        # Merge with fallback values to ensure all required fields are present
        merged_info = FALLBACK_CLIENT_INFO.copy()
        merged_info.update(firebase_client_info)
        
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
    return date.fromisoformat(FALLBACK_CLIENT_INFO["current_date"])