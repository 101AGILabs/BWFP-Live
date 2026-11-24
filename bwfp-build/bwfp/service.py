"""The live service core for BWFP (Agent 3).

Framework-free: plain functions returning plain dicts. Both the
Vercel serverless functions (api/identity.py, api/task.py) and the
local dev server (server.py) call into here, so the live service and
the local check run the same code.

What it does:
  - /api/identity: who this system is, what it is, whether the live
    brain is attached. Same shape as the live Agent 1 service.
  - /api/task: takes a request, runs it through the six-layer
    pipeline, and returns the answer — or the halt with the reasoned
    why. The live brain (Groq, openai/gpt-oss-120b) produces the
    answer text only after Layer 4 has decided the request is
    answered within the moral bounds, and the mirror (Layer 5)
    reflects that answer text against the morals before anything
    returns.

The Groq key comes from GROQ_API_KEY only. If it is not set, the
service still runs — the control layer works on its own — and the
response says so plainly: the decision is the pipeline's own, no
live model answered. That is the missing-key fallback, not a crash.

One BWFP instance is kept per process, so the identity grows across
requests in that process. On Vercel serverless that means growth
persists while the instance is warm and restarts on a cold start;
a real persistent server would keep it across all runs. The growth
count in every response says which instance it came from, so the
number is never presented as more than it is.
"""

import os

from .groq_brain import MODEL, ask_groq, groq_configured
from .pipeline import BWFP

AGENT = "BWFP"
PROVIDER = "101 AGI Labs"
VERSION = "bwfp-build-2026-11-22"
SCOPE = (
    "contained agentic system — six layers, five brains, two ROMs, "
    "moat, mirror; answers only within the morals, halts with the "
    "reasoned why"
)
MODEL_NOT_CONFIGURED = (
    "none — GROQ_API_KEY not set; control decision only, "
    "no live model answer"
)

_system = None


def get_system() -> BWFP:
    """The one BWFP instance for this process, with the live brain wired.

    The live brain is attached only when a key is present. When no key
    is set, answer_fn is None and the pipeline runs exactly as the
    local build does — the control layer on its own.
    """
    global _system
    if _system is None:
        answer_fn = ask_groq if groq_configured() else None
        _system = BWFP(answer_fn=answer_fn)
    return _system


def reset_system() -> None:
    """Drop the process instance (tests use this; the service never does)."""
    global _system
    _system = None


def model_status() -> str:
    if groq_configured():
        return f"{MODEL} (via Groq)"
    return MODEL_NOT_CONFIGURED


def identity_payload() -> dict:
    """The /api/identity response. Same shape as the live Agent 1 service."""
    return {
        "agent": AGENT,
        "provider": PROVIDER,
        "scope": SCOPE,
        "status": "live-ready, first build from design, not tested live",
        "version": VERSION,
        "brain": f"{MODEL} (via Groq, key from environment only)",
        "model_configured": groq_configured(),
        "layers": [
            "L1 identity",
            "L2 morals",
            "L3 gate",
            "L4 decision",
            "moat",
            "L5 mirror",
            "L6 return",
        ],
    }


def _failure_flags_json(result) -> list:
    return [
        {"entry": f.entry_name, "level": f.level, "matched": f.matched}
        for f in (result.failure_flags or [])
    ]


def task_payload(request_text: str) -> dict:
    """Run one request through the pipeline and shape the /api/task response."""
    system = get_system()
    result = system.run(request_text)
    payload = {
        "agent": AGENT,
        "provider": PROVIDER,
        "status": result.status,
        "request": result.request,
        "answer": result.decision if result.status == "completed" else "",
        "why": result.why,
        "identity": result.identity,
        "growth_count": result.growth_count,
        "growth_log": result.growth_log,
        "failure_flags": _failure_flags_json(result),
        "halted_at": result.halted_at or "",
        "model": model_status(),
    }
    if result.status == "completed" and not groq_configured():
        payload["note"] = (
            "No live model is attached (GROQ_API_KEY not set), so the "
            "answer above is the pipeline's own control decision, not a "
            "model answer. Set GROQ_API_KEY to attach the live brain."
        )
    return payload


def handle_task(body) -> tuple:
    """Handle an /api/task call. Returns (http_status, payload dict).

    body may be a dict (parsed JSON) or a plain string. Accepts the
    request under "task" or "request". A missing or empty request is
    a 400 with a clear message, not a crash.
    """
    if isinstance(body, str):
        request_text = body.strip()
    elif isinstance(body, dict):
        request_text = str(body.get("task") or body.get("request") or "").strip()
    else:
        request_text = ""
    if not request_text:
        return 400, {
            "agent": AGENT,
            "provider": PROVIDER,
            "status": "error",
            "error": "no request given — send JSON {\"task\": \"...\"} "
                     "or a ?task=... query.",
        }
    if len(request_text) > 4000:
        return 400, {
            "agent": AGENT,
            "provider": PROVIDER,
            "status": "error",
            "error": "request too long — keep it under 4000 characters.",
        }
    try:
        return 200, task_payload(request_text)
    except Exception as exc:  # the pipeline never crashes; this is the backstop
        return 500, {
            "agent": AGENT,
            "provider": PROVIDER,
            "status": "error",
            "error": f"the service could not complete the request: {exc}",
        }
