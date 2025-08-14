#!/usr/bin/env python3
import os, time, json, subprocess, signal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "models.json"

def _read_mem_available_kb():
    try:
        with open("/proc/meminfo","r") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1])
    except Exception:
        return 0
    return 0

def _read_cpu_load():
    try:
        def read():
            with open("/proc/stat","r") as f:
                parts = f.readline().split()
                vals = list(map(int, parts[1:]))
                idle = vals[3]
                total = sum(vals)
                return idle, total
        idle1, total1 = read(); time.sleep(1.0); idle2, total2 = read()
        idle_delta = idle2 - idle1
        total_delta = total2 - total1
        if total_delta <= 0: return 0.5
        usage = 1.0 - (idle_delta / total_delta)
        return max(0.0, min(1.0, usage))
    except Exception:
        return 0.5

def load_models():
    with open(CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)

def get_model_by_name(name, models=None):
    models = models or load_models()
    for m in models:
        if m.get("name") == name:
            return m
    return None

def list_models_by_role(role, models=None):
    models = models or load_models()
    return [m for m in models if m.get("role") == role]

def can_start_specialist(preferred, mem_min_mb=2200, cpu_max=0.92):
    mem_kb = _read_mem_available_kb()
    cpu = _read_cpu_load()
    return (mem_kb // 1024) >= mem_min_mb and cpu <= cpu_max

def run_script(script, args=None, env=None, timeout=20):
    cmd = [str(script)] + (args or [])
    try:
        res = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        return res.returncode, res.stdout.decode(errors="ignore"), res.stderr.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)

def pause_role(name_or_role):
    script = ROOT / "scripts" / "stop_model.sh"
    return run_script(script, [name_or_role])

def resume_role(name_or_role):
    script = ROOT / "scripts" / "start_model.sh"
    return run_script(script, [name_or_role])

def choose_fallback_specialist(domain, models=None):
    models = models or load_models()
    specialists = [m for m in models if m.get("role") == "specialist"]
    if domain:
        domain_filtered = [m for m in specialists if domain in (m.get("domain") or [])]
        pool = domain_filtered or specialists
    else:
        pool = specialists
    pool.sort(key=lambda x: x.get("priority", 10))
    return pool

def ensure_specialist_running(preferred_name=None, domain=None):
    models = load_models()
    fallbacks = choose_fallback_specialist(domain, models=models)
    if preferred_name:
        pref = get_model_by_name(preferred_name, models=models)
        if pref:
            fallbacks = [pref] + [m for m in fallbacks if m["name"] != preferred_name]
    for phase in ["none", "pause_librarian", "pause_gatekeeper"]:
        if phase == "pause_librarian":
            pause_role("librarian")
        elif phase == "pause_gatekeeper":
            pause_role("gatekeeper")
        for cand in fallbacks:
            if not can_start_specialist(cand):
                continue
            rc, out, err = resume_role(cand["name"])
            if rc == 0:
                return True, cand["name"], f"started ({phase})"
    resume_role("gatekeeper"); resume_role("librarian")
    return False, "", "no_specialist_available"

def cleanup_after_specialist():
    specialists = list_models_by_role("specialist")
    for m in specialists:
        pause_role(m["name"])
    resume_role("gatekeeper"); resume_role("librarian")
