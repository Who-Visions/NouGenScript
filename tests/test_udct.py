"""
Unit and Property Tests for NouGen UDCT Engine.
==============================================
Verifies the four pillars:
1. Universal (Works across abstract parameters, arbitrary dimensions)
2. Deterministic (T(x1, s1, c1) == T(x2, s2, c2))
3. Calculated (Values strictly derived from equations, zero LLM guesswork)
4. Template (Templates render state machine values deterministically)
"""

import math
import pytest
from nougenscript.udct import (
    EasingType,
    MathFunctions,
    UniversalDeterministicEngine,
    UniversalStateConfig,
)


def test_udct_determinism_invariant():
    """Deterministic invariant: T(x1, s1, c1) == T(x2, s2, c2)."""
    cfg1 = UniversalStateConfig(
        duration=10.0,
        fps=30,
        subject="Xoah",
        action="sprint",
        start_pos=(0.0, 0.0),
        end_pos=(18.0, 0.0),
        easing=EasingType.EASE_IN_OUT_CUBIC,
        camera_offset=0.17,
    )
    cfg2 = UniversalStateConfig(
        duration=10.0,
        fps=30,
        subject="Xoah",
        action="sprint",
        start_pos=(0.0, 0.0),
        end_pos=(18.0, 0.0),
        easing=EasingType.EASE_IN_OUT_CUBIC,
        camera_offset=0.17,
    )

    states1 = UniversalDeterministicEngine.calculate_trajectory(cfg1)
    states2 = UniversalDeterministicEngine.calculate_trajectory(cfg2)

    assert len(states1) == 300
    assert len(states2) == 300

    for s1, s2 in zip(states1, states2):
        assert s1.index == s2.index
        assert s1.t == s2.t
        assert s1.position_x == s2.position_x
        assert s1.velocity_x == s2.velocity_x
        assert s1.intensity == s2.intensity
        assert s1.state_hash == s2.state_hash


def test_udct_normalized_time_and_position_math():
    """Calculated property test:
    N = FPS * D = 300.
    t_150 = 150 / 299 = ~0.50167.
    """
    cfg = UniversalStateConfig(
        duration=10.0,
        fps=30,
        subject="Ravenous",
        start_pos=(0.0, 0.0, 0.0),
        end_pos=(18.0, 0.0, 0.0),
        easing=EasingType.LINEAR,
    )
    states = UniversalDeterministicEngine.calculate_trajectory(cfg)

    # Frame 0
    assert states[0].t == 0.0
    assert states[0].position_x == 0.0

    # Frame 150
    f150 = states[150]
    expected_t = 150.0 / 299.0
    assert abs(f150.t - expected_t) < 1e-4
    assert abs(f150.position_x - (18.0 * expected_t)) < 1e-3

    # Frame 299 (last)
    assert states[299].t == 1.0
    assert states[299].position_x == 18.0


def test_udct_template_renderer_expresses_calculated_state():
    """Template test:
    The template renders exact calculated math variables without hallucination.
    """
    cfg = UniversalStateConfig(
        duration=5.0,
        fps=24,
        subject="Xoah",
        action="dash",
        start_pos=(0.0, 0.0),
        end_pos=(10.0, 0.0),
        easing=EasingType.EASE_OUT_CUBIC,
    )
    states = UniversalDeterministicEngine.calculate_trajectory(cfg)
    mid_state = states[60]  # Frame 60 of 120

    template_code = (
        "FRAME {{frame_index}} / {{total_frames}}\n"
        "t = {{t}}\n"
        "pos = ({{calc_position_x}}, {{calc_position_y}})\n"
        "vel = {{velocity_x}}\n"
        "intensity = {{intensity}}\n"
        "hash = {{state_hash}}"
    )

    rendered = UniversalDeterministicEngine.render_template(template_code, mid_state, cfg)

    assert "FRAME 60 / 120" in rendered
    assert f"t = {mid_state.t:.4f}" in rendered
    assert f"pos = ({mid_state.position_x:.4f}, {mid_state.position_y:.4f})" in rendered
    assert f"vel = {mid_state.velocity_x:.4f}" in rendered
    assert f"hash = {mid_state.state_hash}" in rendered


def test_udct_universality_across_domains():
    """Universality test:
    Audio synthesis, UI physics, or camera drones reuse the identical UDCT engine.
    """
    # Audio volume swell & panning
    audio_cfg = UniversalStateConfig(
        duration=2.0,
        fps=100,  # 100 Hz control rate
        subject="SubBassSynthesizer",
        action="modulate",
        start_pos=(-1.0, 0.0),  # Pan full left
        end_pos=(1.0, 0.0),     # Pan full right
        easing=EasingType.SINUSOIDAL,
        intensity_range=(0.0, 1.0),
    )
    audio_states = UniversalDeterministicEngine.calculate_trajectory(audio_cfg)
    assert len(audio_states) == 200

    # Start: left pan, intensity 0
    assert audio_states[0].position_x == -1.0
    assert audio_states[0].intensity == 0.0

    # Midpoint: center pan (0.0), maximum intensity (1.0)
    # At t=0.5: sin^2(pi * 0.5) = sin^2(pi/2) = 1.0
    mid = audio_states[99]
    assert abs(mid.position_x) < 0.05
    assert abs(mid.intensity - 1.0) < 0.05


def test_state_hash_covers_full_configuration():
    base = UniversalStateConfig(duration=1, fps=2, start_pos=(0, 0, 0), end_pos=(1, 2, 3))
    changed = UniversalStateConfig(duration=1, fps=2, action="turn", start_pos=(0, 0, 0), end_pos=(1, 2, 3))
    base_states = UniversalDeterministicEngine.calculate_trajectory(base)
    changed_states = UniversalDeterministicEngine.calculate_trajectory(changed)
    assert base_states[0].state_hash != changed_states[0].state_hash
    assert base_states[0].state_hash == UniversalDeterministicEngine.calculate_trajectory(base)[0].state_hash
    configured_camera = UniversalStateConfig(
        duration=1,
        fps=2,
        end_pos=(1, 2, 3),
        camera_distance=7.0,
        intensity_cycles=2.0,
    )
    configured_state = UniversalDeterministicEngine.calculate_trajectory(configured_camera)[0]
    assert configured_state.state_hash != base_states[0].state_hash
    assert configured_state.camera["z"] != base_states[0].camera["z"]


def test_custom_dynamic_slots_render_deterministically_and_once():
    cfg = UniversalStateConfig(
        duration=1,
        fps=1,
        custom_constants={"domain": "{{subject}}", "weights": {"b": 2, "a": 1}},
    )
    state = UniversalDeterministicEngine.calculate_trajectory(cfg)[0]
    rendered = UniversalDeterministicEngine.render_template(
        "{{domain}} {{weights}} {{subject}} {{note}}",
        state,
        cfg,
        {"note": "{{action}}"},
    )
    assert rendered == '{{subject}} {"a":1,"b":2} Subject {{action}}'
    assert UniversalDeterministicEngine.compile_full_sequence("{{domain}}", cfg) == ["{{subject}}"]


def test_template_rejects_unknown_or_reserved_slots():
    cfg = UniversalStateConfig(duration=1, fps=1)
    state = UniversalDeterministicEngine.calculate_trajectory(cfg)[0]
    with pytest.raises(ValueError, match="unknown slots"):
        UniversalDeterministicEngine.render_template("{{typo}}", state, cfg)
    with pytest.raises(ValueError, match="reserved slot"):
        UniversalDeterministicEngine.render_template("{{subject}}", state, cfg, {"subject": "replacement"})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration": 0},
        {"duration": float("nan")},
        {"fps": 0},
        {"start_pos": (0, 1), "end_pos": (1, 2, 3)},
        {"intensity_range": (2, 1)},
        {"intensity_cycles": -1},
        {"camera_distance": -1},
        {"camera_pitch_range": (float("nan"), 1)},
    ],
)
def test_invalid_configuration_is_rejected(kwargs):
    with pytest.raises(ValueError):
        UniversalStateConfig(**kwargs)
