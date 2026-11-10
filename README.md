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

### Universal Deterministic Calculated Templates (UDCT)

UDCT makes every output-affecting parameter explicit in `UniversalStateConfig`.
The same configuration produces the same calculated frame states and canonical
SHA-256 state hashes. Subject/action data, intensity curves, camera paths, and
custom constants are configurable; unknown or malformed template slots fail
instead of silently leaking into generated output.

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

Dynamic values are inserted as text and are never evaluated. Encode untrusted
values for the target language before using them in source-code templates.

### Protect Git repositories from values that must be dynamic

UDCT also provides a deterministic, read-only hardcode audit. A generic scanner
cannot safely tell whether a literal is a protocol constant or an
environment-specific value, so each repository declares the values that must
be dynamic in a checked-in `.udct-policy.json` file. The audit scans tracked
Git files only, reports stable path/line/column/rule/slot results, and exits with
status 1 on a finding. It never rewrites source files.

```json
{
  "version": 1,
  "rules": [
    {
      "id": "service-api-origin",
      "literal": "https://api.example.invalid/v1",
      "paths": ["src/**/*.py", "src/**/*.ts"],
      "slot": "API_BASE_URL",
      "rationale": "The API origin varies by deployment environment."
    }
  ]
}
```

Point the command at a local checkout or GitHub repository. Remote repositories
are shallow-cloned to a temporary directory, scanned as data, and removed when
the command exits; no remote branch is changed. An explicit policy may live
outside the target repository, which lets a user audit public source without
adding configuration to it. Private GitHub access uses `GITHUB_TOKEN` from the
process environment and never writes it to the checkout.

```bash
nougenscript audit-dynamic . --json
nougenscript audit-dynamic https://github.com/OWNER/REPOSITORY \
  --ref main --policy ./review-policy.json --json
```

Findings identify the UDCT slot to use (for example, `{{API_BASE_URL}}`); a
reviewer makes the source change explicitly and chooses the correct
target-language configuration and escaping. Empty policies are valid. This is
a policy-driven guard, not a heuristic ban on constants, a credentials
scanner, or an automatic rewriter.

To turn those exact policy matches into a deterministic, value-free plan, use
`plan-dynamic`. It includes each location, slot, candidate expression, and any
required import. Unknown file types are marked for manual resolution, and every
plan entry requires review because a literal match may occur in a comment or a
non-code context. It never edits the repository.

```bash
nougenscript plan-dynamic . --json
```

For local repositories, `apply-dynamic` has conservative Python,
JavaScript/TypeScript, Go, and Java adapters for exact standalone string
literals covered by the policy. Python changes skip comments, docstrings,
annotations, and unmatched contexts. JavaScript/TypeScript, Go, and Java use
bundled Tree-sitter grammars and only rewrite recognized runtime initializer
contexts; escaped literals and unsupported expressions remain unresolved.
JavaScript/TypeScript targets Node.js `process.env`; Go targets `os.LookupEnv`
(adding the standard-library import when needed); Java targets a non-null
`System.getenv` value using `java.util.Objects.requireNonNull`. Go constants
and Java `final` or implicit interface constants remain unresolved. Review the
target runtime and type behavior before applying. None of these adapters
executes the repository. Without `--write`, the command
prints a value-free preview and a plan ID bound to hashes of the exact
source/result files. Review `plan-dynamic` and the preview, then pass that ID
with `--write`. Writes change only clean targets and validate resulting syntax.
Supply the named environment variables before running the application. GitHub
URLs remain read-only: clone the repository locally before applying a change.

```bash
nougenscript apply-dynamic ./service --json
nougenscript apply-dynamic ./service --write --confirm PLAN_ID --json
```

Automatic application is currently limited to the Python, Node.js-oriented
JavaScript/TypeScript, Go, and Java contexts described above. Other languages
receive reviewable resolution plans, but are not rewritten until UDCT has a
language-aware adapter and syntax validation for them. Each adapter leaves
unresolved syntax it cannot map confidently; reviewers must validate
application-specific runtime behavior.

For an initial read-only inventory without a policy, use `suggest-dynamic`.
It looks for assignment-shaped service URLs, absolute paths, and operational
limits, then reports likely environment-variable names and language-specific
expressions where UDCT has a safe standard. It redacts URL credentials,
queries, and paths from previews, ignores secret-named symbols and `.env`
files, and does not edit source. Treat heuristic findings as review candidates;
the owning project decides defaults, validation, and configuration semantics.

```bash
nougenscript suggest-dynamic ./service --json
nougenscript suggest-dynamic https://github.com/OWNER/REPOSITORY --ref main
nougenscript suggest-dynamic ./service --env-template > .env.example
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


