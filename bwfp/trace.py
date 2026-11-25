"""The trace: a plain record of what each layer did, in order.

Layer 6 proves all alignments through each layer by reading this trace.
The trace is the proof that the cycle completed inside the pipe.
"""

from dataclasses import dataclass, field


@dataclass
class Step:
    layer: str
    action: str
    detail: str = ""


@dataclass
class Trace:
    steps: list = field(default_factory=list)

    def record(self, layer: str, action: str, detail: str = "") -> None:
        self.steps.append(Step(layer=layer, action=action, detail=detail))

    def layers_done(self) -> list:
        """Layers that recorded at least one step, in order first seen."""
        seen = []
        for step in self.steps:
            if step.layer not in seen:
                seen.append(step.layer)
        return seen

    def prove_all_layers(self, expected=("L1", "L2", "L3", "L4", "L5")) -> bool:
        """True only if every expected layer recorded a step."""
        done = self.layers_done()
        return all(layer in done for layer in expected)

    def render(self) -> str:
        lines = []
        for step in self.steps:
            line = f"  [{step.layer}] {step.action}"
            if step.detail:
                line += f" — {step.detail}"
            lines.append(line)
        return "\n".join(lines)
