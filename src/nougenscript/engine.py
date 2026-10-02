"""Universal Script Engine for Poly-Format Script Parsing, Validation, and Generation.

Handles:
- Movie Scripts (Fountain & Standard Screenplays)
- TV Scripts (Cold Opens, Multi-Act structures, Commercial Tags)
- Playwriting (Theatre stage directions, Acts, Characters)
- Comic Book Scripts (Dark Horse / Marvel 2-column or standard page/panel breakdowns)
- Email Marketing Scripts (Cold Outreach, Nurture Sequences, Hook/Story/Offer/PS)
- Code Scripts (TypeScript, JavaScript, Python, Bash)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from nougenscript.core import Dialogue, Direction, NodeType, Scene, Screenplay, ScriptNode
from nougenscript.dialects import (
    CodeScriptSpec,
    ComicPage,
    ComicPanel,
    CreatorVideoScript,
    EmailSection,
    PolyScript,
    ScriptDomain,
    ScriptKind,
    ScriptMeta,
    TVAct,
    VideoScriptBeat,
)
from nougenscript.parser import FountainParser


class UniversalScriptEngine:
    """Universal script compiler, parser, and generator across narrative, copy, and code."""

    # ----------------------------------------------------------------------- #
    # 1. TV Scripts (Episodic & Pilot)
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_tv_script(cls, source_text: str, title: str = "Untitled TV Episode") -> PolyScript:
        """Parses episodic TV scripts with COLD OPEN, ACT breaks, and TAGS."""
        act_pattern = re.compile(r"^\s*(COLD OPEN|ACT [ONE|TWO|THREE|FOUR|FIVE|\d]+|TAG|END OF EPISODE)\s*$", re.MULTILINE | re.IGNORECASE)
        splits = list(act_pattern.finditer(source_text))
        acts: list[TVAct] = []

        if not splits:
            # Fallback single act
            sp = FountainParser.parse(source_text, title=title)
            acts.append(TVAct(act_number=1, act_name="ACT ONE", scenes=sp.scenes))
        else:
            for i, match in enumerate(splits):
                act_name = match.group(1).upper()
                start_pos = match.end()
                end_pos = splits[i + 1].start() if i + 1 < len(splits) else len(source_text)
                act_chunk = source_text[start_pos:end_pos].strip()

                sp = FountainParser.parse(act_chunk, title=f"{title} - {act_name}")
                act_num = 0 if "COLD" in act_name else (99 if "TAG" in act_name else (i + 1))
                acts.append(TVAct(act_number=act_num, act_name=act_name, scenes=sp.scenes))

        meta = ScriptMeta(
            title=title,
            kind=ScriptKind.TV_EPISODIC,
            domain=ScriptDomain.TELEVISION,
            target_medium="television"
        )
        return PolyScript(meta=meta, body=acts, raw_source=source_text)

    # ----------------------------------------------------------------------- #
    # 2. Stage Plays (Playwrighting)
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_play(cls, source_text: str, title: str = "Untitled Stage Play") -> PolyScript:
        """Parses theatrical stage plays with ACTs, SCENEs, and staging directions."""
        sp = FountainParser.parse(source_text, title=title)
        meta = ScriptMeta(
            title=title,
            kind=ScriptKind.STAGE_PLAY,
            domain=ScriptDomain.THEATRE,
            target_medium="stage"
        )
        return PolyScript(meta=meta, body=sp, raw_source=source_text)

    # ----------------------------------------------------------------------- #
    # 3. Comic Book Scripts
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_comic_script(cls, source_text: str, title: str = "Untitled Comic Issue") -> PolyScript:
        """Parses comic book scripts broken down into PAGE X, PANEL Y, CAPTIONs, and SFX."""
        pages: list[ComicPage] = []
        page_splits = re.split(r"(?i)^\s*PAGE\s+(\d+)\b", source_text, flags=re.MULTILINE)

        if len(page_splits) > 1:
            for i in range(1, len(page_splits), 2):
                page_num = int(page_splits[i])
                page_body = page_splits[i + 1]
                panels: list[ComicPanel] = []

                panel_splits = re.split(r"(?i)^\s*PANEL\s+(\d+)\b", page_body, flags=re.MULTILINE)
                if len(panel_splits) > 1:
                    for j in range(1, len(panel_splits), 2):
                        p_num = int(panel_splits[j])
                        p_content = panel_splits[j + 1].strip()

                        # Extract dialogue, captions, and SFX
                        balloons: list[dict[str, str]] = []
                        captions: list[str] = []
                        sfx_list: list[str] = []
                        vis_lines: list[str] = []

                        for line in p_content.splitlines():
                            line_str = line.strip()
                            if not line_str:
                                continue
                            if re.match(r"(?i)^CAPTION\s*:", line_str):
                                captions.append(re.sub(r"(?i)^CAPTION\s*:\s*", "", line_str))
                            elif re.match(r"(?i)^SFX\s*:", line_str):
                                sfx_list.append(re.sub(r"(?i)^SFX\s*:\s*", "", line_str))
                            elif ":" in line_str and not line_str.startswith("NOTE"):
                                speaker, txt = line_str.split(":", 1)
                                balloons.append({"speaker": speaker.strip().upper(), "text": txt.strip()})
                            else:
                                vis_lines.append(line_str)

                        panels.append(ComicPanel(
                            panel_number=p_num,
                            visual_description=" ".join(vis_lines),
                            dialogue_balloons=balloons,
                            captions=captions,
                            sfx=sfx_list
                        ))
                pages.append(ComicPage(page_number=page_num, panels=panels))
        else:
            # Fallback single page / single panel
            pages.append(ComicPage(
                page_number=1,
                panels=[ComicPanel(panel_number=1, visual_description=source_text.strip())]
            ))

        meta = ScriptMeta(
            title=title,
            kind=ScriptKind.COMIC_SCRIPT,
            domain=ScriptDomain.COMIC_BOOK,
            target_medium="print"
        )
        return PolyScript(meta=meta, body=pages, raw_source=source_text)

    # ----------------------------------------------------------------------- #
    # 4. Email Scripts (Campaigns & Sequences)
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_email_script(cls, source_text: str, title: str = "Email Outreach Script") -> PolyScript:
        """Parses email marketing / outreach scripts with Subject, Body, CTA, and P.S."""
        subject = "No Subject"
        preview = ""
        cta_url = ""
        cta_text = ""
        ps_line = ""
        body_paras: list[str] = []
        salutation = "Hi {{first_name}},"

        lines = source_text.strip().splitlines()
        collecting_body = False

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            if re.match(r"(?i)^SUBJECT\s*:", line_str):
                subject = re.sub(r"(?i)^SUBJECT\s*:\s*", "", line_str)
            elif re.match(r"(?i)^PREVIEW\s*:", line_str):
                preview = re.sub(r"(?i)^PREVIEW\s*:\s*", "", line_str)
            elif re.match(r"(?i)^CTA\s*:", line_str):
                cta_info = re.sub(r"(?i)^CTA\s*:\s*", "", line_str)
                if "|" in cta_info:
                    cta_text, cta_url = [p.strip() for p in cta_info.split("|", 1)]
                else:
                    cta_text, cta_url = cta_info, "#"
            elif re.match(r"(?i)^P[\.\s]*S[\.\s]*[:\-]?\s*", line_str):
                ps_line = re.sub(r"(?i)^P[\.\s]*S[\.\s]*[:\-]?\s*", "", line_str)
            else:
                body_paras.append(line_str)

        section = EmailSection(
            subject_line=subject,
            preview_header=preview,
            salutation=salutation,
            body_paragraphs=body_paras,
            call_to_action_url=cta_url,
            call_to_action_text=cta_text,
            ps_line=ps_line
        )

        meta = ScriptMeta(
            title=title,
            kind=ScriptKind.COLD_EMAIL,
            domain=ScriptDomain.EMAIL_CAMPAIGN,
            target_medium="email"
        )
        return PolyScript(meta=meta, body=section, raw_source=source_text)

    # ----------------------------------------------------------------------- #
    # 5. Creator Video Scripts (Shorts, Reels, YouTube Long-Form)
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_creator_video(cls, source_text: str, title: str = "Untitled Video Script", kind: ScriptKind = ScriptKind.TALKING_HEAD_VIDEO) -> PolyScript:
        """Parses creator video scripts with Hooks, Visual/Audio Beats, and Pattern Interrupts."""
        lines = source_text.strip().splitlines()
        hook_3s = ""
        setup = ""
        cta = ""
        thumb = ""
        beats: list[VideoScriptBeat] = []

        curr_time = "00:00"
        curr_visual = ""
        curr_audio = []
        curr_sound = ""
        curr_interrupt = False

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            lower = line_str.lower()
            if lower.startswith("hook:") or lower.startswith("hook (3s):") or lower.startswith("the hook:"):
                hook_3s = re.sub(r"^(?:hook(?:\s*\(3s\))?|the hook):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif lower.startswith("setup:") or lower.startswith("the setup:"):
                setup = re.sub(r"^(?:setup|the setup):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif lower.startswith("cta:") or lower.startswith("call to action:"):
                cta = re.sub(r"^(?:cta|call to action):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif lower.startswith("thumbnail:") or lower.startswith("thumbnail concept:"):
                thumb = re.sub(r"^(?:thumbnail(?:\s*concept)?):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif line_str.startswith("[") and "]" in line_str:
                # Any bracketed header [00:05] or [PATTERN INTERRUPT] or [00:20 - PATTERN INTERRUPT] creates a beat boundary
                tag = line_str[1:line_str.find("]")].strip()
                if curr_visual or curr_audio:
                    beats.append(VideoScriptBeat(
                        timecode_start=curr_time,
                        visual_action=curr_visual,
                        spoken_audio=" ".join(curr_audio),
                        sound_design=curr_sound,
                        is_pattern_interrupt=curr_interrupt
                    ))
                    curr_visual = ""
                    curr_audio = []
                    curr_sound = ""
                    curr_interrupt = False

                curr_time = tag
                if "pattern interrupt" in tag.lower():
                    curr_interrupt = True
            elif lower.startswith("visual:") or lower.startswith("camera:") or lower.startswith("b-roll:"):
                curr_visual = re.sub(r"^(?:visual|camera|b-roll):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif lower.startswith("sfx:") or lower.startswith("sound:"):
                curr_sound = re.sub(r"^(?:sfx|sound):\s*", "", line_str, flags=re.IGNORECASE).strip()
            elif lower.startswith("audio:") or lower.startswith("spoken:") or lower.startswith("speech:"):
                curr_audio.append(re.sub(r"^(?:audio|spoken|speech):\s*", "", line_str, flags=re.IGNORECASE).strip())
            else:
                # Default text line is treated as spoken audio
                curr_audio.append(line_str)

        if curr_visual or curr_audio:
            beats.append(VideoScriptBeat(
                timecode_start=curr_time,
                visual_action=curr_visual,
                spoken_audio=" ".join(curr_audio),
                sound_design=curr_sound,
                is_pattern_interrupt=curr_interrupt
            ))

        est_sec = max(len(beats) * 3, 30) if beats else 60
        script_obj = CreatorVideoScript(
            hook_3s=hook_3s or (beats[0].spoken_audio[:60] if beats else "Pattern Interrupt Hook"),
            setup=setup or "Context & Stakes established.",
            beats=beats,
            call_to_action=cta,
            thumbnail_concept=thumb,
            title_concept=title,
            estimated_duration_sec=est_sec
        )

        meta = ScriptMeta(
            title=title,
            kind=kind,
            domain=ScriptDomain.CREATOR_VIDEO,
            target_medium="video"
        )
        return PolyScript(meta=meta, body=script_obj, raw_source=source_text)

    # ----------------------------------------------------------------------- #
    # 6. Code Scripts (TypeScript, JavaScript, Python, Bash)
    # ----------------------------------------------------------------------- #
    @classmethod
    def parse_code_script(cls, source_code: str, language: str, entrypoint: str = "main") -> PolyScript:
        """Parses and encapsulates source code scripts with AST analysis."""
        lang = language.lower().strip()
        domain_map = {
            "typescript": (ScriptDomain.CODE_TYPESCRIPT, ScriptKind.TYPESCRIPT_APP),
            "ts": (ScriptDomain.CODE_TYPESCRIPT, ScriptKind.TYPESCRIPT_APP),
            "javascript": (ScriptDomain.CODE_JAVASCRIPT, ScriptKind.JAVASCRIPT_SCRIPT),
            "js": (ScriptDomain.CODE_JAVASCRIPT, ScriptKind.JAVASCRIPT_SCRIPT),
            "python": (ScriptDomain.CODE_PYTHON, ScriptKind.PYTHON_SCRIPT),
            "py": (ScriptDomain.CODE_PYTHON, ScriptKind.PYTHON_SCRIPT),
            "bash": (ScriptDomain.CODE_SHELL, ScriptKind.BASH_SCRIPT),
            "sh": (ScriptDomain.CODE_SHELL, ScriptKind.BASH_SCRIPT),
        }
        domain, kind = domain_map.get(lang, (ScriptDomain.CODE_PYTHON, ScriptKind.PYTHON_SCRIPT))

        # Scan imports and dependencies
        deps: list[str] = []
        exports: list[str] = []

        if "python" in lang or lang == "py":
            import_matches = re.findall(r"^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)", source_code, re.MULTILINE)
            deps = sorted(list(set(m.split(".")[0] for m in import_matches)))
            func_matches = re.findall(r"^\s*def\s+([a-zA-Z0-9_]+)", source_code, re.MULTILINE)
            exports = func_matches
        elif "script" in lang or lang in {"ts", "js"}:
            # Support: import ... from 'pkg' and require('pkg') and import 'pkg'
            from_matches = re.findall(r"(?:from|import)\s+['\"]([^'\"]+)['\"]", source_code)
            req_matches = re.findall(r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", source_code)
            all_raw = from_matches + req_matches
            cleaned_deps = []
            for dep in all_raw:
                if not dep.startswith("."):
                    cleaned_deps.append(dep.split("/")[0] if not dep.startswith("@") else "/".join(dep.split("/")[:2]))
                else:
                    cleaned_deps.append(dep)
            deps = sorted(list(set(cleaned_deps)))
            export_matches = re.findall(r"export\s+(?:default\s+)?(?:class|function|const|let|var|type|interface)\s+([a-zA-Z0-9_]+)", source_code)
            exports = export_matches

        shebang = ""
        first_line = source_code.splitlines()[0] if source_code.splitlines() else ""
        if first_line.startswith("#!"):
            shebang = first_line

        spec = CodeScriptSpec(
            language=lang,
            entrypoint=entrypoint,
            dependencies=deps,
            source_code=source_code,
            shebang=shebang,
            exports=exports,
            ast_summary={"exports_count": len(exports), "deps_count": len(deps)}
        )

        meta = ScriptMeta(
            title=f"{entrypoint}.{lang}",
            kind=kind,
            domain=domain,
            target_medium="runtime"
        )
        return PolyScript(meta=meta, body=spec, raw_source=source_code)
