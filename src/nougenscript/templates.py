"""Elite Scaffold Templates for NouGenScript.

Generators for world-class script frameworks:
- Save the Cat! 15-Beat Sheet scaffold
- Dan Harmon 8-Step Story Circle scaffold
- PAS / BAB / HSO email copy templates
- McCloud panel transition annotations
- Aristotle Unity-constrained play outline
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from nougenscript.validators import (
    AwarenessStage,
    BeatType,
    HarmonStep,
    PanelTransition,
)


# ======================================================================== #
# 1. Save the Cat! Beat Sheet Scaffold
# ======================================================================== #

@dataclass
class BeatEntry:
    """A single beat in the Save the Cat scaffold."""
    beat: BeatType
    page_target: str
    description: str
    scene_hint: str = ""


def generate_beat_sheet(title: str = "Untitled Feature",
                        genre: str = "Drama") -> list[BeatEntry]:
    """Generate a full Save the Cat! 15-beat scaffold."""
    author = os.getenv("NOUGEN_AUTHOR", "Anonymous Author")
    return [
        BeatEntry(BeatType.OPENING_IMAGE, "p.1",
                  f"Visual thesis of {title}'s world before change.",
                  "Establish tone, mood, and the protagonist's ordinary life."),
        BeatEntry(BeatType.THEME_STATED, "p.5",
                  "Someone (not the hero) states the theme — the movie's argument.",
                  "Often disguised as throwaway advice or offhand remark."),
        BeatEntry(BeatType.SETUP, "pp.1-10",
                  "Introduce hero, stakes, and all A-story characters.",
                  "Plant every element that pays off later. Show hero's flaws."),
        BeatEntry(BeatType.CATALYST, "p.10",
                  "The knock on the door — life will never be the same.",
                  "A phone call, meeting, package, death, or discovery."),
        BeatEntry(BeatType.DEBATE, "pp.10-25",
                  "Hero resists the call. Should I go? Can I do this?",
                  "Build internal conflict. Show why change is terrifying."),
        BeatEntry(BeatType.BREAK_INTO_TWO, "p.25",
                  "Hero makes a choice and crosses the threshold of no return.",
                  "The protagonist ACTS — not pushed. This is a decision."),
        BeatEntry(BeatType.B_STORY, "p.30",
                  "The love story, friendship, or mentor relationship begins.",
                  "This subplot carries the thematic argument to its resolution."),
        BeatEntry(BeatType.FUN_AND_GAMES, "pp.30-55",
                  f"The promise of the premise — why people bought tickets to {title}.",
                  "Deliver the genre's core pleasure. Action, comedy, romance set pieces."),
        BeatEntry(BeatType.MIDPOINT, "p.55",
                  "False victory or false defeat — stakes escalate from WANT to NEED.",
                  "The midpoint is the mirror of the ending. Raise or lower the bar."),
        BeatEntry(BeatType.BAD_GUYS_CLOSE_IN, "pp.55-75",
                  "External pressure mounts, internal team fractures, hero's flaws deepen.",
                  "Villains regroup. Allies betray or abandon. Doubt creeps in."),
        BeatEntry(BeatType.ALL_IS_LOST, "p.75",
                  "The whiff of death — death of the old ego, mentor, or hope.",
                  "Something or someone symbolically dies. Lowest point."),
        BeatEntry(BeatType.DARK_NIGHT, "pp.75-85",
                  "Hero sits in despair. Why hast thou forsaken me?",
                  "The moment before synthesis. Silence, grief, or solitude."),
        BeatEntry(BeatType.BREAK_INTO_THREE, "p.85",
                  "Eureka! Hero synthesizes A-story experience with B-story wisdom.",
                  "The solution comes from internal growth, not external luck."),
        BeatEntry(BeatType.FINALE, "pp.85-110",
                  "Hero storms the castle, executes the new plan, transforms.",
                  "Apply all lessons learned. Create new world order."),
        BeatEntry(BeatType.FINAL_IMAGE, "p.110",
                  "Opposite visual of the Opening Image — proof of transformation.",
                  f"Show that {title}'s world has irreversibly changed."),
    ]


# ======================================================================== #
# 2. Dan Harmon Story Circle Scaffold
# ======================================================================== #

@dataclass
class CircleStep:
    """A single step in the Harmon Story Circle."""
    step: HarmonStep
    position: str  # "top", "right", "bottom", "left" (clock position)
    description: str
    writing_prompt: str = ""


def generate_story_circle(protagonist: str = "HERO",
                           episode_title: str = "Untitled Episode") -> list[CircleStep]:
    """Generate a Dan Harmon 8-Step Story Circle scaffold."""
    return [
        CircleStep(HarmonStep.YOU, "12 o'clock",
                   f"{protagonist} in their zone of comfort / status quo.",
                   f"Show {protagonist}'s daily routine, relationships, and established world."),
        CircleStep(HarmonStep.NEED, "1:30",
                   f"{protagonist} discovers an urgent lack or structural imbalance.",
                   f"What does {protagonist} WANT? What's missing that they don't even know yet?"),
        CircleStep(HarmonStep.GO, "3 o'clock",
                   f"{protagonist} crosses into an unfamiliar world or situation.",
                   "The threshold is crossed. No going back without cost."),
        CircleStep(HarmonStep.SEARCH, "4:30",
                   f"{protagonist} struggles, adapts, and tests skills against chaos.",
                   "Trials, failures, small wins. The learning curve of the new world."),
        CircleStep(HarmonStep.FIND, "6 o'clock",
                   f"{protagonist} discovers or secures what they wanted.",
                   "The goal seems achieved. But at what cost? (Bottom of the circle = maximum distance from comfort)"),
        CircleStep(HarmonStep.TAKE, "7:30",
                   f"{protagonist} pays a heavy, unexpected price (the monkey's paw).",
                   "The victory has a hidden cost. Something is taken in exchange."),
        CircleStep(HarmonStep.RETURN, "9 o'clock",
                   f"{protagonist} returns to the initial world.",
                   "Back to familiar territory, but the hero is not the same person."),
        CircleStep(HarmonStep.CHANGE, "10:30",
                   f"{protagonist} has fundamentally transformed or caused irreversible change.",
                   f"Show how {protagonist}'s world and relationships are permanently altered."),
    ]


# ======================================================================== #
# 3. Email Copy Framework Templates
# ======================================================================== #

@dataclass
class EmailTemplate:
    """A structured email copy template."""
    framework: str  # "PAS" | "BAB" | "HSO"
    awareness_stage: AwarenessStage
    subject_line: str
    sections: list[dict[str, str]]
    ps_line: str
    sign_off: str = field(default_factory=lambda: os.getenv("NOUGEN_SIGN_OFF", "Best Regards"))


def generate_pas_template(topic: str = "your challenge",
                           awareness: AwarenessStage = AwarenessStage.PROBLEM_AWARE) -> EmailTemplate:
    """Generate a Problem → Agitate → Solve email template."""
    return EmailTemplate(
        framework="PAS",
        awareness_stage=awareness,
        subject_line=f"The hidden cost of {topic}",
        sections=[
            {"label": "PROBLEM", "content": f"You're dealing with {topic}. It's costing you time, money, and peace of mind."},
            {"label": "AGITATE", "content": f"Every day you wait, {topic} compounds. Your competitors aren't waiting. The gap widens."},
            {"label": "SOLVE", "content": f"There's a proven system that eliminates {topic} in 30 days. Here's how it works:"},
        ],
        ps_line=f"P.S. — The first 50 people who respond get priority access. Don't let {topic} steal another quarter.",
    )


def generate_bab_template(topic: str = "your situation",
                           awareness: AwarenessStage = AwarenessStage.SOLUTION_AWARE) -> EmailTemplate:
    """Generate a Before → After → Bridge email template."""
    return EmailTemplate(
        framework="BAB",
        awareness_stage=awareness,
        subject_line=f"Imagine if {topic} wasn't a problem",
        sections=[
            {"label": "BEFORE", "content": f"Right now, you're stuck with {topic}. The frustration is real."},
            {"label": "AFTER", "content": f"Picture this: {topic} is solved. You have clarity, momentum, and results."},
            {"label": "BRIDGE", "content": f"The bridge between where you are and where you want to be is simpler than you think:"},
        ],
        ps_line=f"P.S. — This exact method helped 200+ teams eliminate {topic}. Reply 'BRIDGE' for the full breakdown.",
    )


def generate_hso_template(topic: str = "a breakthrough",
                           awareness: AwarenessStage = AwarenessStage.UNAWARE) -> EmailTemplate:
    """Generate a Hook → Story → Offer email template."""
    return EmailTemplate(
        framework="HSO",
        awareness_stage=awareness,
        subject_line=f"How we accidentally discovered {topic}",
        sections=[
            {"label": "HOOK", "content": f"Last Tuesday at 2am, something unexpected happened with {topic}."},
            {"label": "STORY", "content": f"We'd been struggling with the same problem for months. Then one engineer asked a question nobody had considered..."},
            {"label": "OFFER", "content": f"We packaged everything we learned into a single actionable guide. It's yours — no strings attached:"},
        ],
        ps_line=f"P.S. — This guide disappears Friday. 90% of people who download it implement within 48 hours.",
    )


# ======================================================================== #
# 4. McCloud Panel Transition Annotations
# ======================================================================== #

@dataclass
class TransitionAnnotation:
    """Annotation for a panel-to-panel transition."""
    transition: PanelTransition
    from_panel: int
    to_panel: int
    page: int
    rationale: str = ""


def annotate_transitions(transitions: list[tuple[int, int, int, PanelTransition]]) -> list[TransitionAnnotation]:
    """Convert raw transition data into annotated objects.

    Each tuple: (page_num, from_panel, to_panel, transition_type)
    """
    return [
        TransitionAnnotation(
            transition=t,
            from_panel=fp,
            to_panel=tp,
            page=pg,
            rationale=_transition_rationale(t),
        )
        for pg, fp, tp, t in transitions
    ]


def _transition_rationale(t: PanelTransition) -> str:
    """Return the McCloud rationale for each transition type."""
    rationales = {
        PanelTransition.MOMENT_TO_MOMENT: "Micro-action: eyes closing, hand trembling, clock ticking. Creates cinematic slow-motion tension.",
        PanelTransition.ACTION_TO_ACTION: "Single subject progressing through distinct actions. The workhorse of Western comics — clear cause-and-effect.",
        PanelTransition.SUBJECT_TO_SUBJECT: "Staying within scene but shifting focus between characters or objects. Builds spatial awareness.",
        PanelTransition.SCENE_TO_SCENE: "Transporting across significant time/space. Requires strong reader closure to bridge the gap.",
        PanelTransition.ASPECT_TO_ASPECT: "Wandering eye bypassing time to establish mood, atmosphere, or spatial tone. Common in manga.",
        PanelTransition.NON_SEQUITUR: "Zero logical relationship between panels. Forces profound reader closure — use sparingly for avant-garde effect.",
    }
    return rationales.get(t, "")


# ======================================================================== #
# 5. Aristotle Unity Play Outline
# ======================================================================== #

@dataclass
class UnityOutline:
    """A play outline constrained by Aristotle's Three Unities."""
    title: str
    single_location: str
    time_span: str  # "one evening", "a single afternoon"
    core_action: str  # The singular dramatic question
    characters: list[str]
    act_structure: list[dict[str, str]]


def generate_unity_outline(title: str = "Untitled Play",
                            location: str = "A cramped apartment kitchen",
                            time_span: str = "one evening",
                            core_question: str = "Will the family survive the revelation?",
                            characters: list[str] | None = None) -> UnityOutline:
    """Generate a Three Unities play outline."""
    chars = characters or ["PROTAGONIST", "ANTAGONIST", "WITNESS"]
    return UnityOutline(
        title=title,
        single_location=location,
        time_span=time_span,
        core_action=core_question,
        characters=chars,
        act_structure=[
            {"act": "ACT ONE — Equilibrium",
             "description": f"Setting: {location}. Time: beginning of {time_span}. "
                            f"{chars[0]} and {chars[1]} share the space under false pretenses. "
                            "Tension simmers beneath polite conversation."},
            {"act": "ACT TWO — Eruption",
             "description": f"The truth surfaces. {core_question} "
                            "Dialogue becomes a weapon. Pinter pauses carry more weight than words. "
                            "Every entrance and exit reshapes the power dynamic."},
            {"act": "ACT THREE — Irreversible Impact",
             "description": f"By the end of {time_span}, the relationships in {location} "
                            "are permanently altered. The final silence speaks the verdict."},
        ],
    )


# ======================================================================== #
# 6. Creator Video Templates (from Visions-Ai Story Rules)
# ======================================================================== #

@dataclass
class VideoTemplateOutput:
    format_name: str
    target_duration: str
    hook_directive: str
    structure_beats: list[dict[str, str]]
    retention_guidelines: list[str]


def generate_talking_head_template(topic: str = "your core thesis",
                                   core_lesson: str = "the fundamental truth") -> VideoTemplateOutput:
    """Scaffold for Talking Head Retention Storytelling (Philipp Humm masterclass)."""
    return VideoTemplateOutput(
        format_name="Talking Head Storytelling",
        target_duration="60s - 90s",
        hook_directive=f"Pattern interrupt within first 3 seconds: 'Most people think {topic} is about X. They are completely wrong.'",
        structure_beats=[
            {"phase": "1. THE HOOK (0-3s)", "direction": f"Pattern interrupt / counter-intuitive thesis on {topic}."},
            {"phase": "2. THE SETUP (3-15s)", "direction": "Who, What, Where. Ground the audience with sensory specifics, not abstract summary."},
            {"phase": "3. INCITING MOMENT (15-30s)", "direction": "Suddenly... the unexpected collision or realization occurs."},
            {"phase": "4. THE STRUGGLE (30-60s)", "direction": f"No struggle, no story. Show the exact friction and resistance before {core_lesson}."},
            {"phase": "5. CLIMAX & LESSON (60-80s)", "direction": f"The emotional breakthrough: {core_lesson}."},
            {"phase": "6. THE RESOLUTION & CTA (80-90s)", "direction": "The new normal + immediate, low-friction next step."},
        ],
        retention_guidelines=[
            "Eye contact: Look down the barrel of the lens, not the display monitor.",
            "Energy dial: Project +20% higher conversational arousal than normal.",
            "Sensory anchoring: State concrete objects and raw feelings over abstract business jargon.",
            "Pre-emphasis pause: Silence before the critical insight amplifies weight."
        ]
    )


def generate_short_form_reel_template(topic: str = "high-velocity concept") -> VideoTemplateOutput:
    """Scaffold for High-Velocity 9:16 Vertical Short / Reel."""
    return VideoTemplateOutput(
        format_name="Vertical Reel / Short (9:16)",
        target_duration="30s - 45s",
        hook_directive="Kinetic visual or typography jolt under 0.5s.",
        structure_beats=[
            {"phase": "1. KINETIC HOOK (0-2s)", "direction": f"High motion text + voiceover punchline: '{topic}'."},
            {"phase": "2. MICRO-BEAT 1 (2-8s)", "direction": "First angle switch / dynamic B-roll cut illustrating the friction."},
            {"phase": "3. PATTERN INTERRUPT (8-14s)", "direction": "Sound effect drop / screen shake / bold color pop."},
            {"phase": "4. ACCELERATION (14-25s)", "direction": "Fast-paced proof / 3 quick consecutive examples."},
            {"phase": "5. SEAMLESS LOOP CLOSURE (25-30s)", "direction": "End phrase loops grammatically back into the first opening word."},
        ],
        retention_guidelines=[
            "Pacing: State change every 2 to 3 seconds minimum.",
            "B-Roll lock: Visual footage must strictly mirror the spoken phonetic noun.",
            "Loop design: Seamless zero-friction loop back to the hook."
        ]
    )


def generate_youtube_longform_template(topic: str = "deep investigation",
                                       promise: str = "the hidden architecture revealed") -> VideoTemplateOutput:
    """Scaffold for YouTube Main Long-Form Video Essay."""
    return VideoTemplateOutput(
        format_name="YouTube Long-Form Video Essay",
        target_duration="8m - 15m",
        hook_directive=f"Deliver the Thumbnail/Title promise payoff up front: {promise}",
        structure_beats=[
            {"phase": "1. PROMISE & STAKES (0-45s)", "direction": f"Hook the payoff: {promise}. Establish what viewer loses by ignoring."},
            {"phase": "2. THE STATUS QUO (45s-2m)", "direction": f"Why the conventional approach to {topic} fails."},
            {"phase": "3. THE DEEP DIVE (2m-5m)", "direction": "Deconstruct the core evidence, data points, or narrative scene."},
            {"phase": "4. MIDPOINT REVERSAL (5m-7m)", "direction": "The unexpected twist: What everyone assumed is inverted."},
            {"phase": "5. THE SYNTHESIS (7m-11m)", "direction": "Building the new framework / applying the breakthrough."},
            {"phase": "6. THE FINAL CONVICTION & PAYOFF (11m-13m)", "direction": "Redeem the original promise in full color."},
        ],
        retention_guidelines=[
            "Scoring: Music swells guide emotional transitions, never flat background elevator music.",
            "Nano Banana rule: Plant weird, highly specific, memorable details that prove human authorship.",
            "Visual variety: Shift focal lengths, angles, or scenes every 15-20 seconds."
        ]
    )


# ======================================================================== #
# 7. The 30-Act Structure ("The Dav3 Standard" from Rhea-Noir)
# ======================================================================== #

@dataclass
class ThirtyActEntry:
    act_number: int
    act_name: str
    phase: str  # META_OPENER | ACT_I_DEPARTURE | META_BRIDGE | ACT_II_INITIATION | ACT_III_RETURN | META_CLOSER
    story_beat: str
    description: str
    pacing_target: str = "4 min"


def generate_thirty_act_scaffold(title: str = "Untitled Epic",
                                  protagonist: str = "PROTAGONIST",
                                  shadow: str = "THE SHADOW") -> list[ThirtyActEntry]:
    """Generates the full 30-Act Dav3 Standard narrative architecture."""
    return [
        # THE META-OPENER
        ThirtyActEntry(1, "The Opening Commencement", "META_OPENER", "Intro Credits & Overture",
                       f"Sets the sonic and visual thesis of {title}. Establishes visual palette, logo reveal, atmospheric baseline.", "2 min"),
        # ACT I: THE DEPARTURE (Beats 2-10)
        ThirtyActEntry(2, "The Status Quo", "ACT_I_DEPARTURE", "Ordinary World",
                       f"{protagonist} in their unshifted equilibrium. Ground the audience in daily physical constraints.", "4 min"),
        ThirtyActEntry(3, "The Inciting Incident", "ACT_I_DEPARTURE", "Call to Adventure",
                       f"The disruption: An external fracture forces {protagonist} to acknowledge that the status quo is broken.", "4 min"),
        ThirtyActEntry(4, "The Refusal", "ACT_I_DEPARTURE", "Reluctance & Cost Calculation",
                       f"{protagonist} retreats or hesitates. Stakes of change are terrifying; old identity resists.", "4 min"),
        ThirtyActEntry(5, "The Mentor", "ACT_I_DEPARTURE", "The Guide & The Artifact",
                       "Encounter with wisdom, tools, or warning that provides the leverage necessary to cross.", "4 min"),
        ThirtyActEntry(6, "Crossing the Threshold", "ACT_I_DEPARTURE", "Entering the Underworld",
                       "Irreversible threshold crossing. Point of no return; familiar rules no longer apply.", "4 min"),
        ThirtyActEntry(7, "Tests, Allies, and Enemies", "ACT_I_DEPARTURE", "The New Reality",
                       "First trial in the new arena. Alliances formed; opposing forces reveal their teeth.", "4 min"),
        ThirtyActEntry(8, "The Approach", "ACT_I_DEPARTURE", "Preparing for the First Challenge",
                       "Regrouping and strategizing for the false summit. Tension accelerates.", "4 min"),
        ThirtyActEntry(9, "The Ordeal (False)", "ACT_I_DEPARTURE", "Premature Battle",
                       "A minor victory or deceptive defeat that tricks the protagonist into thinking the task is known.", "4 min"),
        ThirtyActEntry(10, "The Reward (Temporary)", "ACT_I_DEPARTURE", "Seizing the False Elixir",
                       f"{protagonist} claims what they thought they wanted. False sense of security settles in.", "4 min"),
        # THE META-BRIDGE
        ThirtyActEntry(11, "The Middle Intervention", "META_BRIDGE", "The Intermission / Time-Jump",
                       "The structural breath. Thematic divider, time-jump, or radical tonal reset before descent.", "3 min"),
        # ACT II: THE INITIATION (Beats 12-20)
        ThirtyActEntry(12, "The Road Back (Twist)", "ACT_I_DEPARTURE", "Complication Strikes",
                       "The false reward triggers unexpected consequences. The map was wrong.", "4 min"),
        ThirtyActEntry(13, "The Resurrection (False)", "ACT_II_INITIATION", "The Shadow Re-emerges",
                       f"{shadow} returns in a deadlier, unexpected form. Old tactics completely fail.", "4 min"),
        ThirtyActEntry(14, "The Return with Elixir (Failure)", "ACT_II_INITIATION", "The First Goal Crumbles",
                       "The original plan fails catastrophically. Exterior defenses crumble.", "4 min"),
        ThirtyActEntry(15, "The Second Inciting Incident", "ACT_II_INITIATION", "Raising the True Stakes",
                       "A deeper truth is exposed. The conflict escalates from personal survival to existential reckoning.", "4 min"),
        ThirtyActEntry(16, "The Descent", "ACT_II_INITIATION", "Rock Bottom",
                       "Total loss of external resources, allies, and certainty. The physical low point.", "4 min"),
        ThirtyActEntry(17, "The Dark Night of the Soul", "ACT_II_INITIATION", "Psychological Death",
                       f"{protagonist}'s core ego and self-deception die. Pure internal wrestling in silence.", "4 min"),
        ThirtyActEntry(18, "The Discovery", "ACT_II_INITIATION", "The True Mechanism Revealed",
                       "The epiphany: The answer was never external. The hidden rule of the world is understood.", "4 min"),
        ThirtyActEntry(19, "The Turning Point", "ACT_II_INITIATION", "Decision to Fight on New Terms",
                       f"{protagonist} accepts the ultimate cost and resolves to stand, stripped of illusions.", "4 min"),
        ThirtyActEntry(20, "The Plan", "ACT_II_INITIATION", "Marshalling the True Vanguard",
                       "Assembling what remains for the surgical endgame. Precision over bluster.", "4 min"),
        # ACT III: THE RETURN (Beats 21-29)
        ThirtyActEntry(21, "Storming the Castle", "ACT_III_RETURN", "The Final Approach",
                       "Infiltrating the heart of the adversarial territory. Rhythm and momentum lock into fifth gear.", "4 min"),
        ThirtyActEntry(22, "The High Tower", "ACT_III_RETURN", "Confronting the Primary Defense",
                       "Breaching the antagonist's inner sanctum. Facing the strongest external shield.", "4 min"),
        ThirtyActEntry(23, "The Trap", "ACT_III_RETURN", "The All-Is-Lost Counter-Strike",
                       "The antagonist anticipates the move. A catastrophic ambush tests ultimate resolve.", "4 min"),
        ThirtyActEntry(24, "The Sacrifice", "ACT_III_RETURN", "Paying the Irreversible Price",
                       f"{protagonist} pays the non-negotiable cost. No convenient escapes allowed.", "4 min"),
        ThirtyActEntry(25, "The True Resurrection", "ACT_III_RETURN", "Rebirth from the Ashes",
                       "Rising through the sacrifice. The new consciousness activates in full authority.", "4 min"),
        ThirtyActEntry(26, "The Final Blow", "ACT_III_RETURN", "Defeating the Shadow",
                       f"The climatic clash: {shadow} is dismantled not through luck, but transformed truth.", "4 min"),
        ThirtyActEntry(27, "The New Status Quo", "ACT_III_RETURN", "The World Irreversibly Changed",
                       "The smoke clears. The landscape, laws, and power dynamics are permanently reorganized.", "4 min"),
        ThirtyActEntry(28, "The Elixir", "ACT_III_RETURN", "The True Gift Delivered",
                       "The true wisdom or technology is brought back to heal the collective world.", "4 min"),
        ThirtyActEntry(29, "The Farewell", "ACT_III_RETURN", "Closing the Loops",
                       "Bittersweet resolution of relationships, debts, and departed comrades.", "4 min"),
        # THE META-CLOSER
        ThirtyActEntry(30, "The Grand Finale", "META_CLOSER", "Closing Credits & Post-Credits Seal",
                       f"Final thematic image. Closing audio motif. The definitive authorial seal on {title}.", "3 min"),
    ]


# ======================================================================== #
# 8. Backward-Causal Teleological Planning (from Kaedra VeilEngine)
# ======================================================================== #

@dataclass
class BackwardStep:
    step_number: int
    phase: str  # TERMINAL_ATTRACTOR | VERIFICATION_PROOF | SURGICAL_MUTATION | CAUSAL_ANCHOR
    state_description: str
    dramatic_requirement: str


@dataclass
class TeleologicalNarrativePlan:
    title: str
    terminal_climax: str
    steps: list[BackwardStep]


def generate_backward_plan(title: str = "Untitled Feature",
                           terminal_climax: str = "The protagonist destroys the central machine by sacrificing their own neural implant.",
                           opening_ground: str = "A low-level technician living under the quiet surveillance state.") -> TeleologicalNarrativePlan:
    """Solves narrative backwards from the ending to prune all speculative filler."""
    steps = [
        BackwardStep(
            step_number=4,
            phase="TERMINAL_ATTRACTOR",
            state_description=f"Locked End Condition: {terminal_climax}",
            dramatic_requirement="The climax is non-negotiable. Every preceding scene must be an inescapable domino leading here."
        ),
        BackwardStep(
            step_number=3,
            phase="VERIFICATION_PROOF",
            state_description="Proof of Cost: The sacrifice must be physically and emotionally permanent.",
            dramatic_requirement="Ensure protagonist has no alternative exit (no deus ex machina, no hidden backup)."
        ),
        BackwardStep(
            step_number=2,
            phase="SURGICAL_MUTATION",
            state_description="The Threshold Inversion: Protagonist gains the specific knowledge or artifact required to reach the machine.",
            dramatic_requirement="Every ally and defense stripped away. The discovery in Act II points directly to this mechanism."
        ),
        BackwardStep(
            step_number=1,
            phase="CAUSAL_ANCHOR",
            state_description=f"The Baseline Reality: {opening_ground}",
            dramatic_requirement="Establish the initial flaw or dependency that makes the future sacrifice meaningful."
        ),
    ]
    return TeleologicalNarrativePlan(title=title, terminal_climax=terminal_climax, steps=steps)
