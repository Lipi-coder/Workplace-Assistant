# Intelligent SQL Query Agent

An AI-powered agent built with **LangGraph** and **FastAPI** that translates natural language questions into executable SQL queries, validates them, runs them against a database, and returns human-readable answers. 

This project is fully designed to be deployed for **100% free** on serverless platforms like **Vercel** by utilizing free cloud infrastructure (**Groq** for insanely fast LLM inference and cloud databases like **Turso** or **Supabase**).

---

## 🏗️ Architecture

The agent is orchestrated via a **LangGraph StateGraph** consisting of 4 core nodes:
1. **`generate_sql`**: Uses the database schema as context for the LLM to write a SQL query based on the user's natural language question.
2. **`validate_sql`**: Acts as a security and syntax guard. It strictly prohibits Data Manipulation Language (DML) like `INSERT`, `UPDATE`, `DROP`, or `DELETE`, ensuring the agent only executes safe `SELECT` statements.
3. **`execute_query`**: Runs the validated SQL statement securely against the target database (supports Postgres, SQLite, etc. via SQLAlchemy).
4. **`interpret_results`**: Takes the raw database row output and uses the LLM to format it into a friendly, natural language answer for the user.

*(If the agent fails at validation or execution, it loops back and attempts to rewrite the query up to 3 times).*

---

## 🛠️ Tech Stack & Free Tier Providers
* **Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph/) + [LangChain](https://www.langchain.com/)
* **LLM**: [Groq](https://groq.com/) API (Llama 3.3 70B Model) - *Lightning fast and free*
* **Web Server**: [FastAPI](https://fastapi.tiangolo.com/) - *Compatible with Vercel's Python Serverless environments*
* **Database Driver**: [SQLAlchemy](https://www.sqlalchemy.org/) - *Agnostic ORM for Cloud Databases*

---

## 🚀 Running Locally

1. **Clone and Setup Virtual Environment:**
   ```bash
   git clone <your-repo-url>
   cd "Intelligent SQL Query Agent"
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\\.venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Rename `.env.example` to `.env` and configure your API keys:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   DATABASE_URL=sqlite:///employee_data.db  # Or your Supabase Postgres URL
   ```

3. **Start the API (Terminal 1):**
   Leave this terminal running! Do not press `CTRL+C` while testing.
   ```bash
   uvicorn api.index:app --reload
   ```

4. **Test the Agent (Terminal 2):**
   Open a *second* terminal window in the project directory, activate the virtual environment again, and run the test client script:
   ```bash
   python test_client.py
   ```
   Or send a direct request via `curl`:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/chat \\
        -H "Content-Type: application/json" \\
        -d '{"question": "How many employees are there in total?"}'
   ```

*(Note: Groq's local free tier has a strict requests-per-minute limit. If you encounter a 500 Server Error due to `rate_limit_exceeded`, simply wait a minute or two and try again.)*

---

## ☁️ Deploying to Vercel (For Free!)

1. Create a free GitHub repository and push this code to it.
2. Go to [Vercel](https://vercel.com/) and click **Add New -> Project**.
3. Import your GitHub repository.
4. Expand the **Environment Variables** section and insert your `GROQ_API_KEY` and `DATABASE_URL`.
5. Click **Deploy**. Vercel will install the requirements and launch the FastAPI app using the `vercel.json` configuration.

Your agent is now live and can be queried from any frontend application anywhere in the world!
