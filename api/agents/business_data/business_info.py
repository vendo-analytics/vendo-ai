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
}


def get_info() -> Dict[str, Any]:
    """
    Get the client information dictionary.
    
    Returns:
        Dict[str, Any]: Client information including name, company, timezone, etc.
    """
    return CLIENT_INFO.copy()