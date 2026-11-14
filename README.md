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
6. **Creator Video Scripts**: Talking Head, Short-Form Reel, and YouTube Long-Form with 3-second hook directives, retention gates, and pattern interrupts.
7. **Code Scripts (TypeScript, JavaScript, Python, Bash)**: Engineering scripts with syntax encapsulation, dependency detection, export tracking, and AST metadata.
8. **Dual-Plane Script Architecture (`DisplayPlane != SpeechPlane`)**:
   - Authored scripts decompose bijectively into talent-facing display elements (`DIRECTION`, `CUE`, `PAUSE`, `MEDIA`) and speech-recognition / voice-synthesis stream tokens (`SPOKEN`).
9. **SPITE Psychological Depth Engine**:
   - Character shadow-self tracking, volatility indices ($0.0 \dots 1.0$), teleological core motives, and subtext leakage detection across lines.
10. **Deterministic Persona & Behavioral Masks (`persona.py`)**:
   - 25 Composable behavioral masks including the **Dav1d Hip-Hop Mogul Voices** (`sosa`, `curtis`, `ye`, `hov`, `lupe`).
   - 20-Pack emotional spectrum (`ecstatic` $\dots$ `enraged`) for delivery cues and somatic inflection.
11. **Elite 0.001% Narrative Validators (`validators.py` & `narrative_craft.py`)**:
   - **Mamet Auditing**: 3 non-negotiable scene questions (Objective, Stakes, Urgency).
   - **Sorkin Cadence Analysis**: Dialogue velocity, turn distribution, repetition rhythms.
   - **Thirty-Act Structure**: The Dav3 Standard 30-Act feature architecture with meta-bridges.
   - **Mythic Noir Anti-Cliché**: MCU quip purge and somatic power-cost laws.
   - **Causal Momentum**: 'Therefore' / 'But' vs 'And then' narrative propulsion.
12. **Kaedra Continuity & Teleological Planning (`core.py`, `templates.py`)**:
   - **ContinuityTracker**: Real-time state machine tracking props, active threads, locations, and character emotional parentheticals.
   - **Backward-Causal Planning**: Reverse-engineering plotlines backwards from the locked ending.
13. **Dav1d Bayesian Instinct Engine & Reasoning Sandwich (`instincts.py`, `sandwich.py`)**:
   - **InstinctRecorder**: Asymptotically learned behavioral reflexes with Bayesian confidence scoring.
   - **ReasoningSandwich**: 11-step outcome verification pipeline for production-ready screenplay assurance.

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
from nougenscript import (
    Screenplay,
    SpiteProfile,
    SubtextAnalyzer,
    CharacterPersona,
    blend,
    get_emotion,
    ContinuityTracker,
    generate_backward_plan,
    generate_thirty_act_scaffold,
    ReasoningSandwich,
    InstinctRecorder,
)

# 1. Backward-Causal Teleological Planning
plan = generate_backward_plan(
    title="Project Nightfall",
    terminal_climax="Corbin burns the archive to prevent the uplink."
)

# 2. 11-Step Reasoning Sandwich Audit
result = ReasoningSandwich.audit_script_outcome(
    spec="Feature Noir scene compliance",
    script_text="INT. ARCHIVE - NIGHT\nCORBIN\nThe resonance burns through my collar.\n"
)
print("Sandwich Status:", result.overall_passed)

# 3. Dav1d Mogul Persona Composition
char = CharacterPersona(
    character_name="CORBIN",
    masks=blend("hov", "curtis"),
    current_emotion=get_emotion("focused")
)
```

### CLI Usage
```bash
# Elite Craft & Status Auditing
nougenscript craft screenplay.fountain
nougenscript status-map screenplay.fountain

# 11-Step Reasoning Sandwich
nougenscript sandwich screenplay.fountain --spec "Feature Noir Act I"

# Bayesian Instincts
nougenscript instinct record --category anti_cliche --pattern "Well that just happened" --response "Purge MCU quip."
nougenscript instinct list

# Scaffold Generators
nougenscript generate thirty-acts --title "Veil City" --protagonist "CORBIN" --shadow "THE ARCHITECT"
nougenscript generate backward-plan --title "Veil City"
nougenscript generate talking-head --topic "Zero-Cost Swarm Architecture"
```

---

## 📦 File Architecture
- `src/nougenscript/core.py`: Canonical AST nodes (`Scene`, `Dialogue`, `Direction`, `Cue`, `ContinuityTracker`).
- `src/nougenscript/dialects.py`: PolyScript domain matrix (`NARRATIVE_FILM`, `CREATOR_VIDEO`, `TELEVISION`, `THEATRE`, `COMIC_BOOK`, `EMAIL_CAMPAIGN`, `CODE_TYPESCRIPT`, `CODE_PYTHON`).
- `src/nougenscript/engine.py`: Universal poly-script compiler, parser, and code encapsulator.
- `src/nougenscript/dual_plane.py`: Bijective Display vs Speech plane projector and word anchor locator.
- `src/nougenscript/spite.py`: SPITE psychological depth, character profiling, and subtext analyzer.
- `src/nougenscript/persona.py`: Signals, deterministic persona resolver, 25 behavioral masks (including `sosa`, `curtis`, `ye`, `hov`, `lupe`), and 20 emotions.
- `src/nougenscript/instincts.py`: Dav1d Bayesian-lite adaptive behavioral instinct recorder.
- `src/nougenscript/sandwich.py`: Dav1d 11-step reasoning sandwich verification engine.
- `src/nougenscript/narrative_craft.py`: Top 0.001% master craft suite (Mamet, Sorkin cadence, causality, status transactions, recursion).
- `src/nougenscript/validators.py`: Elite dialect validators (Save the Cat, Harmon Circle, 30-Act, Mythic Noir, Video Retention).
- `src/nougenscript/templates.py`: Scaffolds (30-Act, Harmon Circle, Aristotle Unity, Creator Video, Backward-Causal).
- `src/nougenscript/cli.py`: Unified command-line interface with `sandwich`, `instinct`, `craft`, `generate`, and `poly`.
- `tests/`: 75 comprehensive tests covering all engines and validators.



