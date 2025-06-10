user_state = {}
current_connection_id = "001"  # Default fallback
current_session_id = None  # Default session ID
debug_mode = False  # Global debug mode state

def set_current_connection_id(connection_id: str):
    """Set the current active connection ID globally"""
    global current_connection_id
    current_connection_id = connection_id
    print(f"[DEBUG] Set current connection ID to: {connection_id}", flush=True)

def get_current_connection_id() -> str:
    """Get the current active connection ID"""
    return current_connection_id

def set_current_session_id(session_id: str):
    """Set the current active session ID globally"""
    global current_session_id
    current_session_id = session_id
    print(f"[DEBUG] Set current session ID to: {session_id}", flush=True)

def get_current_session_id() -> str:
    """Get the current active session ID"""
    return current_session_id

def set_debug_mode(is_debug: bool):
    """Set global debug mode"""
    global debug_mode
    debug_mode = is_debug
    print(f"[DEBUG] Set debug mode to: {is_debug}", flush=True)

def get_debug_mode() -> bool:
    """Get global debug mode"""
    return debug_mode

# def update_business_context_in_state(connection_id: str, context: dict):
#     """Update business context and set as current connection"""
#     set_current_connection_id(connection_id)
#     user_state[connection_id] = context

# def get_business_context_from_state() -> dict:
#     """Get business context for current connection"""
#     return user_state.get(current_connection_id, {})

# def update_annotations_in_state(connection_id: str, annotations: list):
#     """Update annotations and set as current connection"""
#     set_current_connection_id(connection_id)
#     if current_connection_id not in user_state:
#         user_state[current_connection_id] = {}
#     user_state[current_connection_id]["annotations"] = annotations

# def get_annotations_in_state():
#     """Get annotations for current connection"""
#     return user_state.get(current_connection_id, {}).get("annotations", [])