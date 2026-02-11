#!/usr/bin/env python3
"""
Lena Vectorizer — Convert PDF docs to FAISS vector index
Uses Ollama (Qwen 3 7B Instruct) for embeddings + FAISS for indexing.

Requires:
  pip install faiss-cpu PyPDF2 requests
  ollama pull qwen3:7b-instruct
"""

import json
import os
import re
import struct
import sys
from pathlib import Path

import requests

# ── Config ─────────────────────────────────────────────────────
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = "qwen3-embedding:8b"
CHUNK_SIZE = 512   # tokens (~2000 chars)
CHUNK_OVERLAP = 64 # tokens (~256 chars)
EMBED_DIM = 4096   # Qwen3-Embedding-8B dimension (#1 MTEB)

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
VECTORDB_DIR = BASE_DIR / "vectordb"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("ERROR: pip install PyPDF2")
        sys.exit(1)

    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 256) -> list[str]:
    """Split text into overlapping chunks by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            last_newline = chunk.rfind("\n")
            break_point = max(last_period, last_newline)
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def get_embedding(text: str) -> list[float]:
    """Get embedding from Ollama."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    # Ollama returns {"embeddings": [[...]]}
    return data["embeddings"][0]


def build_index(chunks: list[dict]) -> None:
    """Build FAISS index from chunks with embeddings."""
    try:
        import faiss
    except ImportError:
        # Fallback: save embeddings as numpy-like binary
        print("⚠ FAISS not available — saving raw embeddings + metadata")
        save_raw_embeddings(chunks)
        return

    import numpy as np

    embeddings = np.array([c["embedding"] for c in chunks], dtype="float32")
    dim = embeddings.shape[1]

    # Build IVF index for fast search
    n = len(chunks)
    nlist = min(max(1, n // 10), 100)
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    index.train(embeddings)
    index.add(embeddings)

    # Save index
    index_path = VECTORDB_DIR / "docs.faiss"
    faiss.write_index(index, str(index_path))
    print(f"  ✅ FAISS index: {index_path} ({n} vectors, dim={dim})")

    # Save metadata
    metadata = [{"source": c["source"], "text": c["text"], "section": c["section"]} for c in chunks]
    meta_path = VECTORDB_DIR / "docs_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✅ Metadata: {meta_path}")


def save_raw_embeddings(chunks: list[dict]) -> None:
    """Fallback: save embeddings as JSON (no FAISS)."""
    output = []
    for c in chunks:
        output.append({
            "source": c["source"],
            "section": c["section"],
            "text": c["text"],
            "embedding": c["embedding"],
        })

    path = VECTORDB_DIR / "docs_vectors.json"
    with open(path, "w") as f:
        json.dump(output, f)
    print(f"  ✅ Raw embeddings: {path} ({len(output)} vectors)")


def main():
    VECTORDB_DIR.mkdir(parents=True, exist_ok=True)

    # Discover all PDFs
    pdf_files = sorted(DOCS_DIR.rglob("*.pdf"))
    if not pdf_files:
        print("❌ No PDFs found. Run crawl_docs_to_pdf.py first.")
        sys.exit(1)

    print(f"📚 Found {len(pdf_files)} PDFs")
    print(f"🤖 Embedding model: {EMBED_MODEL} via {OLLAMA_HOST}")
    print(f"📁 Output: {VECTORDB_DIR}")

    # Check Ollama connectivity
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        if not any(EMBED_MODEL in m for m in models):
            print(f"⚠ Model {EMBED_MODEL} not found. Available: {models}")
            print(f"  Run: ollama pull {EMBED_MODEL}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot reach Ollama at {OLLAMA_HOST}: {e}")
        sys.exit(1)

    all_chunks = []

    for i, pdf in enumerate(pdf_files, 1):
        # Determine section from path
        section = pdf.parent.parent.name  # opencode / openclaw / oh-my-opencode
        print(f"\n[{i}/{len(pdf_files)}] {section}/{pdf.name}")

        text = extract_text_from_pdf(pdf)
        if not text.strip():
            print(f"  ⏭ Empty PDF, skipping")
            continue

        chunks = chunk_text(text)
        print(f"  📄 {len(text)} chars → {len(chunks)} chunks")

        for j, chunk in enumerate(chunks):
            print(f"    Embedding chunk {j+1}/{len(chunks)}...", end="\r")
            try:
                embedding = get_embedding(chunk)
                all_chunks.append({
                    "source": f"{section}/{pdf.stem}",
                    "section": section,
                    "text": chunk,
                    "embedding": embedding,
                })
            except Exception as e:
                print(f"    ❌ Chunk {j+1} failed: {e}")

        print(f"  ✅ {len(chunks)} chunks embedded")

    print(f"\n{'='*60}")
    print(f"📊 Total: {len(all_chunks)} chunks from {len(pdf_files)} PDFs")

    if all_chunks:
        print("🔨 Building FAISS index...")
        build_index(all_chunks)

    print("🏁 Vectorization complete!")


if __name__ == "__main__":
    main()
