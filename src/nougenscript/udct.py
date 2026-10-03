"""
NouGen Universal Deterministic Calculated Template (UDCT) Engine.
================================================================

Architecture Specification:
    UDCT = G(S, Theta, F, C)
    Output = T(calculated values), NOT Output = AI vibes.

The Four Pillars:
    1. Universal:
       Abstract parameters (DURATION, FPS, SUBJECT, INTENSITY, POSITION, VELOCITY, PHASE)
       independent of domain (video, screenplay, audio synth, UI physics, telemetry).
    2. Deterministic:
       T(x, s, c) = y.
       If x1 == x2 and s1 == s2 and c1 == c2, then T(x1, s1, c1) == T(x2, s2, c2).
       No random drift or subjective model variance.
    3. Calculated:
       All values derived from mathematical functions:
       - N = FPS * D
       - t_i = i / (N - 1)
       - x(t) = LERP(x0, x1, E(t))
       - v(t) = dx / dt
       - I(t) = I_min + (I_max - I_min) * sin^2(pi * t)
       - theta(t) = theta_0 + (theta_1 - theta_0) * E(t)
    4. Template:
       The template is merely the renderer for an underlying deterministic state machine.
       Language models and rendering engines only narrate or format the computed state.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Union


class EasingType(str, Enum):
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    SINUSOIDAL = "sinusoidal"


class MathFunctions:
    """Core deterministic mathematical primitives."""

    @staticmethod
    def normalized_time(index: int, total_steps: int) -> float:
        """t_i = i / (N - 1) for N > 1, else 0.0."""
        if total_steps <= 1:
            return 0.0
        return max(0.0, min(1.0, float(index) / float(total_steps - 1)))

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """Linear interpolation: a + (b - a) * t."""
        return a + (b - a) * t

    @staticmethod
    def ease(t: float, easing: Union[EasingType, str] = EasingType.LINEAR) -> float:
        """Apply deterministic easing curve E(t)."""
        t = max(0.0, min(1.0, t))
        e = EasingType(easing) if isinstance(easing, str) else easing

        if e == EasingType.LINEAR:
            return t
        elif e == EasingType.EASE_IN_QUAD:
            return t * t
        elif e == EasingType.EASE_OUT_QUAD:
            return t * (2.0 - t)
        elif e == EasingType.EASE_IN_OUT_QUAD:
            return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t
        elif e == EasingType.EASE_IN_CUBIC:
            return t * t * t
        elif e == EasingType.EASE_OUT_CUBIC:
            t1 = t - 1.0
            return t1 * t1 * t1 + 1.0
        elif e == EasingType.EASE_IN_OUT_CUBIC:
            return 4.0 * t * t * t if t < 0.5 else (t - 1.0) * (2.0 * t - 2.0) * (2.0 * t - 2.0) + 1.0
        elif e == EasingType.SINUSOIDAL:
            return (1.0 - math.cos(t * math.pi)) / 2.0
        return t

    @staticmethod
    def harmonic_intensity(t: float, i_min: float = 0.0, i_max: float = 1.0, cycles: float = 1.0) -> float:
        """I(t) = I_min + (I_max - I_min) * sin^2(pi * cycles * t)."""
        s = math.sin(math.pi * cycles * t)
        return i_min + (i_max - i_min) * (s * s)

    @staticmethod
    def orbit_camera(
        t: float,
        start_yaw: float = 0.0,
        end_yaw: float = 360.0,
        pitch_min: float = -15.0,
        pitch_max: float = 25.0,
        distance: float = 5.0,
    ) -> Dict[str, float]:
        """C(t) calculating camera azimuth, elevation, and 3D position."""
        yaw_deg = MathFunctions.lerp(start_yaw, end_yaw, t)
        yaw_rad = math.radians(yaw_deg)
        pitch_deg = pitch_min + (pitch_max - pitch_min) * math.sin(math.pi * t)
        pitch_rad = math.radians(pitch_deg)

        cx = distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        cy = distance * math.sin(pitch_rad)
        cz = distance * math.cos(pitch_rad) * math.cos(yaw_rad)

        return {
            "yaw": round(yaw_deg, 4),
            "pitch": round(pitch_deg, 4),
            "x": round(cx, 4),
            "y": round(cy, 4),
            "z": round(cz, 4),
        }


@dataclass(frozen=True)
class FrameCalculatedState:
    """Calculated deterministic snapshot for a discrete step/frame i."""
    index: int
    total_steps: int
    t: float
    eased_t: float
    position_x: float
    position_y: float
    position_z: float
    velocity_x: float
    velocity_y: float
    intensity: float
    phase_angle: float
    camera: Dict[str, float]
    state_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UniversalStateConfig:
    """Theta configuration parameters for UDCT = G(S, Theta, F, C)."""
    duration: float = 10.0
    fps: int = 30
    subject: str = "Subject"
    action: str = "transit"
    start_pos: Sequence[float] = (0.0, 0.0, 0.0)
    end_pos: Sequence[float] = (18.0, 0.0, 0.0)
    easing: EasingType = EasingType.EASE_IN_OUT_CUBIC
    camera_offset: float = 0.17
    intensity_range: Sequence[float] = (0.1, 1.0)
    custom_constants: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_frames(self) -> int:
        """N = FPS * D."""
        return max(1, int(round(self.fps * self.duration)))

    @property
    def delta_t(self) -> float:
        """Delta t in seconds = 1 / FPS."""
        return 1.0 / max(1, self.fps)


class UniversalDeterministicEngine:
    """Deterministic State Machine G(S, Theta, F, C).
    Calculates trajectories and evaluates template expressions without LLM drift.
    """

    @classmethod
    def calculate_trajectory(cls, config: UniversalStateConfig) -> List[FrameCalculatedState]:
        """Calculates exact kinematic and photometric state array for every frame."""
        n = config.total_frames
        dt = config.delta_t
        states: List[FrameCalculatedState] = []

        prev_x, prev_y = config.start_pos[0], config.start_pos[1]

        for i in range(n):
            t = MathFunctions.normalized_time(i, n)
            et = MathFunctions.ease(t, config.easing)

            # Positions
            px = MathFunctions.lerp(config.start_pos[0], config.end_pos[0], et)
            py = MathFunctions.lerp(config.start_pos[1], config.end_pos[1], et)
            pz = (
                MathFunctions.lerp(config.start_pos[2], config.end_pos[2], et)
                if len(config.start_pos) > 2 and len(config.end_pos) > 2
                else 0.0
            )

            # Velocity: v = (x_i - x_{i-1}) / dt
            vx = 0.0 if i == 0 else (px - prev_x) / dt
            vy = 0.0 if i == 0 else (py - prev_y) / dt
            prev_x, prev_y = px, py

            # Harmonic intensity
            i_min, i_max = config.intensity_range[0], config.intensity_range[1]
            intensity = MathFunctions.harmonic_intensity(t, i_min=i_min, i_max=i_max, cycles=1.0)

            # Phase angle in radians
            phase = (t * 2.0 * math.pi + config.camera_offset) % (2.0 * math.pi)

            # Camera orbit
            cam_t = (t + config.camera_offset) % 1.0
            cam = MathFunctions.orbit_camera(cam_t, start_yaw=0.0, end_yaw=360.0)

            # State hash invariant
            raw_signature = f"{i}:{n}:{round(t, 6)}:{round(px, 4)}:{round(py, 4)}:{round(vx, 4)}:{round(intensity, 4)}"
            state_hash = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()

            states.append(
                FrameCalculatedState(
                    index=i,
                    total_steps=n,
                    t=round(t, 6),
                    eased_t=round(et, 6),
                    position_x=round(px, 4),
                    position_y=round(py, 4),
                    position_z=round(pz, 4),
                    velocity_x=round(vx, 4),
                    velocity_y=round(vy, 4),
                    intensity=round(intensity, 4),
                    phase_angle=round(phase, 4),
                    camera=cam,
                    state_hash=state_hash,
                )
            )

        return states

    @classmethod
    def render_template(
        cls,
        template_str: str,
        state: FrameCalculatedState,
        config: UniversalStateConfig,
        custom_slots: Optional[Dict[str, str]] = None,
    ) -> str:
        """Renders template string by replacing slots with calculated math values.
        Supports {{slot}} syntax without third-party template dependencies.
        """
        replacements = {
            "{{frame_index}}": str(state.index),
            "{{total_frames}}": str(state.total_steps),
            "{{t}}": f"{state.t:.4f}",
            "{{eased_t}}": f"{state.eased_t:.4f}",
            "{{subject}}": config.subject,
            "{{action}}": config.action,
            "{{calc_position_x}}": f"{state.position_x:.4f}",
            "{{calc_position_y}}": f"{state.position_y:.4f}",
            "{{calc_position_z}}": f"{state.position_z:.4f}",
            "{{velocity_x}}": f"{state.velocity_x:.4f}",
            "{{velocity_y}}": f"{state.velocity_y:.4f}",
            "{{intensity}}": f"{state.intensity:.4f}",
            "{{phase}}": f"{state.phase_angle:.4f}",
            "{{calc_camera_yaw}}": f"{state.camera['yaw']:.2f}",
            "{{calc_camera_pitch}}": f"{state.camera['pitch']:.2f}",
            "{{calc_camera_x}}": f"{state.camera['x']:.2f}",
            "{{calc_camera_y}}": f"{state.camera['y']:.2f}",
            "{{calc_camera_z}}": f"{state.camera['z']:.2f}",
            "{{state_hash}}": state.state_hash,
        }

        if custom_slots:
            for k, v in custom_slots.items():
                replacements[f"{{{{{k}}}}}"] = str(v)

        rendered = template_str
        for k, v in replacements.items():
            rendered = rendered.replace(k, v)
        return rendered

    @classmethod
    def compile_full_sequence(
        cls,
        template_str: str,
        config: UniversalStateConfig,
        sample_indices: Optional[Sequence[int]] = None,
    ) -> List[str]:
        """Calculates trajectory and renders full or sampled sequence deterministically."""
        states = cls.calculate_trajectory(config)
        indices = sample_indices if sample_indices is not None else range(len(states))
        rendered_outputs = []
        for idx in indices:
            if 0 <= idx < len(states):
                rendered_outputs.append(cls.render_template(template_str, states[idx], config))
        return rendered_outputs
