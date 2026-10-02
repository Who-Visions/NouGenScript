"""Poly-Script Dialect Matrix for NouGenScript.

Universal abstraction supporting all script types:
- MOVIE (Screenplays, Scene Headings, Dual-Plane Prompters, Fountain, FDX)
- TV_EPISODIC (Cold Opens, Act Breaks, Commercial tags, Series Arcs)
- PLAYWRIGHT (Acts, Stage Directions, Monologues, Proscenium / Black-Box staging)
- COMIC_BOOK (Pages, Panels, Captions, SFX, Balloon Dialogue)
- EMAIL_CAMPAIGN (Subject lines, Preheaders, CTA buttons, Body, P.S. anchors)
- TYPESCRIPT (Modules, Interfaces, Functions, Strict Typing AST)
- JAVASCRIPT (ESM / CJS modules, Functions, Event Listeners)
- PYTHON (PEP 8 AST, Docstrings, Classes, Functions, Async loops)
- BASH_SHELL (Shebangs, Commands, Traps, Pipes, Exit Codes)
"""
from __future__ import annotations

import enum
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


class ScriptDomain(str, enum.Enum):
    """Supported universal script domains."""
    NARRATIVE_FILM = "NARRATIVE_FILM"          # Feature movies, short films
    TELEVISION = "TELEVISION"                  # Episodic TV, pilots, cold opens, act breaks
    THEATRE = "THEATRE"                        # Stage plays, playwriting, proscenium staging
    COMIC_BOOK = "COMIC_BOOK"                  # Comic books, manga, graphic novels (pages/panels/SFX)
    EMAIL_CAMPAIGN = "EMAIL_CAMPAIGN"          # Cold emails, lifecycle sequences, nurture tracks
    CODE_TYPESCRIPT = "CODE_TYPESCRIPT"        # TypeScript (.ts, .tsx)
    CODE_JAVASCRIPT = "CODE_JAVASCRIPT"        # JavaScript (.js, .mjs, .jsx)
    CODE_PYTHON = "CODE_PYTHON"                # Python (.py)
    CODE_SHELL = "CODE_SHELL"                  # Shell / Bash (.sh)


class ScriptKind(str, enum.Enum):
    """Specific script formats recognized and generated."""
    # Cinematic / Stage
    MOVIE_SCREENPLAY = "movie_screenplay"
    TV_PILOT = "tv_pilot"
    TV_EPISODIC = "tv_episodic"
    STAGE_PLAY = "stage_play"
    COMIC_SCRIPT = "comic_script"

    # Business / Copy
    COLD_EMAIL = "cold_email"
    DRIP_SEQUENCE = "drip_sequence"
    NEWSLETTER = "newsletter"

    # Software / Engineering Code Scripts
    TYPESCRIPT_APP = "typescript_app"
    JAVASCRIPT_SCRIPT = "javascript_script"
    PYTHON_SCRIPT = "python_script"
    BASH_SCRIPT = "bash_script"


@dataclass
class ScriptMeta:
    title: str
    author: str = field(default_factory=lambda: os.getenv("NOUGEN_AUTHOR", "Anonymous Author"))
    kind: ScriptKind = ScriptKind.MOVIE_SCREENPLAY
    domain: ScriptDomain = ScriptDomain.NARRATIVE_FILM
    version: str = "1.0.0"
    target_medium: str = "screen"  # screen, stage, print, browser, node, runtime
    extra: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Specialized Domain Data Structures
# --------------------------------------------------------------------------- #

@dataclass
class ComicPanel:
    panel_number: int
    visual_description: str
    camera_angle: str = "WIDE SHOT"  # CLOSE-UP, BIRD'S EYE, SPLASH, etc.
    dialogue_balloons: list[dict[str, str]] = field(default_factory=list)  # [{"speaker": "XOAH", "text": "..."}]
    captions: list[str] = field(default_factory=list)
    sfx: list[str] = field(default_factory=list)  # "KRRAKK!", "BZZZT"
    panel_id: str = ""

    def __post_init__(self):
        if not self.panel_id:
            h = hashlib.sha256(f"panel_{self.panel_number}:{self.visual_description}".encode()).hexdigest()[:10]
            self.panel_id = h


@dataclass
class ComicPage:
    page_number: int
    panels: list[ComicPanel] = field(default_factory=list)
    is_splash_page: bool = False


@dataclass
class TVAct:
    act_number: int  # 0 = Cold Open, 1..5 = Acts, 99 = Tag / Stinger
    act_name: str = "ACT ONE"
    scenes: list[Any] = field(default_factory=list)


@dataclass
class EmailSection:
    subject_line: str
    preview_header: str
    salutation: str
    body_paragraphs: list[str]
    call_to_action_url: str
    call_to_action_text: str
    ps_line: str = ""
    sign_off: str = field(default_factory=lambda: os.getenv("NOUGEN_SIGN_OFF", "Best Regards"))


@dataclass
class CodeScriptSpec:
    language: str  # typescript | javascript | python | bash
    entrypoint: str
    dependencies: list[str] = field(default_factory=list)
    source_code: str = ""
    shebang: str = ""
    exports: list[str] = field(default_factory=list)
    ast_summary: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Universal PolyScript Container
# --------------------------------------------------------------------------- #

@dataclass
class PolyScript:
    meta: ScriptMeta
    body: Any  # Screenplay | list[TVAct] | list[ComicPage] | EmailSection | CodeScriptSpec
    raw_source: str = ""
    script_hash: str = ""

    def __post_init__(self):
        if not self.script_hash:
            self.recompute_hash()

    def recompute_hash(self) -> str:
        s = f"{self.meta.kind.value}:{self.meta.title}:{self.raw_source}"
        self.script_hash = hashlib.sha256(s.encode("utf-8")).hexdigest()
        return self.script_hash

    def summary(self) -> str:
        return (
            f"PolyScript[{self.meta.kind.value.upper()}] \"{self.meta.title}\" "
            f"Domain: {self.meta.domain.value} (Hash: {self.script_hash[:12]})"
        )
