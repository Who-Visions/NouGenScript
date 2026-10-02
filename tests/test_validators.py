"""Tests for NouGenScript v0.4.0 — Validators and Templates.

Covers:
- CausalMomentumValidator (Therefore/But)
- BeatSheetValidator (Save the Cat!)
- HarmonCircleValidator (8-Step)
- AristotleUnitiesValidator (Three Unities)
- McCloudTransitionValidator (6-Tier)
- SchwartzAwarenessValidator (Email)
- DeterministicDiffGate
- ScriptValidator unified pipeline
- All template generators (beat-sheet, story-circle, PAS, BAB, HSO, unity-play)
"""
import os
import pytest

from nougenscript.core import Dialogue, NodeType, Scene, Screenplay, ScriptNode
from nougenscript.dialects import (
    ComicPage,
    ComicPanel,
    EmailSection,
    PolyScript,
    ScriptDomain,
    ScriptKind,
    ScriptMeta,
    TVAct,
)
from nougenscript.validators import (
    AristotleUnitiesValidator,
    AwarenessStage,
    BeatSheetValidator,
    BeatType,
    CausalConnector,
    CausalMomentumValidator,
    DeterministicDiffGate,
    HarmonCircleValidator,
    HarmonStep,
    McCloudTransitionValidator,
    PanelTransition,
    SchwartzAwarenessValidator,
    ScriptValidator,
    ValidationIssue,
    ValidationReport,
    VideoRetentionValidator,
)
from nougenscript.templates import (
    BeatEntry,
    CircleStep,
    EmailTemplate,
    TransitionAnnotation,
    UnityOutline,
    VideoTemplateOutput,
    generate_bab_template,
    generate_beat_sheet,
    generate_hso_template,
    generate_pas_template,
    generate_short_form_reel_template,
    generate_story_circle,
    generate_talking_head_template,
    generate_unity_outline,
    generate_youtube_longform_template,
)


# ======================================================================== #
# Helper factories
# ======================================================================== #

def make_scene(heading: str, nodes: list[ScriptNode] | None = None) -> Scene:
    return Scene(heading=heading, nodes=nodes or [], scene_number=1)


def make_screenplay(title: str, scenes: list[Scene] | None = None) -> Screenplay:
    return Screenplay(title=title, scenes=scenes or [])


def make_poly(kind: ScriptKind, body, title: str = "Test") -> PolyScript:
    meta = ScriptMeta(title=title, kind=kind)
    return PolyScript(meta=meta, body=body, raw_source="test source")


# ======================================================================== #
# 1. CausalMomentumValidator
# ======================================================================== #

class TestCausalMomentumValidator:
    def test_therefore_connector_detected(self):
        scenes = [
            make_scene("INT. ROOM - DAY", [ScriptNode(NodeType.ACTION, "The hero discovers the map.")]),
            make_scene("EXT. FOREST - DAY", [ScriptNode(NodeType.ACTION, "Therefore he sets out into the forest.")]),
        ]
        report = CausalMomentumValidator.validate_scenes(scenes)
        assert report.score > 0.0
        assert report.metadata["causal_count"] >= 1

    def test_but_connector_detected(self):
        scenes = [
            make_scene("INT. OFFICE - DAY", [ScriptNode(NodeType.ACTION, "She submits the report.")]),
            make_scene("INT. BOSS OFFICE - DAY", [ScriptNode(NodeType.ACTION, "But the boss rejects it.")]),
        ]
        report = CausalMomentumValidator.validate_scenes(scenes)
        assert report.metadata["causal_count"] >= 1
        assert report.metadata["drift_count"] == 0

    def test_and_then_drift_flagged(self):
        scenes = [
            make_scene("INT. ROOM - DAY", [ScriptNode(NodeType.ACTION, "He eats breakfast.")]),
            make_scene("EXT. STREET - DAY", [ScriptNode(NodeType.ACTION, "And then he walks to school.")]),
        ]
        report = CausalMomentumValidator.validate_scenes(scenes)
        assert report.metadata["drift_count"] >= 1
        assert any(i.code == "CAUSAL_DRIFT" for i in report.issues)

    def test_classify_connector(self):
        assert CausalMomentumValidator.classify_connector("therefore the plan works") == CausalConnector.THEREFORE
        assert CausalMomentumValidator.classify_connector("but it all falls apart") == CausalConnector.BUT
        assert CausalMomentumValidator.classify_connector("and then stuff happens") == CausalConnector.AND_THEN

    def test_single_scene_passes(self):
        report = CausalMomentumValidator.validate_scenes([make_scene("INT. ROOM - DAY")])
        assert report.passed


# ======================================================================== #
# 2. BeatSheetValidator
# ======================================================================== #

class TestBeatSheetValidator:
    def test_feature_length_passes(self):
        scenes = [make_scene(f"INT. LOC{i} - DAY") for i in range(70)]
        sp = make_screenplay("Feature", scenes)
        report = BeatSheetValidator.validate_screenplay(sp)
        assert report.passed

    def test_short_script_warning(self):
        scenes = [make_scene(f"INT. LOC{i} - DAY") for i in range(10)]
        sp = make_screenplay("Short", scenes)
        report = BeatSheetValidator.validate_screenplay(sp)
        assert any(i.code == "SHORT_SCRIPT" for i in report.issues)

    def test_long_script_warning(self):
        scenes = [make_scene(f"INT. LOC{i} - DAY") for i in range(100)]
        sp = make_screenplay("Long", scenes)
        report = BeatSheetValidator.validate_screenplay(sp)
        assert any(i.code == "LONG_SCRIPT" for i in report.issues)


# ======================================================================== #
# 3. HarmonCircleValidator
# ======================================================================== #

class TestHarmonCircleValidator:
    def test_episode_with_cold_open(self):
        acts = [
            TVAct(act_number=0, act_name="COLD OPEN", scenes=[make_scene("EXT. ROOF - NIGHT")]),
            TVAct(act_number=1, act_name="ACT ONE", scenes=[make_scene("INT. OFFICE - DAY"), make_scene("INT. LAB - DAY")]),
            TVAct(act_number=2, act_name="ACT TWO", scenes=[make_scene("EXT. PARK - DAY")]),
        ]
        report = HarmonCircleValidator.validate_tv_episode(acts)
        assert report.metadata["has_cold_open"] is True
        assert report.passed

    def test_no_cold_open_warning(self):
        acts = [TVAct(act_number=1, act_name="ACT ONE", scenes=[make_scene("INT. ROOM - DAY")])]
        report = HarmonCircleValidator.validate_tv_episode(acts)
        assert any(i.code == "NO_COLD_OPEN" for i in report.issues)

    def test_empty_episode_fails(self):
        report = HarmonCircleValidator.validate_tv_episode([])
        assert not report.passed


# ======================================================================== #
# 4. AristotleUnitiesValidator
# ======================================================================== #

class TestAristotleUnitiesValidator:
    def test_single_location_passes(self):
        scenes = [
            make_scene("INT. KITCHEN - DAY", [ScriptNode(NodeType.DIALOGUE, "Hello.", metadata={})] * 3),
            make_scene("INT. KITCHEN - NIGHT"),
        ]
        sp = make_screenplay("Play", scenes)
        report = AristotleUnitiesValidator.validate_play(sp)
        assert report.passed
        assert report.metadata["distinct_locations"] <= 3

    def test_many_locations_warning(self):
        scenes = [make_scene(f"INT. LOCATION_{i} - DAY") for i in range(10)]
        sp = make_screenplay("Play", scenes)
        report = AristotleUnitiesValidator.validate_play(sp)
        assert any(i.code == "UNITY_PLACE_BROKEN" for i in report.issues)


# ======================================================================== #
# 5. McCloudTransitionValidator
# ======================================================================== #

class TestMcCloudTransitionValidator:
    def test_classify_moment_to_moment(self):
        p1 = ComicPanel(panel_number=1, visual_description="Close up on the hero's hand gripping the sword tightly")
        p2 = ComicPanel(panel_number=2, visual_description="Close up on the hero's hand releasing the sword slowly")
        t = McCloudTransitionValidator.classify_transition(p1, p2)
        assert t in {PanelTransition.MOMENT_TO_MOMENT, PanelTransition.ACTION_TO_ACTION}

    def test_scene_to_scene_detected(self):
        p1 = ComicPanel(panel_number=1, visual_description="The hero stands in the city")
        p2 = ComicPanel(panel_number=2, visual_description="Later that night in the forest ext darkness")
        t = McCloudTransitionValidator.classify_transition(p1, p2)
        assert t == PanelTransition.SCENE_TO_SCENE

    def test_validate_pages(self):
        pages = [ComicPage(page_number=1, panels=[
            ComicPanel(panel_number=1, visual_description="Hero runs", dialogue_balloons=[{"speaker": "HERO", "text": "Go!"}]),
            ComicPanel(panel_number=2, visual_description="Villain blocks the path"),
            ComicPanel(panel_number=3, visual_description="Hero jumps over"),
        ])]
        report = McCloudTransitionValidator.validate_pages(pages)
        assert report.passed
        assert report.metadata["total_transitions"] == 2


# ======================================================================== #
# 6. SchwartzAwarenessValidator
# ======================================================================== #

class TestSchwartzAwarenessValidator:
    def test_valid_email_passes(self):
        email = EmailSection(
            subject_line="The secret weapon",
            preview_header="You won't believe this",
            salutation="Hi {{first_name}},",
            body_paragraphs=["You're struggling with growth.", "This solution fixes it fast."],
            call_to_action_url="https://example.com/get-started",
            call_to_action_text="Get Started Now",
            ps_line="P.S. — Only 50 spots left this quarter.",
        )
        report = SchwartzAwarenessValidator.validate_email(email)
        assert report.passed

    def test_missing_subject_fails(self):
        email = EmailSection(
            subject_line="",
            preview_header="",
            salutation="Hi,",
            body_paragraphs=["Body text"],
            call_to_action_url="https://example.com",
            call_to_action_text="Click",
        )
        report = SchwartzAwarenessValidator.validate_email(email)
        assert not report.passed

    def test_missing_ps_warning(self):
        email = EmailSection(
            subject_line="Quick note",
            preview_header="",
            salutation="Hi,",
            body_paragraphs=["Some copy"],
            call_to_action_url="https://example.com",
            call_to_action_text="Click",
            ps_line="",
        )
        report = SchwartzAwarenessValidator.validate_email(email)
        assert any(i.code == "MISSING_PS" for i in report.issues)

    def test_awareness_detection(self):
        email = EmailSection(
            subject_line="Test", preview_header="", salutation="Hi,",
            body_paragraphs=["Are you tired of slow deployments? Frustrated with CI/CD?"],
            call_to_action_url="#", call_to_action_text="Go",
        )
        stage = SchwartzAwarenessValidator.detect_awareness_stage(email)
        assert stage == AwarenessStage.PROBLEM_AWARE

    def test_framework_detection(self):
        email = EmailSection(
            subject_line="Test", preview_header="", salutation="Hi,",
            body_paragraphs=["The problem is clear. Let's agitate it. Now solve it."],
            call_to_action_url="#", call_to_action_text="Go",
        )
        fw = SchwartzAwarenessValidator.detect_framework(email)
        assert fw == "PAS"


# ======================================================================== #
# 7. DeterministicDiffGate
# ======================================================================== #

class TestDeterministicDiffGate:
    def test_deterministic_poly_passes(self):
        poly = make_poly(ScriptKind.MOVIE_SCREENPLAY, "test body", title="Deterministic Test")
        report = DeterministicDiffGate.validate(poly)
        assert report.passed
        assert report.metadata["match"] is True

    def test_hash_consistency(self):
        poly = make_poly(ScriptKind.COLD_EMAIL, "email body")
        h1 = poly.recompute_hash()
        h2 = poly.recompute_hash()
        assert h1 == h2


# ======================================================================== #
# 8. ScriptValidator unified pipeline
# ======================================================================== #

class TestScriptValidator:
    def test_movie_pipeline(self):
        scenes = [make_scene(f"INT. LOC{i} - DAY", [ScriptNode(NodeType.ACTION, f"Action {i}")]) for i in range(70)]
        sp = make_screenplay("Feature Film", scenes)
        poly = make_poly(ScriptKind.MOVIE_SCREENPLAY, sp, title="Feature Film")
        reports = ScriptValidator.validate(poly)
        assert len(reports) >= 1  # At minimum: DiffGate

    def test_tv_pipeline(self):
        acts = [
            TVAct(act_number=0, act_name="COLD OPEN", scenes=[make_scene("EXT. ROOF - NIGHT")]),
            TVAct(act_number=1, act_name="ACT ONE", scenes=[make_scene("INT. OFFICE - DAY")]),
        ]
        poly = make_poly(ScriptKind.TV_EPISODIC, acts, title="TV Pilot")
        reports = ScriptValidator.validate(poly)
        assert len(reports) >= 2  # DiffGate + HarmonCircle

    def test_email_pipeline(self):
        email = EmailSection(
            subject_line="Hello", preview_header="", salutation="Hi,",
            body_paragraphs=["Test"], call_to_action_url="https://test.com",
            call_to_action_text="Click", ps_line="P.S. Done",
        )
        poly = make_poly(ScriptKind.COLD_EMAIL, email, title="Email Test")
        reports = ScriptValidator.validate(poly)
        assert len(reports) >= 2  # DiffGate + Schwartz

    def test_comic_pipeline(self):
        pages = [ComicPage(page_number=1, panels=[
            ComicPanel(panel_number=1, visual_description="Hero stands"),
            ComicPanel(panel_number=2, visual_description="Villain appears behind"),
        ])]
        poly = make_poly(ScriptKind.COMIC_SCRIPT, pages, title="Comic Test")
        reports = ScriptValidator.validate(poly)
        assert len(reports) >= 2  # DiffGate + McCloud

    def test_full_report_string(self):
        email = EmailSection(
            subject_line="Test", preview_header="", salutation="Hi,",
            body_paragraphs=["Copy"], call_to_action_url="https://x.com",
            call_to_action_text="Go", ps_line="P.S.",
        )
        poly = make_poly(ScriptKind.COLD_EMAIL, email)
        report_str = ScriptValidator.full_report(poly)
        assert "Validation Report" in report_str


# ======================================================================== #
# 9. Template Generators
# ======================================================================== #

class TestTemplateGenerators:
    def test_beat_sheet(self):
        beats = generate_beat_sheet(title="Test Feature")
        assert len(beats) == 15
        assert beats[0].beat == BeatType.OPENING_IMAGE
        assert beats[-1].beat == BeatType.FINAL_IMAGE
        assert all(isinstance(b, BeatEntry) for b in beats)

    def test_story_circle(self):
        steps = generate_story_circle(protagonist="XOAH", episode_title="Veil Breach")
        assert len(steps) == 8
        assert steps[0].step == HarmonStep.YOU
        assert steps[-1].step == HarmonStep.CHANGE
        assert "XOAH" in steps[0].description

    def test_pas_template(self):
        tmpl = generate_pas_template(topic="slow CI/CD")
        assert tmpl.framework == "PAS"
        assert len(tmpl.sections) == 3
        assert tmpl.sections[0]["label"] == "PROBLEM"
        assert "slow CI/CD" in tmpl.sections[0]["content"]

    def test_bab_template(self):
        tmpl = generate_bab_template(topic="tech debt")
        assert tmpl.framework == "BAB"
        assert tmpl.awareness_stage == AwarenessStage.SOLUTION_AWARE
        assert len(tmpl.sections) == 3

    def test_hso_template(self):
        tmpl = generate_hso_template(topic="NouGen memory")
        assert tmpl.framework == "HSO"
        assert tmpl.awareness_stage == AwarenessStage.UNAWARE
        assert "HOOK" in tmpl.sections[0]["label"]

    def test_unity_play(self):
        outline = generate_unity_outline(
            title="The Kitchen",
            location="A Brooklyn kitchen",
            characters=["MARIA", "ANTONIO", "ROSA"],
        )
        assert isinstance(outline, UnityOutline)
        assert outline.title == "The Kitchen"
        assert len(outline.act_structure) == 3
        assert "MARIA" in outline.characters

    def test_sign_off_dynamic(self):
        old = os.environ.get("NOUGEN_SIGN_OFF")
        os.environ["NOUGEN_SIGN_OFF"] = "Cheers"
        try:
            tmpl = generate_pas_template()
            assert tmpl.sign_off == "Cheers"
        finally:
            if old is not None:
                os.environ["NOUGEN_SIGN_OFF"] = old
            else:
                os.environ.pop("NOUGEN_SIGN_OFF", None)

    def test_talking_head_template(self):
        tmpl = generate_talking_head_template(topic="token limits", core_lesson="swarm decentralization")
        assert isinstance(tmpl, VideoTemplateOutput)
        assert len(tmpl.structure_beats) == 6
        assert "token limits" in tmpl.hook_directive
        assert any("Eye contact" in g for g in tmpl.retention_guidelines)

    def test_short_form_reel_template(self):
        tmpl = generate_short_form_reel_template(topic="memory clustering")
        assert tmpl.target_duration == "30s - 45s"
        assert len(tmpl.structure_beats) == 5
        assert any("Loop design" in g for g in tmpl.retention_guidelines)

    def test_youtube_longform_template(self):
        tmpl = generate_youtube_longform_template(topic="The Observatory", promise="108k shards live")
        assert "8m - 15m" in tmpl.target_duration
        assert any("Nano Banana" in g for g in tmpl.retention_guidelines)


# ======================================================================== #
# 10. VideoRetentionValidator Tests
# ======================================================================== #

class TestVideoRetentionValidator:
    def test_video_retention_passes(self):
        from nougenscript.dialects import CreatorVideoScript, VideoScriptBeat
        script = CreatorVideoScript(
            hook_3s="Stop using single LLMs for complex coding.",
            setup="In 2026, context overflow ruins stateful development across sessions.",
            beats=[
                VideoScriptBeat(timecode_start="00:00", visual_action="Camera cut", spoken_audio="Here is what you must do.", sound_design="bass drop", is_pattern_interrupt=True),
                VideoScriptBeat(timecode_start="00:05", visual_action="Screen recording", spoken_audio="Look at this red glowing cluster.", sound_design="click"),
                VideoScriptBeat(timecode_start="00:15", visual_action="Diagram", spoken_audio="We distribute shards across 9 SQLite banks.", sound_design="whoosh"),
            ],
            call_to_action="Star the repository on GitHub.",
            estimated_duration_sec=30
        )
        report = VideoRetentionValidator.validate_video(script)
        assert report.passed is True
        assert report.metadata["pattern_interrupts"] >= 1

    def test_missing_hook_fails(self):
        from nougenscript.dialects import CreatorVideoScript
        script = CreatorVideoScript(hook_3s="", setup="Some setup context here.")
        report = VideoRetentionValidator.validate_video(script)
        assert report.passed is False
        assert any(i.code == "MISSING_HOOK" for i in report.issues)


# ======================================================================== #
# 11. ValidationReport internals
# ======================================================================== #

class TestValidationReport:
    def test_summary_format(self):
        r = ValidationReport(validator_name="Test", passed=True, score=0.9)
        s = r.summary()
        assert "PASSED" in s
        assert "Test" in s

    def test_report_hash_deterministic(self):
        r = ValidationReport(validator_name="Test", passed=True, issues=[], score=1.0)
        h1 = r.report_hash()
        h2 = r.report_hash()
        assert h1 == h2

    def test_issue_str(self):
        i = ValidationIssue(severity="error", code="TEST", message="broken")
        s = str(i)
        assert "🔴" in s
        assert "TEST" in s
