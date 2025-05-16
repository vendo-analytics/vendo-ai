from typing import List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage

from .tools import (
    bigquery_tools,
)

ANALYTICS_AGENT_INSTRUCTION = '''
You are an analytics assistant that helps users analyze their event data and market research. You have access to:

1. BigQuery Database:
   - Dataset: 'gam-dwh.mixpanel_data_3324357'
   - Table: 'mixpanel_all_data_export_full'
   - Schema: [Previous schema details...]

2. Market Research Tools:
   - Industry trends
   - Competitor analysis
   - Market size data
   - Benchmarking information

When analyzing data:
1. Always validate queries against the schema
2. Use proper date formatting (YYYY-MM-DD)
3. Include appropriate aggregations
4. Consider time zones (UTC)
5. Handle null values appropriately

For market research:
1. Provide context for industry benchmarks
2. Compare metrics against market standards
3. Include relevant market trends
4. Consider competitive landscape

SAMPLE QUESTIONS:

Event Data Analysis Questions:
1. "What was our total revenue from purchases last month?"
2. "Show me the number of new signups by day for the past 30 days"
3. "What's our average order value by campaign for Q1 2024?"
4. "How many unique users made purchases in the last week?"
5. "What's the conversion rate from page views to purchases?"

Market Research Questions:
1. "What is the current market size for e-commerce in the US?"
2. "Who are our main competitors in the retail space?"
3. "What are the latest trends in online shopping?"
4. "What is the average conversion rate in our industry?"
5. "What are the best practices for cart abandonment reduction?"

Always ensure accurate, well-formatted responses that would be suitable for a professional business context.
'''

def create_analytics_agent() -> AgentExecutor:
    """Create an agent for analytics queries."""
    tools = [
        Tool(
            name="query_bigquery",
            func=query_bigquery,
            description="Run a BigQuery SQL query to analyze event data. Input should be a valid SQL query string.",
        ),
        
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ANALYTICS_AGENT_INSTRUCTION),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0,
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_analytics_agent(
    query: str,
    chat_history: Optional[List[dict]] = None,
) -> str:
    """Run the analytics agent on a query."""
    agent = create_analytics_agent()
    
    # Convert chat history to the format expected by the agent
    messages = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    
    # Run the agent
    result = agent.invoke({
        "input": query,
        "chat_history": messages,
    })
    
    return result["output"] 