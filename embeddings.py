"""Text -> vector. Real use goes through Ollama; a tiny offline 'hash' embedder exists
only so the test-suite can run without a model server."""
import hashlib
import math
import re

import config


def _ollama_embed(texts: list[str]) -> list[list[float]]:
    import ollama

    client = ollama.Client(host=config.OLLAMA_HOST)
    out: list[list[float]] = []
    for i in range(0, len(texts), 32):  # batch to keep requests small
        resp = client.embed(model=config.EMBED_MODEL, input=texts[i : i + 32])
        out.extend(resp["embeddings"])
    return out


def _hash_embed(texts: list[str], dim: int = 256) -> list[list[float]]:
    """Bag-of-words hashing. Crude, but deterministic and dependency-free."""
    vectors = []
    for text in texts:
        v = [0.0] * dim
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            v[h % dim] += 1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        vectors.append([x / norm for x in v])
    return vectors


def embed(texts: list[str]) -> list[list[float]]:
    if config.EMBED_BACKEND == "hash":
        return _hash_embed(texts)
    return _ollama_embed(texts)
