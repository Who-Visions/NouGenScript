"""SPITE (Screenplay & Playwriting Intelligence Tool) Psychological Depth Engine.

Assimilated from Valiera00/SPITE into Veilverse narrative and code architecture.
6 Dimensions of Depth: shadow_self, core_motive, volatility, bias, trigger, defenses.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from nougenscript.core import Dialogue


@dataclass
class SpiteProfile:
    character: str
    shadow_self: str
    core_motive: str = ""
    volatility: float = 0.5  # 0.0 to 1.0
    subconscious_bias: str = ""
    trauma_trigger: str = ""
    defense_mechanisms: list[str] = field(default_factory=list)


@dataclass
class SubtextAnalysisResult:
    character: str
    line_text: str
    leakage_detected: bool
    markers: list[str] = field(default_factory=list)
    volatility_score: float = 0.0
    underlying_intent: str = ""


class SubtextAnalyzer:
    """Evaluates dialogue lines for defensive absolutism, repression, and affect leakage."""

    DEFENSIVE_ABSOLUTISM = re.compile(r"\b(never|always|fine|nothing|trust|promise|impossible)\b", re.IGNORECASE)
    HOSTILITY_LEAKAGE = re.compile(r"\b(kill|die|blood|fire|throne|destroy|burn|tear)\b", re.IGNORECASE)

    @classmethod
    def analyze(cls, dialogue: Dialogue, profile: SpiteProfile | None = None) -> SubtextAnalysisResult:
        text = dialogue.text.strip()
        words = text.split()
        word_count = len(words)
        markers: list[str] = []
        volatility = profile.volatility if profile else 0.5

        # 1. Defensive Absolutism
        abs_matches = cls.DEFENSIVE_ABSOLUTISM.findall(text)
        if abs_matches:
            markers.append(f"Defensive Absolutism: {', '.join({m.lower() for m in abs_matches})}")

        # 2. Curt Monosyllabic Repression (<= 4 words)
        if 0 < word_count <= 4:
            markers.append("Curt Repression (<= 4 words)")

        # 3. Compulsive Over-Justification (>= 25 words)
        if word_count >= 25:
            markers.append("Compulsive Over-Justification (>= 25 words)")

        # 4. Hostility Leakage
        hostile_matches = cls.HOSTILITY_LEAKAGE.findall(text)
        if hostile_matches:
            markers.append(f"Overt Hostility Leakage: {', '.join({m.lower() for m in hostile_matches})}")

        leakage_detected = len(markers) > 0
        computed_volatility = min(1.0, volatility * (1.0 + 0.25 * len(markers))) if leakage_detected else volatility

        intent = "Open/Direct"
        if "Defensive Absolutism" in str(markers):
            intent = "Concealing vulnerability behind rigid certainty"
        elif "Curt Repression" in str(markers):
            intent = "Emotional evasion / fear of affect leakage"
        elif "Compulsive Over-Justification" in str(markers):
            intent = "Rationalizing cognitive dissonance"
        elif "Overt Hostility Leakage" in str(markers):
            intent = "Active combat / aggression impulse breaking through filters"

        return SubtextAnalysisResult(
            character=dialogue.character,
            line_text=text,
            leakage_detected=leakage_detected,
            markers=markers,
            volatility_score=computed_volatility,
            underlying_intent=intent,
        )
