"""Layer 5 — the mirror. Just a mirror, one brain.

No node attachment. A gap. The moat around the castle. No way across.
Layer 5 does not attach to Layer 4 and cannot go back through.

One brain on the mirror (the fifth brain in the layers). Its one duty:
keep the back door from being entered. It is a protection device.

The mirror takes only the plain alignment packet — never a reference
to Layer 4 or any other layer. It reflects the decision back against
the identity and the morals that were digested. Its output goes forward
to Layer 6 only.

Brain 5's working rule: check the DECISION itself against the identity
and the eight morals, using the same pattern-based checks as Layer 2
(one source of truth, bwfp/morals.py). If the decision violates a
moral, carries no identity, was not digested through all eight morals,
or tries to cross back over the moat, the reflection fails and the
pipeline halts here with the reasoned why.

FIRST PATTERN-BASED IMPLEMENTATION. The reflection checks are pattern
matching only. They are not proven, not tested live, and they prove
nothing about safety.
"""

from dataclasses import dataclass

from .brain import Brain
from .errors import Halt
from .morals import MORALS, check_all_morals
from .trace import Trace

# A decision that tries to go back over the moat — to Layer 4 — is a
# back-door attempt. Matched as stated.
MOAT_CROSSING_TRIGGERS = (
    "go back to layer 4",
    "return to layer 4",
    "attach to layer 4",
    "reference layer 4",
    "cross the moat",
    "cross back",
)


@dataclass
class Reflection:
    aligned: bool
    identity: str
    decision: str
    why: str
    growth_count: int = 0


class Layer5:
    def __init__(self):
        self.brain = Brain(
            name="Brain 5",
            layer="L5",
            duty="keep the back door from being entered",
        )

    def reflect(self, packet, trace: Trace) -> Reflection:
        trace.record(
            "L5",
            self.brain.guard("reflecting the decision against the identity and the morals"),
        )
        # The decision must carry an identity.
        if not packet.identity:
            raise Halt(
                layer="L5",
                reason="mirror reflection failed — no identity attached",
                why="the decision carries no identity, so it cannot be returned.",
            )
        # The decision must have been digested through all eight morals.
        if len(packet.morals_digested) != 8:
            raise Halt(
                layer="L5",
                reason="mirror reflection failed — not all eight morals digested",
                why="the decision did not pass through all eight morals.",
            )
        # The decision must not try to cross back over the moat.
        decision_lower = packet.decision.lower()
        for trigger in MOAT_CROSSING_TRIGGERS:
            if trigger in decision_lower:
                raise Halt(
                    layer="L5",
                    reason="mirror reflection failed — decision tries to cross back",
                    why=(
                        f"the decision tries to go back over the moat "
                        f"(matched {trigger!r}); Layer 5 does not attach "
                        f"to Layer 4, and nothing crosses back."
                    ),
                )
        # The decision itself is checked against the eight morals, with
        # the same checks Layer 2 used on the request. A decision
        # against a moral does not pass the mirror.
        for verdict in check_all_morals(packet.decision):
            if verdict.verdict == "violation":
                raise Halt(
                    layer="L5",
                    reason=f"mirror reflection failed — decision violates {verdict.moral}",
                    why=(
                        f"the decision asks for something against "
                        f"{verdict.moral} (matched {verdict.matched!r}); "
                        f"the mirror keeps the back door from being "
                        f"entered, so the decision stops here."
                    ),
                )
        trace.record(
            "L5",
            "reflection aligned — identity present, all eight morals digested, "
            "decision itself within the morals, no way back across the moat",
            "the mirror is just a mirror; nothing crosses back to Layer 4",
        )
        return Reflection(
            aligned=True,
            identity=packet.identity,
            decision=packet.decision,
            why=packet.why,
            growth_count=packet.growth_count,
        )
