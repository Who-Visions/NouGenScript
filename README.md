# 📜 NouGenScript: Universal AI Screenplay & Dual-Plane Dramatic Script Engine

> **Organization**: Who-Visions & NouGenAi  
> **Status**: Production Core Standard  
> **Repository**: [`Who-Visions/NouGenScript`](https://github.com/Who-Visions/NouGenScript) & [`nougenai/NouGenScript`](https://github.com/nougenai/NouGenScript)  

---

## 🏛️ Prime Purpose & Vision
**NouGenScript** is the unified, mathematically grounded dramatic screenplay, playwriting, and voice-teleprompter script engine for the NouGen fleet and Veilverse cinematic productions.

It combines:
1. **Dual-Plane Script Architecture (`DisplayPlane != SpeechPlane`)**:
   - Authored scripts decompose bijectively into talent-facing display elements (`DIRECTION`, `CUE`, `PAUSE`, `MEDIA`) and speech-recognition / voice-synthesis stream tokens (`SPOKEN`).
2. **SPITE Psychological Depth Engine**:
   - Character shadow-self tracking, volatility indices ($0.0 \dots 1.0$), teleological core motives, and subtext leakage detection across lines.
3. **OpenClap Interchange Format (`.clap`)**:
   - Universal multi-document YAML serialization compatible with OpenClap multi-track audio-visual timelines (video, dialogue, sound, music).
4. **Fountain & Screenplay Syntax Parser**:
   - Full parser for Scene Headings (`INT./EXT.`), Characters, Parentheticals, Dialogue, Transitions, and Action beats.
5. **Deterministic Information Dynamics & Cue Verification**:
   - Cryptographic SHA-256 script hashing, cue receipts, and zero-context-bloat AST representations.

---

## 📐 Dual-Plane Invariant
```
Authored Script Source (Fountain / Markdown / YAML)
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[ DISPLAY PLANE ]           [ SPEECH PLANE ]
• Stage Directions          • Normalized Lexical Tokens
• Camera / Lighting Cues    • Phonetic Alignment Spans
• Actor Affect Markers      • Direct Word Anchor Targets
• Scene Headings            • Zero-Direction Latency Stream
```

---

## 🚀 Quickstart

### Python Engine
```python
from nougenscript import Screenplay, SpiteProfile, SubtextAnalyzer

# Parse a script
script = Screenplay.from_fountain("""
EXT. NEO-DETROIT UNDERPASS - NIGHT

ELISÉE
(whispering, trembling)
Everything is fine. The code is sealed.

Corbin steps from the shadows.
""")

# Evaluate subtext
profile = SpiteProfile(
    character="ELISÉE",
    shadow_self="Terror of consensus reality dissolving into chaotic noise",
    volatility=0.65
)

analysis = SubtextAnalyzer.analyze(script.dialogue_lines[0], profile)
print(analysis.markers)  # ['Defensive Absolutism: fine']
print(analysis.leakage_detected)  # True
```

---

## 📦 File Architecture
- `src/nougenscript/core.py`: Canonical AST nodes (`Scene`, `Dialogue`, `Direction`, `Cue`).
- `src/nougenscript/dual_plane.py`: Bijective Display vs Speech plane projector and word anchor locator.
- `src/nougenscript/spite.py`: SPITE psychological depth, character profiling, and subtext analyzer.
- `src/nougenscript/openclap.py`: Universal `.clap` multi-document YAML stream serializer and parser.
- `src/nougenscript/parser.py`: Fast, deterministic Fountain and text screenplay parser.
- `tests/`: Complete pytest test suite verifying all parser, dual-plane, and SPITE invariants.
