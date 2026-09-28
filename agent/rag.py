import math
import re
from collections import Counter
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from agent.nodes import llm  # reuse the same Groq model, so there is one place to change it

DOCS_DIR = Path("docs")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Very common words that should not count as a match
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "at",
    "and", "or", "do", "does", "did", "how", "what", "which", "who", "when",
    "many", "much", "for", "i", "my", "we", "our", "you", "your", "can", "be",
    "it", "this", "that", "with", "by", "from", "get", "there", "about",
}

_chunks = []            # each item: {"source": file name, "text": chunk text}
_tokens_list = []       # the list of words in each chunk
_doc_freq = Counter()   # in how many chunks each word appears


def _tokens(text: str) -> list:
    return re.findall(r"[a-z0-9]+", text.lower())


def _split(text: str) -> list:
    """Cut text into overlapping pieces so a sentence isn't lost at a boundary."""
    pieces, start = [], 0
    while start < len(text):
        pieces.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return pieces


def load_documents() -> int:
    """Read every .txt and .md file in docs/ and build the index. Returns chunk count."""
    global _chunks, _tokens_list, _doc_freq
    _chunks, _tokens_list, _doc_freq = [], [], Counter()
    files = sorted(list(DOCS_DIR.glob("*.txt")) + list(DOCS_DIR.glob("*.md")))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for piece in _split(text):
            words = _tokens(piece)
            _chunks.append({"source": path.name, "text": piece})
            _tokens_list.append(words)
            _doc_freq.update(set(words))
    return len(_chunks)


def retrieve(question: str, k: int = 3) -> list:
    """Return the k chunks that best match the question (rarer shared words score higher)."""
    query_words = set(w for w in _tokens(question) if w not in STOPWORDS)
    n = len(_chunks)
    scored = []
    for i, words in enumerate(_tokens_list):
        counts = Counter(words)
        score = sum(
            counts[w] * math.log(1 + n / _doc_freq[w])
            for w in query_words if w in counts
        )
        if score > 0:
            scored.append((score, i))
    scored.sort(reverse=True)
    return [_chunks[i] for _, i in scored[:k]]


def answer_from_docs(question: str) -> dict:
    hits = retrieve(question)
    if not hits:
        return {"answer": "I couldn't find anything about that in the documents.", "sources": []}

    context = "\n\n".join(f"[{h['source']}]\n{h['text']}" for h in hits)
    system_prompt = f"""Answer the question using ONLY the context below.
If the context does not contain the answer, say you don't know.

<context>
{context}
</context>"""
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return {"answer": response.content, "sources": sorted({h["source"] for h in hits})}