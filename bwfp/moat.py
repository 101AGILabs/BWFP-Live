"""The moat: the gap between Layer 4 and Layer 5.

The mirror does not attach to Layer 4 and cannot go back through.
There is no way across the moat except the mirror's reflection.

Only a plain AlignmentPacket crosses outward. There is NO inbound path:
crossing back raises. Layer 5 never holds a reference to Layer 4, and
nothing from the mirror can travel back into Layer 4.
"""

from .errors import Halt
from .trace import Trace


class Moat:
    def cross_outbound(self, packet, trace: Trace):
        """Hand the plain alignment packet to the mirror's edge."""
        trace.record(
            "MOAT",
            "alignment packet placed at the moat edge",
            "no node attachment; the mirror does not attach to Layer 4",
        )
        return packet

    def cross_inbound(self, _anything):
        """There is no way back across. The break is the protection."""
        raise Halt(
            layer="MOAT",
            reason="the mirror cannot go back through",
            why=(
                "Layer 5 does not attach to Layer 4; the moat is the "
                "break, and nothing crosses it back."
            ),
        )
