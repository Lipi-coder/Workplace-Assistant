# Deploying Intelligent SQL Query Agent to Vercel (100% Free)

Vercel is an excellent platform for deploying web applications and serverless APIs for free. However, Vercel's free "Hobby" tier has specific constraints:
1. **Serverless Architecture**: It cannot run persistent background processes (like a local Ollama server).
2. **Ephemeral Storage**: Local files like `employee_data.db` (SQLite) will reset every time the function runs.

To deploy this agent **completely for free** on Vercel, we must adapt the architecture to use **Free Cloud APIs** instead of local hardware.

Here is the step-by-step plan:

## Phase 1: Adapt the Architecture for Vercel

### 1. Replace Local Ollama with a Free Cloud LLM (Groq)
We cannot run Ollama inside a Vercel serverless function. Instead, we will use **Groq**, which provides an ultra-fast, 100% free API tier for open-source models like Llama 3.
- Go to [GroqCloud](https://console.groq.com/) and sign up for free.
- Generate a free API Key.
- Update `requirements.txt` to include `langchain-groq`.
- In `agent/nodes.py`, swap `ChatOllama` for `ChatGroq`.

### 2. Replace Local SQLite with a Free Cloud Database (Turso or Supabase)
Vercel's filesystem is read-only in production. We need a free hosted database.
- Go to [Turso](https://turso.tech/) (free serverless SQLite) or [Supabase](https://supabase.com/) (free PostgreSQL).
- Create a free database and get the Connection URL.
- Update `utils/database.py` to connect to this remote URL instead of the local `.db` file.

### 3. Create a FastAPI Entry Point
Vercel executes Python backend code via Serverless Functions. We need to wrap our LangGraph agent in a simple HTTP API.
- Install `fastapi` and `uvicorn`.
- Create a file named `api/index.py` (Vercel looks here for Python functions).
- Write a basic POST endpoint that accepts a `{"question": "..."}` JSON payload and returns the agent's answer.

---

## Phase 2: Project Setup & Configuration

### 1. File Structure
Modify your directory to look like this:
```text
Intelligent SQL Query Agent/
├── api/
│   └── index.py         <-- New FastAPI entry point
├── agent/               <-- Your existing nodes, state, graph
├── utils/               <-- Your existing DB connection logic
├── requirements.txt     <-- Add fastapi, langchain-groq
└── vercel.json          <-- Vercel configuration file
```

### 2. Create `vercel.json`
Create a `vercel.json` file in the root directory to tell Vercel how to build the Python app:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

---

## Phase 3: Deployment Steps

### 1. Push Code to GitHub
Vercel deploys directly from your Git repository.
1. Initialize a git repository: `git init`
2. Create a `.gitignore` file and add `.venv`, `.env`, `__pycache__`, and `*.db`.
3. Commit your code and push it to a new, free GitHub repository.

### 2. Connect to Vercel
1. Go to [Vercel](https://vercel.com/) and sign up with your GitHub account.
2. Click **Add New** -> **Project**.
3. Import the GitHub repository you just created.

### 3. Configure Environment Variables
Before clicking deploy, you must tell Vercel your free API keys and Database URL.
In the **Environment Variables** section of the Vercel dashboard, add:
- `GROQ_API_KEY` (Your free LLM key)
- `DATABASE_URL` (Your Turso/Supabase free database connection string)

### 4. Deploy!
Click the **Deploy** button. Vercel will install your `requirements.txt` and launch the FastAPI server. 

Once finished, Vercel will provide you with a free live URL (e.g., `https://your-sql-agent.vercel.app`). You can now send POST requests to this URL from any frontend, mobile app, or terminal anywhere in the world, completely free!
