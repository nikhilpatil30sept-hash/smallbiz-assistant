"""Build (or rebuild) the vector database from everything in data/web and data/my_docs.

Usage:
    python ingest.py
"""
import shutil

import chromadb

import config
from chunking import load_all_chunks
from embeddings import embed


def get_collection(reset: bool = False):
    if reset and config.DB_DIR.exists():
        shutil.rmtree(config.DB_DIR)
    client = chromadb.PersistentClient(path=str(config.DB_DIR))
    return client.get_or_create_collection(
        name=config.COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def main() -> None:
    chunks = load_all_chunks()
    if not chunks:
        raise SystemExit(
            "No documents found. Run `python fetch_sources.py` and/or add files to data/my_docs/."
        )
    print(f"Embedding {len(chunks)} chunks with {config.EMBED_BACKEND}:{config.EMBED_MODEL} ...")
    vectors = embed([c.text for c in chunks])

    col = get_collection(reset=True)  # simple and safe for a small corpus
    batch = 128
    for i in range(0, len(chunks), batch):
        part = chunks[i : i + batch]
        col.add(
            ids=[c.id for c in part],
            documents=[c.text for c in part],
            embeddings=vectors[i : i + batch],
            metadatas=[c.metadata for c in part],
        )
    print(f"Done. {col.count()} chunks stored in {config.DB_DIR}")


if __name__ == "__main__":
    main()
