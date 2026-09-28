from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import generate_sql, validate_sql, execute_query, interpret_results

def should_execute(state: AgentState):
    """Conditional edge decision node after validation."""
    if state["is_valid_sql"]:
        return "execute_query"
    
    # If validation or execution fails too many times, stop to prevent infinite loops
    error_count = state.get("error_count", 0)
    if error_count >= 3:
        return END
        
    return "generate_sql" # Try again if invalid

def build_graph() -> StateGraph:
    """
    Constructs the LangGraph connecting our nodes.
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_query", execute_query)
    workflow.add_node("interpret_results", interpret_results)
    
    # Define edges
    # Start -> generate
    workflow.set_entry_point("generate_sql")
    
    # generate -> validate
    workflow.add_edge("generate_sql", "validate_sql")
    
    # validate -> execute OR back to generate (conditional)
    workflow.add_conditional_edges(
        "validate_sql",
        should_execute,
        {
            "execute_query": "execute_query",
            "generate_sql": "generate_sql",
            END: END
        }
    )
    
    # execute -> interpret
    workflow.add_edge("execute_query", "interpret_results")
    
    # interpret -> END
    workflow.add_edge("interpret_results", END)
    
    return workflow.compile()
