#!/usr/bin/env python3
import os, json, asyncio
from pathlib import Path
from aiohttp import web
from resource_controller import load_models, ensure_specialist_running, cleanup_after_specialist
from gatekeeper import gatekeeper_answer
from librarian import librarian_lookup
from specialist import pick_specialist, call_specialist

ROOT = Path(__file__).resolve().parent
MODELS = load_models()

def get_port(role_or_name):
    for m in MODELS:
        if m.get("role") == role_or_name or m.get("name") == role_or_name:
            return m.get("port")
    return None

async def api_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except:
        body = await request.text()
        data = {"text": body}

    text = (data.get("text") or "").strip()
    dive_confirmed = bool(data.get("dive_confirmed", False))
    domain_hint = data.get("domain")  # optional

    if not text:
        return web.json_response({"status": "error", "message": "empty input"})

    # 1) Gatekeeper first pass
    gk_port = get_port("gatekeeper")
    lib_port = get_port("librarian")

    if not gk_port:
        return web.json_response({"status": "error", "message": "gatekeeper not configured"})

    gk_ans = await gatekeeper_answer(gk_port, f"Answer if certain; else say 'LOWCONF':\n{text}")
    if gk_ans and "LOWCONF" not in gk_ans and len(gk_ans) > 20:
        return web.json_response({"status": "ok", "answer": gk_ans})

    # 2) Librarian fallback
    if lib_port:
        lib_ans = await librarian_lookup(lib_port, text)
        if lib_ans and len(lib_ans) > 20:
            gk_refined = await gatekeeper_answer(
                gk_port,
                f"Refine this answer with better clarity:\nUser: {text}\nLibrarian notes: {lib_ans}"
            )
            if gk_refined and len(gk_refined) > 20:
                return web.json_response({"status": "ok", "answer": gk_refined})
            return web.json_response({"status": "ok", "answer": lib_ans})

    # 3) Not confident → offer Dive Deeper
    if not dive_confirmed:
        return web.json_response({
            "status": "needs_deeper",
            "prompt": "I'm unable to provide a complete answer right now. Would you like me to dive deeper? This may take a moment."
        })

    # 4) Specialist flow
    pref = pick_specialist(domain_hint)
    ok, used, notes = ensure_specialist_running(pref["name"] if pref else None, domain=domain_hint)
    if not ok:
        fallback = await gatekeeper_answer(gk_port, f"Provide best-effort general guidance:\n{text}")
        return web.json_response({
            "status": "ok",
            "answer": fallback or "I can't go deeper right now. I'll keep improving this topic during idle learning."
        })

    used_model = next((m for m in MODELS if m.get("name") == used), pref)
    if not used_model:
        fallback = await gatekeeper_answer(gk_port, f"Provide best-effort general guidance:\n{text}")
        return web.json_response({"status": "ok", "answer": fallback or "No specialist available"})

    # Call specialist
    spec_prompt = f"User question:\n{text}\nPlease produce a precise, helpful answer."
    spec_ans = await call_specialist(used_model, spec_prompt)

    # Cleanup
    cleanup_after_specialist()

    # Final polish via Gatekeeper
    final = await gatekeeper_answer(gk_port, f"Rephrase for clarity and completeness:\n{spec_ans}")
    return web.json_response({"status": "ok", "answer": final or spec_ans})

def main():
    app = web.Application()
    app.router.add_post("/api", api_handler)
    web.run_app(app, host="127.0.0.1", port=8765)

if __name__ == "__main__":
    main()
