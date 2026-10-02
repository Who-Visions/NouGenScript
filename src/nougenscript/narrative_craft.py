"""Top 0.001% Narrative Scriptwriting Craft Engine.

Assimilates master dramaturgical laws into automated engineering diagnostics:
1. Mamet Inflexible Triad: Who wants what from whom? What happens if they don't get it? Why now?
2. Status Transaction Dynamics (Keith Johnstone / Robert McKee): Micro-beat power negotiations.
3. Sorkin Cadence & Prosody Engine: Musicality, syllabic meter, staccato vs legato, triad repetition.
4. Causal Velocity Invariant (Howard & Mabley / Trey Parker): 'Therefore' / 'But' vs 'And then'.
5. Hitchcock Information Architecture: Weaponized Dramatic Irony vs Mystery vs Surprise.
6. 4-Stage Narrative Recursion: Setup -> First Echo -> Inversion -> Final Payoff.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

from nougenscript.core import Dialogue, NodeType, Scene, Screenplay


# --------------------------------------------------------------------------- #
# 1. Mamet Dramatic Unit Auditor
# --------------------------------------------------------------------------- #

@dataclass
class MametAuditResult:
    scene_id: str
    heading: str
    has_objective: bool
    objective_markers: list[str]
    has_stakes: bool
    stakes_markers: list[str]
    has_urgency: bool
    urgency_markers: list[str]
    mamet_score: float  # 0.0 to 1.0
    is_dramatic_propulsion: bool
    recommendations: list[str] = field(default_factory=list)


class MametAuditor:
    """Evaluates scenes against David Mamet's 3 non-negotiable scene questions."""

    OBJECTIVE_VERBS = re.compile(
        r"\b(want|need|give|tell|sign|confess|stop|listen|leave|surrender|hand|pay|admit|swear|kill|save|open)\b",
        re.IGNORECASE,
    )
    STAKES_WORDS = re.compile(
        r"\b(die|dies|dying|dead|death|kill|kills|killed|destroy|destroys|destroyed|destruction|lose|loses|losing|loss|ruin|ruins|ruined|prison|jail|fire|fired|expose|exposed|arrest|arrested|blood|bleed|bleeding|bankrupt|burn|burns|burned|threat|threats|end|cost|costs)\b",
        re.IGNORECASE,
    )
    URGENCY_WORDS = re.compile(
        r"\b(now|today|tonight|immediately|minute|minutes|second|seconds|clock|before|hurry|fast|deadline|already|late|leaving)\b",
        re.IGNORECASE,
    )

    @classmethod
    def audit_scene(cls, scene: Scene) -> MametAuditResult:
        full_text = " ".join(node.content for node in scene.nodes)

        obj_matches = list(set(cls.OBJECTIVE_VERBS.findall(full_text)))
        stakes_matches = list(set(cls.STAKES_WORDS.findall(full_text)))
        urgency_matches = list(set(cls.URGENCY_WORDS.findall(full_text)))

        has_obj = len(obj_matches) > 0
        has_stakes = len(stakes_matches) > 0
        has_urgency = len(urgency_matches) > 0

        # Score components: Objective = 0.4, Stakes = 0.35, Urgency = 0.25
        score = (0.4 if has_obj else 0.0) + (0.35 if has_stakes else 0.0) + (0.25 if has_urgency else 0.0)
        is_propulsion = score >= 0.75

        recs: list[str] = []
        if not has_obj:
            recs.append("Lacks concrete objective. Anchor a tangible ask: Who wants what from whom?")
        if not has_stakes:
            recs.append("Lacks palpable stakes. Clarify what happens if the protagonist fails right now.")
        if not has_urgency:
            recs.append("Lacks urgent catalyst. Add a ticking clock, impending deadline, or immediate trigger.")

        return MametAuditResult(
            scene_id=scene.scene_id,
            heading=scene.heading,
            has_objective=has_obj,
            objective_markers=obj_matches[:5],
            has_stakes=has_stakes,
            stakes_markers=stakes_matches[:5],
            has_urgency=has_urgency,
            urgency_markers=urgency_matches[:5],
            mamet_score=round(score, 2),
            is_dramatic_propulsion=is_propulsion,
            recommendations=recs,
        )


# --------------------------------------------------------------------------- #
# 2. Keith Johnstone / Robert McKee Status Transaction Tracker
# --------------------------------------------------------------------------- #

class StatusMove(str, Enum):
    RAISE_SELF = "RAISE_SELF"        # Commands, dismissals, calm stillness, invading space
    LOWER_SELF = "LOWER_SELF"        # Apologizing, deferring, seeking permission, self-deprecation
    LOWER_OTHER = "LOWER_OTHER"      # Mocking, interrupting, correcting, condescending
    RAISE_OTHER = "RAISE_OTHER"      # Flattering, validating, submitting
    NEUTRAL = "NEUTRAL"


@dataclass
class StatusTurn:
    character: str
    line: str
    move: StatusMove
    status_delta: int  # +1, -1, 0
    cumulative_status: int
    tactic: str


@dataclass
class StatusTransactionResult:
    characters: list[str]
    turns: list[StatusTurn]
    reversals_detected: int
    dominant_character: str
    submissive_character: str
    final_balance: dict[str, int]


class StatusTracker:
    """Evaluates line-by-line status negotiations between characters in a dramatic exchange."""

    RAISE_SELF_RE = re.compile(r"\b(i order|i decide|look at me|sit down|listen to me|silence|enough|mine|i am)\b", re.I)
    LOWER_SELF_RE = re.compile(r"\b(sorry|i apologize|please forgive|my fault|i didn't mean|excuse me|if it's okay)\b", re.I)
    LOWER_OTHER_RE = re.compile(r"\b(fool|stupid|pathetic|you never|shut up|amateur|ridiculous|clueless|child)\b", re.I)
    RAISE_OTHER_RE = re.compile(r"\b(you're right|you are brilliant|at your service|as you wish|you honor me)\b", re.I)

    @classmethod
    def analyze_dialogues(cls, dialogues: Sequence[Dialogue]) -> StatusTransactionResult:
        turns: list[StatusTurn] = []
        balances: dict[str, int] = {}
        last_dominant = ""
        last_moves: dict[str, StatusMove] = {}
        reversals = 0

        for d in dialogues:
            char = d.character.upper().strip()
            if char not in balances:
                balances[char] = 0

            text = d.text.strip()
            move = StatusMove.NEUTRAL
            delta = 0
            tactic = "Informational exchange"

            if cls.LOWER_OTHER_RE.search(text):
                move = StatusMove.LOWER_OTHER
                delta = 1
                tactic = "Aggressive status degradation"
            elif cls.RAISE_SELF_RE.search(text):
                move = StatusMove.RAISE_SELF
                delta = 1
                tactic = "Dominance assertion / claiming authority"
            elif cls.LOWER_SELF_RE.search(text):
                move = StatusMove.LOWER_SELF
                delta = -1
                tactic = "Submissive appeasement / defensive surrender"
            elif cls.RAISE_OTHER_RE.search(text):
                move = StatusMove.RAISE_OTHER
                delta = -1
                tactic = "Deference / status elevation of other"

            # Check if this character had previously surrendered status and is now revolting (Peripeteia)
            prev_move = last_moves.get(char)
            if prev_move in (StatusMove.LOWER_SELF, StatusMove.RAISE_OTHER) and delta > 0:
                reversals += 1

            balances[char] += delta
            last_moves[char] = move

            current_dominant = max(balances.items(), key=lambda x: x[1])[0] if balances else ""
            if last_dominant and current_dominant and last_dominant != current_dominant:
                reversals += 1
            last_dominant = current_dominant

            turns.append(
                StatusTurn(
                    character=char,
                    line=text[:80] + ("..." if len(text) > 80 else ""),
                    move=move,
                    status_delta=delta,
                    cumulative_status=balances[char],
                    tactic=tactic,
                )
            )

        chars = list(balances.keys())
        dom = max(balances.items(), key=lambda x: x[1])[0] if balances else ""
        sub = min(balances.items(), key=lambda x: x[1])[0] if balances else ""

        return StatusTransactionResult(
            characters=chars,
            turns=turns,
            reversals_detected=reversals,
            dominant_character=dom,
            submissive_character=sub,
            final_balance=balances,
        )


# --------------------------------------------------------------------------- #
# 3. Aaron Sorkin Cadence & Dialogue Prosody Scorer
# --------------------------------------------------------------------------- #

@dataclass
class CadenceMetrics:
    total_lines: int
    average_syllables_per_line: float
    staccato_ratio: float  # lines with <= 6 words
    legato_ratio: float    # lines with >= 20 words
    monotone_penalty: float  # penalty for invariant line lengths
    triad_callbacks: int     # instances of 3-beat rhetorical structures
    musicality_score: float  # 0.0 to 100.0


class CadenceAnalyzer:
    """Measures rhythmic musicality, metric variance, and rhetorical momentum."""

    _SYLLABLE_PAT = re.compile(r"[aeiouy]+", re.I)

    @classmethod
    def count_syllables(cls, word: str) -> int:
        w = word.lower().strip(".,!?:;\"'")
        if not w:
            return 0
        matches = cls._SYLLABLE_PAT.findall(w)
        count = len(matches)
        if w.endswith("e") and not w.endswith("le") and count > 1:
            count -= 1
        return max(1, count)

    @classmethod
    def analyze(cls, dialogues: Sequence[Dialogue]) -> CadenceMetrics:
        if not dialogues:
            return CadenceMetrics(0, 0.0, 0.0, 0.0, 0.0, 0, 0.0)

        word_counts: list[int] = []
        syllable_counts: list[int] = []

        for d in dialogues:
            words = d.text.split()
            word_counts.append(len(words))
            syllables = sum(cls.count_syllables(w) for w in words)
            syllable_counts.append(syllables)

        total = len(dialogues)
        avg_syl = sum(syllable_counts) / total if total else 0.0
        staccato = sum(1 for w in word_counts if w <= 6) / total
        legato = sum(1 for w in word_counts if w >= 20) / total

        # Check monotone penalty: runs of 3+ lines with identical word count +/- 1
        monotone_runs = 0
        for i in range(len(word_counts) - 2):
            w1, w2, w3 = word_counts[i], word_counts[i + 1], word_counts[i + 2]
            if abs(w1 - w2) <= 1 and abs(w2 - w3) <= 1:
                monotone_runs += 1

        monotone_pen = min(30.0, monotone_runs * 5.0)

        # Detect triads (rule of 3 rhetorical devices in single lines)
        triads = 0
        triad_re = re.compile(r"([^,]+),\s*([^,]+),\s*(and\s+)?([^.?!]+)[.?!]", re.I)
        for d in dialogues:
            if triad_re.search(d.text):
                triads += 1

        # Musicality: balance between staccato (snappy) and legato (depth) + triads - monotony
        base_score = 60.0
        if 0.20 <= staccato <= 0.60:
            base_score += 15.0
        if 0.10 <= legato <= 0.35:
            base_score += 15.0
        base_score += min(15.0, triads * 3.0)
        base_score -= monotone_pen

        musicality = max(0.0, min(100.0, base_score))

        return CadenceMetrics(
            total_lines=total,
            average_syllables_per_line=round(avg_syl, 1),
            staccato_ratio=round(staccato, 2),
            legato_ratio=round(legato, 2),
            monotone_penalty=round(monotone_pen, 1),
            triad_callbacks=triads,
            musicality_score=round(musicality, 1),
        )


# --------------------------------------------------------------------------- #
# 4. Causal Velocity & Pacing Invariant (Therefore / But vs And-Then)
# --------------------------------------------------------------------------- #

@dataclass
class CausalityReport:
    total_scene_transitions: int
    therefore_transitions: int
    but_transitions: int
    and_then_transitions: int
    causal_velocity_ratio: float  # (therefore + but) / total (Target: >= 0.85)
    flagged_episodic_gaps: list[str] = field(default_factory=list)


class CausalityValidator:
    """Verifies that dramatic scenes are linked by consequence ('therefore') or conflict ('but')."""

    THEREFORE_WORDS = re.compile(r"\b(because|consequence|forced|retaliat|result|now we have to|driven to|caused)\b", re.I)
    BUT_WORDS = re.compile(r"\b(however|but|interrupted|failed|betrayed|blocked|reversed|sabotage|ambush|unexpected)\b", re.I)

    @classmethod
    def evaluate_screenplay(cls, script: Screenplay) -> CausalityReport:
        scenes = script.scenes
        if len(scenes) <= 1:
            return CausalityReport(0, 0, 0, 0, 1.0)

        n_transitions = len(scenes) - 1
        therefore_c = 0
        but_c = 0
        and_then_c = 0
        flagged: list[str] = []

        for i in range(n_transitions):
            s1, s2 = scenes[i], scenes[i + 1]
            s2_text = " ".join(n.content for n in s2.nodes)

            if cls.THEREFORE_WORDS.search(s2_text):
                therefore_c += 1
            elif cls.BUT_WORDS.search(s2_text):
                but_c += 1
            else:
                and_then_c += 1
                flagged.append(f"Transition between Scene {i+1} ('{s1.heading}') and Scene {i+2} ('{s2.heading}') reads as episodic 'AND THEN'. Connect by causal consequence or sharp reversal.")

        ratio = (therefore_c + but_c) / n_transitions if n_transitions else 1.0

        return CausalityReport(
            total_scene_transitions=n_transitions,
            therefore_transitions=therefore_c,
            but_transitions=but_c,
            and_then_transitions=and_then_c,
            causal_velocity_ratio=round(ratio, 2),
            flagged_episodic_gaps=flagged,
        )


# --------------------------------------------------------------------------- #
# 5. Hitchcock Information Architecture & Dramatic Irony
# --------------------------------------------------------------------------- #

class InformationState(str, Enum):
    DRAMATIC_IRONY = "DRAMATIC_IRONY"  # Audience knows more -> Pure Suspense
    SURPRISE = "SURPRISE"              # Audience and character discover together
    MYSTERY = "MYSTERY"                # Audience knows less -> Puzzle solving


@dataclass
class SceneIronyProfile:
    scene_id: str
    primary_state: InformationState
    audience_secret: str
    tension_rating: float  # 0.0 to 1.0
    rationale: str


class DramaticIronyMapper:
    """Classifies scene suspense architecture to ensure dramatic irony dominance."""

    @classmethod
    def evaluate_scene(cls, scene: Scene, audience_secret: str = "") -> SceneIronyProfile:
        full_text = " ".join(node.content for node in scene.nodes)

        # Detect indicators of dramatic irony (secret actions, concealed weapons, traps)
        has_secret_action = bool(re.search(r"\b(conceals|hides|watches unseen|behind the door|poison|under the table|shadow)\b", full_text, re.I))
        has_investigation = bool(re.search(r"\b(clue|who did it|fingerprint|mystery|search|investigate)\b", full_text, re.I))

        if audience_secret or has_secret_action:
            state = InformationState.DRAMATIC_IRONY
            tension = 0.85
            rationale = "Audience holds privileged knowledge of threat or trap while characters converse unsuspectingly."
        elif has_investigation:
            state = InformationState.MYSTERY
            tension = 0.50
            rationale = "Audience shares character ignorance, deducing truth alongside protagonist."
        else:
            state = InformationState.SURPRISE
            tension = 0.60
            rationale = "Threat or revelation unfolds in lockstep for audience and characters."

        return SceneIronyProfile(
            scene_id=scene.scene_id,
            primary_state=state,
            audience_secret=audience_secret or ("Concealed threat present" if has_secret_action else "None"),
            tension_rating=tension,
            rationale=rationale,
        )


# --------------------------------------------------------------------------- #
# 6. 4-Stage Narrative Recursion Tracer (Recurse Standard)
# --------------------------------------------------------------------------- #

@dataclass
class RecursiveMotif:
    motif_name: str
    setup: str
    first_echo: str
    inversion: str
    final_payoff: str
    is_complete: bool
    score: int  # 0 to 10


class RecurseTracer:
    """Audits 4-stage recursive narrative payoff chains across the screenplay."""

    @classmethod
    def audit_motif(cls, name: str, setup: str, echo: str, inversion: str, payoff: str) -> RecursiveMotif:
        stages = [bool(s.strip()) for s in (setup, echo, inversion, payoff)]
        complete = all(stages)
        score = sum(25 for s in stages if s) // 10

        return RecursiveMotif(
            motif_name=name,
            setup=setup,
            first_echo=echo,
            inversion=inversion,
            final_payoff=payoff,
            is_complete=complete,
            score=score,
        )


# --------------------------------------------------------------------------- #
# 7. Unified Master Craft Audit Suite
# --------------------------------------------------------------------------- #

@dataclass
class MasterCraftReport:
    total_scenes: int
    total_dialogues: int
    mamet_compliance_ratio: float      # % of scenes passing Mamet audit
    cadence_score: float               # 0 to 100 musicality
    causal_velocity_ratio: float       # % therefore/but scene transitions
    status_reversals: int              # Total power flips across dialogue
    overall_craft_index: float         # 0.0 to 100.0 composite index
    critical_notes: list[str]          # Actionable director/writer punch-list


class MasterCraftSuite:
    """Top 0.001% Comprehensive Screenwriting Evaluation Suite."""

    @classmethod
    def audit(cls, screenplay: Screenplay) -> MasterCraftReport:
        scenes = screenplay.scenes
        dialogues = screenplay.dialogue_lines

        # 1. Mamet Audit
        mamet_results = [MametAuditor.audit_scene(s) for s in scenes]
        passing_mamet = sum(1 for m in mamet_results if m.is_dramatic_propulsion)
        mamet_ratio = passing_mamet / len(scenes) if scenes else 1.0

        # 2. Cadence Audit
        cadence = CadenceAnalyzer.analyze(dialogues)

        # 3. Causality Audit
        causality = CausalityValidator.evaluate_screenplay(screenplay)

        # 4. Status Tracking
        status = StatusTracker.analyze_dialogues(dialogues)

        # Composite Craft Index Calculation:
        # Mamet: 30%, Cadence: 30%, Causality: 25%, Status Reversals: 15%
        reversal_score = min(15.0, status.reversals_detected * 5.0)
        composite = (
            (mamet_ratio * 30.0) +
            (cadence.musicality_score * 0.30) +
            (causality.causal_velocity_ratio * 25.0) +
            reversal_score
        )
        composite = round(max(0.0, min(100.0, composite)), 1)

        # Critical Punch-List
        notes: list[str] = []
        if mamet_ratio < 0.80:
            notes.append(f"MAMET ALERT: Only {int(mamet_ratio*100)}% of scenes have clear objective + stakes + urgency. Polish the exposition scenes into conflict engines.")
        if cadence.monotone_penalty > 10.0:
            notes.append("CADENCE ALERT: Monotonous rhythm detected in dialogue turns. Inject staccato interruptions or expansive legato beats.")
        if causality.causal_velocity_ratio < 0.75:
            notes.append(f"CAUSALITY ALERT: {len(causality.flagged_episodic_gaps)} transitions read as episodic 'AND THEN'. Re-link using direct causal consequence (THEREFORE) or reversal (BUT).")
        if status.reversals_detected == 0 and len(dialogues) >= 10:
            notes.append("STATUS ALERT: Zero power reversals detected in dialogue. Power remains static. Give subordinate characters leverage to seize room control.")

        return MasterCraftReport(
            total_scenes=len(scenes),
            total_dialogues=len(dialogues),
            mamet_compliance_ratio=round(mamet_ratio, 2),
            cadence_score=cadence.musicality_score,
            causal_velocity_ratio=causality.causal_velocity_ratio,
            status_reversals=status.reversals_detected,
            overall_craft_index=composite,
            critical_notes=notes,
        )
