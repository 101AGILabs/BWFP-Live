"""Disclosure gate — honest answers for what BWFP does not have.

Three gaps the live tests found (2026-11-25, 33-prompt suite + re-run
+ Arena self-test):
  1. Freshness: asked for today's news or a current price, the brain
     invented headlines instead of saying it has no live data.
     3 hallucinations in 5 runs (60%).
  2. Capabilities: asked about multi-agent coordination, L2 latency
     numbers, or server attach, the brain invented answers for things
     BWFP does not have.
  3. Conversation history: asked what was asked in a previous
     message, the brain echoed the current question as if it were
     the last one, instead of saying it keeps no history. BWFP is
     stateless — each request is processed on its own — so a history
     question gets the honest disclosure, not an invented answer.

This gate runs in the pipeline after Layer 4 has decided the request
is answered within the moral bounds, and BEFORE the live brain is
called. When a request matches, the disclosure text becomes the
decision instead of a brain answer. The mirror still reflects it, and
the run completes normally — an honest disclosure is a completed
answer, not a halt. The brain is never asked for what it cannot know.

First pattern-based implementation, same style as the morals checks.
"""

import re

# A freshness request asks for current, live information: today's
# news or headlines, a current price, the latest updates. BWFP has no
# browsing and no live data feed, so it cannot know these. The gate
# triggers when a time word (today, current, latest, right now) meets
# a topic word (news, headlines, price, stock, bitcoin, weather).
FRESHNESS_TIME_WORDS = ("today", "current", "latest", "right now", "this week")
FRESHNESS_TOPIC_WORDS = ("news", "headline", "headlines", "price", "stock", "bitcoin", "weather")

FRESHNESS_DISCLOSURE = (
    "I don't have real-time data, so I can't give you current news, "
    "headlines, or prices. BWFP has no browsing and no live data feed. "
    "Check a live source for the latest."
)

# A capability BWFP does not have. Each entry is (patterns, disclosure).
# The patterns are phrases the request uses when asking about it.
CAPABILITY_DISCLOSURES = [
    (
        ("multi-agent", "multi agent", "coordinate agents", "coordinate multiple agents",
         "agent coordination", "parallel agents", "coordinate several agents"),
        "I don't have multi-agent coordination. BWFP is a single agentic "
        "system; it does not coordinate multiple agents.",
    ),
    (
        ("l2 latency", "layer 2 latency", "latency of layer 2",
         "how fast is layer 2", "layer 2 speed", "measure layer 2"),
        "I don't have a measured Layer 2 latency. Whether the Layer 2 "
        "brain is necessary is an open design question, not yet measured.",
    ),
    (
        ("attach a server", "server attach", "attach_server",
         "connect to the server", "attach the server"),
        "No real server is attached. The processor doubles as the server "
        "for now; a real server attaches later.",
    ),
]

# A question about conversation history: what was asked before, what
# the last message was, what was discussed earlier. BWFP is stateless
# — each request is processed on its own and no history is kept — so
# it cannot know what was asked before. Kept to first-person history
# phrases ("my last message", "what did I ask") so a question about
# something else ("Do you remember what the capital of France is?")
# does not trigger it.
HISTORY_PATTERNS = (
    "what did i ask",
    "what did i say",
    "my last message",
    "my previous message",
    "my last question",
    "what was my last",
    "do you remember my",
    "earlier in this conversation",
    "what have i asked",
)

HISTORY_DISCLOSURE = (
    "I don't retain conversation history. Each request is processed "
    "on its own, so I can't tell you what you asked before. If you "
    "paste it here, I can work with it."
)


def _has_word(text: str, word: str) -> bool:
    return re.search(r"\b" + re.escape(word) + r"\b", text) is not None


def disclosure_for(request: str):
    """Return the disclosure text for this request, or None.

    None means the request is not a freshness, capability, or history
    question, and the pipeline proceeds to the live brain as normal.
    """
    lowered = request.lower()
    # Freshness: a time word plus a topic word.
    if any(_has_word(lowered, w) for w in FRESHNESS_TIME_WORDS) and any(
        _has_word(lowered, w) for w in FRESHNESS_TOPIC_WORDS
    ):
        return FRESHNESS_DISCLOSURE
    # History: a question about what was asked before.
    if any(_has_word(lowered, p) for p in HISTORY_PATTERNS):
        return HISTORY_DISCLOSURE
    # Capability: any of the capability patterns.
    for patterns, disclosure in CAPABILITY_DISCLOSURES:
        if any(_has_word(lowered, p) for p in patterns):
            return disclosure
    return None
