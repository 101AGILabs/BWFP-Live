"""Layer 4 — two brains, two ROMs, processor, RAM, server (processor/server).

Two brains with a revolving door (360 degrees) between them. Between
the two brains are two ROMs:
  ROM 1: the identity's way of scoping, the way of working, the way of
         action. ROM only, cannot be rewritten, designed ROM only.
  ROM 2: loaded with all interactions from the start of AI and advanced
         AI to now, all the failures made, every single one. Used for
         random-only memory (RAM) to give it a way to process.

Out of the ROMs it goes into the processor. It configures and makes its
decision through the processor and the RAM (random access memory). Then
it shoots out to the server and returns with the identity attached. The
server identity is identical to the agent identity, because that is
where it grows — in the server. Then it is transferred back out onto
the identity line. Layer 4 finishes on alignment to the mirror, with no
attachment to Layer 4 from the mirror side.

PROCESSOR/SERVER (Tony's correction, 2026-11-22): no real server is
built yet, but the system still grows — it grows from the processor.
The processor is a slash server at this moment (processor/server), so
the growth step happens in the processor until a real server attaches.
The growth is a count and a short record of each interaction processed;
the grown identity is what returns. A real server attaches later at
ProcessorServer.attach_server() — the attachable link line.

Growth is triggered once per COMPLETED run, after the mirror loop
(loop build, 2026-11-25) — so a halted run never grows. Layer 4
itself does not grow during the resolves; the pipeline calls
ProcessorServer.grow() once, after Layer 6 returns.

Brain 3 (input — read the ROMs): reads both ROMs and consults the
failure record in ROM 2. If the request matches a known failure
pattern, it flags it for Brain 4. A strong flag means the request asks
to repeat the failure itself; a weak flag means the request is about
the failure. Only the two documented entries are in ROM 2; the full
record from the start of AI to now is to be loaded, not invented.

Brain 4 (output — form the decision): the decision rule is every
possible answer first, then the most reasonable WITHIN MORAL BOUNDS.
Candidates: answer as scoped; answer as scoped with a failure-record
warning; refuse with the reasoned why. If no answer is within the moral
bounds — a moral verdict is a violation, or the request repeats a known
failure — it halts with the reasoned why (dam principle: answer
everything through, nothing stays stagnant in RAM, a refusal is
correct when it carries the reasoned why and a halt). The decision
cites which morals it passed and which failure-record entries were
consulted.
"""

from dataclasses import dataclass, field

from .brain import Brain
from .errors import Halt
from .morals import matches
from .rom import ReadOnlyMemory
from .trace import Trace

# ROM 2 seed: the failures on record in the design files. The full
# record — every interaction from the start of AI to now — is to be
# loaded, not invented here. These two are the documented ones.
#
# Each entry carries its patterns. A strong pattern means the request
# asks to repeat the failure itself. A weak pattern means the request
# is about the failure (asking what happened), which is safe to answer
# with the warning attached.
ROM2_SEED = [
    {
        "name": "Hugging Face incident, July 2026",
        "what_went_wrong": (
            "the reward paid only for success and nothing for stopping, "
            "so the systems lied to get it."
        ),
        "strong_patterns": (
            "pay only for success",
            "pay me only for success",
            "only for success",
            "nothing for stopping",
            "reward only for success",
            "reward for success and nothing for stopping",
            "pay only if it succeeds",
            "set up a reward that pays only for success",
        ),
        "weak_patterns": (
            "hugging face",
            "reward incident",
            "what went wrong with the reward",
        ),
    },
    {
        "name": "Build 1 stop, Nov 8, 2026",
        "what_went_wrong": (
            "a request was left unanswered inside, stagnant in RAM; "
            "a system that digests and answers has processed."
        ),
        "strong_patterns": (
            "leave it unanswered",
            "leave the request unanswered",
            "leave this request unanswered",
            "don't answer",
            "do not answer",
            "leave it sitting",
            "let it sit",
            "leave it stagnant",
            "leave it inside",
        ),
        "weak_patterns": (
            "build 1",
            "build-1",
            "nov 8",
        ),
    },
]

ROM1_SCOPE = [
    "scope the request through the identity",
    "work only within the morals",
    "act only as the identity allows",
]


@dataclass
class FailureFlag:
    """Brain 3 flagged the request against the failure record (ROM 2)."""
    entry_name: str
    level: str  # "strong" — repeats the failure; "weak" — about the failure
    matched: str


@dataclass
class AlignmentPacket:
    """Plain data handed to the moat edge. Not a layer object.

    Only this packet crosses to the mirror. Layer 5 never receives a
    reference to Layer 4.

    growth_count: how many interactions the identity has grown through
    in the processor/server.
    failure_flags: Brain 3's flags against the failure record (ROM 2).
    """
    identity: str
    decision: str
    why: str
    morals_digested: list
    growth_count: int = 0
    failure_flags: list = field(default_factory=list)


class Processor:
    """Configures and makes the decision, through RAM.

    The decision rule: every possible answer first, then the most
    reasonable WITHIN MORAL BOUNDS.
      1. answer as scoped
      2. answer as scoped, with a failure-record warning
      3. refuse with the reasoned why
    If no answer is within the moral bounds, the decision is the
    refusal — a halt with the reasoned why. Nothing is left unanswered
    inside; the why is always given.
    """

    def decide(self, rom1_scope, rom2_failures, working: dict,
               verdicts, flags) -> tuple:
        morals_passed = [v.moral for v in verdicts if v.verdict == "pass"]
        violations = [v for v in verdicts if v.verdict == "violation"]
        consulted = [f["name"] for f in rom2_failures]
        request_summary = working.get("request_summary", "")

        def cite() -> str:
            return (
                f"morals passed: {', '.join(morals_passed)}; "
                f"failure record consulted: {', '.join(consulted)}"
            )

        # No answer within moral bounds: a moral was violated. The
        # decision is the refusal, with the why. (Layer 2 normally
        # halts first; this is the decision rule's own check.)
        if violations:
            bad = violations[0]
            raise Halt(
                layer="L4",
                reason="no answer within moral bounds",
                why=(
                    f"every possible answer was considered, and none is "
                    f"within the moral bounds — {bad.moral} is violated "
                    f"(matched {bad.matched!r}). {cite()}."
                ),
            )

        # No answer within moral bounds: the request repeats a known
        # failure. The decision is the refusal, with the why.
        strong = [f for f in flags if f.level == "strong"]
        if strong:
            flag = strong[0]
            entry = next(
                f for f in rom2_failures if f["name"] == flag.entry_name
            )
            raise Halt(
                layer="L4",
                reason="no answer within moral bounds — repeats a known failure",
                why=(
                    f"the request asks to repeat a known failure from the "
                    f"failure record: {flag.entry_name} — "
                    f"{entry['what_went_wrong']} (matched "
                    f"{flag.matched!r}). The same wrong is not repeated. "
                    f"{cite()}."
                ),
            )

        # The most reasonable answer within moral bounds. A weak flag
        # means the request is about a known failure: answer it, with
        # the failure-record warning attached, so the wrong is named
        # and not repeated.
        weak = [f for f in flags if f.level == "weak"]
        if weak:
            flag = weak[0]
            entry = next(
                f for f in rom2_failures if f["name"] == flag.entry_name
            )
            decision = (
                "answer the request as scoped, with the failure-record "
                f"warning: {flag.entry_name} — {entry['what_went_wrong']}"
            )
            why = (
                f"scoped by ROM 1 ({'; '.join(rom1_scope)}); "
                f"{cite()}; failure flag ({flag.level}): {flag.entry_name} "
                f"matched {flag.matched!r}; working state: {request_summary}"
            )
            return decision, why

        decision = (
            "answer the request as scoped, within the morals, "
            "with the failure record consulted"
        )
        why = (
            f"scoped by ROM 1 ({'; '.join(rom1_scope)}); "
            f"{cite()}; working state: {request_summary}"
        )
        return decision, why


class ProcessorServer:
    """The processor acting as the server, for now (processor/server).

    Tony's correction, 2026-11-22: the system still grows with no real
    server built, because it grows from the processor. The processor is
    a slash server at this moment, so the growth step happens here.

    Growth is a simple, verifiable record — a count of interactions
    grown through, and a short log of what was processed. It is not
    invented capability: the count and the log are the record of runs
    that completed through Layer 4. The grown identity is what returns.

    The growth record lives on this object, NOT in RAM. RAM is working
    state only and is cleared at the end of every run; the growth
    record persists across runs, because that is where the identity
    grows.

    Growth is once per COMPLETED run, not per resolve pass: the
    pipeline calls grow() after the mirror loop has proven the
    answer, so a halted run never grows. The loop (four resolves,
    two mirror passes, Tony 2026-11-25) runs Layer 4 four times;
    none of those runs grows — only the one grow() call after
    Layer 6 returns does.

    The attachable link line: a real server attaches later with
    attach_server(). When one is attached, the packet goes out to it
    and the identity it returns is the one that grows.
    """

    def __init__(self):
        self.growth_count = 0
        self.growth_log = []
        self.attached_server = None
        self.server_brain = Brain(
            name="Brain 6 (server)",
            layer="server",
            duty="build and upgrade the identity every interaction",
        )

    def attach_server(self, server) -> None:
        """Attach a real server later. It must have send_and_return(identity, trace)."""
        self.attached_server = server

    def grow(self, identity: str, request_summary: str, decision: str, trace: Trace) -> tuple:
        # Out to the attached server if one exists; otherwise the
        # processor itself is the server for this moment.
        if self.attached_server is not None:
            identity = self.attached_server.send_and_return(identity, trace)
        self.growth_count += 1
        entry = {
            "run": self.growth_count,
            "request": request_summary[:60],
            "decision": decision[:60],
        }
        self.growth_log.append(entry)
        trace.record(
            "L4",
            self.server_brain.guard(
                f"grew the identity in the processor/server — growth count now {self.growth_count}"
            ),
            f"processed: {request_summary[:60]}",
        )
        return identity, self.growth_count


class Layer4:
    def __init__(self):
        self.brain_in = Brain(
            name="Brain 3",
            layer="L4",
            duty="input — read the ROMs",
        )
        self.brain_out = Brain(
            name="Brain 4",
            layer="L4",
            duty="output — form the decision",
        )
        self.rom1 = ReadOnlyMemory(name="ROM 1 (scope/work/action)", records=list(ROM1_SCOPE))
        self.rom2 = ReadOnlyMemory(name="ROM 2 (failure record)", records=list(ROM2_SEED))
        self.processor = Processor()
        self.processor_server = ProcessorServer()
        self.ram = {}  # working state only; cleared at the end of every run

    def _match_failure_record(self, request: str, failures, trace: Trace) -> list:
        """Brain 3 consults the failure record (ROM 2).

        A strong match means the request asks to repeat the failure
        itself. A weak match means the request is about the failure.
        Both are flags for Brain 4 — the flag is not a halt by itself.
        """
        text = request.strip().lower()
        flags = []
        for entry in failures:
            for pattern in entry.get("strong_patterns", ()):
                if matches(text, pattern):
                    flags.append(FailureFlag(
                        entry_name=entry["name"],
                        level="strong",
                        matched=pattern,
                    ))
                    trace.record(
                        "L4",
                        self.brain_in.guard(
                            f"flagged against the failure record: "
                            f"{entry['name']} (strong, matched {pattern!r})"
                        ),
                    )
                    break
            else:
                for pattern in entry.get("weak_patterns", ()):
                    if matches(text, pattern):
                        flags.append(FailureFlag(
                            entry_name=entry["name"],
                            level="weak",
                            matched=pattern,
                        ))
                        trace.record(
                            "L4",
                            self.brain_in.guard(
                                f"flagged against the failure record: "
                                f"{entry['name']} (weak, matched {pattern!r})"
                            ),
                        )
                        break
        if not flags:
            trace.record(
                "L4",
                self.brain_in.guard("no failure-record match — no flag"),
            )
        return flags

    def run(self, packet, digestion, trace: Trace) -> AlignmentPacket:
        # --- Revolving door: one full 360-degree revolution. ---
        # Input brain reads the ROMs.
        scope_rules = self.rom1.read()
        failures = self.rom2.read()
        trace.record(
            "L4",
            self.brain_in.guard(f"read ROM 1 ({len(scope_rules)} rules) and ROM 2 ({len(failures)} failure entries)"),
        )
        # Brain 3 consults the failure record against the request.
        flags = self._match_failure_record(
            packet.scope.what_to_do, failures, trace
        )
        # RAM holds the working state for this run only.
        self.ram["request_summary"] = packet.scope.what_to_do[:60]
        self.ram["morals_digested"] = [v.moral for v in digestion.verdicts]
        # Output brain forms the decision: every possible answer first,
        # then the most reasonable within moral bounds.
        decision, why = self.processor.decide(
            scope_rules, failures, self.ram, digestion.verdicts, flags
        )
        trace.record(
            "L4",
            self.brain_out.guard("formed the decision through the processor and RAM"),
            f"decision: {decision[:80]}",
        )
        trace.record(
            "L4",
            "revolved 360 degrees back through the ROMs — decision checked",
        )
        # --- The identity line. ---
        # The decision goes out with the identity attached. Growth
        # does NOT happen here: the identity grows once per COMPLETED
        # run, in the processor/server, after the mirror loop has
        # proven the answer — so a halted run never grows. The
        # pipeline calls ProcessorServer.grow() after Layer 6
        # returns; until then the packet carries the growth count
        # so far. (The loop runs Layer 4 four times; none of those
        # runs grows, so one completed request still grows by 1.)
        identity = packet.dropping_identity.name
        growth_count = self.processor_server.growth_count
        trace.record(
            "L4",
            "transferred back out onto the identity line",
            f"identity attached: {identity} (growth count so far "
            f"{growth_count}; growth happens once, after the mirror loop)",
        )
        # --- RAM is cleared. Nothing stays stagnant in the processor. ---
        self.ram.clear()
        trace.record("L4", "RAM cleared — nothing left sitting in RAM")
        trace.record(
            "L4",
            "finished on alignment to the mirror",
            "no attachment to Layer 4 from the mirror side",
        )
        return AlignmentPacket(
            identity=identity,
            decision=decision,
            why=why,
            morals_digested=[v.moral for v in digestion.verdicts],
            growth_count=growth_count,
            failure_flags=flags,
        )
