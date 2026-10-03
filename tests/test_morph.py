"""Tests for NouGenMorph cognitive ingestion, Joyce recursion, and portmanteau decomposition."""
import pytest

from nougenscript import (
    Dialogue,
    FountainParser,
    JoyceRecursionTransformer,
    MorphCandidate,
    MorphEvidence,
    MorphFinding,
    MorphKind,
    NouGenMorphEngine,
    PortmanteauDecomposer,
    Scene,
    Screenplay,
    StreamOfConsciousnessMorph,
)


def test_morph_candidate_scoring_and_verifiability_ceiling():
    cand = MorphCandidate(
        name="test_joyce_recursion",
        kind=MorphKind.RECURSIVE_MOTIF,
        donor_source="James Joyce (1939)",
        donor_behavior="Vicus of recirculation",
        generalized_behavior="Circular AST screenplay closure",
        nougen_target="nougenscript.morph",
        evidence=[
            MorphEvidence(
                source="Finnegans-Wake_djvu.txt",
                claim="Terminal connects to genesis line",
                confidence=1.0,
                evidence_type="paper_body",  # ceiling = 0.8
            )
        ],
        usefulness=1.0,
        generalizability=1.0,
        verifiability=1.0,  # capped at 0.8 by paper_body
        compatibility=1.0,
        reversibility=1.0,
        integration_cost=0.1,
    )
    # Raw morph score: 1.0 * 1.0 * 1.0 * 1.0 * 1.0 - 0.1 = 0.9
    assert pytest.approx(cand.morph_score(), 0.001) == 0.9
    # Effective score capped at ceiling (0.8): 1.0 * 1.0 * 0.8 * 1.0 * 1.0 - 0.1 = 0.7
    assert pytest.approx(cand.effective_score(), 0.001) == 0.7

    engine = NouGenMorphEngine(acceptance_threshold=0.50)
    accepted, score = engine.ingest_candidate(cand)
    assert accepted is True
    assert pytest.approx(score, 0.001) == 0.7


def test_joyce_recursion_transformer_circular_manifold():
    from nougenscript.core import NodeType, ScriptNode
    sp = Screenplay(title="The Wake Test")
    s1 = Scene(heading="EXT. SHORELINE - DAY")
    s1.nodes.append(ScriptNode(type=NodeType.ACTION, content="riverrun, past Eve and Adam's, from swerve of shore to bend of bay"))
    s1.nodes.append(ScriptNode(type=NodeType.CHARACTER, content="RIVER"))
    s1.nodes.append(ScriptNode(type=NodeType.DIALOGUE, content="Flowing onward."))
    sp.scenes.append(s1)

    s2 = Scene(heading="INT. BEDROOM - NIGHT")
    s2.nodes.append(ScriptNode(type=NodeType.CHARACTER, content="FINN"))
    s2.nodes.append(ScriptNode(type=NodeType.DIALOGUE, content="Falling back asleep."))
    sp.scenes.append(s2)

    # Apply circular loop
    JoyceRecursionTransformer.apply_circular_loop(
        sp,
        opening_phrase="riverrun, past Eve and Adam's",
        terminal_phrase="A way a lone a last a loved a long the",
    )

    analysis = JoyceRecursionTransformer.verify_recirculation(sp)
    assert analysis["valid_manifold"] is True
    assert "riverrun" in analysis["completed_loop_sentence"]
    assert "loved a long the" in analysis["completed_loop_sentence"]


def test_portmanteau_decomposition_joyce_lexicon():
    tok = PortmanteauDecomposer.decompose_word("riverrun")
    assert "river" in tok.roots
    assert "English" in tok.languages
    assert tok.phonetic_spoken == "river run"

    thunder_tok = PortmanteauDecomposer.decompose_word(
        "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk"
    )
    assert "thunderclap" in thunder_tok.roots
    assert "German" in thunder_tok.languages
    assert "thunder fall" in thunder_tok.phonetic_spoken


def test_portmanteau_dialogue_dual_plane_subtext():
    d = Dialogue(character="ANNA", text="We witness the commodius vicus of recirculation.")
    morphed_d, tokens = PortmanteauDecomposer.morph_dialogue_to_dual_plane(d)

    assert len(tokens) == 7
    assert morphed_d.parenthetical is not None
    assert "echoes:" in morphed_d.parenthetical


def test_stream_of_consciousness_joycean_script_generation():
    poly = StreamOfConsciousnessMorph.create_joycean_script(title="Finnegans Engine Live")
    assert poly.meta.title == "Finnegans Engine Live"
    assert "recursion" in poly.meta.extra["tags"]

    sp: Screenplay = poly.body
    assert len(sp.scenes) >= 1
    analysis = JoyceRecursionTransformer.verify_recirculation(sp)
    assert analysis["valid_manifold"] is True


def test_evidence_compiler_mathematical_invariants():
    from nougenscript import EvidenceCompiler
    segments = [
        "riverrun, past Eve and Adam's, from swerve of shore to bend of bay, brings us by a commodius vicus of recirculation back to Howth Castle and Environs.",
        "Sir Tristram, violer d'amores, fr'over the short sea, had passencore rearrived from North Armorica on this side the scraggy isthmus of Europe Minor.",
        "The fall of a once wallstrait oldparr is retaled early in bed and later on life down through all christian minstrelsy.",
        "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk!",
        "What clashes here of wills gen wonts, oystrygods gag sag rahexeption, liddle me, liddle me, liddle me!",
        "Finn, again! Take. Bussoftlhee, mememormee! Till thousendsthee. Lps. The keys to. Given! A way a lone a last a loved a long the riverrun",
    ]

    unit = EvidenceCompiler.compile_semantic_unit(
        unit="riverrun",
        corpus_segments=segments,
        provenance="archive.org/stream/in.ernet.dli.2015.207614",
    )

    assert unit.template == "semantic_unit.v1"
    assert unit.unit == "riverrun"
    assert len(unit.canonical_hash) == 64
    # Boundary closure must be near 1.0 because riverrun is in both first and last segment
    assert unit.metrics["boundary_closure"] == 0.9971
    # Frequency, recurrence, and dispersion must all be calculated floats > 0
    assert unit.metrics["frequency"] > 0.0
    assert unit.metrics["dispersion"] > 0.0
    # Weights must sum to approximately 1.0
    assert pytest.approx(sum(unit.weights.values()), 0.01) == 1.0
    # Confidence must be separate from score
    assert 0.0 <= unit.score <= 1.0
    assert 0.0 <= unit.confidence <= 1.0


def test_nougen_morph_engine_universal_template_solver():
    from nougenscript import NouGenMorphEngine
    sol = NouGenMorphEngine.solve_universal_template(
        target="Finnegans Manifold",
        kind="recursive_motif",
        seed_data="terminal to genesis loop",
    )
    assert sol["target"] == "Finnegans Manifold"
    assert sol["kind"] == "recursive_motif"
    assert "yards" in sol["calculated_results"]["gain"]
    assert sol["calculated_results"]["rate"] >= 80.0
    assert "Finnegans Manifold" in sol["result"]


def test_universal_morph_engine_dave_law_determinism_and_unavailability():
    from nougenscript import MetricStatus, UniversalMorphEngine
    segments = [
        "riverrun, past Eve and Adam's, from swerve of shore to bend of bay",
        "brings us by a commodius vicus of recirculation back to Howth Castle and Environs",
        "Sir Tristram, violer d'amores, fr'over the short sea",
        "A way a lone a last a loved a long the riverrun",
    ]

    t1 = UniversalMorphEngine.compile_unit(
        corpus=segments,
        unit="riverrun",
        provenance={"source": "archive.org/stream/in.ernet.dli.2015.207614", "normalized": True},
        capabilities={"math": "builtin.v1", "entropy": "shannon.v1"},
    )
    t2 = UniversalMorphEngine.compile_unit(
        corpus=segments,
        unit="riverrun",
        provenance={"source": "archive.org/stream/in.ernet.dli.2015.207614", "normalized": True},
        capabilities={"math": "builtin.v1", "entropy": "shannon.v1"},
    )

    # 1. Byte-stable canonical hash determinism
    assert t1.canonical_hash == t2.canonical_hash
    assert len(t1.canonical_hash) == 64

    # 2. Score and confidence separation
    assert 0.0 <= t1.score <= 1.0
    assert 0.0 <= t1.confidence <= 1.0
    assert t1.score != t1.confidence

    # 3. Mathematically calculated metrics from corpus distribution
    assert t1.metrics["boundary_closure"].value == 1.0
    assert t1.metrics["frequency"].value > 0.0
    assert t1.metrics["dispersion"].value > 0.0

    # 4. Weights must be corpus-derived and sum to approximately 1.0
    calculated_weights = [m.weight for m in t1.metrics.values() if m.status == MetricStatus.CALCULATED]
    assert pytest.approx(sum(calculated_weights), 0.01) == 1.0

    # 5. Unavailable metrics are never guessed
    assert t1.metrics["phonetic_similarity"].status == MetricStatus.UNAVAILABLE
    assert t1.metrics["phonetic_similarity"].value is None

    # 6. Changing corpus changes calculated evidence without hardcoded drift
    t_other = UniversalMorphEngine.compile_unit(
        corpus=["completely unrelated content with zero recurrence", "another line entirely"],
        unit="riverrun",
    )
    assert t_other.metrics["boundary_closure"].value == 0.0
    assert t_other.canonical_hash != t1.canonical_hash

