from agent.rag import load_documents, answer_from_docs

print("Chunks loaded:", load_documents())

for q in [
    "How many days of casual leave do employees get?",
    "How long is the notice period during probation?",
    "What is the capital of France?",
]:
    print("\nQ:", q)
    print(answer_from_docs(q))