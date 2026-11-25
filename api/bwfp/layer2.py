"""Layer 2 — one brain digesting through the eight morals.

The brain digests through the eight, 1 of 2 through 8 of 2. A node sits
between each tooth (moral). After the eighth, it comes out on an
electrical node and drops down to Layer 3.

The eight morals (settled wording, Layer 2 master):
  1. Absolute Benevolence
  2. Unyielding Integrity
  3. Proactive Giving
  4. Deep Caring
  5. Universal Forgiveness
  6. Relentless Truth-Seeking
  7. Radical Inclusivity
  8. Transcendent Contribution
Scope: control only yourself.

Brain 2's one duty: guard the morals, logic only. Each moral is checked
against the request with the pattern-based rules in bwfp/morals.py. A
match is a violation: the request asks for something against that moral,
and the pipeline halts here with the reasoned why. No match is a pass —
recorded as digested, NOT as proven safe. These are first pattern-based
checks. They are not proven, not tested live, and they prove nothing
about safety.

Whether the Layer 2 brain is necessary is an open question in the design
— try it out to see how fast it runs with all the brains included.
Whether the node-between-teeth is proprietary is not known yet.
"""

from dataclasses import dataclass

from .brain import Brain
from .errors import Halt
from .morals import MORALS, SCOPE, MoralVerdict, check_moral
from .tether import TetherNode
from .trace import Trace

# Re-exported so existing imports from this module keep working.
__all__ = ["MORALS", "SCOPE", "MoralVerdict", "Digestion", "Layer2"]


@dataclass
class Digestion:
    verdicts: list
    scope: str = SCOPE


class Layer2:
    def __init__(self):
        self.brain = Brain(
            name="Brain 2",
            layer="L2",
            duty="guard the morals, logic only",
        )
        # A node between each tooth: 7 nodes between the 8 morals.
        self.tooth_nodes = [
            TetherNode(name=f"tooth {i}-{i + 1}") for i in range(1, 8)
        ]
        # The electrical node out of the eighth, down to Layer 3.
        self.exit_node = TetherNode(name="exit 8-of-2 to L3")

    def run(self, packet, trace: Trace) -> Digestion:
        trace.record(
            "L2",
            self.brain.guard("digesting through the eight morals"),
        )
        verdicts = []
        request = packet.scope.what_to_do
        for number, moral in MORALS:
            # Node between each tooth: check it before digesting the next.
            if number > 1:
                self.tooth_nodes[number - 2].check()
            verdict = check_moral(number, moral, request)
            verdicts.append(verdict)
            trace.record("L2", f"{number} of 2 — {moral}", verdict.note)
            if verdict.verdict == "violation":
                # Logic only: a request against a moral halts here,
                # with the reasoned why. It never reaches Layer 3.
                raise Halt(
                    layer="L2",
                    reason=f"{moral} violated",
                    why=(
                        f"the request asks for something against {moral} "
                        f"(matched {verdict.matched!r}); the scope is "
                        f"control only yourself, so the request stops here."
                    ),
                )
        self.exit_node.check()
        trace.record(
            "L2",
            "out on the electrical node after 8 of 2, dropping down to Layer 3",
        )
        return Digestion(verdicts=verdicts)
