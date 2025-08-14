#!/usr/bin/env python3
import json, aiohttp, asyncio
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "data"
KB_DIR.mkdir(parents=True, exist_ok=True)
KB_FILE = KB_DIR / "kb.json"

def load_kb():
    if KB_FILE.exists():
        try:
            return json.loads(KB_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_kb(kb):
    KB_FILE.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")

async def librarian_lookup(port: int, query: str, n_predict: int = 128):
    """
    Ask the Librarian model for a concise answer or search result.
    """
    url = f"http://127.0.0.1:{port}/completion"
    payload = {
        "prompt": f"Answer concisely:\n{query}\n",
        "n_predict": n_predict,
        "temperature": 0.3
    }
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload, timeout=25) as r:
                r.raise_for_status()
                data = await r.json()
                text = data.get("content") or data.get("text") or ""
                return text.strip()
    except Exception as e:
        print(f"Librarian error: {e}")
        return ""
