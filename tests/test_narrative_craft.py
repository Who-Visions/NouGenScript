"""Unit tests for Top 0.001% Narrative Scriptwriting Craft Engine."""
from nougenscript import (
    FountainParser,
    MametAuditor,
    StatusTracker,
    StatusMove,
    CadenceAnalyzer,
    CausalityValidator,
    DramaticIronyMapper,
    InformationState,
    RecurseTracer,
    MasterCraftSuite,
)

SAMPLE_SCREENPLAY = """
EXT. GLASS TOWER - ROOF - NIGHT

Rain lashes the reinforced helipad. ELISÉE stands at the edge.

CORBIN
(calm, holding the detonator)
Sit down. I decide when the ledger opens, Elisée. Look at me.

ELISÉE
(trembling, backing away)
Sorry. I apologize for what happened in Sector 4. It was my fault.

CORBIN
You are a fool if you think apologies settle debts with the Veil.

ELISÉE
(eyes blazing, stepping forward)
Enough. I am the one holding the cipher. Silence, Corbin. Look at the skyline.

CORBIN
(stiffening)
You wouldn't dare.

ELISÉE
Give me the key now. Because if you refuse, every server burns in thirty seconds.

CORBIN
However, the breach is already sealed.
"""


def test_mamet_auditor():
    sp = FountainParser.parse(SAMPLE_SCREENPLAY)
    scene = sp.scenes[0]
    audit = MametAuditor.audit_scene(scene)

    assert audit.has_objective is True
    assert audit.has_stakes is True
    assert audit.has_urgency is True
    assert audit.mamet_score >= 0.75
    assert audit.is_dramatic_propulsion is True


def test_status_tracker_and_reversal():
    sp = FountainParser.parse(SAMPLE_SCREENPLAY)
    res = StatusTracker.analyze_dialogues(sp.dialogue_lines)

    assert "CORBIN" in res.characters
    assert "ELISÉE" in res.characters
    # There should be at least one power reversal when Elisée says "Enough. I am the one holding the cipher."
    assert res.reversals_detected >= 1
    assert len(res.turns) == 7


def test_cadence_analyzer():
    sp = FountainParser.parse(SAMPLE_SCREENPLAY)
    cadence = CadenceAnalyzer.analyze(sp.dialogue_lines)

    assert cadence.total_lines == 7
    assert cadence.average_syllables_per_line > 0
    assert cadence.musicality_score >= 50.0


def test_causality_and_dramatic_irony():
    sp = FountainParser.parse(SAMPLE_SCREENPLAY)
    irony = DramaticIronyMapper.evaluate_scene(sp.scenes[0], audience_secret="Elisée has an EMP device strapped to his arm")

    assert irony.primary_state == InformationState.DRAMATIC_IRONY
    assert irony.tension_rating >= 0.8


def test_recurse_tracer():
    motif = RecurseTracer.audit_motif(
        name="Wind from Graves",
        setup="The wind always blows from the graves.",
        echo="The dust never settled, did it?",
        inversion="The wind isn't coming from the graves; it's blowing towards them.",
        payoff="I was the wind.",
    )
    assert motif.is_complete is True
    assert motif.score == 10


def test_master_craft_suite():
    sp = FountainParser.parse(SAMPLE_SCREENPLAY)
    report = MasterCraftSuite.audit(sp)

    assert report.total_scenes == 1
    assert report.total_dialogues == 7
    assert report.mamet_compliance_ratio == 1.0
    assert report.overall_craft_index >= 70.0
