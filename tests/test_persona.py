"""Unit tests for NouGenScript persona and character voice engine."""
import pytest
from nougenscript.core import Dialogue
from nougenscript.persona import (
    BEHAVIORAL_MASKS,
    EMOTIONS,
    CharacterPersona,
    EmotionState,
    MaskBlend,
    Signals,
    blend,
    get_emotion,
    get_mask,
    list_masks,
    resolve,
)


def test_20_pack_masks_completeness():
    assert len(BEHAVIORAL_MASKS) == 20
    masks = list_masks()
    assert "charming" in masks
    assert "stoic" in masks
    assert "gremlin" in masks
    assert "villain" in masks
    assert "genius" in masks


def test_mask_blend_prompt_stack():
    b = blend("stoic", "villain")
    assert b.mask_names == ("stoic", "villain")
    assert "disciplined" in b.traits
    assert "cold" in b.traits
    prompt = b.system_prompt("Corbin Varas")
    assert "Base Character/Actor: Corbin Varas." in prompt
    assert "Active Behavioral Mask: Stoic + Villain." in prompt
    assert "[Stoic]:" in prompt
    assert "[Villain]:" in prompt


def test_20_pack_emotional_spectrum():
    assert len(EMOTIONS) == 20
    ecstatic = get_emotion("ecstatic")
    assert ecstatic.intensity == 1.0
    assert ecstatic.opposite == "enraged"

    enraged = get_emotion("enraged")
    assert enraged.intensity == -1.0
    assert enraged.opposite == "ecstatic"

    cue = ecstatic.direction_cue()
    assert "Ecstatic" in cue


def test_persona_resolution_deterministic():
    texts = [
        "EXT. NEO-DETROIT ROOFTOP - NIGHT",
        "Xoah draws the dark matter blade and steps into the veil.",
        "Nothing escapes the architect.",
    ]
    sig1 = Signals.from_texts(texts)
    sig2 = Signals.from_texts(texts)
    p1 = resolve(sig1)
    p2 = resolve(sig2)
    assert p1.fingerprint() == p2.fingerprint()
    assert p1.market == "veilverse-cinema"
    assert p1.audience == "screenplay-writer"


def test_character_persona_validation():
    char = CharacterPersona(
        character_name="XOAH",
        masks=blend("stoic"),
        current_emotion=get_emotion("furious"),
        vocabulary_register="terse",
        taboo_words={"mercy", "surrender"},
    )

    # Check parenthetical auto-fill from emotional state
    d = char.format_dialogue("The throne belongs to the dust.")
    assert d.character == "XOAH"
    assert "Furious" in (d.parenthetical or "")

    # Check taboo validation
    violations = char.validate_line("I will grant you no mercy.")
    assert len(violations) == 1
    assert "taboo violation" in violations[0]

    # Check register violation
    long_line = "I am speaking so many unnecessary words right now to deliberately violate the terse register constraint set upon this character."
    v_long = char.validate_line(long_line)
    assert any("register violation" in v for v in v_long)
