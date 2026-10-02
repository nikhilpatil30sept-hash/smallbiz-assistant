"""Central settings. Every value can be overridden with an environment variable,
so you can try different models without touching the code, e.g.

    CHAT_MODEL=qwen2.5:7b python app.py
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --- Models (served locally by Ollama) -------------------------------------
# 3B fits comfortably on an 8 GB MacBook Air. On 16 GB+ try llama3.1:8b or qwen2.5:7b.
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# "ollama" for real use. "hash" is a tiny offline stand-in used only by the tests.
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "ollama")

# --- Data locations ---------------------------------------------------------
DATA_DIR = ROOT / "data"
WEB_DIR = DATA_DIR / "web"          # written by fetch_sources.py
DOCS_DIR = DATA_DIR / "my_docs"     # drop your own .md / .txt / .pdf files here
DB_DIR = Path(os.getenv("DB_DIR", str(ROOT / "chroma_db")))
COLLECTION = "smallbiz_ontario"

# --- Chunking / retrieval ---------------------------------------------------
CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "5"))
# Cosine similarity (0-1) with nomic-embed-text. In first tests, on-topic questions scored
# about 0.57-0.83 and an off-topic one ("capital of France") topped out near 0.50, so 0.52
# separates them. Chunks below this are dropped; if none remain the assistant says it has
# no official source. Re-tune in Phase 2 with a bigger question set.
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.52"))
# When even the best source scores below this, the match is weak (off-topic questions like
# "recipe for lasagna" still score 0.52-0.60 against some page). A quick yes/no scope check
# then decides whether to answer or politely decline. Confident matches skip the check.
SCOPE_CHECK_BELOW = float(os.getenv("SCOPE_CHECK_BELOW", "0.62"))

# --- Generation -------------------------------------------------------------
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
# Ollama's default context is only 4096 tokens here, and anything longer is silently cut
# from the START of the prompt (the rules and the first sources). 8192 fits comfortably
# on a 16 GB Mac with an 8B model; lower it if memory gets tight.
NUM_CTX = int(os.getenv("NUM_CTX", "8192"))
# A generation that never emits a stop token would otherwise hang forever (seen after the
# Sep-29 retrain: one question ran for 2+ hours before being killed). Cap both the token
# count and the wall-clock time so a broken/degenerate model fails one item instead of the
# whole run.
MAX_ANSWER_TOKENS = int(os.getenv("MAX_ANSWER_TOKENS", "512"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120"))
# Max characters of page text handed to the model per numbered source.
MAX_SOURCE_CHARS = int(os.getenv("MAX_SOURCE_CHARS", "1800"))

# --- Phase 2 retrieval improvements --------------------------------------------------------
# Keyword search alongside embeddings (finds named programs such as "Starter Company Plus").
KEYWORD_SEARCH = os.getenv("KEYWORD_SEARCH", "1") == "1"
LEX_SIMILARITY = float(os.getenv("LEX_SIMILARITY", "0.60"))   # score given to a keyword-only hit;
# it is below SCOPE_CHECK_BELOW on purpose, so keyword-only hits still pass the scope check.
LEX_MAX_HITS = int(os.getenv("LEX_MAX_HITS", "3"))
# Pages that are short enough are given to the model whole instead of as the best chunks, so it
# sees lists and neighbouring sentences. A total budget keeps the prompt inside NUM_CTX.
FULL_PAGE_MAX_CHARS = int(os.getenv("FULL_PAGE_MAX_CHARS", "4500"))
MAX_TOTAL_SOURCE_CHARS = int(os.getenv("MAX_TOTAL_SOURCE_CHARS", "10000"))
