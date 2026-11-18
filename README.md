<!-- nougen-readme-compiler: v1 -->

# 📜 NouGenScript

Universal Poly-Script Engine: Movie, TV, Playwriting, Comic, Email, TypeScript, JavaScript, and Python scripts.

## 📚 Contents
- [Overview](#overview)
- [Dual-Plane Invariant](#dual-plane-invariant)
- [Quick Start](#quick-start)
- [Universal Deterministic Calculated Templates (UDCT)](#universal-deterministic-calculated-templates-udct)
- [Hardcode Audit](#hardcode-audit)
- [File Architecture](#file-architecture)
- [License](#license)

## 🧠 Overview

**NouGenScript** is the universal, mathematically grounded script engine for the NouGen fleet, Veilverse productions, marketing infrastructure, and engineering workflows.

It handles **all script paradigms under one unified AST**:

1. **Movie Screenplays**: Feature screenplays, Scene Headings (`INT./EXT.`), action beats, transitions, and dual-plane prompter streams.
2. **Television Scripts**: Episodic TV, pilots, cold opens, multi-act structures (`ACT ONE` … `ACT FIVE`), and tag stingers.
3. **Playwriting & Theatre**: Stage plays, proscenium and black-box stage directions, character entrances/exits, and monologues.
4. **Comic Book Scripts**: Page-by-page, panel-by-panel comic scripts with visual descriptions, dialogue balloons, captions, and SFX.
5. **Email Outreach Scripts**: Marketing, cold outreach, and nurture sequences (Subject lines, Preview headers, Body, CTA buttons, and P.S. lines).
6. **Creator Video Scripts**: Talking Head, Short-Form Reel, and YouTube Long-Form with 3-second hook directives, retention gates, and pattern interrupts.
7. **Code Scripts (TypeScript, JavaScript, Python, Bash)**: Engineering scripts with syntax encapsulation, dependency detection, export tracking, and AST metadata.
8. **Dual-Plane Script Architecture (`DisplayPlane != SpeechPlane`)**: authored scripts decompose bijectively into talent-facing display elements (`DIRECTION`, `CUE`, `PAUSE`, `MEDIA`) and speech-recognition / voice-synthesis stream tokens (`SPOKEN`).
9. **SPITE Psychological Depth Engine**: character shadow-self tracking, volatility indices (0.0 … 1.0), teleological core motives, and subtext leakage detection across lines.
10. **Deterministic Persona & Behavioral Masks (`persona.py`)**: 25 composable behavioral masks including the **Dav1d Hip-Hop Mogul Voices** (`sosa`, `curtis`, `ye`, `hov`, `lupe`), and a 20-pack emotional spectrum (`ecstatic` … `enraged`) for delivery cues and somatic inflection.
11. **Elite 0.001% Narrative Validators (`validators.py` & `narrative_craft.py`)**: Mamet Auditing (Objective, Stakes, Urgency); Sorkin Cadence Analysis; the Thirty-Act Structure (the Dav3 Standard 30-Act feature architecture with meta-bridges); Mythic Noir Anti-Cliché (MCU quip purge and somatic power-cost laws); Causal Momentum (‘Therefore’ / ‘But’ vs ‘And then’).
12. **Kaedra Continuity & Teleological Planning (`core.py`, `templates.py`)**: `ContinuityTracker` (real-time state machine tracking props, active threads, locations, and character emotional parentheticals) and Backward-Causal Planning (reverse-engineering plotlines backwards from the locked ending).
13. **Dav1d Bayesian Instinct Engine & Reasoning Sandwich (`instincts.py`, `sandwich.py`)**: `InstinctRecorder` (asymptotically learned behavioral reflexes with Bayesian confidence scoring) and `ReasoningSandwich` (11-step outcome verification pipeline for production-ready screenplay assurance).

**Status**: Production Core Standard. **Organization**: Who-Visions & NouGenAi.

## 📌 Dual-Plane Invariant

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

## 🚀 Quick Start

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

## 📌 Universal Deterministic Calculated Templates (UDCT)

UDCT makes every output-affecting parameter explicit in `UniversalStateConfig`. The same configuration produces the same calculated frame states and canonical SHA-256 state hashes. Subject/action data, intensity curves, camera paths, and custom constants are configurable; unknown or malformed template slots fail instead of silently leaking into generated output.

```python
from nougenscript.udct import UniversalDeterministicEngine, UniversalStateConfig

config = UniversalStateConfig(
    duration=2,
    fps=24,
    subject="Warehouse robot",
    action="turn",
    start_pos=(0, 0, 0),
    end_pos=(4, 0, 2),
    camera_distance=7,
    intensity_cycles=2,
    custom_constants={"domain": {"site": "warehouse", "revision": 3}},
)
template = '{"frame":{{frame_index}},"position":[{{calc_position_x}},{{calc_position_y}},{{calc_position_z}}],"domain":{{domain}},"state_hash":"{{state_hash}}"}'
frames = UniversalDeterministicEngine.compile_full_sequence(
    template, config, sample_indices=[0, 24, 47]
)
```

Dynamic values are inserted as text and are never evaluated. Encode untrusted values for the target language before using them in source-code templates.

## 📌 Hardcode Audit

UDCT also provides a deterministic, read-only hardcode audit. Each repository declares the values that must be dynamic in a checked-in `.udct-policy.json` file. The audit scans tracked Git files only, reports stable path/line/column/rule/slot results, and exits with status 1 on a finding. It never rewrites source files.

```bash
nougenscript audit-dynamic . --json
nougenscript audit-dynamic https://github.com/OWNER/REPOSITORY --ref main --policy ./review-policy.json --json
```

`plan-dynamic` turns exact policy matches into a deterministic, value-free plan (location, slot, candidate expression, required import). Every plan entry requires review — a literal match may occur in a comment or a non-code context. It never edits the repository.

```bash
nougenscript plan-dynamic . --json
```

`apply-dynamic` has conservative Python, JavaScript/TypeScript, Go, and Java adapters for exact standalone string literals covered by the policy. Without `--write` it prints a value-free preview and a plan ID bound to hashes of the exact source/result files; pass that ID with `--write` to apply. Writes change only clean targets and validate resulting syntax. GitHub URLs remain read-only: clone the repository locally before applying a change.

```bash
nougenscript apply-dynamic ./service --json
nougenscript apply-dynamic ./service --write --confirm PLAN_ID --json
```

`suggest-dynamic` gives a read-only inventory without a policy: it looks for assignment-shaped service URLs, absolute paths, and operational limits, then reports likely environment-variable names. It redacts URL credentials, queries, and paths from previews, ignores secret-named symbols and `.env` files, and does not edit source. Treat heuristic findings as review candidates.

```bash
nougenscript suggest-dynamic ./service --json
nougenscript suggest-dynamic https://github.com/OWNER/REPOSITORY --ref main
nougenscript suggest-dynamic ./service --env-template > .env.example
```

## 🏗️ File Architecture

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

## 📄 License

Who Visions Source-Available License (v1.1) — see `LICENSE.md`. Note: `pyproject.toml` declares MIT, which does not match `LICENSE.md`; the license file is the authority here, and the mismatch needs the owner to resolve it.

## 🔗 Links

- [NouGenScript on GitHub (Who-Visions)](<https://github.com/Who-Visions/NouGenScript>)
- [NouGenScript on GitHub (nougenai)](<https://github.com/nougenai/NouGenScript>)
