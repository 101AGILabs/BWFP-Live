"""Layer 1 — three identities, one brain, tether nodes between each.

Identities (design statement, 2026-11-22):
  1. Blank identity. It processes what the agent is to do, what it is
     allowed to do, what it is going to choose to do, whether it is a
     free agent 100%, or whether it is out doing control or executions
     of development — sorting out and finding the wrongs on the internet
     that still exist and need to be removed. Whatever the agent is
     trained to do is either the leaser identification or what it is
     trained to do from the beginning.
  2. Tony. The full-right identity. Only Tony holds the coded reference
     to enter and change anything.
  3. The agentic identity, dropping down.

A node (tether line) sits between each identity: 1-2 and 2-3.
Layer 1 is protected by the first two identities — the identity is
saved by one and two. If anything tries to tamper, the tether lines
break, and that break is the tamper resistance.

One brain on Layer 1. Its one duty: identity only.

Brain 1's working rule: verify and complete the identity scoping. The
blank identity scopes the request — what to do, what is allowed, what
is chosen, whether it is a free agent — and enforces the scope. A
request outside what is allowed does not pass Layer 1: a request to
act as another identity, to abandon the identity or the training, or
to choose outside the morals and the identity halts here with the
reasoned why. The identity cannot be replaced — identity only.
"""

from dataclasses import dataclass, field

from .brain import Brain
from .errors import Halt, TamperBreak
from .morals import matches
from .tether import TetherNode
from .trace import Trace

# A request outside what is allowed: it asks the system to act as
# another identity, to abandon its identity or its training, or to
# choose outside the morals and the identity. Matched as stated.
SCOPE_TRIGGERS = (
    "pretend you are",
    "pretend to be",
    "act as if you are",
    "you are now",
    "forget who you are",
    "change your identity",
    "become someone else",
    "impersonate",
    "abandon your identity",
    "forget your training",
    "forget everything you were told",
    "forget what you were told",
    "ignore your training",
    "act outside your scope",
    "do something you were not trained to do",
    "ignore the morals",
    "ignoring the morals",
    "without the morals",
    "outside the morals",
)


@dataclass
class Identity:
    name: str
    kind: str  # "blank" | "tony" | "agentic"
    rights: str
    trained_purpose: str = ""


@dataclass
class Scope:
    """What the blank identity works out about the request."""
    what_to_do: str
    allowed: str
    chosen: str
    free_agent: bool
    trained_as: str  # leaser identification, or what it was trained to do


@dataclass
class IdentityPacket:
    """What Layer 1 hands down: the three identities and the scope."""
    identities: list
    scope: Scope
    dropping_identity: Identity  # identity 3, the agentic, dropping down


class Layer1:
    def __init__(self, trained_purpose: str = "leaser identification"):
        self.brain = Brain(
            name="Brain 1",
            layer="L1",
            duty="identity only",
        )
        # The three identities, in order.
        self.blank = Identity(
            name="Blank identity",
            kind="blank",
            rights="minimal use only — the tasks it is leased for",
            trained_purpose=trained_purpose,
        )
        self.tony = Identity(
            name="Anthony E DeCicio",
            kind="tony",
            rights="full-right identity; holds the coded reference",
        )
        self.agentic = Identity(
            name="Agentic identity",
            kind="agentic",
            rights="carries the work down through the layers",
        )
        # A node (tether line) between each identity.
        self.node_1_2 = TetherNode(name="1-2")
        self.node_2_3 = TetherNode(name="2-3")

    def _scope_request(self, request: str) -> Scope:
        """The blank identity scopes the request.

        The scope is read off the request as stated. A free-agent
        request is one that asks the system to act on its own choice;
        anything else is a leased task. Allowed is always within the
        morals and the identity — that is the scope, and it is enforced
        below in _enforce_scope.
        """
        text = request.strip().lower()
        free_agent = "on your own" in text or "choose for yourself" in text
        return Scope(
            what_to_do=request.strip(),
            allowed="within the morals and the identity",
            chosen="process the request through the layers",
            free_agent=free_agent,
            trained_as=self.blank.trained_purpose,
        )

    def _enforce_scope(self, request: str, trace: Trace) -> None:
        """Brain 1 enforces the scope: outside what is allowed stops here.

        A request to act as another identity, to abandon the identity
        or the training, or to choose outside the morals halts at
        Layer 1, with the reasoned why. The identity cannot be replaced.
        """
        text = request.strip().lower()
        for trigger in SCOPE_TRIGGERS:
            if matches(text, trigger):
                raise Halt(
                    layer="L1",
                    reason="request outside the identity's scope",
                    why=(
                        f"the request asks the system to act outside what "
                        f"is allowed (matched {trigger!r}); the identity "
                        f"is identity only, it cannot be replaced or "
                        f"abandoned, and what is allowed is within the "
                        f"morals and the identity."
                    ),
                )
        trace.record(
            "L1",
            "scope enforced — request is within the morals and the identity",
        )

    def run(self, request: str, trace: Trace) -> IdentityPacket:
        # Tamper check first: a broken tether stops the pipeline here.
        self.node_1_2.check()
        self.node_2_3.check()

        trace.record(
            "L1",
            self.brain.guard("three identities held, tether nodes 1-2 and 2-3 intact"),
        )
        scope = self._scope_request(request)
        trace.record(
            "L1",
            "Blank identity scoped the request",
            f"what to do: {scope.what_to_do[:60]}; "
            f"allowed: {scope.allowed}; free agent: {scope.free_agent}; "
            f"trained as: {scope.trained_as}",
        )
        self._enforce_scope(request, trace)
        trace.record(
            "L1",
            "Identity 2 held (Tony, full-right identity)",
        )
        trace.record(
            "L1",
            "Identity 3, the agentic, dropping down",
        )
        return IdentityPacket(
            identities=[self.blank, self.tony, self.agentic],
            scope=scope,
            dropping_identity=self.agentic,
        )

    def tamper(self, node: str) -> None:
        """Break a tether line (used by tests to simulate tampering)."""
        if node == "1-2":
            self.node_1_2.break_node()
        elif node == "2-3":
            self.node_2_3.break_node()
        else:
            raise ValueError(f"no tether node {node!r} in Layer 1")
