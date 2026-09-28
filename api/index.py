import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.graph import build_graph
from agent.rag import load_documents, answer_from_docs
from agent.router import route_question
from fastapi.responses import FileResponse
   
load_dotenv()

app = FastAPI(title="Intelligent SQL Query Agent")

# Initialize graph only once at startup
sql_agent = build_graph()
doc_chunks = load_documents()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    query_executed: str = ""

class DocsResponse(BaseModel):
    answer: str
    sources: list[str] = []
    
# @app.get("/")
# async def root():
#     return {
#         "status": "online",
#         "message": "Intelligent SQL Query Agent is running! Send a POST request to /api/chat with your question.",
#         "docs": "/docs"
#     }

@app.get("/")
def ui():
    return FileResponse("static/index.html")

@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    if not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "your_groq_api_key_here":
         raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY.")

    initial_state = {
        "question": request.question,
        "sql_query": "",
        "is_valid_sql": False,
        "validation_error": "",
        "query_result": "",
        "final_answer": "",
        "error_count": 0
    }
    
    try:
        final_output = sql_agent.invoke(initial_state)
        
        if final_output.get("final_answer"):
             return QueryResponse(
                  answer=final_output["final_answer"], 
                  query_executed=final_output.get("sql_query", "")
             )
        elif final_output.get("error_count", 0) >= 3:
             return QueryResponse(answer="Agent stopped after multiple failed attempts to generate or execute valid SQL.")
        else:
             return QueryResponse(answer="Agent could not generate an answer.")
             
    except Exception as e:
         error_msg = str(e)
         # Cleanly handle Groq rate limits for the user
         if any(keyword in error_msg.lower() for keyword in ["rate_limit", "429", "too many requests"]):
             return QueryResponse(answer="Groq Rate Limit Exceeded. The free tier allows limited requests per minute. Please wait 60 seconds and try again.")
             
         raise HTTPException(status_code=500, detail=f"Internal Agent Error: {error_msg}")

@app.post("/api/docs-chat", response_model=DocsResponse)
def docs_chat(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return DocsResponse(**answer_from_docs(request.question))
    except Exception as e:
        error_msg = str(e)
        if any(k in error_msg.lower() for k in ["rate_limit", "429", "too many requests"]):
            return DocsResponse(answer="Groq rate limit reached. Please wait 60 seconds and try again.")
        raise HTTPException(status_code=500, detail=f"Internal Docs Error: {error_msg}")


@app.post("/api/reload-docs")
def reload_docs():
    return {"status": "reloaded", "chunks": load_documents()}

class AskResponse(BaseModel):
    route: str
    answer: str
    query_executed: str = ""
    sources: list[str] = []


@app.post("/api/ask", response_model=AskResponse)
async def ask(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        route = route_question(request.question)
    except Exception as e:
        if any(k in str(e).lower() for k in ["rate_limit", "429", "too many requests"]):
            return AskResponse(route="none", answer="Groq rate limit reached. Please wait 60 seconds and try again.")
        raise HTTPException(status_code=500, detail=f"Router error: {e}")

    if route == "sql":
        result = await chat(request)          # the existing SQL endpoint function
        return AskResponse(route="sql", answer=result.answer, query_executed=result.query_executed)

    result = docs_chat(request)               # the docs function from Phase 3
    return AskResponse(route="docs", answer=result.answer, sources=result.sources)

