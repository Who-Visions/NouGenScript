#!/usr/bin/env python3
"""NouGenScript Command-Line Interface.

Handles script parsing, dual-plane decomposition, SPITE psychological depth analysis,
OpenClap (.clap) bundling, and deterministic persona resolution with behavioral masks.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nougenscript import (
    Screenplay,
    FountainParser,
    DualPlaneProjector,
    OpenClapSerializer,
    SpiteProfile,
    SubtextAnalyzer,
    CharacterPersona,
    Signals,
    blend,
    get_emotion,
    list_masks,
    resolve,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nougenscript",
        description="Universal Screenplay, Dual-Plane Prompter & Dramatic Persona Engine."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. Parse Fountain / Screenplay
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

    args = parser.parse_args(argv)

    if args.command == "parse":
        text = args.file.read_text(encoding="utf-8")
        sp = FountainParser.parse(text)
        if args.json:
            print(json.dumps(sp.to_dict(), indent=2))
        else:
            print(f"🎬 Screenplay: {len(sp.scenes)} scenes, {len(sp.dialogue_lines)} dialogue lines, hash={sp.script_hash}")
            for sc in sp.scenes:
                print(f"  • {sc.heading} ({len(sc.dialogue)} lines)")
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
