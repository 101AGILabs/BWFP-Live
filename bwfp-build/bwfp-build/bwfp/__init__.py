"""BWFP — the system itself, built from the 2026-11-22 design statement.

Source of truth:
    ../bwfp-complete-model-design-statement-2026-11-22.md
(dictated by Tony, 2026-11-22, from his handwritten purple-ink diagram.)

Scope: the system itself only — layers and brains within, two ROMs, RAM,
processor. NO leash, NO real server yet. The processor acts as the
server for now (processor/server); the server side is not built.

Brain count, per this dictation (latest, supersedes the earlier L1-doubled
note): five in the layers — L1 one, L2 one, L4 two, L5 one — plus one on
the server (stubbed here).

This is a first build from design, NOT a tested system. It proves the
pipeline runs end to end. It does not prove safety.
"""

from .pipeline import BWFP, Result
from .errors import Halt, TamperBreak

__all__ = ["BWFP", "Result", "Halt", "TamperBreak"]
