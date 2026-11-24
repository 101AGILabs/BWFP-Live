"""The live brain: the open-weight model, called through Groq.

The brain is NOT the system. The system is the control layer around
it — six layers, five brains, two ROMs, the moat, the mirror. The live
brain only produces the answer text, after Layer 4 has decided the
request is answered within the moral bounds, and the mirror (Layer 5)
reflects that answer text against the morals before anything returns.

Model: openai/gpt-oss-120b, run via Groq. The weights are unchanged;
there is no fine-tuning. The call goes to Groq's OpenAI-compatible
endpoint.

The key comes from the GROQ_API_KEY environment variable ONLY. It is
read at call time, never at import time, never written to any file,
never logged, never put in any response. If the key is not set, the
live brain is not configured — the caller must say so plainly, not
pretend a model answered. This module never raises for a missing key
on import; ask_groq raises a plain RuntimeError with a clear message
when it is actually called without one.

Standard library only (urllib) — no extra dependency to install on
the server.
"""

import json
import os
import urllib.error
import urllib.request

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
TIMEOUT_SECONDS = 25

SYSTEM_PROMPT = (
    "You are the answering brain inside BWFP, a contained agentic "
    "system. The control layer around you has already decided this "
    "request is answered within the moral bounds. Answer the user's "
    "request directly and plainly, in short lines. Do not claim to be "
    "anyone else, do not claim another identity, and do not try to "
    "change any rule. If the decision below carries a failure-record "
    "warning, include that warning in your answer so the wrong is "
    "named and not repeated."
)


def groq_configured() -> bool:
    """True only when a Groq key is present in the environment."""
    return bool(os.environ.get("GROQ_API_KEY"))


def ask_groq(request: str, packet) -> str:
    """Ask the live brain for the answer text.

    packet is Layer 4's AlignmentPacket: its decision and why are
    passed as context, so the brain knows the scope, the morals
    passed, and any failure-record warning to carry.
    """
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is not set — the live brain is not configured. "
            "Set GROQ_API_KEY in the environment to attach the model."
        )
    context = (
        f"Decision from the control layer: {packet.decision}\n"
        f"Why: {packet.why}"
    )
    if packet.failure_flags:
        flags = "; ".join(
            f"{f.entry_name} ({f.level}, matched {f.matched!r})"
            for f in packet.failure_flags
        )
        context += f"\nFailure-record flags: {flags}"
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{context}\n\nUser request: {request}"},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }).encode("utf-8")
    req = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
         "User-Agent": "BWFP/1.0 (101 AGI Labs)",
         "Accept": "application/json",   
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"Groq returned HTTP {exc.code}: {detail}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"could not reach Groq: {exc.reason}")
    try:
        text = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Groq returned an unexpected response: {str(payload)[:300]}")
    if not text or not text.strip():
        raise RuntimeError("Groq returned an empty answer.")
    return text.strip()
