#!/usr/bin/env python3
"""
Lena MCP Vector Search Server
Exposes FAISS index over the MCP (Model Context Protocol) stdio transport.

Usage:
  python3 mcp_vector_search.py

Tools exposed:
  - search_docs: Semantic search over OpenCode/OpenClaw/Oh My OpenCode documentation

Requires:
  pip install faiss-cpu PyPDF2 requests
  Pre-built index in ../vectordb/docs.faiss + ../vectordb/docs_metadata.json
"""

import json
import os
import sys
from pathlib import Path

import requests

# ── Config ─────────────────────────────────────────────────────
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "qwen3-embedding:8b")
TOP_K = int(os.environ.get("SEARCH_TOP_K", "5"))

BASE_DIR = Path(__file__).resolve().parent.parent
VECTORDB_DIR = BASE_DIR / "vectordb"
INDEX_PATH = VECTORDB_DIR / "docs.faiss"
META_PATH = VECTORDB_DIR / "docs_metadata.json"

# ── MCP Protocol ───────────────────────────────────────────────

def send_response(response_id, result):
    """Send JSON-RPC response to stdout."""
    msg = {"jsonrpc": "2.0", "id": response_id, "result": result}
    out = json.dumps(msg)
    sys.stdout.write(f"Content-Length: {len(out)}\r\n\r\n{out}")
    sys.stdout.flush()


def send_error(response_id, code, message):
    """Send JSON-RPC error response."""
    msg = {"jsonrpc": "2.0", "id": response_id, "error": {"code": code, "message": message}}
    out = json.dumps(msg)
    sys.stdout.write(f"Content-Length: {len(out)}\r\n\r\n{out}")
    sys.stdout.flush()


def get_embedding(text: str) -> list[float]:
    """Get embedding from Ollama."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


class VectorSearchServer:
    def __init__(self):
        self.index = None
        self.metadata = None
        self._load_index()

    def _load_index(self):
        """Load FAISS index and metadata."""
        if not INDEX_PATH.exists():
            # Try fallback to JSON vectors
            json_path = VECTORDB_DIR / "docs_vectors.json"
            if json_path.exists():
                sys.stderr.write(f"📦 Loading raw vectors from {json_path}\n")
                with open(json_path) as f:
                    data = json.load(f)
                self.metadata = [{"source": d["source"], "text": d["text"], "section": d["section"]} for d in data]
                # Build in-memory FAISS index
                try:
                    import faiss
                    import numpy as np
                    embeddings = np.array([d["embedding"] for d in data], dtype="float32")
                    faiss.normalize_L2(embeddings)
                    dim = embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(dim)
                    self.index.add(embeddings)
                    sys.stderr.write(f"✅ Built FAISS index from JSON: {len(data)} vectors\n")
                except ImportError:
                    sys.stderr.write("⚠ FAISS not available, using brute-force search\n")
                    self._raw_vectors = data
                return
            sys.stderr.write(f"⚠ No index found at {INDEX_PATH}\n")
            return

        try:
            import faiss
            self.index = faiss.read_index(str(INDEX_PATH))
            sys.stderr.write(f"✅ FAISS index loaded: {self.index.ntotal} vectors\n")
        except Exception as e:
            sys.stderr.write(f"❌ Failed to load FAISS index: {e}\n")
            return

        if META_PATH.exists():
            with open(META_PATH) as f:
                self.metadata = json.load(f)
            sys.stderr.write(f"✅ Metadata loaded: {len(self.metadata)} entries\n")

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """Search the vector index."""
        if self.index is None and not hasattr(self, '_raw_vectors'):
            return [{"error": "No index loaded. Run vectorize_docs.py first."}]

        try:
            import faiss
            import numpy as np

            query_vec = np.array([get_embedding(query)], dtype="float32")
            faiss.normalize_L2(query_vec)

            distances, indices = self.index.search(query_vec, top_k)

            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:
                    continue
                meta = self.metadata[idx] if self.metadata and idx < len(self.metadata) else {}
                results.append({
                    "rank": i + 1,
                    "score": float(dist),
                    "source": meta.get("source", "unknown"),
                    "section": meta.get("section", "unknown"),
                    "text": meta.get("text", "")[:500],  # Truncate for MCP
                })
            return results

        except Exception as e:
            return [{"error": str(e)}]

    def handle_request(self, request: dict):
        """Handle a JSON-RPC request."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            send_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {
                    "name": "lena-docs-search",
                    "version": "1.0.0",
                },
            })

        elif method == "tools/list":
            send_response(req_id, {
                "tools": [
                    {
                        "name": "search_docs",
                        "description": (
                            "Search Lena's documentation knowledge base. "
                            "Covers OpenCode, OpenClaw, and Oh My OpenCode documentation. "
                            "Returns the most relevant documentation snippets for your query."
                        ),
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Natural language search query",
                                },
                                "top_k": {
                                    "type": "integer",
                                    "description": "Number of results to return (default: 5)",
                                    "default": 5,
                                },
                                "section": {
                                    "type": "string",
                                    "description": "Filter by section: opencode, openclaw, or oh-my-opencode",
                                    "enum": ["opencode", "openclaw", "oh-my-opencode"],
                                },
                            },
                            "required": ["query"],
                        },
                    }
                ]
            })

        elif method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

            if tool_name == "search_docs":
                query = args.get("query", "")
                top_k = args.get("top_k", TOP_K)
                section_filter = args.get("section")

                results = self.search(query, top_k=top_k * 2 if section_filter else top_k)

                # Apply section filter
                if section_filter:
                    results = [r for r in results if r.get("section") == section_filter][:top_k]

                text_output = f"## 📚 Search Results for: \"{query}\"\n\n"
                for r in results:
                    if "error" in r:
                        text_output += f"❌ Error: {r['error']}\n"
                    else:
                        text_output += f"### [{r['rank']}] {r['source']} (score: {r['score']:.3f})\n"
                        text_output += f"{r['text']}\n\n---\n\n"

                send_response(req_id, {
                    "content": [{"type": "text", "text": text_output}],
                    "isError": False,
                })
            else:
                send_error(req_id, -32601, f"Unknown tool: {tool_name}")

        elif method == "notifications/initialized":
            pass  # No response needed for notifications

        elif method == "ping":
            send_response(req_id, {})

        else:
            if req_id is not None:
                send_error(req_id, -32601, f"Method not found: {method}")

    def run(self):
        """Run the MCP server on stdio."""
        sys.stderr.write("🦞 Lena Docs Search MCP Server starting...\n")
        sys.stderr.write(f"📁 Index: {INDEX_PATH}\n")
        sys.stderr.write(f"🤖 Model: {EMBED_MODEL}\n")

        buffer = ""
        content_length = None

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                buffer += line

                # Parse Content-Length header
                if content_length is None:
                    if buffer.startswith("Content-Length: "):
                        content_length = int(buffer.split(":")[1].strip())
                        buffer = ""
                    elif buffer == "\r\n" or buffer == "\n":
                        buffer = ""
                    continue

                # Skip empty line after header
                if buffer.strip() == "":
                    buffer = ""
                    continue

                # Try to parse JSON body
                if len(buffer.encode()) >= content_length:
                    try:
                        request = json.loads(buffer[:content_length])
                        self.handle_request(request)
                    except json.JSONDecodeError as e:
                        sys.stderr.write(f"JSON parse error: {e}\n")

                    buffer = ""
                    content_length = None

            except KeyboardInterrupt:
                break
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")


if __name__ == "__main__":
    server = VectorSearchServer()
    server.run()
