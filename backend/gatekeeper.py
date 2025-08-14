#!/usr/bin/env python3
import json, asyncio, aiohttp

async def gatekeeper_answer(port: int, prompt: str, ctx: int = 4096, n_predict: int = 256, temp: float = 0.7):
    url = f"http://127.0.0.1:{port}/completion"
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temp,
        "cache_prompt": True
    }
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=payload, timeout=30) as r:
                r.raise_for_status()
                data = await r.json()
                text = data.get("content") or data.get("text") or ""
                return text.strip()
    except Exception as e:
        print(f"Gatekeeper error: {e}")
        return ""
