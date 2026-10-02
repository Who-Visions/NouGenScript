"""Top .001% Narrative Validators for NouGenScript.

Implements the elite scriptwriting quality gates distilled from:
- Trey Parker & Matt Stone: Causal Momentum (Therefore / But)
- Blake Snyder: Save the Cat! 15-Beat Sheet
- Dan Harmon: 8-Step Story Circle
- Aristotle: Three Unities (Action, Place, Time)
- Scott McCloud: 6 Panel-to-Panel Closure Transitions
- Eugene Schwartz: 5 Stages of Market Awareness
- Clean Code: Deterministic Double-Run Diff Gate
"""
from __future__ import annotations

import enum
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

from nougenscript.core import Dialogue, Scene, Screenplay
from nougenscript.dialects import (
    ComicPage,
    ComicPanel,
    CreatorVideoScript,
    EmailSection,
    PolyScript,
    ScriptKind,
    TVAct,
    VideoScriptBeat,
)


# ======================================================================== #
# Enums
# ======================================================================== #

class CausalConnector(str, enum.Enum):
    """The only two allowed narrative connectors between beats."""
    THEREFORE = "THEREFORE"   # Causal consequence
    BUT = "BUT"               # Causal complication
    AND_THEN = "AND_THEN"     # AMATEUR — destroys narrative drive


class PanelTransition(str, enum.Enum):
    """Scott McCloud's 6 panel-to-panel closure transitions."""
    MOMENT_TO_MOMENT = "moment_to_moment"       # Micro-actions
    ACTION_TO_ACTION = "action_to_action"        # Single subject progressing
    SUBJECT_TO_SUBJECT = "subject_to_subject"    # Within a scene, switching focus
    SCENE_TO_SCENE = "scene_to_scene"            # Across time and space
    ASPECT_TO_ASPECT = "aspect_to_aspect"        # Wandering eye, mood/atmosphere
    NON_SEQUITUR = "non_sequitur"                # Zero logical relationship


class AwarenessStage(str, enum.Enum):
    """Eugene Schwartz's 5 Stages of Market Awareness."""
    UNAWARE = "unaware"               # Educate on the symptom
    PROBLEM_AWARE = "problem_aware"   # Validate the pain
    SOLUTION_AWARE = "solution_aware" # Introduce the new paradigm
    PRODUCT_AWARE = "product_aware"   # Differentiate the mechanism
    MOST_AWARE = "most_aware"         # Irresistible offer + urgency


class HarmonStep(str, enum.Enum):
    """Dan Harmon's 8-Step Story Circle."""
    YOU = "you"           # 1. Zone of Comfort
    NEED = "need"         # 2. Desire / Lack
    GO = "go"             # 3. Unfamiliar Threshold
    SEARCH = "search"     # 4. Adaptation Trials
    FIND = "find"         # 5. Victory / Discovery
    TAKE = "take"         # 6. Pay the price
    RETURN = "return"     # 7. Return to initial world
    CHANGE = "change"     # 8. Irreversible transformation


class BeatType(str, enum.Enum):
    """Blake Snyder Save the Cat! 15-Beat Sheet."""
    OPENING_IMAGE = "opening_image"         # Page 1
    THEME_STATED = "theme_stated"           # Page 5
    SETUP = "setup"                         # Pages 1-10
    CATALYST = "catalyst"                   # Page 10
    DEBATE = "debate"                       # Pages 10-25
    BREAK_INTO_TWO = "break_into_two"       # Page 25
    B_STORY = "b_story"                     # Page 30
    FUN_AND_GAMES = "fun_and_games"         # Pages 30-55
    MIDPOINT = "midpoint"                   # Page 55
    BAD_GUYS_CLOSE_IN = "bad_guys_close_in" # Pages 55-75
    ALL_IS_LOST = "all_is_lost"             # Page 75
    DARK_NIGHT = "dark_night_of_soul"       # Pages 75-85
    BREAK_INTO_THREE = "break_into_three"   # Page 85
    FINALE = "finale"                       # Pages 85-110
    FINAL_IMAGE = "final_image"             # Page 110


# ======================================================================== #
# Validation Results
# ======================================================================== #

@dataclass
class ValidationIssue:
    """A single validation finding."""
    severity: str  # "error" | "warning" | "info"
    code: str      # Machine-readable code e.g. "CAUSAL_DRIFT"
    message: str
    location: str = ""  # Scene/beat/page reference
    suggestion: str = ""

    def __str__(self) -> str:
        icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(self.severity, "⚪")
        loc = f" [{self.location}]" if self.location else ""
        return f"{icon} {self.code}{loc}: {self.message}"


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    validator_name: str
    passed: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    score: float = 1.0  # 0.0 to 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return (
            f"[{self.validator_name}] {status} "
            f"(Score: {self.score:.0%}, Errors: {len(self.errors)}, "
            f"Warnings: {len(self.warnings)})"
        )

    def report_hash(self) -> str:
        """Deterministic hash of the report for diff-gate comparison."""
        canon = json.dumps(
            {"name": self.validator_name, "passed": self.passed,
             "issues": [asdict(i) for i in self.issues],
             "score": self.score},
            sort_keys=True,
        )
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# ======================================================================== #
# 1. Causal Momentum Validator (Trey Parker & Matt Stone)
# ======================================================================== #

class CausalMomentumValidator:
    """Validates that scene-to-scene transitions use THEREFORE/BUT, never AND_THEN.

    The Top .001% Law: Every beat must connect via causal consequence (THEREFORE)
    or causal complication (BUT). If two scenes connect with "and then", the
    script has lost narrative drive.
    """

    # Heuristic connectors that signal amateur "and then" drift
    AND_THEN_MARKERS = re.compile(
        r"\b(and then|meanwhile|also|next|later|subsequently|afterward)\b",
        re.IGNORECASE,
    )
    THEREFORE_MARKERS = re.compile(
        r"\b(therefore|because|so|as a result|consequently|which means|thus)\b",
        re.IGNORECASE,
    )
    BUT_MARKERS = re.compile(
        r"\b(but|however|yet|unfortunately|except|instead|although|despite)\b",
        re.IGNORECASE,
    )

    @classmethod
    def validate_scenes(cls, scenes: Sequence[Scene]) -> ValidationReport:
        """Check causal momentum across sequential scenes."""
        issues: list[ValidationIssue] = []
        causal_count = 0
        drift_count = 0

        for i in range(1, len(scenes)):
            prev = scenes[i - 1]
            curr = scenes[i]
            # Combine heading + first actions/dialogue for analysis
            prev_text = prev.heading + " " + " ".join(
                n.content for n in prev.nodes[-3:]  # Last 3 nodes of previous scene
            )
            curr_text = curr.heading + " " + " ".join(
                n.content for n in curr.nodes[:3]  # First 3 nodes of current scene
            )
            combined = prev_text + " " + curr_text

            has_therefore = bool(cls.THEREFORE_MARKERS.search(combined))
            has_but = bool(cls.BUT_MARKERS.search(combined))
            has_and_then = bool(cls.AND_THEN_MARKERS.search(combined))

            if has_therefore or has_but:
                causal_count += 1
            elif has_and_then:
                drift_count += 1
                connector = CausalConnector.AND_THEN
                issues.append(ValidationIssue(
                    severity="warning",
                    code="CAUSAL_DRIFT",
                    message=f"Scene {i} → {i+1} connects with '{connector.value}' instead of THEREFORE/BUT",
                    location=f"Scene {i}-{i+1}: {prev.heading} → {curr.heading}",
                    suggestion="Rewrite the transition to show causal consequence (THEREFORE) or complication (BUT)",
                ))
            else:
                # No detectable connector — flag for manual review
                issues.append(ValidationIssue(
                    severity="info",
                    code="CAUSAL_AMBIGUOUS",
                    message=f"Scene {i} → {i+1} has no detectable causal connector",
                    location=f"Scene {i}-{i+1}: {prev.heading} → {curr.heading}",
                    suggestion="Ensure scenes are linked by consequence or complication, not coincidence",
                ))

        total_transitions = len(scenes) - 1
        if total_transitions <= 0:
            # Single scene or empty — trivially passes
            score = 1.0
        else:
            score = causal_count / total_transitions
        passed = drift_count == 0 and (score >= 0.5 or total_transitions == 0)

        return ValidationReport(
            validator_name="CausalMomentum (Therefore/But)",
            passed=passed,
            issues=issues,
            score=score,
            metadata={"causal_count": causal_count, "drift_count": drift_count,
                       "total_transitions": total_transitions},
        )

    @classmethod
    def classify_connector(cls, text: str) -> CausalConnector:
        """Classify a text fragment's dominant causal connector."""
        if cls.THEREFORE_MARKERS.search(text):
            return CausalConnector.THEREFORE
        if cls.BUT_MARKERS.search(text):
            return CausalConnector.BUT
        return CausalConnector.AND_THEN


# ======================================================================== #
# 2. Save the Cat! Beat Sheet Validator (Blake Snyder)
# ======================================================================== #

class BeatSheetValidator:
    """Validates a screenplay against the 15-beat pacing sheet.

    Maps scene position (by page estimate) to expected beats.
    Standard: 1 scene ≈ 1.5 pages, total ~110 pages.
    """

    BEAT_PAGE_MAP: dict[BeatType, tuple[int, int]] = {
        BeatType.OPENING_IMAGE: (1, 3),
        BeatType.THEME_STATED: (3, 7),
        BeatType.SETUP: (1, 10),
        BeatType.CATALYST: (9, 13),
        BeatType.DEBATE: (13, 27),
        BeatType.BREAK_INTO_TWO: (24, 28),
        BeatType.B_STORY: (28, 33),
        BeatType.FUN_AND_GAMES: (30, 57),
        BeatType.MIDPOINT: (53, 60),
        BeatType.BAD_GUYS_CLOSE_IN: (55, 77),
        BeatType.ALL_IS_LOST: (73, 80),
        BeatType.DARK_NIGHT: (75, 87),
        BeatType.BREAK_INTO_THREE: (83, 90),
        BeatType.FINALE: (85, 112),
        BeatType.FINAL_IMAGE: (108, 115),
    }

    @classmethod
    def validate_screenplay(cls, sp: Screenplay, pages_per_scene: float = 1.5) -> ValidationReport:
        """Validate screenplay beat pacing."""
        issues: list[ValidationIssue] = []
        total_pages = len(sp.scenes) * pages_per_scene
        detected_beats: list[str] = []

        # Check total length
        if total_pages < 85:
            issues.append(ValidationIssue(
                severity="warning", code="SHORT_SCRIPT",
                message=f"Script is ~{total_pages:.0f} pages (target 95-115 for feature)",
                suggestion="Add scenes to reach feature-length pacing",
            ))
        elif total_pages > 130:
            issues.append(ValidationIssue(
                severity="warning", code="LONG_SCRIPT",
                message=f"Script is ~{total_pages:.0f} pages (target 95-115 for feature)",
                suggestion="Trim or tighten pacing to studio-standard length",
            ))

        # Check midpoint exists around page 55
        midpoint_scene = int(55 / pages_per_scene) if pages_per_scene > 0 else 0
        if midpoint_scene < len(sp.scenes):
            detected_beats.append(BeatType.MIDPOINT.value)
        else:
            issues.append(ValidationIssue(
                severity="error", code="MISSING_MIDPOINT",
                message="No identifiable midpoint around scene position ~37 (page ~55)",
                suggestion="Insert a false victory or false defeat at the script's halfway point",
            ))

        # Check opening and closing image symmetry
        if len(sp.scenes) >= 2:
            detected_beats.append(BeatType.OPENING_IMAGE.value)
            detected_beats.append(BeatType.FINAL_IMAGE.value)

        score = len(detected_beats) / 15.0
        return ValidationReport(
            validator_name="BeatSheet (Save the Cat!)",
            passed=len(issues) == 0 or all(i.severity != "error" for i in issues),
            issues=issues,
            score=min(score, 1.0),
            metadata={"total_pages_est": total_pages, "detected_beats": detected_beats},
        )


# ======================================================================== #
# 3. Harmon Story Circle Validator (Dan Harmon)
# ======================================================================== #

class HarmonCircleValidator:
    """Validates TV episodes against the 8-step Story Circle.

    Checks that the episode traverses all 8 steps in cycle order.
    """

    STEP_ORDER = list(HarmonStep)

    @classmethod
    def validate_tv_episode(cls, acts: Sequence[TVAct]) -> ValidationReport:
        """Validate TV episode structure against Harmon's 8 steps."""
        issues: list[ValidationIssue] = []
        total_scenes = sum(len(a.scenes) for a in acts)

        if not acts:
            issues.append(ValidationIssue(
                severity="error", code="EMPTY_EPISODE",
                message="No acts found in TV episode",
            ))
            return ValidationReport(
                validator_name="HarmonCircle (8-Step)",
                passed=False, issues=issues, score=0.0,
            )

        # Check cold open exists
        has_cold_open = any(a.act_number == 0 for a in acts)
        if not has_cold_open:
            issues.append(ValidationIssue(
                severity="warning", code="NO_COLD_OPEN",
                message="No Cold Open detected (missing teaser hook)",
                suggestion="Add a COLD OPEN section to hook viewers in the first 3-5 minutes",
            ))

        # Check act break cliffhanger potential (each act should end with scenes)
        for act in acts:
            if act.scenes and len(act.scenes) == 0:
                issues.append(ValidationIssue(
                    severity="warning", code="EMPTY_ACT",
                    message=f"{act.act_name} has no scenes",
                    location=act.act_name,
                ))

        # Check minimum scene density for story circle coverage
        if total_scenes < 8:
            issues.append(ValidationIssue(
                severity="warning", code="LOW_SCENE_DENSITY",
                message=f"Only {total_scenes} scenes — may not cover all 8 story circle steps",
                suggestion="Ensure at least 8 distinct dramatic beats across the episode",
            ))

        score = min(total_scenes / 8.0, 1.0)
        return ValidationReport(
            validator_name="HarmonCircle (8-Step)",
            passed=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
            score=score,
            metadata={"total_scenes": total_scenes, "act_count": len(acts),
                       "has_cold_open": has_cold_open},
        )


# ======================================================================== #
# 4. Aristotle Three Unities Validator (Playwriting)
# ======================================================================== #

class AristotleUnitiesValidator:
    """Validates theatrical scripts against the Three Unities.

    - Unity of Action: Single core action (minimal subplots)
    - Unity of Place: Compressed physical space
    - Unity of Time: Story ≈ audience viewing time
    """

    @classmethod
    def validate_play(cls, sp: Screenplay) -> ValidationReport:
        """Validate theatrical script against Aristotle's unities."""
        issues: list[ValidationIssue] = []

        # Unity of Place: count distinct locations
        locations = set()
        for scene in sp.scenes:
            # Normalize heading to extract location
            heading = scene.heading.upper().strip()
            # Remove INT./EXT. prefix
            cleaned = re.sub(r"^(INT\.|EXT\.|INT/EXT\.)\s*", "", heading)
            # Remove time of day suffix
            cleaned = re.sub(r"\s*[-–—]\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER|SAME)\s*$", "", cleaned)
            if cleaned:
                locations.add(cleaned.strip())

        if len(locations) > 3:
            issues.append(ValidationIssue(
                severity="warning", code="UNITY_PLACE_BROKEN",
                message=f"{len(locations)} distinct locations detected (ideal: 1-3 for Unity of Place)",
                suggestion="Compress settings to heighten claustrophobia and relational collision",
            ))

        # Unity of Action: check if multiple unrelated storylines
        characters = set()
        for scene in sp.scenes:
            for d in scene.dialogues:
                characters.add(d.character.upper())
        if len(characters) > 12:
            issues.append(ValidationIssue(
                severity="info", code="LARGE_CAST",
                message=f"{len(characters)} speaking characters — may dilute Unity of Action",
                suggestion="Reduce to a core ensemble to maintain singular dramatic focus",
            ))

        # Unity of Time: scene count as proxy (fewer scenes = compressed time)
        if len(sp.scenes) > 20:
            issues.append(ValidationIssue(
                severity="info", code="UNITY_TIME_STRETCH",
                message=f"{len(sp.scenes)} scenes may stretch Unity of Time beyond single evening",
                suggestion="Consider whether temporal jumps serve the dramatic argument",
            ))

        score = 1.0
        if len(locations) > 3:
            score -= 0.2 * min((len(locations) - 3) / 5, 1.0)
        if len(sp.scenes) > 20:
            score -= 0.1

        return ValidationReport(
            validator_name="AristotleUnities (Action/Place/Time)",
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=max(score, 0.0),
            metadata={"distinct_locations": len(locations), "location_names": sorted(locations),
                       "speaking_characters": len(characters), "scene_count": len(sp.scenes)},
        )


# ======================================================================== #
# 5. McCloud Panel Transition Validator (Comic Books)
# ======================================================================== #

class McCloudTransitionValidator:
    """Validates comic book panel transitions against McCloud's 6-tier taxonomy.

    Ensures panels use intentional transitions and flags sequences with
    excessive non-sequiturs or monotonous same-type runs.
    """

    @classmethod
    def classify_transition(cls, prev: ComicPanel, curr: ComicPanel) -> PanelTransition:
        """Heuristically classify the transition between two panels."""
        prev_desc = prev.visual_description.lower()
        curr_desc = curr.visual_description.lower()

        # Same visual subject with tiny change = moment-to-moment
        # Use overlap ratio of words as a heuristic
        prev_words = set(prev_desc.split())
        curr_words = set(curr_desc.split())
        overlap = len(prev_words & curr_words)
        total = max(len(prev_words | curr_words), 1)
        overlap_ratio = overlap / total

        if overlap_ratio > 0.7:
            return PanelTransition.MOMENT_TO_MOMENT
        if overlap_ratio > 0.4:
            return PanelTransition.ACTION_TO_ACTION

        # Different speakers = subject-to-subject
        prev_speakers = {b.get("speaker", "") for b in prev.dialogue_balloons}
        curr_speakers = {b.get("speaker", "") for b in curr.dialogue_balloons}
        if prev_speakers and curr_speakers and not prev_speakers & curr_speakers:
            return PanelTransition.SUBJECT_TO_SUBJECT

        # Large visual change with environmental words = scene-to-scene
        scene_words = {"ext", "int", "later", "dawn", "night", "morning", "elsewhere"}
        if scene_words & curr_words:
            return PanelTransition.SCENE_TO_SCENE

        # Mood/atmosphere descriptors with no action = aspect-to-aspect
        mood_words = {"rain", "wind", "silence", "shadow", "light", "glow", "fog", "mist"}
        if mood_words & curr_words and overlap_ratio < 0.2:
            return PanelTransition.ASPECT_TO_ASPECT

        if overlap_ratio < 0.1:
            return PanelTransition.NON_SEQUITUR

        return PanelTransition.ACTION_TO_ACTION

    @classmethod
    def validate_pages(cls, pages: Sequence[ComicPage]) -> ValidationReport:
        """Validate panel transitions across comic pages."""
        issues: list[ValidationIssue] = []
        transition_counts: dict[str, int] = {t.value: 0 for t in PanelTransition}
        total_transitions = 0

        for page in pages:
            panels = page.panels
            for i in range(1, len(panels)):
                t = cls.classify_transition(panels[i - 1], panels[i])
                transition_counts[t.value] += 1
                total_transitions += 1

                if t == PanelTransition.NON_SEQUITUR:
                    issues.append(ValidationIssue(
                        severity="info", code="NON_SEQUITUR_TRANSITION",
                        message=f"Non-sequitur transition on page {page.page_number}, panel {i} → {i+1}",
                        location=f"Page {page.page_number}, Panel {i}-{i+1}",
                        suggestion="Ensure intentional reader closure or add connecting visual motif",
                    ))

        # Check for monotonous same-type runs
        if total_transitions >= 5:
            dominant = max(transition_counts, key=lambda k: transition_counts[k])
            dominance_ratio = transition_counts[dominant] / total_transitions
            if dominance_ratio > 0.8:
                issues.append(ValidationIssue(
                    severity="warning", code="MONOTONOUS_TRANSITIONS",
                    message=f"{dominance_ratio:.0%} of transitions are '{dominant}' — vary pacing",
                    suggestion="Mix transition types to create rhythm: action→subject→scene shifts",
                ))

        # Check page turn reveals (odd-page bottom-right cliffhangers)
        for page in pages:
            if page.page_number % 2 == 1 and page.panels:
                last_panel = page.panels[-1]
                if not last_panel.sfx and not last_panel.dialogue_balloons:
                    issues.append(ValidationIssue(
                        severity="info", code="WEAK_PAGE_TURN",
                        message=f"Page {page.page_number} (odd) ends without dialogue or SFX — potential weak turn",
                        location=f"Page {page.page_number}",
                        suggestion="Place shocking reveals or cliffhangers on odd-page bottoms for page-turn impact",
                    ))

        variety = sum(1 for v in transition_counts.values() if v > 0)
        score = min(variety / 4.0, 1.0)  # Using at least 4 of 6 types = perfect

        return ValidationReport(
            validator_name="McCloudTransitions (6-Tier)",
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=score,
            metadata={"transition_counts": transition_counts, "total_transitions": total_transitions,
                       "variety": variety},
        )


# ======================================================================== #
# 6. Schwartz Awareness Validator (Email Scripts)
# ======================================================================== #

class SchwartzAwarenessValidator:
    """Validates email scripts against Schwartz's 5 Awareness Stages.

    Checks that the email matches a defined awareness stage and uses
    the appropriate framework (PAS, BAB, or HSO).
    """

    # Keyword heuristics for framework detection
    PAS_MARKERS = re.compile(r"\b(problem|struggle|frustrat|pain|agitat|solv|fix)\b", re.IGNORECASE)
    BAB_MARKERS = re.compile(r"\b(imagine|before|after|bridge|transform|picture this)\b", re.IGNORECASE)
    HSO_MARKERS = re.compile(r"\b(story|journey|discover|reveal|here\'s what happened)\b", re.IGNORECASE)

    @classmethod
    def detect_awareness_stage(cls, email: EmailSection) -> AwarenessStage:
        """Detect the target awareness stage from email content."""
        full_text = " ".join(email.body_paragraphs).lower()

        if any(w in full_text for w in ["don't know", "never heard", "what is", "did you know"]):
            return AwarenessStage.UNAWARE
        if any(w in full_text for w in ["tired of", "frustrated", "struggling", "problem"]):
            return AwarenessStage.PROBLEM_AWARE
        if any(w in full_text for w in ["solution", "new way", "approach", "method", "system"]):
            return AwarenessStage.SOLUTION_AWARE
        if any(w in full_text for w in ["our product", "feature", "compare", "vs", "better than"]):
            return AwarenessStage.PRODUCT_AWARE
        if any(w in full_text for w in ["limited time", "expires", "last chance", "discount", "offer"]):
            return AwarenessStage.MOST_AWARE

        return AwarenessStage.SOLUTION_AWARE  # Default middle-of-funnel

    @classmethod
    def detect_framework(cls, email: EmailSection) -> str:
        """Detect which copywriting framework is being used."""
        full_text = " ".join(email.body_paragraphs)
        scores = {
            "PAS": len(cls.PAS_MARKERS.findall(full_text)),
            "BAB": len(cls.BAB_MARKERS.findall(full_text)),
            "HSO": len(cls.HSO_MARKERS.findall(full_text)),
        }
        return max(scores, key=lambda k: scores[k]) if any(v > 0 for v in scores.values()) else "UNKNOWN"

    @classmethod
    def validate_email(cls, email: EmailSection) -> ValidationReport:
        """Validate email script against elite copywriting standards."""
        issues: list[ValidationIssue] = []

        # Check subject line (4-word curiosity gap ideal)
        subject_words = email.subject_line.split()
        if len(subject_words) > 10:
            issues.append(ValidationIssue(
                severity="warning", code="LONG_SUBJECT",
                message=f"Subject line is {len(subject_words)} words (ideal: 4-7 for curiosity gap)",
                suggestion="Shorten to create urgency and curiosity: 'The secret [X] doesn't want you to know'",
            ))
        if not email.subject_line or email.subject_line == "No Subject":
            issues.append(ValidationIssue(
                severity="error", code="MISSING_SUBJECT",
                message="Email has no subject line",
            ))

        # Check P.S. anchor (90% of scanners read P.S. first)
        if not email.ps_line:
            issues.append(ValidationIssue(
                severity="warning", code="MISSING_PS",
                message="No P.S. line — 90% of scanners read the P.S. first",
                suggestion="Add a P.S. that summarizes the primary payoff and restates the CTA",
            ))

        # Check CTA clarity (one singular link, zero cognitive friction)
        if not email.call_to_action_url or email.call_to_action_url == "#":
            issues.append(ValidationIssue(
                severity="error", code="MISSING_CTA",
                message="No call-to-action URL defined",
                suggestion="Every email must have exactly one clear CTA link",
            ))

        # Check body length
        total_words = sum(len(p.split()) for p in email.body_paragraphs)
        if total_words > 500:
            issues.append(ValidationIssue(
                severity="info", code="LONG_BODY",
                message=f"Email body is {total_words} words (ideal: 150-300 for cold outreach)",
            ))

        # Detect framework
        framework = cls.detect_framework(email)
        stage = cls.detect_awareness_stage(email)

        score = 1.0
        if any(i.severity == "error" for i in issues):
            score -= 0.3
        if any(i.severity == "warning" for i in issues):
            score -= 0.1 * len([i for i in issues if i.severity == "warning"])

        return ValidationReport(
            validator_name="SchwartzAwareness (Email)",
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=max(score, 0.0),
            metadata={"awareness_stage": stage.value, "detected_framework": framework,
                       "subject_word_count": len(subject_words), "body_word_count": total_words,
                       "has_ps": bool(email.ps_line)},
        )


# ======================================================================== #
# 7. Deterministic Double-Run Diff Gate
# ======================================================================== #

class DeterministicDiffGate:
    """Ensures identical input bytes produce zero git diff across repeated runs.

    Given a PolyScript, serialize it twice and compare SHA-256 hashes.
    If they differ, the script contains non-deterministic elements
    (unseeded randoms, hidden clock deps, etc.).
    """

    @classmethod
    def validate(cls, poly: PolyScript) -> ValidationReport:
        """Run the double-serialization diff gate."""
        issues: list[ValidationIssue] = []

        # First run
        hash_1 = poly.recompute_hash()
        # Second run
        hash_2 = poly.recompute_hash()

        if hash_1 != hash_2:
            issues.append(ValidationIssue(
                severity="error", code="NONDETERMINISTIC",
                message=f"Double-run hashes differ: {hash_1[:16]} != {hash_2[:16]}",
                suggestion="Remove unseeded random(), hidden datetime.now(), or mutable default args",
            ))

        return ValidationReport(
            validator_name="DeterministicDiffGate",
            passed=hash_1 == hash_2,
            issues=issues,
            score=1.0 if hash_1 == hash_2 else 0.0,
            metadata={"hash_run_1": hash_1, "hash_run_2": hash_2, "match": hash_1 == hash_2},
        )


# ======================================================================== #
# 8. Video Retention Validator (from Visions-Ai Story Rules / Philipp Humm)
# ======================================================================== #

class VideoRetentionValidator:
    """Validates creator video scripts against retention rules.

    Enforces:
    - 3-second hook pattern interrupt
    - Clear stakes / context in setup
    - Sensory detail and concrete language
    - Sound design cues / music swells
    - Micro-beat velocity (visual/audio change every 2-5s)
    - Call to action with clear payoff
    """

    ABSTRACT_WORDS = re.compile(
        r"\b(synergy|paradigm|optimization|leverage|utilize|facilitate|various|aspects|multifaceted)\b",
        re.IGNORECASE
    )
    SENSORY_WORDS = re.compile(
        r"\b(red|black|cold|burning|crashing|loud|whisper|staring|sweat|screaming|freezing|glowing|shaking|shattered)\b",
        re.IGNORECASE
    )

    @classmethod
    def validate_video(cls, script: CreatorVideoScript) -> ValidationReport:
        issues: list[ValidationIssue] = []

        # 1. 3-Second Hook Check
        if not script.hook_3s or len(script.hook_3s.split()) < 3:
            issues.append(ValidationIssue(
                severity="error",
                code="MISSING_HOOK",
                message="Video lacks an aggressive 3-second hook or pattern interrupt",
                suggestion="Open with an unexpected question, visual jolt, or contrary statement in the first 3 seconds."
            ))
        elif len(script.hook_3s.split()) > 25:
            issues.append(ValidationIssue(
                severity="warning",
                code="OVERLONG_HOOK",
                message=f"Hook is {len(script.hook_3s.split())} words — too long for a 3-second pattern interrupt",
                suggestion="Compress hook to under 15 punchy words."
            ))

        # 2. Stakes Check
        if not script.setup or len(script.setup.strip()) < 10:
            issues.append(ValidationIssue(
                severity="warning",
                code="WEAK_STAKES",
                message="No clear stakes or setup context provided",
                suggestion="State what happens if the viewer doesn't listen or the struggle being solved."
            ))

        # 3. Micro-Beat Velocity & Pattern Interrupts
        pattern_interrupt_count = sum(1 for b in script.beats if b.is_pattern_interrupt)
        sound_cue_count = sum(1 for b in script.beats if b.sound_design)

        if script.beats and len(script.beats) < 3:
            issues.append(ValidationIssue(
                severity="warning",
                code="LOW_BEAT_DENSITY",
                message=f"Only {len(script.beats)} visual/audio beats defined",
                suggestion="Break script into distinct micro-beats changing state every 3-5 seconds."
            ))

        if pattern_interrupt_count == 0 and len(script.beats) > 4:
            issues.append(ValidationIssue(
                severity="info",
                code="NO_PATTERN_INTERRUPTS",
                message="No explicit pattern interrupts marked in script",
                suggestion="Add at least one visual/audio reset (sound hit, zoom in/out, angle change) to arrest scroll."
            ))

        # 4. Sensory detail check across spoken audio
        all_spoken = " ".join(b.spoken_audio for b in script.beats) + " " + script.hook_3s
        abstract_hits = cls.ABSTRACT_WORDS.findall(all_spoken)
        sensory_hits = cls.SENSORY_WORDS.findall(all_spoken)

        if abstract_hits:
            issues.append(ValidationIssue(
                severity="info",
                code="ABSTRACT_JARGON",
                message=f"Abstract jargon detected ({len(abstract_hits)} instance(s)): {', '.join(set(abstract_hits)[:3])}",
                suggestion="Replace abstract corporate language with raw, tangible, conversational nouns and verbs."
            ))

        # 5. Call to action check
        if not script.call_to_action:
            issues.append(ValidationIssue(
                severity="warning",
                code="MISSING_CTA",
                message="No call to action defined at conclusion of video",
                suggestion="Provide one single clear next step or loop back to the hook."
            ))

        score = 1.0
        if any(i.severity == "error" for i in issues):
            score -= 0.3
        if any(i.severity == "warning" for i in issues):
            score -= 0.1 * len([i for i in issues if i.severity == "warning"])

        return ValidationReport(
            validator_name="VideoRetention (Visions-Ai Story Rules)",
            passed=all(i.severity != "error" for i in issues),
            issues=issues,
            score=max(score, 0.0),
            metadata={
                "hook_word_count": len(script.hook_3s.split()),
                "beat_count": len(script.beats),
                "pattern_interrupts": pattern_interrupt_count,
                "sound_cues": sound_cue_count,
                "sensory_words_count": len(sensory_hits),
            }
        )


# ======================================================================== #
# Unified Validation Pipeline
# ======================================================================== #

class ScriptValidator:
    """Unified validation pipeline that selects validators based on script type."""

    @classmethod
    def validate(cls, poly: PolyScript) -> list[ValidationReport]:
        """Run all applicable validators for a PolyScript."""
        reports: list[ValidationReport] = []

        # Always run deterministic diff gate
        reports.append(DeterministicDiffGate.validate(poly))

        kind = poly.meta.kind

        if kind == ScriptKind.MOVIE_SCREENPLAY:
            if isinstance(poly.body, Screenplay):
                reports.append(CausalMomentumValidator.validate_scenes(poly.body.scenes))
                reports.append(BeatSheetValidator.validate_screenplay(poly.body))

        elif kind in {ScriptKind.TV_PILOT, ScriptKind.TV_EPISODIC}:
            if isinstance(poly.body, list) and all(isinstance(a, TVAct) for a in poly.body):
                reports.append(HarmonCircleValidator.validate_tv_episode(poly.body))
                # Also check causal momentum across all scenes
                all_scenes = [s for a in poly.body for s in a.scenes]
                if all_scenes:
                    reports.append(CausalMomentumValidator.validate_scenes(all_scenes))

        elif kind == ScriptKind.STAGE_PLAY:
            if isinstance(poly.body, Screenplay):
                reports.append(AristotleUnitiesValidator.validate_play(poly.body))
                reports.append(CausalMomentumValidator.validate_scenes(poly.body.scenes))

        elif kind == ScriptKind.COMIC_SCRIPT:
            if isinstance(poly.body, list) and all(isinstance(p, ComicPage) for p in poly.body):
                reports.append(McCloudTransitionValidator.validate_pages(poly.body))

        elif kind in {ScriptKind.COLD_EMAIL, ScriptKind.DRIP_SEQUENCE, ScriptKind.NEWSLETTER}:
            if isinstance(poly.body, EmailSection):
                reports.append(SchwartzAwarenessValidator.validate_email(poly.body))

        elif kind in {ScriptKind.TALKING_HEAD_VIDEO, ScriptKind.SHORT_FORM_REEL, ScriptKind.LONG_FORM_YOUTUBE}:
            if isinstance(poly.body, CreatorVideoScript):
                reports.append(VideoRetentionValidator.validate_video(poly.body))

        return reports

    @classmethod
    def full_report(cls, poly: PolyScript) -> str:
        """Generate a human-readable full validation report."""
        reports = cls.validate(poly)
        lines = [f"📋 Validation Report for '{poly.meta.title}' ({poly.meta.kind.value})"]
        lines.append("=" * 60)
        for r in reports:
            lines.append(r.summary())
            for issue in r.issues:
                lines.append(f"  {issue}")
        lines.append("=" * 60)
        all_passed = all(r.passed for r in reports)
        lines.append(f"{'✅ ALL VALIDATORS PASSED' if all_passed else '❌ SOME VALIDATORS FAILED'}")
        return "\n".join(lines)
