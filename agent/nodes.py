import os
import re
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agent.state import AgentState
from utils.database import get_db_schema, execute_sql_query

# Initialize Groq LLM (100% free and lightning fast cloud API)
# Llama 3.1 8b is very fast and has higher rate limits for free tier
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, request_timeout=30.0)

# def extract_sql_query(text: str) -> str:
#     """Helper to extract SQL query from markdown backticks if present."""
#     match = re.search(r'```sql\\s*(.*?)\\s*```', text, re.DOTALL)
#     if match:
#         return match.group(1).strip()
#     return text.strip()

def extract_sql_query(text: str) -> str:
    """Pull the SQL out of a markdown code block if there is one."""
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()

def generate_sql(state: AgentState) -> dict:
    """
    Node to translate natural language to SQL.
    """
    question = state["question"]
    schema = get_db_schema()
    
    # Provide schema and prompt to the model
    system_prompt = f"""You are an expert SQL assistant. Your task is to generate a valid SQLite SQL query to answer the user's question, given the following database schema:

{schema}

IMPORTANT:
- ONLY return a SELECT statement to retrieve the answer.
- DO NOT return any Data Manipulation Language (DML) statements like INSERT, UPDATE, DELETE, or DROP.
- ALWAYS wrap your SQL query in ```sql ... ``` block.
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    
    # If there was a previous validation error, feed it back to correct the query
    if state.get("validation_error"):
        error_msg = f"Your previous SQL query was invalid. The error was:\\n{state['validation_error']}\\nPlease fix the query."
        messages.append(HumanMessage(content=error_msg))
    
    response = llm.invoke(messages)
    sql_query = extract_sql_query(response.content)
    print("GENERATED SQL:", sql_query)
    return {"sql_query": sql_query}

def validate_sql(state: AgentState) -> dict:
    """
    Node to validate the generated SQL query before execution.
    Ensures it's not a modifying query.
    """
    query = state["sql_query"]
    query_upper = query.upper().strip()
    
    # Basic security check
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE"]
    
    if any(keyword in query_upper for keyword in forbidden_keywords):
        return {
            "is_valid_sql": False, 
            "validation_error": "Query contains forbidden DML instructions (e.g., INSERT, UPDATE, DELETE). Only SELECT is allowed.",
            "error_count": state.get("error_count", 0) + 1
        }
        
    if not query_upper.startswith("SELECT"):
        return {
            "is_valid_sql": False,
            "validation_error": "Query must start with SELECT.",
            "error_count": state.get("error_count", 0) + 1
        }
    print("VALIDATION: OK")
    return {"is_valid_sql": True, "validation_error": ""}

def execute_query(state: AgentState) -> dict:
    """
    Node to execute the validated SQL against the database.
    """
    query = state["sql_query"]
    result = execute_sql_query(query)
    
    # Check if execution failed
    if result.startswith("Database error") or result.startswith("Unknown error"):
        # Let's consider execution errors as validation errors so we can retry
        return {
            "is_valid_sql": False,
            "validation_error": result,
            "error_count": state.get("error_count", 0) + 1
        }
        
    return {"query_result": result, "error_count": 0} # reset error count on success

def interpret_results(state: AgentState) -> dict:
    """
    Node to translate raw database results into a natural language string.
    """
    question = state["question"]
    query = state["sql_query"]
    result = state["query_result"]
    
    system_prompt = f"""You are an advanced data assistant. You must directly answer the user's question based on the raw results of their SQL query.Salaries and budgets are in Indian rupees (INR). Write amounts with the rupee sign or "INR", never dollars.

User Question: {question}
Executed SQL Query: {query}
Raw SQL Results:
{result}

Provide a concise, human-friendly answer. Do not show the SQL query unless explicitly asked. Just provide the final answer clearly."""

    response = llm.invoke([SystemMessage(content=system_prompt)])
    
    return {"final_answer": response.content}
