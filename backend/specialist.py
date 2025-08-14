#!/usr/bin/env python3
import json, aiohttp, asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = json.loads((ROOT / "models.json").read_text(encoding="utf-8"))

def pick_specialist(domain_hint: str | None):
    """
    Select the most appropriate specialist model based on domain hint and priority.
    """
    pool = [m for m in MODELS if m.get("role") == "specialist"]
    if domain_hint:
        domain_filtered = [m for m in pool if domain_hint in (m.get("domain") or [])]
        pool = domain_filtered or pool
    pool.sort(key=lambda x: x.get("priority", 10))
    return pool[0] if pool else None

async def call_specialist(model, prompt: str, n_predict: int = 512, temp: float = 0.7):
    """
    Send a query to the selected specialist model's llama.cpp server.
    """
    port = model["port"]
    url = f"http://127.0.0.1:{port}/completion"
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temp
    }
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload, timeout=60) as r:
                r.raise_for_status()
                data = await r.json()
                text = data.get("content") or data.get("text") or ""
                return text.strip()
    except Exception as e:
        print(f"Specialist error: {e}")
        return ""
