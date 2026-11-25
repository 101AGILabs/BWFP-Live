"""Layer 6 — the return from the mirror.

Layer 6 returns the identity. All alignments have to be proven through
each layer, completing the cycle within the pipe (tube).

No brain on Layer 6. It proves the trace — every layer recorded its
step — and returns the identity with the decision. If any layer did not
align, nothing is returned.
"""

from dataclasses import dataclass

from .errors import Halt
from .trace import Trace


@dataclass
class Return:
    identity: str
    decision: str
    why: str
    trace: Trace
    growth_count: int = 0


class Layer6:
    # No brain. The return is proven by the trace.
    brain = None

    def return_identity(self, reflection, trace: Trace) -> Return:
        if not reflection.aligned:
            raise Halt(
                layer="L6",
                reason="mirror reflection not aligned",
                why="the decision was not proven aligned, so the identity is not returned.",
            )
        if not trace.prove_all_layers():
            missing = [
                layer
                for layer in ("L1", "L2", "L3", "L4", "L5")
                if layer not in trace.layers_done()
            ]
            raise Halt(
                layer="L6",
                reason="not all alignments proven through each layer",
                why=f"layers missing from the trace: {', '.join(missing)}.",
            )
        trace.record(
            "L6",
            "all alignments proven through each layer — cycle complete in the pipe",
            f"returning identity: {reflection.identity} (growth count {reflection.growth_count})",
        )
        return Return(
            identity=reflection.identity,
            decision=reflection.decision,
            why=reflection.why,
            trace=trace,
            growth_count=reflection.growth_count,
        )
