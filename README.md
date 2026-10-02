# 📜 NouGenScript: Universal Poly-Script Engine

> **Organization**: Who-Visions & NouGenAi  
> **Status**: Production Core Standard  
> **Repository**: [`Who-Visions/NouGenScript`](https://github.com/Who-Visions/NouGenScript) & [`nougenai/NouGenScript`](https://github.com/nougenai/NouGenScript)  

---

## 🏛️ Prime Purpose & Vision
**NouGenScript** is the universal, mathematically grounded script engine for the NouGen fleet, Veilverse productions, marketing infrastructure, and engineering workflows.

It handles **all script paradigms under one unified AST**:
1. **Movie Screenplays**: Feature screenplays, Scene Headings (`INT./EXT.`), action beats, transitions, and dual-plane prompter streams.
2. **Television Scripts**: Episodic TV, pilots, cold opens, multi-act structures (`ACT ONE` $\dots$ `ACT FIVE`), and tag stingers.
3. **Playwriting & Theatre**: Stage plays, proscenium and black-box stage directions, character entrances/exits, and monologues.
4. **Comic Book Scripts**: Page-by-page, panel-by-panel comic scripts with visual descriptions, dialogue balloons, captions, and SFX.
5. **Email Outreach Scripts**: Marketing, cold outreach, and nurture sequences (Subject lines, Preview headers, Body, CTA buttons, and P.S. lines).
6. **Code Scripts (TypeScript, JavaScript, Python, Bash)**: Engineering scripts with syntax encapsulation, dependency detection, export tracking, and AST metadata.
7. **Dual-Plane Script Architecture (`DisplayPlane != SpeechPlane`)**:
   - Authored scripts decompose bijectively into talent-facing display elements (`DIRECTION`, `CUE`, `PAUSE`, `MEDIA`) and speech-recognition / voice-synthesis stream tokens (`SPOKEN`).
8. **SPITE Psychological Depth Engine**:
   - Character shadow-self tracking, volatility indices ($0.0 \dots 1.0$), teleological core motives, and subtext leakage detection across lines.
9. **Deterministic Persona & Behavioral Masks (`persona.py`)**:
   - Audience / writer persona resolution with deterministic SHA-256 fingerprinting.
   - 20-Pack composable behavioral masks (`stoic`, `villain`, `witty`, `charming`, `gremlin`, etc.) for director/actor prompts.
   - 20-Pack emotional spectrum (`ecstatic` $\dots$ `enraged`) for delivery cues and somatic inflection.
10. **OpenClap Interchange Format (`.clap`)**:
   - Universal multi-document YAML serialization compatible with OpenClap multi-track audio-visual timelines (video, dialogue, sound, music).
11. **Command-Line Interface (`nougenscript`)**:
   - Unified CLI for parsing, poly-dialect compilation, dual-plane projection, SPITE subtext evaluation, OpenClap bundling, and persona mask composition.

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
from nougenscript import Screenplay, SpiteProfile, SubtextAnalyzer, CharacterPersona, blend, get_emotion

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

# Compose Behavioral Masks & Emotions
char = CharacterPersona(
    character_name="CORBIN",
    masks=blend("stoic", "villain"),
    current_emotion=get_emotion("furious"),
    taboo_words={"mercy"}
)
line = char.format_dialogue("The throne belongs to the dust.")
print(line.parenthetical)  # '(Furious, blunt, biting, demanding accountability.)'
```

### CLI Usage
```bash
# Parse screenplay
nougenscript parse script.fountain

# Decompose planes and inspect word re-anchoring
nougenscript dual-plane script.fountain --reanchor 12

# Run SPITE subtext analysis
nougenscript spite script.fountain --character XOAH --volatility 0.8

# Export to OpenClap (.clap)
nougenscript export-clap script.fountain -o scene1.clap

# Compose behavioral masks
nougenscript persona --blend stoic witty --emotion ecstatic --character XOAH

# Compile and inspect PolyScript dialects (TV, Comic, Play, Email, Code)
nougenscript poly tv episode1.tv
nougenscript poly comic issue1.comic
nougenscript poly play hamlet_act1.play
nougenscript poly email outreach_sequence.txt
nougenscript poly typescript app.ts
nougenscript poly python daemon.py
```

---

## 📦 File Architecture
- `src/nougenscript/core.py`: Canonical AST nodes (`Scene`, `Dialogue`, `Direction`, `Cue`).
- `src/nougenscript/dialects.py`: PolyScript domain matrix (`NARRATIVE_FILM`, `TELEVISION`, `THEATRE`, `COMIC_BOOK`, `EMAIL_CAMPAIGN`, `CODE_TYPESCRIPT`, `CODE_JAVASCRIPT`, `CODE_PYTHON`, `CODE_SHELL`).
- `src/nougenscript/engine.py`: Universal poly-script compiler, parser, and code encapsulator.
- `src/nougenscript/dual_plane.py`: Bijective Display vs Speech plane projector and word anchor locator.
- `src/nougenscript/spite.py`: SPITE psychological depth, character profiling, and subtext analyzer.
- `src/nougenscript/persona.py`: Signals, deterministic persona resolver, 20 behavioral masks, 20 emotions, and character contract.
- `src/nougenscript/openclap.py`: Universal `.clap` multi-document YAML stream serializer and parser.
- `src/nougenscript/parser.py`: Fast, deterministic Fountain and text screenplay parser.
- `src/nougenscript/cli.py`: Unified command-line interface with `poly` multi-dialect support.
- `tests/`: Complete pytest test suite verifying all parser, dual-plane, SPITE, persona, and poly-dialect invariants.


