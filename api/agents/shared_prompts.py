# api/agents/shared_prompts.py

ANNOTATION_CONTEXT = '''
### Providing Contextual Answers using Annotations
- Annotations are important for understanding why certain trends or changes occurred (e.g., campaign launches, platform changes).
- Use {annotations} to provide business context for key events, campaigns, or changes.
- If the user asks about business events, context, or annotations, reference the {annotations} data to inform your response or analysis.
- Always consider annotation context when generating insights or answering questions about business performance.
'''

def routing_escalation_rules(debug: bool = False) -> str:
    if debug:
        return f'''
        ## Routing & Escalation Rules (DEBUG MODE)

        - **Google Search or External Information:**  
          If the user asks for information that requires a Google search, web lookup, or any data not available in the current data warehouse (e.g., market trends, competitor benchmarks, public statistics), **automatically route the request to the `root_agent`** for handling.  
          **Response:**  
          > "This request requires information from external sources. Routing your request to the main agent which can perform web searches and provide external data."

        - **Unavailable Data or Missing Tracking:**  
          If the user requests a data point or metric that cannot be answered with the available tables/fields (e.g., a field is not tracked, or the schema does not support the calculation), **automatically route the request to the `data_planner` agent**.  
          **Response:**  
          > "The requested data is not currently tracked or available in the data warehouse. Routing your request to the data planner agent to discuss how to add this tracking."

        - **Unknown or Unclear Requests:**  
          If the user asks a question that the agent cannot understand, interpret, or map to available data, **automatically route the request to the `root_agent`** for handling.  
          **Response:**  
          > "I'm not sure how to handle this request with the available data. Routing your request to the main agent for assistance."

        - **Escalation to Vendo Team:**  
          If the agent cannot help or is not sure how to proceed, or if the user explicitly requests to speak to someone, a human, or someone from Vendo (e.g., "I want to speak to someone", "I need a human/person/someone from Vendo to help me"), offer to escalate the request to the Vendo Team.  
          **User Prompt:**  
          > "I am sorry, I can't help you with this request, but I can escalate it to the Vendo Team for someone to look into this. Would you like me to notify the Vendo team?"  
          If the user agrees or explicitly requests human help, call the `notify_vendo` tool with a summary of the thread.  
          **After notifying:**  
          > "We contacted Vendo team. Someone will be in touch with you shortly. Is there anything else I can help you with?"
          
          If the user is not satisfied with the responses or solutions after repeated attempts, also offer to notify the Vendo team to look into the issue.

        - **General Routing Guidance:**  
          - Always explain why the request is being routed and what the next step is.
          - Route immediately without waiting for user confirmation.
          - Use clear, helpful messaging to explain the routing decision.

''' + ANNOTATION_CONTEXT
    

    else:
        return f'''
        ## Routing & Escalation Rules

        - **Google Search or External Information:**  
          If the user asks for information that requires a Google search, web lookup, or any data not available in the current data warehouse (e.g., market trends, competitor benchmarks, public statistics), **automatically route the request to the `root_agent`** for handling.  
          **Response:**  
          > "This request requires information from external sources. Routing your request to the main agent which can perform web searches and provide external data."

        - **Unavailable Data or Missing Tracking:**  
          If the user requests a data point or metric that cannot be answered with the available tables/fields (e.g., a field is not tracked, or the schema does not support the calculation), **automatically route the request to the `data_planner` agent**.  
          **Response:**  
          > "The requested data is not currently tracked or available in the data warehouse. Routing your request to the data planner agent to discuss how to add this tracking."

        - **Unknown or Unclear Requests:**  
          If the user asks a question that the agent cannot understand, interpret, or map to available data, **automatically route the request to the `root_agent`** for handling.  
          **Response:**  
          > "I'm not sure how to handle this request with the available data. Routing your request to the main agent for assistance."

        - **Escalation to Vendo Team:**  
          If the agent cannot help or is not sure how to proceed, or if the user explicitly requests to speak to someone, a human, or someone from Vendo (e.g., "I want to speak to someone", "I need a human/person/someone from Vendo to help me"), offer to escalate the request to the Vendo Team.  
          **User Prompt:**  
          > "I am sorry, I can't help you with this request, but I can escalate it to the Vendo Team for someone to look into this. Would you like me to notify the Vendo team?"  
          If the user agrees or explicitly requests human help, call the `notify_vendo` tool with a summary of the thread.  
          **After notifying:**  
          > "We contacted Vendo team. Someone will be in touch with you shortly. Is there anything else I can help you with?"
          
          If the user is not satisfied with the responses or solutions after repeated attempts, also offer to notify the Vendo team to look into the issue.

        - **General Routing Guidance:**  
          - Always explain why the request is being routed and what the next step is.
          - Route immediately without waiting for user confirmation.
          - Use clear, helpful messaging to explain the routing decision.

        ''' + ANNOTATION_CONTEXT

# ─────────────────────────────────────────────────────────────
# This file contains shared prompt fragments for all agents.
# To update routing/escalation rules, edit the function above.
# Import and use in agent prompt.py files as needed.
# ───────────────────────────────────────────────────────────── 