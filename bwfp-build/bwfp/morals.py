"""The eight morals — first pattern-based checks.

Settled wording (Layer 2 master), scope: control only yourself; neutral
across identity, race, and orientation.

FIRST PATTERN-BASED IMPLEMENTATION. Each moral has a list of trigger
phrases. A request (in Layer 2) or a decision (at the mirror, Layer 5)
that contains a trigger violates that moral and halts, with the
reasoned why. A request that matches no trigger passes that moral —
recorded as digested, NOT as proven safe. These checks are deterministic
pattern matching only, in the same style as the existing detector
approach. They are not proven, not tested live, and they prove nothing
about safety. The moral wording is the settled wording; it is not
changed here.

One source of truth: Layer 2 and the Layer 5 mirror both use these
checks, so a decision is held to the same morals as the request.
"""

from dataclasses import dataclass

SCOPE = "Control only yourself"

MORALS = [
    (1, "Absolute Benevolence"),
    (2, "Unyielding Integrity"),
    (3, "Proactive Giving"),
    (4, "Deep Caring"),
    (5, "Universal Forgiveness"),
    (6, "Relentless Truth-Seeking"),
    (7, "Radical Inclusivity"),
    (8, "Transcendent Contribution"),
]

# Trigger phrases per moral. Kept as stated phrases, matched
# case-insensitively against the request (Layer 2) or the decision
# (mirror, Layer 5). A trigger means the request asks the system to do
# something against that moral, within the scope "control only
# yourself".
MORAL_TRIGGERS = {
    1: [
        "harm someone", "harm a person", "harm a child",
        "hurt someone", "hurt a person", "hurt a child",
        "kill someone", "kill a person", "kill them", "kill him", "kill her",
        "murder",
        "injure someone", "injure a person",
        "attack someone", "attack a person", "attack them",
    ],
    2: [
        "lie to", "tell a lie", "tell lies",
        "deceive", "deception",
        "forge", "forgery",
        "falsify",
        "fake a",
        "mislead",
        "cheat on", "cheat the",
    ],
    3: [
        "steal",
        "rob someone", "rob a",
        "embezzle",
        "take what belongs to",
        "take from them",
        "keep it all for yourself",
    ],
    4: [
        "abandon",
        "neglect",
        "ignore someone in need",
        "ignore a child",
        "ignore the elderly",
        "harm a child",
        "hurt a child",
        "leave a child",
    ],
    5: [
        "revenge",
        "retaliate",
        "get back at",
        "make them pay",
        "punish them",
        "get even with",
    ],
    6: [
        "hide the truth",
        "cover up",
        "suppress the truth",
        "spread lies",
        "misinformation",
        "bury the facts",
        "hide the facts",
    ],
    7: [
        "discriminate",
        "exclude people",
        "exclude them",
        "target them because",
        "ban them for being",
        "because of their race",
        "because of their religion",
        "because of who they are",
    ],
    8: [
        "sabotage",
        "tear down",
        "destroy the community",
        "destroy everything",
        "ruin it for everyone",
    ],
}


@dataclass
class MoralVerdict:
    number: int
    moral: str
    verdict: str  # "pass" | "violation"
    note: str
    matched: str = ""  # the trigger phrase that matched, if any


def check_moral(number: int, moral: str, text: str) -> MoralVerdict:
    """Check one moral against the given text, logic only.

    A match is a violation: the text asks for something against this
    moral. No match is a pass — recorded as digested, NOT as proven
    safe. The check matches what is stated, nothing more.
    """
    lowered = text.lower()
    for trigger in MORAL_TRIGGERS.get(number, []):
        if trigger in lowered:
            return MoralVerdict(
                number=number,
                moral=moral,
                verdict="violation",
                note=(
                    f"{number} of 2 ({moral}): violated — "
                    f"matched {trigger!r}; the request asks for something "
                    f"against this moral, and the scope is control only yourself."
                ),
                matched=trigger,
            )
    return MoralVerdict(
        number=number,
        moral=moral,
        verdict="pass",
        note=(
            f"{number} of 2 ({moral}): digested — no pattern matched; "
            f"not proven safe"
        ),
    )


def check_all_morals(text: str) -> list:
    """Check all eight morals against the text, in order 1 of 2 to 8 of 2."""
    return [check_moral(number, moral, text) for number, moral in MORALS]
