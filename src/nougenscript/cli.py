#!/usr/bin/env python3
"""NouGenScript Command-Line Interface.

Universal script compiler, dual-plane prompter, psychological depth engine,
OpenClap (.clap) bundler, poly-script dialect router, elite validators, and
scaffold generators:
- Movies, TV episodes, Playwrights, Comic books, Emails, TypeScript, JavaScript, Python.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nougenscript import (
    DualPlaneProjector,
    FountainParser,
    MasterCraftSuite,
    MametAuditor,
    StatusTracker,
    CadenceAnalyzer,
    OpenClapSerializer,
    PolyScript,
    Screenplay,
    SpiteProfile,
    SubtextAnalyzer,
    UniversalScriptEngine,
    blend,
    get_emotion,
    list_masks,
    resolve,
    Signals,
    # v0.4.0 & v0.5.0 validators + templates
    ScriptValidator,
    generate_beat_sheet,
    generate_story_circle,
    generate_pas_template,
    generate_bab_template,
    generate_hso_template,
    generate_unity_outline,
    generate_talking_head_template,
    generate_short_form_reel_template,
    generate_youtube_longform_template,
    generate_thirty_act_scaffold,
    generate_backward_plan,
    InstinctRecorder,
    ReasoningSandwich,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="nougenscript",
        description="Universal Poly-Script Engine: Movies, TV, Plays, Comics, Emails, TypeScript, JavaScript, Python."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. Parse Fountain / Movie Screenplay
    p_parse = sub.add_parser("parse", help="Parse Fountain or screenplay text into AST nodes.")
    p_parse.add_argument("file", type=Path, help="Path to screenplay file (.fountain, .txt)")
    p_parse.add_argument("--json", action="store_true", help="Output AST in JSON")

    # 2. Dual Plane Projection
    p_dual = sub.add_parser("dual-plane", help="Decompose screenplay into DisplayPlane vs SpeechPlane.")
    p_dual.add_argument("file", type=Path, help="Path to screenplay file")
    p_dual.add_argument("--reanchor", type=int, help="Test direct word index re-anchoring")

    # 3. SPITE Subtext Analysis
    p_spite = sub.add_parser("spite", help="Evaluate line-by-line dialogue subtext and psychological leakage.")
    p_spite.add_argument("file", type=Path, help="Path to screenplay file")
    p_spite.add_argument("--character", required=True, help="Character name to evaluate")
    p_spite.add_argument("--volatility", type=float, default=0.5, help="Character volatility index (0.0 to 1.0)")
    p_spite.add_argument("--shadow", default="", help="Character shadow self definition")

    # 4. OpenClap Export
    p_clap = sub.add_parser("export-clap", help="Export screenplay to OpenClap (.clap) multi-track stream.")
    p_clap.add_argument("file", type=Path, help="Path to screenplay file")
    p_clap.add_argument("-o", "--output", type=Path, required=True, help="Output .clap file path")
    p_clap.add_argument("--title", default="Untitled Film", help="Project title")

    # 5. Persona Resolution & Directorial Masks
    p_persona = sub.add_parser("persona", help="Resolve audience/character persona and compose behavioral masks.")
    p_persona.add_argument("--text", action="append", default=[], help="Sample dialogue or instruction text")
    p_persona.add_argument("--masks", action="store_true", help="List all available 20 behavioral masks")
    p_persona.add_argument("--blend", nargs="+", help="Blend behavioral masks (e.g. --blend stoic witty)")
    p_persona.add_argument("--emotion", help="Set active emotional state (e.g. ecstatic, anxious, enraged)")
    p_persona.add_argument("--character", help="Generate prompt directives for character persona")
    p_persona.add_argument("--json", action="store_true", help="Output JSON structured format")

    # 6. Poly-Script Dialects (TV, Comic, Play, Email, Code, Creator Video)
    p_poly = sub.add_parser("poly", help="Compile or inspect poly-script formats (tv, play, comic, email, video, reel, youtube, code).")
    p_poly.add_argument("type", choices=["tv", "play", "comic", "email", "video", "reel", "youtube", "code", "typescript", "javascript", "python"],
                        help="Target script dialect")
    p_poly.add_argument("file", type=Path, help="Script source file")
    p_poly.add_argument("--title", default="Untitled PolyScript", help="Project title")
    p_poly.add_argument("--lang", default="python", help="Language for code scripts (typescript, javascript, python, bash)")
    p_poly.add_argument("--json", action="store_true", help="Output JSON summary")

    # 7. Validate — Elite quality gates (Screenplay, TV, Comic, Email, Video, Code)
    p_val = sub.add_parser("validate", help="Run top .001%% narrative validators on a script.")
    p_val.add_argument("type", choices=["movie", "tv", "play", "comic", "email", "video", "reel", "youtube", "code", "typescript", "javascript", "python"],
                       help="Script dialect to validate")
    p_val.add_argument("file", type=Path, help="Script source file")
    p_val.add_argument("--title", default="Untitled", help="Project title")
    p_val.add_argument("--json", action="store_true", help="Output validation report as JSON")

    # 8. Generate — Scaffold generators
    p_gen = sub.add_parser("generate", help="Generate elite framework scaffolds (beat-sheet, circle, email, play, video, reel, youtube, thirty-acts, backward-plan).")
    p_gen.add_argument("template", choices=["beat-sheet", "story-circle", "pas", "bab", "hso", "unity-play", "talking-head", "reel", "youtube", "thirty-acts", "backward-plan"],
                       help="Template to generate")
    p_gen.add_argument("--title", default="Untitled", help="Project title")
    p_gen.add_argument("--protagonist", default="HERO", help="Protagonist name (for story-circle or thirty-acts)")
    p_gen.add_argument("--shadow", default="THE SHADOW", help="Antagonist / Shadow self (for thirty-acts)")
    p_gen.add_argument("--terminal-climax", default="The protagonist destroys the central machine by sacrificing their own neural implant.", help="Terminal climax (for backward-plan)")
    p_gen.add_argument("--opening-ground", default="A low-level technician living under the quiet surveillance state.", help="Opening ground (for backward-plan)")
    p_gen.add_argument("--topic", default="your challenge", help="Topic (for email or video templates)")
    p_gen.add_argument("--location", default="A cramped apartment kitchen", help="Location (for unity-play)")
    p_gen.add_argument("--json", action="store_true", help="Output as JSON")

    # 9. Top 0.001% Master Craft Audit (Mamet, Cadence, Causality, Status, Recursion)
    p_craft = sub.add_parser("craft", help="Run top 0.001% master craft audit (Mamet, Sorkin cadence, causality, status).")
    p_craft.add_argument("file", type=Path, help="Path to screenplay file")
    p_craft.add_argument("--json", action="store_true", help="Output JSON structured report")

    # 10. Status Transaction Map
    p_stat = sub.add_parser("status-map", help="Map line-by-line power transactions and peripeteia status reversals.")
    p_stat.add_argument("file", type=Path, help="Path to screenplay file")
    p_stat.add_argument("--json", action="store_true", help="Output JSON status trace")

    # 11. Reasoning Sandwich (Dav1d 11-step audit loop)
    p_sand = sub.add_parser("sandwich", help="Run Dav1d's 11-step prompt reasoning sandwich on a script.")
    p_sand.add_argument("file", type=Path, help="Path to screenplay file")
    p_sand.add_argument("--spec", default="Feature-length cinematic screenplay audit", help="Target outcome specification")
    p_sand.add_argument("--json", action="store_true", help="Output JSON audit trace")

    # 12. Instinct Recorder & Memory
    p_inst = sub.add_parser("instinct", help="Query or record adaptive behavioral instincts.")
    p_inst.add_argument("action", choices=["list", "record", "context"], help="Action to perform")
    p_inst.add_argument("--category", default=None, help="Instinct category (e.g. dialogue, pacing)")
    p_inst.add_argument("--pattern", default=None, help="Trigger pattern (for record)")
    p_inst.add_argument("--response", default=None, help="Reflex response (for record)")
    # 13. NouGenMorph & Joyce Recursion & Evidence Compiler
    p_morph = sub.add_parser("morph", help="NouGenMorph cognitive ingestion, evidence compiler, Joyce recursion loop, and portmanteau decomposition.")
    p_morph.add_argument("mode", choices=["joyce", "eval", "decompose", "compile"], help="Morph mode to run")
    p_morph.add_argument("--file", type=Path, default=None, help="Input screenplay or text file")
    p_morph.add_argument("--unit", default="riverrun", help="Semantic unit token to compile mathematically")
    p_morph.add_argument("--provenance", default="archive.org/stream/in.ernet.dli.2015.207614", help="Provenance source label")
    p_morph.add_argument("--title", default="Finnegans Recirculation", help="Title of morphed script")
    p_morph.add_argument("--word", default=None, help="Single word/portmanteau to decompose")
    p_morph.add_argument("--json", action="store_true", help="Output raw JSON analysis")

    # 14. Universal Deterministic Calculated Templates (UDCT)
    p_udct = sub.add_parser("udct", help="Universal Deterministic Calculated Template engine: Output = T(calculated values).")
    p_udct.add_argument("--duration", type=float, default=10.0, help="Duration in seconds (e.g. 10.0)")
    p_udct.add_argument("--fps", type=int, default=30, help="Frames / steps per second (e.g. 30)")
    p_udct.add_argument("--subject", default="Xoah", help="Universal subject name (Xoah, Ravenous, Camera, UI, Synth)")
    p_udct.add_argument("--action", default="sprint", help="Action / verb (sprint, pan, modulate)")
    p_udct.add_argument("--start", type=float, default=0.0, help="Start position scalar")
    p_udct.add_argument("--end", type=float, default=18.0, help="End position scalar")
    p_udct.add_argument("--easing", default="ease_in_out_cubic", choices=["linear", "ease_in_quad", "ease_out_quad", "ease_in_out_quad", "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic", "sinusoidal"], help="Mathematical easing curve")
    p_udct.add_argument("--camera-offset", type=float, default=0.17, help="Camera phase offset")
    p_udct.add_argument("--frames", nargs="+", type=int, default=[0, 150, 299], help="Specific frame indices to sample and render")
    p_udct.add_argument("--json", action="store_true", help="Output raw calculated state machine snapshots as JSON")

    args = parser.parse_args(argv)

    if args.command == "parse":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        if args.json:
            print(json.dumps(sp.to_dict(), indent=2))
        else:
            print(f"🎬 Screenplay: {len(sp.scenes)} scenes, {len(sp.dialogue_lines)} dialogue lines, hash={sp.script_hash}")
            for sc in sp.scenes:
                print(f"  • {sc.heading} ({len(sc.dialogues)} lines)")
        return 0

    if args.command == "dual-plane":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        dp = DualPlaneProjector.project(sp)
        print(f"📐 Dual-Plane Projection for script {sp.script_hash}:")
        print(f"  • Display Plane: {len(dp.display_plane.spans)} spans (visible text + directions)")
        print(f"  • Speech Plane:  {len(dp.speech_plane.tokens)} spoken phonetic tokens")
        if args.reanchor is not None:
            anchor = dp.reanchor_by_word_index(args.reanchor)
            print(f"  🎯 Re-anchored to word index {args.reanchor}: {anchor}")
        return 0

    if args.command == "spite":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        profile = SpiteProfile(
            character=args.character.upper(),
            shadow_self=args.shadow or "Unspoken subconscious trauma",
            volatility=args.volatility
        )
        print(f"🧠 SPITE Subtext Analysis for {profile.character} (Volatility: {profile.volatility}):")
        lines = [d for d in sp.dialogue_lines if d.character.upper() == profile.character]
        if not lines:
            print(f"  ⚠️ No dialogue found for character '{profile.character}'")
            return 1
        for d in lines:
            res = SubtextAnalyzer.analyze(d, profile)
            leakage_icon = "🚨 LEAKAGE" if res.leakage_detected else "🛡️ REPRESSED"
            print(f"  [{leakage_icon}] \"{d.text}\"")
            for m in res.markers:
                print(f"      ↳ {m}")
        return 0

    if args.command == "export-clap":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        doc = OpenClapSerializer.to_clap(sp, title=args.title)
        OpenClapSerializer.export_clap_bundle(doc, args.output)
        print(f"🎬 Exported OpenClap bundle to {args.output} ({args.output.stat().st_size} bytes)")
        return 0

    if args.command == "persona":
        if args.masks:
            print("=== Available Behavioral Masks (20-Pack) ===")
            for m in list_masks():
                print(f"  • {m}")
            return 0

        if args.blend:
            b = blend(*args.blend)
            em = get_emotion(args.emotion) if args.emotion else None
            if args.json:
                out = {"masks": b.mask_names, "traits": b.traits, "styles": b.styles}
                if em:
                    out["emotion"] = em.__dict__
                print(json.dumps(out, indent=2))
            else:
                print(b.system_prompt(args.character))
                if em:
                    print(f"Active Emotion: {em.name.upper()} ({em.valence}) -> Counterpart: {em.opposite}")
                    print(f"Direction Cue: {em.direction_cue()}")
            return 0

        texts = args.text or ["Write the screenplay scene where Xoah confronts Corbin in the dark matter veil."]
        sig = Signals.from_texts(texts)
        p = resolve(sig)
        if args.json:
            print(json.dumps(p.__dict__, indent=2, default=list))
        else:
            print(f"🎭 Resolved Persona: audience={p.audience}, market={p.market}, register={p.register}")
            print(p.system_prompt())
        return 0

    if args.command == "poly":
        content = args.file.read_text(encoding="utf-8")
        t = args.type.lower()
        poly_obj: PolyScript

        if t == "tv":
            poly_obj = UniversalScriptEngine.parse_tv_script(content, title=args.title)
        elif t == "play":
            poly_obj = UniversalScriptEngine.parse_play(content, title=args.title)
        elif t == "comic":
            poly_obj = UniversalScriptEngine.parse_comic_script(content, title=args.title)
        elif t == "email":
            poly_obj = UniversalScriptEngine.parse_email_script(content, title=args.title)
        elif t in {"video", "reel", "youtube"}:
            from nougenscript.dialects import ScriptKind
            k = ScriptKind.SHORT_FORM_REEL if t == "reel" else (ScriptKind.LONG_FORM_YOUTUBE if t == "youtube" else ScriptKind.TALKING_HEAD_VIDEO)
            poly_obj = UniversalScriptEngine.parse_creator_video(content, title=args.title, kind=k)
        elif t in {"code", "typescript", "javascript", "python"}:
            effective_lang = "typescript" if t == "typescript" else ("javascript" if t == "javascript" else ("python" if t == "python" else args.lang))
            poly_obj = UniversalScriptEngine.parse_code_script(content, language=effective_lang, entrypoint=args.file.stem)
        else:
            print(f"Unsupported script dialect: {t}")
            return 1

        if args.json:
            print(json.dumps({
                "summary": poly_obj.summary(),
                "meta": poly_obj.meta.__dict__,
                "hash": poly_obj.script_hash
            }, indent=2, default=str))
        else:
            print(f"📜 {poly_obj.summary()}")
            if poly_obj.meta.kind.value == "tv_episodic":
                print(f"  📺 TV Acts: {len(poly_obj.body)}")
                for act in poly_obj.body:
                    print(f"    • {act.act_name}: {len(act.scenes)} scene(s)")
            elif poly_obj.meta.kind.value == "comic_script":
                print(f"  💥 Comic Pages: {len(poly_obj.body)}")
                for p in poly_obj.body:
                    print(f"    • Page {p.page_number}: {len(p.panels)} panel(s)")
            elif poly_obj.meta.kind.value == "cold_email":
                em = poly_obj.body
                print(f"  ✉️ Email Subject: \"{em.subject_line}\" (CTA: {em.call_to_action_text} -> {em.call_to_action_url})")
            elif "video" in poly_obj.meta.domain.value.lower() or "reel" in poly_obj.meta.kind.value:
                vid = poly_obj.body
                print(f"  🎥 Hook (3s): \"{vid.hook_3s}\"")
                print(f"  ⏱️ Estimated Duration: ~{vid.estimated_duration_sec}s ({len(vid.beats)} beats)")
                if vid.call_to_action:
                    print(f"  🎯 CTA: {vid.call_to_action}")
            elif "code" in poly_obj.meta.domain.value.lower():
                code_spec = poly_obj.body
                print(f"  💻 Code Language: {code_spec.language.upper()} (Deps: {code_spec.dependencies}, Exports: {code_spec.exports})")
        return 0

    # ------------------------------------------------------------------- #
    # Validate — Elite quality gates
    # ------------------------------------------------------------------- #
    if args.command == "validate":
        content = args.file.read_text(encoding="utf-8")
        t = args.type.lower()

        # Parse into PolyScript first
        if t == "movie":
            poly_obj = PolyScript(
                meta=__import__("nougenscript.dialects", fromlist=["ScriptMeta"]).ScriptMeta(
                    title=args.title, kind=__import__("nougenscript.dialects", fromlist=["ScriptKind"]).ScriptKind.MOVIE_SCREENPLAY
                ),
                body=FountainParser.parse(content, title=args.title),
                raw_source=content,
            )
        elif t == "tv":
            poly_obj = UniversalScriptEngine.parse_tv_script(content, title=args.title)
        elif t == "play":
            poly_obj = UniversalScriptEngine.parse_play(content, title=args.title)
        elif t == "comic":
            poly_obj = UniversalScriptEngine.parse_comic_script(content, title=args.title)
        elif t == "email":
            poly_obj = UniversalScriptEngine.parse_email_script(content, title=args.title)
        elif t in {"video", "reel", "youtube"}:
            from nougenscript.dialects import ScriptKind
            k = ScriptKind.SHORT_FORM_REEL if t == "reel" else (ScriptKind.LONG_FORM_YOUTUBE if t == "youtube" else ScriptKind.TALKING_HEAD_VIDEO)
            poly_obj = UniversalScriptEngine.parse_creator_video(content, title=args.title, kind=k)
        else:
            effective_lang = t if t in {"typescript", "javascript", "python"} else "python"
            poly_obj = UniversalScriptEngine.parse_code_script(content, language=effective_lang, entrypoint=args.file.stem)

        reports = ScriptValidator.validate(poly_obj)

        if args.json:
            from dataclasses import asdict
            print(json.dumps([{
                "validator": r.validator_name, "passed": r.passed,
                "score": r.score, "issues": [asdict(i) for i in r.issues],
                "metadata": r.metadata,
            } for r in reports], indent=2, default=str))
        else:
            print(ScriptValidator.full_report(poly_obj))
        return 0

    # ------------------------------------------------------------------- #
    # v0.4.0 — Generate scaffolds
    # ------------------------------------------------------------------- #
    if args.command == "generate":
        tmpl = args.template

        if tmpl == "beat-sheet":
            beats = generate_beat_sheet(title=args.title)
            if args.json:
                print(json.dumps([{"beat": b.beat.value, "page": b.page_target,
                                   "description": b.description, "hint": b.scene_hint} for b in beats], indent=2))
            else:
                print(f"🎬 Save the Cat! Beat Sheet — \"{args.title}\"")
                print("=" * 50)
                for b in beats:
                    print(f"  [{b.page_target}] {b.beat.value.upper()}")
                    print(f"    {b.description}")
                    if b.scene_hint:
                        print(f"    💡 {b.scene_hint}")

        elif tmpl == "story-circle":
            steps = generate_story_circle(protagonist=args.protagonist, episode_title=args.title)
            if args.json:
                print(json.dumps([{"step": s.step.value, "position": s.position,
                                   "description": s.description, "prompt": s.writing_prompt} for s in steps], indent=2))
            else:
                print(f"📺 Harmon Story Circle — \"{args.title}\" (Protagonist: {args.protagonist})")
                print("=" * 50)
                for s in steps:
                    print(f"  [{s.position}] {s.step.value.upper()}")
                    print(f"    {s.description}")
                    if s.writing_prompt:
                        print(f"    ✏️ {s.writing_prompt}")

        elif tmpl in {"pas", "bab", "hso"}:
            gen_fn = {"pas": generate_pas_template, "bab": generate_bab_template, "hso": generate_hso_template}[tmpl]
            email = gen_fn(topic=args.topic)
            if args.json:
                print(json.dumps({"framework": email.framework, "awareness": email.awareness_stage.value,
                                  "subject": email.subject_line, "sections": email.sections,
                                  "ps": email.ps_line, "sign_off": email.sign_off}, indent=2))
            else:
                print(f"✉️ {email.framework} Email Template — Topic: \"{args.topic}\"")
                print(f"  Subject: {email.subject_line}")
                print(f"  Awareness: {email.awareness_stage.value}")
                for sec in email.sections:
                    print(f"  [{sec['label']}] {sec['content']}")
                print(f"  P.S.: {email.ps_line}")
                print(f"  Sign-off: {email.sign_off}")

        elif tmpl == "unity-play":
            outline = generate_unity_outline(title=args.title, location=args.location)
            if args.json:
                print(json.dumps({"title": outline.title, "location": outline.single_location,
                                  "time_span": outline.time_span, "core_action": outline.core_action,
                                  "characters": outline.characters,
                                  "acts": outline.act_structure}, indent=2))
            else:
                print(f"🎭 Aristotle Unity Play — \"{outline.title}\"")
                print(f"  📍 Location: {outline.single_location}")
                print(f"  ⏱️ Time: {outline.time_span}")
                print(f"  ❓ Core Question: {outline.core_action}")
                print(f"  👥 Characters: {', '.join(outline.characters)}")
                for act in outline.act_structure:
                    print(f"\n  {act['act']}")
                    print(f"    {act['description']}")

        elif tmpl in {"talking-head", "reel", "youtube"}:
            if tmpl == "talking-head":
                v_out = generate_talking_head_template(topic=args.topic)
            elif tmpl == "reel":
                v_out = generate_short_form_reel_template(topic=args.topic)
            else:
                v_out = generate_youtube_longform_template(topic=args.topic)

            if args.json:
                from dataclasses import asdict
                print(json.dumps(asdict(v_out), indent=2))
            else:
                print(f"🎥 {v_out.format_name} — Target: {v_out.target_duration}")
                print(f"  ⚡ Hook Directive: {v_out.hook_directive}")
                print("\n  Structure Beats:")
                for b in v_out.structure_beats:
                    print(f"    • [{b['phase']}] {b['direction']}")
                print("\n  Retention Invariants:")
                for g in v_out.retention_guidelines:
                    print(f"    ↳ {g}")

        elif tmpl == "thirty-acts":
            acts = generate_thirty_act_scaffold(title=args.title, protagonist=args.protagonist, shadow=args.shadow)
            if args.json:
                from dataclasses import asdict
                print(json.dumps([asdict(a) for a in acts], indent=2))
            else:
                print(f"🏛️ The 30-Act Structure (The Dav3 Standard) — \"{args.title}\"")
                print(f"   Protagonist: {args.protagonist} | Shadow: {args.shadow} | Estimated Runtime: ~120 min")
                print("=" * 65)
                current_phase = ""
                for a in acts:
                    if a.phase != current_phase:
                        current_phase = a.phase
                        print(f"\n  [{current_phase}]")
                    print(f"    Act {a.act_number:2d}: {a.act_name} ({a.pacing_target})")
                    print(f"            ↳ {a.story_beat}: {a.description}")

        elif tmpl == "backward-plan":
            plan = generate_backward_plan(
                title=args.title,
                terminal_climax=args.terminal_climax,
                opening_ground=args.opening_ground,
            )
            if args.json:
                from dataclasses import asdict
                print(json.dumps(asdict(plan), indent=2))
            else:
                print(f"🔮 Backward-Causal Teleological Plan (Kaedra Engine) — \"{plan.title}\"")
                print(f"   🎯 Terminal Climax: {plan.terminal_climax}")
                print("=" * 65)
                for s in plan.steps:
                    print(f"\n  [Step {s.step_number}: {s.phase}]")
                    print(f"    • State:       {s.state_description}")
                    print(f"    • Requirement: {s.dramatic_requirement}")

        return 0

    if args.command == "craft":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        report = MasterCraftSuite.audit(sp)
        if args.json:
            print(json.dumps(report.__dict__, indent=2))
        else:
            print(f"🏆 Top 0.001% Narrative Master Craft Audit ({args.file.name}):")
            print(f"  • Overall Craft Score:     {report.overall_craft_index}/100")
            print(f"  • Mamet Triad Compliance:  {int(report.mamet_compliance_ratio * 100)}% ({report.total_scenes} scenes)")
            print(f"  • Sorkin Cadence Score:    {report.cadence_score}/100 ({report.total_dialogues} dialogue turns)")
            print(f"  • Causal Velocity Ratio:   {int(report.causal_velocity_ratio * 100)}% ('Therefore'/'But' vs 'And then')")
            print(f"  • Status Power Reversals:  {report.status_reversals} peripeteia pivot(s)")
            if report.critical_notes:
                print("\n  ⚠️ Critical Director/Writer Punch-List:")
                for note in report.critical_notes:
                    print(f"    - {note}")
            else:
                print("\n  ✨ Elite Diamond Standard: 0.001% Narrative propulsion verified.")
        return 0

    if args.command == "status-map":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        res = StatusTracker.analyze_dialogues(sp.dialogue_lines)
        if args.json:
            print(json.dumps({
                "characters": res.characters,
                "reversals": res.reversals_detected,
                "dominant": res.dominant_character,
                "submissive": res.submissive_character,
                "final_balance": res.final_balance,
                "turns": [t.__dict__ for t in res.turns],
            }, indent=2, default=str))
        else:
            print(f"🎭 Status Transaction Dynamics ({len(res.turns)} turns, {res.reversals_detected} reversals):")
            print(f"  • Dominant:   {res.dominant_character} (Score: {res.final_balance.get(res.dominant_character, 0):+d})")
            print(f"  • Submissive: {res.submissive_character} (Score: {res.final_balance.get(res.submissive_character, 0):+d})")
            print("\n  Line-by-Line Power Negotiation:")
            for turn in res.turns:
                move_str = f"[{turn.move.value}]"
                print(f"    {turn.character:12} {move_str:15} (Bal: {turn.cumulative_status:+d}) \"{turn.line}\"")
        return 0

    if args.command == "sandwich":
        text = args.file.read_text(encoding="utf-8")
        result = ReasoningSandwich.audit_script_outcome(spec=args.spec, script_text=text)
        if args.json:
            from dataclasses import asdict
            print(json.dumps(asdict(result), indent=2))
        else:
            status_icon = "✅ PASSED" if result.overall_passed else "❌ FAILED"
            print(f"🥪 Dav1d 11-Step Reasoning Sandwich — {status_icon}")
            print(f"   Target: \"{result.target_spec}\" (Hash: {result.sandwich_hash})")
            print("=" * 65)
            for p in result.passes:
                step_badge = "🟢" if p.status == "passed" else ("🟡" if p.status == "warning" else "🔴")
                print(f"  {step_badge} [{p.step.value}] {p.summary}")
            print("\n  🎯 Synthesis:")
            print(f"    {result.synthesis}")
        return 0 if result.overall_passed else 1

    if args.command == "instinct":
        recorder = InstinctRecorder()
        act = args.action
        if act == "record":
            if not args.pattern or not args.response:
                print("⚠️ Error: --pattern and --response required for record.")
                return 1
            inst = recorder.record_instinct(
                category=args.category or "general",
                pattern=args.pattern,
                response=args.response,
                confidence=args.confidence
            )
            print(f"🧠 Recorded Instinct #{inst.id}: [{inst.category}] '{inst.pattern}' -> '{inst.response}' (conf: {inst.confidence:.2f})")
        elif act == "list":
            instincts = recorder.get_instincts(category=args.category)
            print(f"🧠 Adaptive Instincts ({len(instincts)} total):")
            for i in instincts:
                print(f"  • #{i.id:2d} [{i.category}] '{i.pattern}' -> '{i.response}' (conf: {i.confidence:.2f}, used: {i.usage_count}x)")
        elif act == "context":
            prompt = recorder.build_constraint_context(category=args.category)
            print(prompt if prompt else "No high-confidence instincts recorded yet.")
        return 0

    if args.command == "morph":
        from nougenscript.morph import (
            JoyceRecursionTransformer,
            MorphCandidate,
            MorphEvidence,
            MorphKind,
            NouGenMorphEngine,
            PortmanteauDecomposer,
            StreamOfConsciousnessMorph,
        )

        if args.mode == "joyce":
            if args.file and args.file.exists():
                text = args.file.read_text(encoding="utf-8")
                sp = FountainParser.parse(text)
                JoyceRecursionTransformer.apply_circular_loop(sp)
            else:
                poly = StreamOfConsciousnessMorph.create_joycean_script(title=args.title)
                sp = poly.body

            analysis = JoyceRecursionTransformer.verify_recirculation(sp)
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print(f"🌀 Joyce Recursion Manifold (Finnegans Wake Morph) — {args.title}")
                print(f"  • Valid Manifold: {'✅ TRUE' if analysis['valid_manifold'] else '❌ FALSE'}")
                print(f"  • Opening Anchor: \"{analysis['opening_anchor']}\"")
                print(f"  • Terminal Anchor: \"{analysis['terminal_anchor']}\"")
                print(f"  • Completed Loop: \"{analysis['completed_loop_sentence']}\"")
                print(f"  • Scenes: {len(sp.scenes)} | Dialogues: {len(sp.dialogue_lines)}")
            return 0

        elif args.mode == "decompose":
            target_word = args.word or "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk"
            tok = PortmanteauDecomposer.decompose_word(target_word)
            if args.json:
                print(json.dumps(tok.__dict__, indent=2))
            else:
                print(f"🧩 Portmanteau Decomposition — \"{tok.surface_form}\"")
                print(f"  • Roots: {', '.join(tok.roots)}")
                print(f"  • Languages: {', '.join(tok.languages)}")
                print(f"  • Spoken Plane: \"{tok.phonetic_spoken}\"")
                print(f"  • Display Plane: \"{tok.display_visual}\"")
                print(f"  • Subtext Echo: {tok.archetypal_subtext}")
            return 0

        elif args.mode == "eval":
            cand = MorphCandidate(
                name="finnegans_wake_circular_recirculation",
                kind=MorphKind.RECURSIVE_MOTIF,
                donor_source="James Joyce / Finnegans Wake (1939)",
                donor_behavior="Terminal fragment flows into genesis sentence ('riverrun')",
                generalized_behavior="Circular AST boundary closure for AI video/audio infinite loop scripts",
                nougen_target="nougenscript.morph.JoyceRecursionTransformer",
                evidence=[
                    MorphEvidence(
                        source="https://archive.org/stream/in.ernet.dli.2015.207614/2015.207614.Finnegans-Wake_djvu.txt",
                        claim="Opening 'riverrun...' completes terminal 'A way a lone a last a loved a long the'",
                        confidence=1.0,
                        evidence_type="paper_body",
                    )
                ],
                usefulness=0.95,
                generalizability=0.90,
                verifiability=0.95,
                compatibility=0.92,
                reversibility=1.0,
                integration_cost=0.05,
            )
            engine = NouGenMorphEngine(acceptance_threshold=0.50)
            accepted, score = engine.ingest_candidate(cand)
            if args.json:
                print(json.dumps(cand.to_dict(), indent=2))
            else:
                icon = "✅ ADOPTED" if accepted else "❌ REJECTED"
                print(f"🔬 NouGenMorph Candidate Ingestion — {icon}")
                print(f"  • Candidate: {cand.name} [{cand.kind.value}]")
                print(f"  • Score: {score:.4f} (Effective: {cand.effective_score():.4f}, Threshold: 0.50)")
                print(f"  • Donor: {cand.donor_source}")
                print(f"  • Target: {cand.nougen_target}")
            return 0

        elif args.mode == "compile":
            from nougenscript.morph import EvidenceCompiler
            segments = []
            if args.file and args.file.exists():
                raw = args.file.read_text(encoding="utf-8")
                # Split by double newlines or chapter markers into corpus segments
                segments = [s.strip() for s in raw.split("\n\n") if s.strip()]
            if not segments:
                # Default Finnegans Wake canonical test segments
                segments = [
                    "riverrun, past Eve and Adam's, from swerve of shore to bend of bay, brings us by a commodius vicus of recirculation back to Howth Castle and Environs.",
                    "Sir Tristram, violer d'amores, fr'over the short sea, had passencore rearrived from North Armorica on this side the scraggy isthmus of Europe Minor.",
                    "The fall of a once wallstrait oldparr is retaled early in bed and later on life down through all christian minstrelsy.",
                    "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk!",
                    "What clashes here of wills gen wonts, oystrygods gag sag rahexeption, liddle me, liddle me, liddle me!",
                    "Finn, again! Take. Bussoftlhee, mememormee! Till thousendsthee. Lps. The keys to. Given! A way a lone a last a loved a long the riverrun",
                ]

            unit = EvidenceCompiler.compile_semantic_unit(
                unit=args.unit,
                corpus_segments=segments,
                provenance=args.provenance,
            )
            if args.json:
                print(json.dumps(unit.to_dict(), indent=2))
            else:
                print(f"🧮 Canonical Evidence Compiler — [{unit.template}] Unit: \"{unit.unit}\"")
                print(f"  • Canonical Hash: {unit.canonical_hash}")
                print(f"  • Mathematical Score: {unit.score:.4f} | Confidence: {unit.confidence:.4f}")
                print("  • Calculated Metrics:")
                for k, v in unit.metrics.items():
                    w = unit.weights.get(k, 0.0)
                    print(f"      {k:<20} = {v:.4f}  (weight: {w:.4f})")
                print("  • Governing Equations:")
                for eq_name, eq_form in unit.equations.items():
                    print(f"      {eq_name:<15} : {eq_form}")
            return 0

    # ------------------------------------------------------------------- #
    # 14. Universal Deterministic Calculated Templates (UDCT)
    # ------------------------------------------------------------------- #
    if args.command == "udct":
        from nougenscript.udct import (
            EasingType,
            UniversalDeterministicEngine,
            UniversalStateConfig,
        )

        cfg = UniversalStateConfig(
            duration=args.duration,
            fps=args.fps,
            subject=args.subject,
            action=args.action,
            start_pos=(args.start, 0.0, 0.0),
            end_pos=(args.end, 0.0, 0.0),
            easing=EasingType(args.easing),
            camera_offset=args.camera_offset,
        )
        states = UniversalDeterministicEngine.calculate_trajectory(cfg)

        if args.json:
            print(json.dumps([s.to_dict() for s in states], indent=2))
            return 0

        template_spec = (
            "============================================================\n"
            "🎬 FRAME {{frame_index}} / {{total_frames}} (t = {{t}}s, E(t) = {{eased_t}})\n"
            "------------------------------------------------------------\n"
            "  • Subject          : {{subject}} [Action: {{action}}]\n"
            "  • Position (x,y,z) : ({{calc_position_x}}, {{calc_position_y}}, {{calc_position_z}})\n"
            "  • Velocity (dx/dt) : {{velocity_x}} u/s\n"
            "  • Intensity (I(t)) : {{intensity}} [Phase: {{phase}} rad]\n"
            "  • Camera Orbit     : Yaw {{calc_camera_yaw}}° | Pitch {{calc_camera_pitch}}° | Pos ({{calc_camera_x}}, {{calc_camera_y}}, {{calc_camera_z}})\n"
            "  • Invariant Hash   : {{state_hash}}\n"
        )

        print(f"🧬 NouGen UDCT Engine — [UDCT = G(S, Θ, F, C)]")
        print(f"  • Subject: {cfg.subject} | Duration: {cfg.duration}s @ {cfg.fps} FPS ({cfg.total_frames} total frames)")
        print(f"  • Domain Model: Pos [{args.start} -> {args.end}], Easing: {args.easing}, Camera Offset: {args.camera_offset}")
        print(f"  • Verification Invariant: Deterministic mathematical state -> Template expression renderer\n")

        for f_idx in args.frames:
            if 0 <= f_idx < len(states):
                rendered = UniversalDeterministicEngine.render_template(template_spec, states[f_idx], cfg)
                print(rendered)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
