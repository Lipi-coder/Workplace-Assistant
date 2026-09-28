import operator
from typing import Annotated, TypedDict

class AgentState(TypedDict):
    """
    State dictionary for the SQL Query Agent LangGraph.
    """
    question: str
    sql_query: str
    is_valid_sql: bool
    validation_error: str
    query_result: str
    final_answer: str
    error_count: int
