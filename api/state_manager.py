user_state = {}

def update_business_context_in_state(user_id: str, context: dict):
    user_state[user_id] = context

def get_business_context_from_state(user_id: str) -> dict:
    return user_state.get(user_id, {})