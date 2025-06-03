user_state = {}

def update_business_context_in_state(connection_id: str, context: dict):
    user_state[connection_id] = context

def get_business_context_from_state(connection_id: str) -> dict:
    return user_state.get(connection_id, {})

def update_annotations_in_state(connection_id: str, annotations: list):
    user_state[connection_id]["annotations"] = annotations

def get_annotations_in_state(connection_id: str):
    return user_state.get(connection_id, {}).get("annotations", [])