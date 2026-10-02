"""Test suite for NouGenScript engine, dual-plane projector, SPITE subtext, and OpenClap."""
import gzip

import yaml

from nougenscript.core import NodeType
from nougenscript.dual_plane import DualPlaneProjector
from nougenscript.openclap import OpenClapSerializer
from nougenscript.parser import FountainParser
from nougenscript.spite import SpiteProfile, SubtextAnalyzer

FOUNTAIN_SAMPLE = """
EXT. NEO-DETROIT UNDERPASS - NIGHT

Rain lashes against the rusted concrete pillars. Distant sirens wail.

ELISÉE
(whispering, trembling)
Everything is fine. The code is sealed.

CORBIN
You always promise what you cannot keep.

Corbin steps from the shadows, his cybernetic eye pulsing red.

ELISÉE
Never cross that threshold.
"""


def test_fountain_parser():
    script = FountainParser.parse(FOUNTAIN_SAMPLE, title="Veilverse: The Underpass")
    assert script.title == "Veilverse: The Underpass"
    assert len(script.scenes) == 1
    scene = script.scenes[0]
    assert "EXT. NEO-DETROIT UNDERPASS" in scene.heading
    assert len(scene.dialogues) == 3
    assert scene.dialogues[0].character == "ELISÉE"
    assert scene.dialogues[0].parenthetical == "whispering, trembling"
    assert "Everything is fine" in scene.dialogues[0].text
    assert scene.dialogues[1].character == "CORBIN"
    assert script.script_hash != ""


def test_dual_plane_projection():
    script = FountainParser.parse(FOUNTAIN_SAMPLE, title="Dual-Plane Test")
    display_spans, speech_tokens = DualPlaneProjector.project(script)

    assert len(display_spans) == 10
    assert len(speech_tokens) == 18
    # Action and character nodes must NOT be spoken
    spoken_spans = [s for s in display_spans if s.is_spoken]
    assert len(spoken_spans) == 3
    assert all(s.node_type == NodeType.DIALOGUE for s in spoken_spans)

    # Speech tokens must contain the words from dialogues
    words = [t.normalized for t in speech_tokens]
    assert "everything" in words
    assert "fine" in words
    assert "always" in words
    assert "rain" not in words  # Action beat must be excluded from speech plane

    # Reanchor test
    anchor = DualPlaneProjector.reanchor_by_word_index(speech_tokens, 2)
    assert anchor is not None
    assert anchor.token_index == 2


def test_spite_subtext_analysis():
    script = FountainParser.parse(FOUNTAIN_SAMPLE)
    dialogues = script.dialogue_lines

    profile_elisee = SpiteProfile(
        character="ELISÉE",
        shadow_self="Terror of consensus reality dissolving into chaotic noise",
        volatility=0.65,
    )

    # 1. "Everything is fine. The code is sealed." -> Defensive absolutism ("fine")
    res1 = SubtextAnalyzer.analyze(dialogues[0], profile_elisee)
    assert res1.leakage_detected is True
    assert any("Defensive Absolutism" in m for m in res1.markers)
    assert "Concealing vulnerability" in res1.underlying_intent

    # 2. "Never cross that threshold." -> Curt Repression (<= 4 words) & Absolutism ("never")
    res3 = SubtextAnalyzer.analyze(dialogues[2], profile_elisee)
    assert res3.leakage_detected is True
    assert any("Curt Repression" in m for m in res3.markers)
    assert res3.volatility_score > 0.65


def test_openclap_serializer():
    script = FountainParser.parse(FOUNTAIN_SAMPLE, title="OpenClap Test")
    yaml_stream = OpenClapSerializer.to_yaml_stream(script)
    docs = list(yaml.safe_load_all(yaml_stream))

    assert len(docs) == 5
    header, meta, entities, scenes, segments = docs
    assert header["format"] == "clap-0"
    assert meta["title"] == "OpenClap Test"
    assert len(entities["entities"]) == 2  # ELISÉE and CORBIN
    assert len(scenes["scenes"]) == 1
    assert len(segments["segments"]) == 3

    # Binary .clap package
    clap_bytes = OpenClapSerializer.to_clap_binary(script)
    unzipped = gzip.decompress(clap_bytes).decode("utf-8")
    assert "format: clap-0" in unzipped
