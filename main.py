import os
import argparse
from dotenv import load_dotenv

# Load environment variables (OPENAI_API_KEY)
load_dotenv()

from agent.graph import build_graph

def main():
    parser = argparse.ArgumentParser(description="Intelligent SQL Query Agent")
    parser.add_argument("question", nargs="?", help="The natural language question to ask the database.")
    args = parser.parse_args()

    # Create the db if it doesn't exist
    if not os.path.exists("employee_data.db"):
        print("Database not found. Setting up mock database...")
        from setup_db import setup_database
        setup_database()

    app = build_graph()

    if args.question:
        # Run single question mode
        process_question(app, args.question)
    else:
        # Run interactive CLI mode
        print("SQL Query Agent Initialized. Type 'exit' or 'quit' to stop.")
        while True:
            try:
                user_input = input("\\nAsk a question about the database: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue
                process_question(app, user_input)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\\nAn error occurred: {e}")

def process_question(app, question: str):
    print(f"\\nProcessing: '{question}'...")
    
    initial_state = {
        "question": question,
        "sql_query": "",
        "is_valid_sql": False,
        "validation_error": "",
        "query_result": "",
        "final_answer": "",
        "error_count": 0
    }
    
    try:
        # Stream the results to show progress
        for event in app.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"✅ Finished step: {node_name}")
                if "sql_query" in state_update and node_name == "generate_sql":
                    # Only print sql query generation if it's the first time or retries
                    print(f"   Generated SQL: {state_update['sql_query']}")
                if "validation_error" in state_update and state_update["validation_error"] and not state_update.get("is_valid_sql", True):
                    print(f"   Validation/Execution Error: {state_update['validation_error']}")
                
        # The final compiled graph output is stored in state of the last node run
        print("\\n✨ Final Answer ✨")
        print("-" * 20)
        # Fetch actual final state by invoking to get the fully merged TypedDict output
        # But stream above misses the final merge easily, so a standard .invoke is better to get the concrete final dict.
        # However, stream() is already yielding dicts. We can just capture the final_answer from the interpret_results node.
    except Exception as e:
         print(f"\\nWorkflow interrupted: {e}")
         return
         
    # To get the final merged state reliably after stream, standard practice is tracking the latest dict:
    final_output = app.invoke(initial_state)
    
    if final_output.get("final_answer"):
        print(final_output["final_answer"])
    elif final_output.get("error_count", 0) >= 3:
        print("Agent stopped after multiple failed attempts to generate or execute valid SQL.")
    else:
        print("Agent could not generate an answer.")

if __name__ == "__main__":
    main()
