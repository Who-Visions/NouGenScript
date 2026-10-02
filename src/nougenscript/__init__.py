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
from nougenscript.spite import SpiteProfile, SubtextAnalysisResult, SubtextAnalyzer

__version__ = "0.1.0"
__all__ = [
    "ClapDocument",
    "Cue",
    "Dialogue",
    "Direction",
    "DisplaySpan",
    "DualPlaneProjector",
    "FountainParser",
    "NodeType",
    "OpenClapSerializer",
    "Scene",
    "Screenplay",
    "ScriptNode",
    "SpiteProfile",
    "SpokenToken",
    "SubtextAnalysisResult",
    "SubtextAnalyzer",
]
