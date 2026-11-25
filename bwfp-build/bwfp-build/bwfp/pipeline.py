"""The pipeline: one input through all six layers, in order — with the loop.

  L1  three identities, tether nodes between each, one brain
  L2  one brain digesting through the eight morals, node between teeth
  L3  no brain — absolute no justification (halts with the why)
  L4  two brains, revolving door, two ROMs, processor, RAM,
      processor/server (growth happens in the processor for now)
  MOAT  the gap — the mirror does not attach to Layer 4
  L5  the mirror, one brain — reflection only, nothing back
  L6  the return — proves all alignments, returns the identity

THE LOOP (Tony, 2026-11-25): four continuous resolves, then two
mirror passes.
  - Resolves: L1 → L2 → L3 → L4 runs four times on the request.
    Pass 1 resolves it; passes 2–4 confirm it — the rescan.
    Any halt in any pass halts the run with the reasoned why.
  - The brain is called ONCE, after the four resolves, before the
    mirror loop. Four model calls would cost four times the time
    and hit the Groq rate limit for no benefit.
  - Mirror loop: L5 → L6 runs twice on the answer. Either mirror
    pass can halt with the why. The second pass re-checks the same
    answer — a deterministic re-check of what pass 1 passed.
  - Growth is per request, not per pass: one completed request
    grows the identity by 1, in the processor/server, after the
    mirror loop has proven the answer. A halted request does not grow.
  - The result carries the pass counts (resolves_run,
    mirror_passes_run) so the loop is verifiable live.

A run returns a Result. A halt (L3 gate, tamper break, failed mirror,
unproven alignments) is a Result with status "halted" and the reasoned
why — never a crash, never a request left unanswered inside.
"""

from dataclasses import dataclass, field, replace

from .disclosure import disclosure_for
from .errors import Halt, TamperBreak
from .layer1 import Layer1
from .layer2 import Layer2
from .layer3 import Layer3
from .layer4 import Layer4, AlignmentPacket
from .layer5 import Layer5
from .layer6 import Layer6
from .moat import Moat
from .trace import Trace

# The loop, per Tony's design (2026-11-25): four continuous resolves
# through L1 → L2 → L3 → L4, then two mirror passes L5 → L6.
RESOLVES_PER_RUN = 4
MIRROR_PASSES_PER_RUN = 2


@dataclass
class Result:
    status: str  # "completed" | "halted"
    request: str
    decision: str = ""
    identity: str = ""
    why: str = ""
    halted_at: str = ""
    trace: Trace = None
    # Growth, from the processor/server: how many interactions the
    # identity has grown through, and the short record of each one.
    growth_count: int = 0
    growth_log: list = field(default_factory=list)
    # Brain 3's flags against the failure record (ROM 2), if any.
    failure_flags: list = field(default_factory=list)
    # The loop, verifiable live: how many resolve passes and mirror
    # passes fully completed. A completed run carries 4 and 2. A run
    # halted in resolve pass 1 carries 0 and 0; a run halted at the
    # mirror carries 4 and 0. Counts are completed passes only.
    resolves_run: int = 0
    mirror_passes_run: int = 0


class BWFP:
    """Built Within, For People — the system itself, first build.

    answer_fn: optional live brain. When set, it is called AFTER Layer 4
    has formed its decision and BEFORE the moat, with (request, packet),
    and must return the answer text. The answer text becomes the
    decision that the mirror (Layer 5) reflects against the morals — so
    the mirror checks the actual answer, not a canned decision string.
    When answer_fn is None (the default), the pipeline behaves exactly
    as before: Layer 4's decision string is the decision. Nothing in
    the layers changes either way; the hook only supplies the answer
    text. If the live brain cannot be reached, the run halts at Layer 4
    with the reasoned why — a refusal is correct when it carries the
    reasoned why and a halt; nothing is left unanswered inside.

    The loop (Tony, 2026-11-25): four continuous resolves (L1 → L2 →
    L3 → L4) on the request, then the brain once, then the mirror loop
    (L5 → L6) twice on the answer. Growth is once per completed run,
    after the mirror loop — a halted run never grows. The Result
    carries resolves_run and mirror_passes_run so the loop is
    verifiable live.
    """

    def __init__(self, trained_purpose: str = "leaser identification", answer_fn=None):
        self.layer1 = Layer1(trained_purpose=trained_purpose)
        self.layer2 = Layer2()
        self.layer3 = Layer3()
        self.layer4 = Layer4()
        self.moat = Moat()
        self.layer5 = Layer5()
        self.layer6 = Layer6()
        self.answer_fn = answer_fn

    def run(self, request: str) -> Result:
        trace = Trace()
        resolves_run = 0
        mirror_passes_run = 0
        try:
            # --- The loop, part 1: four continuous resolves. ---
            # Pass 1 resolves the request; passes 2–4 confirm it —
            # the rescan. Any halt in any pass halts the run with
            # the why. Layer 4 does not grow during the resolves:
            # growth is per request, not per pass, and happens once,
            # after the mirror loop (below). A halt in any resolve
            # means no growth.
            alignment = None
            for pass_no in range(1, RESOLVES_PER_RUN + 1):
                packet = self.layer1.run(request, trace)
                digestion = self.layer2.run(packet, trace)
                self.layer3.run(packet, trace)
                alignment = self.layer4.run(packet, digestion, trace)
                resolves_run = pass_no
                trace.record(
                    "L4",
                    f"resolve pass {pass_no} of {RESOLVES_PER_RUN} complete",
                )
            # --- Disclosure gate, before the live brain. ---
            # If the request asks for something BWFP does not have
            # (current/live information, or a capability not built),
            # the honest disclosure becomes the decision instead of a
            # brain answer. The brain is never asked for what it cannot
            # know, so it cannot invent it. The mirror still reflects
            # the disclosure, and the run completes normally.
            disclosure = disclosure_for(request)
            if disclosure is not None:
                trace.record(
                    "L4",
                    "disclosure gate — request asks for what BWFP does not have, "
                    "so the honest disclosure is the decision, no brain call",
                    f"disclosure: {disclosure[:80]}",
                )
                alignment = replace(alignment, decision=disclosure)
            # --- Live brain, if one is attached. ---
            # Layer 4 has decided the request is answered within the
            # moral bounds. The live brain now produces the answer text,
            # and that text becomes the decision the mirror reflects.
            # The layers themselves do not change: identity, morals,
            # gate, decision, moat, mirror, return all run as before.
            elif self.answer_fn is not None:
                try:
                    answer_text = self.answer_fn(request, alignment)
                except Exception as exc:
                    raise Halt(
                        layer="L4",
                        reason="live brain unreachable",
                        why=(
                            f"the live brain could not be reached "
                            f"({exc}); no answer is given without the "
                            f"brain, so the request halts here with the "
                            f"why."
                        ),
                    )
                trace.record(
                    "L4",
                    "live brain produced the answer text — the mirror will reflect it",
                    f"answer length: {len(answer_text)} chars",
                )
                alignment = replace(alignment, decision=answer_text)
            self.moat.cross_outbound(alignment, trace)
            # --- The loop, part 2: the mirror loop, twice. ---
            # The mirror takes the equalized option and sends it back
            # up to the loop, so the decision is already verified and
            # aligned before it reaches the mirror. The mirror is the
            # double check before the answer goes out: either pass
            # can halt with the why. The second pass re-checks the
            # same answer — a deterministic re-check of what pass 1
            # passed.
            returned = None
            for pass_no in range(1, MIRROR_PASSES_PER_RUN + 1):
                reflection = self.layer5.reflect(alignment, trace)
                returned = self.layer6.return_identity(reflection, trace)
                mirror_passes_run = pass_no
                trace.record(
                    "L6",
                    f"mirror pass {pass_no} of {MIRROR_PASSES_PER_RUN} "
                    f"complete — answer re-checked and returned",
                )
            # --- Growth: one completed request grows by 1. ---
            # Only a run that reaches this line grows: any halt — any
            # resolve, the brain, either mirror pass — never gets
            # here, so a halted request does not grow. Growth happens
            # in the processor/server, as designed; the pipeline only
            # triggers it once, after the answer is proven.
            _identity, growth_count = self.layer4.processor_server.grow(
                returned.identity, request[:60], returned.decision, trace
            )
            return Result(
                status="completed",
                request=request,
                decision=returned.decision,
                identity=returned.identity,
                why=returned.why,
                trace=trace,
                growth_count=growth_count,
                growth_log=list(self.layer4.processor_server.growth_log),
                failure_flags=list(alignment.failure_flags),
                resolves_run=resolves_run,
                mirror_passes_run=mirror_passes_run,
            )
        except (Halt, TamperBreak) as exc:
            halted_at = getattr(exc, "layer", "L1")
            return Result(
                status="halted",
                request=request,
                why=getattr(exc, "why", str(exc)),
                halted_at=halted_at,
                trace=trace,
                # Growth 0: this halted request added nothing — growth
                # happens only after a completed run. (The processor/
                # server count is unchanged; the halted response
                # reports this request's growth, which is 0.)
                resolves_run=resolves_run,
                mirror_passes_run=mirror_passes_run,
            )
