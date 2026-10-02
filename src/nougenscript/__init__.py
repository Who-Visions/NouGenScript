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
from nougenscript.dialects import (
    CodeScriptSpec,
    ComicPage,
    ComicPanel,
    EmailSection,
    PolyScript,
    ScriptDomain,
    ScriptKind,
    ScriptMeta,
    TVAct,
)
from nougenscript.dual_plane import DisplaySpan, DualPlaneProjector, SpokenToken
from nougenscript.engine import UniversalScriptEngine
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

__version__ = "0.3.0"
__all__ = [
    "Audience",
    "BEHAVIORAL_MASKS",
    "CharacterPersona",
    "ClapDocument",
    "CodeScriptSpec",
    "ComicPage",
    "ComicPanel",
    "Cue",
    "Dialogue",
    "Direction",
    "DisplaySpan",
    "DualPlaneProjector",
    "EMOTIONS",
    "EmailSection",
    "EmotionState",
    "FountainParser",
    "MaskBlend",
    "NodeType",
    "OpenClapSerializer",
    "Persona",
    "PolyScript",
    "Scene",
    "Screenplay",
    "ScriptDomain",
    "ScriptKind",
    "ScriptMeta",
    "ScriptNode",
    "Signals",
    "SpiteProfile",
    "SpokenToken",
    "SubtextAnalysisResult",
    "SubtextAnalyzer",
    "TVAct",
    "UniversalScriptEngine",
    "blend",
    "get_emotion",
    "get_mask",
    "list_masks",
    "resolve",
]


