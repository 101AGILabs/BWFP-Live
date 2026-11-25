"""A brain: one cell, one duty.

Each brain is its own firewall and its own deciding ROM within its layer.
One brain, one duty, 100%, nothing else. A brain refuses a second duty —
that is enforced here, not just documented.
"""

from dataclasses import dataclass


@dataclass
class Brain:
    name: str
    layer: str
    duty: str  # the one and only duty of this brain

    def guard(self, note: str) -> str:
        """Record the brain doing its one duty. Returns a trace detail."""
        return f"{self.name} ({self.duty}): {note}"

    def assign_duty(self, new_duty: str) -> None:
        """A brain takes no second duty. This is a hard refusal."""
        raise ValueError(
            f"{self.name} already has its one duty ({self.duty!r}); "
            f"it cannot also take {new_duty!r}."
        )
