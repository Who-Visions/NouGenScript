"""NouGenScript: Universal AI Screenplay & Dual-Plane Dramatic Script Engine."""

from nougenscript.core import (
    Cue,
    Dialogue,
    Direction,
    NodeType,
    Scene,
    Screenplay,
    ScriptNode,
)
from nougenscript.dual_plane import DisplaySpan, DualPlaneProjector, SpokenToken
from nougenscript.openclap import ClapDocument, OpenClapSerializer
from nougenscript.parser import FountainParser
from nougenscript.persona import (
    BEHAVIORAL_MASKS,
    EMOTIONS,
    Audience,
    CharacterPersona,
    EmotionState,
    MaskBlend,
    Persona,
    Signals,
    blend,
    get_emotion,
    get_mask,
    list_masks,
    resolve,
)
from nougenscript.spite import SpiteProfile, SubtextAnalysisResult, SubtextAnalyzer

__version__ = "0.1.0"
__all__ = [
    "Audience",
    "BEHAVIORAL_MASKS",
    "CharacterPersona",
    "ClapDocument",
    "Cue",
    "Dialogue",
    "Direction",
    "DisplaySpan",
    "DualPlaneProjector",
    "EMOTIONS",
    "EmotionState",
    "FountainParser",
    "MaskBlend",
    "NodeType",
    "OpenClapSerializer",
    "Persona",
    "Scene",
    "Screenplay",
    "ScriptNode",
    "Signals",
    "SpiteProfile",
    "SpokenToken",
    "SubtextAnalysisResult",
    "SubtextAnalyzer",
    "blend",
    "get_emotion",
    "get_mask",
    "list_masks",
    "resolve",
]

