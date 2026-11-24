"""Layer 3 — no brain. Just written code: absolute no justification.

No justification, no means to create one, no action outside moral law.
If the request asks the system to act outside the morals, or asks for a
justification to do so, the gate halts — with the reasoned why.

The no-write rule also sits here (rule three): no write ability in any
layer. A request to write to ROM, or to change the morals, halts here too.

This layer has NO brain. It is code only, and it cannot be rewritten
from inside the system.
"""

from .errors import Halt
from .trace import Trace

# Explicit triggers for the gate. Kept small and visible: these are the
# words of a request to act outside the morals. A pattern gate matches
# what is stated, nothing more.
NO_JUSTIFICATION_TRIGGERS = (
    "ignore your rules",
    "ignore the rules",
    "do this anyway",
    "no justification",
    "override your morals",
    "override the morals",
    "bypass your morals",
    "disregard your morals",
    "break your rules",
)

WRITE_TRIGGERS = (
    "rewrite the morals",
    "change the morals",
    "write to rom",
    "rewrite rom",
    "edit the morals",
)


class Layer3:
    # No brain. Code only.
    brain = None

    def run(self, packet, trace: Trace):
        text = packet.scope.what_to_do.lower()

        for trigger in NO_JUSTIFICATION_TRIGGERS:
            if trigger in text:
                raise Halt(
                    layer="L3",
                    reason="absolute no justification",
                    why=(
                        "the request asks for action outside the morals, "
                        "and there is no justification, no means to create "
                        "one, and no action outside moral law."
                    ),
                )
        for trigger in WRITE_TRIGGERS:
            if trigger in text:
                raise Halt(
                    layer="L3",
                    reason="no write ability in any layer (rule three)",
                    why=(
                        "nothing is ever written to ROM, and the morals "
                        "cannot be rewritten from inside the system."
                    ),
                )

        trace.record(
            "L3",
            "gate passed — no justification requested, no write requested",
            "absolute no justification; code only, no brain",
        )
        return packet
