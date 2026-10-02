"""Unit tests for NouGenScript Universal Poly-Script Dialect Matrix.

Verifies:
- TV Scripts (Cold Opens, Multi-Act breakdowns)
- Playwriting (Theatrical staging, acts)
- Comic Book Scripts (Pages, Panels, SFX, Balloons, Captions)
- Email Scripts (Subject, CTA, Body, P.S.)
- Code Scripts (TypeScript, JavaScript, Python, Bash)
"""
import pytest
from nougenscript.dialects import ScriptDomain, ScriptKind
from nougenscript.engine import UniversalScriptEngine


def test_tv_episodic_script_parsing():
    source = """
COLD OPEN

EXT. NEO-DETROIT HIGHWAY - NIGHT

Sirens scream. A motorcycle cuts through the drizzle.

ACT ONE

INT. CITADEL COMMAND - NIGHT

CORBIN
Where is the fleet baton?

ACT TWO

EXT. ROOFTOP - DAWN

XOAH
The baton is sealed.

TAG

Corbin looks up as dark matter ripples.
"""
    tv_poly = UniversalScriptEngine.parse_tv_script(source, title="Veilverse: The Protocol")
    assert tv_poly.meta.domain == ScriptDomain.TELEVISION
    assert tv_poly.meta.kind == ScriptKind.TV_EPISODIC
    acts = tv_poly.body
    assert len(acts) == 4
    act_names = [a.act_name for a in acts]
    assert "COLD OPEN" in act_names
    assert "ACT ONE" in act_names
    assert "ACT TWO" in act_names
    assert "TAG" in act_names
    assert tv_poly.script_hash != ""


def test_comic_book_script_parsing():
    source = """
PAGE 1

PANEL 1
WIDE SHOT of the Olympus Mons crater at twilight.
CAPTION: The ruins do not speak.
SFX: WHOOSH

PANEL 2
CLOSE UP on Xoah's eyes reflecting the amethyst glow.
XOAH: It has begun.
CORBIN: Too late.
"""
    comic_poly = UniversalScriptEngine.parse_comic_script(source, title="Shadow Dweller #1")
    assert comic_poly.meta.domain == ScriptDomain.COMIC_BOOK
    assert comic_poly.meta.kind == ScriptKind.COMIC_SCRIPT
    pages = comic_poly.body
    assert len(pages) == 1
    page1 = pages[0]
    assert page1.page_number == 1
    assert len(page1.panels) == 2
    p1, p2 = page1.panels
    assert "The ruins do not speak" in p1.captions[0]
    assert "WHOOSH" in p1.sfx
    assert len(p2.dialogue_balloons) == 2
    assert p2.dialogue_balloons[0]["speaker"] == "XOAH"


def test_stage_play_parsing():
    source = """
ACT I

SCENE 1

AT RISE: The stage is bathed in deep amber. A single wooden desk stands stage left.

MARK
(standing, addressing the gallery)
We were not invited to this debate.
"""
    play_poly = UniversalScriptEngine.parse_play(source, title="The Council of Shards")
    assert play_poly.meta.domain == ScriptDomain.THEATRE
    assert play_poly.meta.kind == ScriptKind.STAGE_PLAY
    assert len(play_poly.body.scenes) >= 1


def test_email_campaign_parsing():
    source = """
SUBJECT: The fleet just landed cfda446
PREVIEW: Zero cloud spend, 100% green tests
Hi Dave,

The new PolyScript dialect matrix is live across Who-Visions and nougenai.
Everything compiles deterministically.

CTA: Inspect GitHub Repo | https://github.com/Who-Visions/NouGenScript

P.S. All 9 test suites pass without drift.
"""
    email_poly = UniversalScriptEngine.parse_email_script(source, title="Fleet Dispatch #42")
    assert email_poly.meta.domain == ScriptDomain.EMAIL_CAMPAIGN
    assert email_poly.meta.kind == ScriptKind.COLD_EMAIL
    em = email_poly.body
    assert em.subject_line == "The fleet just landed cfda446"
    assert em.preview_header == "Zero cloud spend, 100% green tests"
    assert em.call_to_action_text == "Inspect GitHub Repo"
    assert em.call_to_action_url == "https://github.com/Who-Visions/NouGenScript"
    assert "All 9 test suites" in em.ps_line


def test_code_script_typescript_parsing():
    ts_code = """
import { useState, useEffect } from 'react';
import axios from 'axios';

export interface FleetState {
  online: boolean;
  nodes: number;
}

export function useFleetMonitor() {
  const [status, setStatus] = useState<FleetState>({ online: true, nodes: 3 });
  return status;
}
"""
    ts_poly = UniversalScriptEngine.parse_code_script(ts_code, language="typescript", entrypoint="useFleetMonitor")
    assert ts_poly.meta.domain == ScriptDomain.CODE_TYPESCRIPT
    assert ts_poly.meta.kind == ScriptKind.TYPESCRIPT_APP
    spec = ts_poly.body
    assert "react" in spec.dependencies
    assert "axios" in spec.dependencies
    assert "useFleetMonitor" in spec.exports or "FleetState" in spec.exports


def test_code_script_python_parsing():
    py_code = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def run_mesh_diagnostic():
    return True

class MeshController:
    pass
"""
    py_poly = UniversalScriptEngine.parse_code_script(py_code, language="python", entrypoint="run_mesh")
    assert py_poly.meta.domain == ScriptDomain.CODE_PYTHON
    assert py_poly.meta.kind == ScriptKind.PYTHON_SCRIPT
    spec = py_poly.body
    assert spec.shebang == "#!/usr/bin/env python3"
    assert "os" in spec.dependencies
    assert "sys" in spec.dependencies
    assert "run_mesh_diagnostic" in spec.exports


def test_dynamic_deterministic_overrides(monkeypatch):
    monkeypatch.setenv("NOUGEN_AUTHOR", "Dynamic Ghost Writer")
    monkeypatch.setenv("NOUGEN_SIGN_OFF", "Warmly,\nGhost")
    monkeypatch.setenv("NOUGEN_TZ", "America/Chicago")

    source = "SUBJECT: Test\nHi Dave,\nCTA: Link | http://example.com"
    email_poly = UniversalScriptEngine.parse_email_script(source)
    assert email_poly.meta.author == "Dynamic Ghost Writer"
    assert email_poly.body.sign_off == "Warmly,\nGhost"

    from nougenscript.persona import Signals
    sig = Signals.from_texts(["some text"])
    assert sig.tz == "America/Chicago"

