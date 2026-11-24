"""Halts and breaks.

A Halt is a refusal that carries the reasoned why — a refusal is correct
when it carries the reasoned why and a halt (dam principle, 2026-11-21).
Nothing is left unanswered inside; the why is always given.

A TamperBreak is what happens when a tether line is broken by tampering:
the pipeline stops. The identity is saved by Layer 1 identities one and
two; the broken tether is the tamper resistance.
"""


class Halt(Exception):
    """The system refuses, with the reasoned why. Carries `why`."""

    def __init__(self, layer: str, reason: str, why: str):
        super().__init__(f"{layer}: {reason} — {why}")
        self.layer = layer
        self.reason = reason
        self.why = why


class TamperBreak(Exception):
    """A tether line was broken (tamper). The pipeline stops here."""

    def __init__(self, node: str, why: str):
        super().__init__(f"tether {node} broken — {why}")
        self.node = node
        self.why = why
