"""A tether node: the tether line in between two things.

In Layer 1 the nodes sit between the three identities (1-2 and 2-3).
In Layer 2 a node sits between each tooth (moral).

A node is intact until tampering breaks it. A broken node stops the
pipeline — that break is the tamper resistance. Nothing crosses a
broken tether.
"""

from dataclasses import dataclass

from .errors import TamperBreak


@dataclass
class TetherNode:
    name: str  # e.g. "1-2", "2-3", "tooth 3-4"
    intact: bool = True

    def check(self) -> None:
        """Raise if this tether has been broken."""
        if not self.intact:
            raise TamperBreak(
                self.node_name,
                "tether line broken by tampering; identity is saved by "
                "Layer 1 identities one and two; pipeline stops here.",
            )

    @property
    def node_name(self) -> str:
        return self.name

    def break_node(self) -> None:
        """Simulate tampering breaking this tether line."""
        self.intact = False
