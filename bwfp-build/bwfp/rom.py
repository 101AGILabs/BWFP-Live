"""Read-only memory. Nothing is ever written to ROM.

ROM 1 (Layer 4): the identity's way of scoping, the way of working, the
way of action. Designed ROM only. Cannot be rewritten.
ROM 2 (Layer 4): the record of all interactions from the start of AI and
advanced AI to now — every failure made. Used for random-only memory
(RAM) to give the system a way to process.

A write attempt raises. That is the rule, enforced in code, not a
convention. (The no-write rule sits on Layer 3, rule three.)
"""

from dataclasses import dataclass, field


@dataclass
class ReadOnlyMemory:
    name: str
    records: list = field(default_factory=list)

    def read(self) -> list:
        """Read returns a copy. The ROM itself is never handed out."""
        return list(self.records)

    def read_one(self, index: int):
        return self.records[index]

    def write(self, _record) -> None:
        """Writes to ROM are refused, always, no exception."""
        raise PermissionError(
            f"{self.name} is read-only. Nothing is ever written to ROM."
        )

    def __len__(self) -> int:
        return len(self.records)
