"""Client information and configuration."""

from typing import Dict, Any
from datetime import date
from zoneinfo import ZoneInfo

# Client information dictionary
CLIENT_INFO: Dict[str, Any] = {
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
    "current_date": "2025-05-21"
}


def get_client_info() -> Dict[str, Any]:
    """
    Get the client information dictionary.
    
    Returns:
        Dict[str, Any]: Client information including name, company, timezone, etc.
    """
    return CLIENT_INFO.copy()


def get_client_timezone() -> ZoneInfo:
    """
    Get the client's timezone as a ZoneInfo object.
    
    Returns:
        ZoneInfo: The client's timezone.
    """
    return ZoneInfo(CLIENT_INFO["timezone"])


def get_current_date() -> date:
    """
    Get the current date as configured for the client.
    
    Returns:
        date: The current date for the client context.
    """
    return date.fromisoformat(CLIENT_INFO["current_date"])