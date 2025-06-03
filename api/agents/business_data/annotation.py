from typing import List, Dict

def get_annotations() -> List[Dict[str, str]]:
    """Return a list of business annotations with date and description."""
    return [
        {"date": "2025-01-02", "description": "Google Ads campaign started"},
        {"date": "2025-02-05", "description": "Meta Campaign stopped."},
    ] 