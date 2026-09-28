from langchain_core.messages import SystemMessage, HumanMessage
from agent.nodes import llm
from utils.database import get_db_schema


def route_question(question: str) -> str:
    """Return 'sql' or 'docs'. When unsure, fall back to 'docs' (it cannot touch the database)."""
    schema = get_db_schema()
    system_prompt = f"""You are a router. Decide where a question should be answered.

Reply with exactly one word:
- sql  : the question asks for facts, counts, lists or numbers stored in the employee database described below
- docs : the question is about company policies or procedures in the handbook (working hours, leave, remote work, notice period, expenses, performance reviews)

Database schema:
{schema}

Reply with only 'sql' or 'docs'."""

    reply = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)]).content
    print("ROUTER:", question, "->", reply.strip())
    text = reply.strip().lower()
    return "sql" if ("sql" in text and "docs" not in text) else "docs"