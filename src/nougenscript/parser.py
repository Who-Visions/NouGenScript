"""Fountain & Screenplay Syntax Parser for NouGenScript.

Parses industry-standard Fountain syntax into NouGenScript AST:
- Scene Headings: INT./EXT./INT./EXT./I/E
- Characters: UPPERCASE lines followed by Dialogue
- Parentheticals: (surrounded by parentheses)
- Dialogue: Spoken dialogue lines
- Transitions: CUT TO:, FADE IN:, FADE OUT: or lines ending in TO:
- Action / Directions: General narrative description beats
"""
from __future__ import annotations

import re

from nougenscript.core import NodeType, Scene, Screenplay, ScriptNode

_SCENE_HEADING_REGEX = re.compile(r"^(INT|EXT|EST|INT\./EXT|I/E)\.?\s+", re.IGNORECASE)
_CHARACTER_REGEX = re.compile(r"^[A-Z0-9\-_'\. ]+(\s*\([A-Za-z0-9'\. ]+\))?$")
_TRANSITION_REGEX = re.compile(r"^(CUT TO:|FADE IN:|FADE OUT:|DISSOLVE TO:|[A-Z ]+ TO:)$")


class FountainParser:
    """Deterministic parser converting Fountain or formatted screenplay text into Screenplay AST."""

    @classmethod
    def parse(cls, text: str, title: str = "Untitled Screenplay") -> Screenplay:
        lines = [line.rstrip() for line in text.splitlines()]
        scenes: list[Scene] = []
        current_scene: Scene = Scene(heading="PROLOGUE", scene_number=1)
        scene_count = 1

        i = 0
        n = len(lines)

        while i < n:
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # 1. Scene Heading
            if _SCENE_HEADING_REGEX.match(line):
                if current_scene.nodes or current_scene.heading != "PROLOGUE":
                    scenes.append(current_scene)
                    scene_count += 1
                current_scene = Scene(heading=line, scene_number=scene_count)
                i += 1
                continue

            # 2. Transition
            if _TRANSITION_REGEX.match(line) or (line.isupper() and line.endswith("TO:")):
                current_scene.nodes.append(ScriptNode(type=NodeType.TRANSITION, content=line))
                i += 1
                continue

            # 3. Character + Dialogue Block
            # A line in UPPERCASE with a following non-empty line is parsed as Character + Dialogue
            if line.isupper() and (i + 1 < n and lines[i + 1].strip()):
                char_name = line
                current_scene.nodes.append(ScriptNode(type=NodeType.CHARACTER, content=char_name))
                i += 1

                # Optional parenthetical
                if i < n and lines[i].strip().startswith("(") and lines[i].strip().endswith(")"):
                    paren = lines[i].strip()[1:-1]
                    current_scene.nodes.append(ScriptNode(type=NodeType.PARENTHETICAL, content=paren))
                    i += 1

                # Dialogue lines
                dialogue_parts = []
                while i < n and lines[i].strip():
                    dialogue_parts.append(lines[i].strip())
                    i += 1

                if dialogue_parts:
                    current_scene.nodes.append(
                        ScriptNode(type=NodeType.DIALOGUE, content=" ".join(dialogue_parts))
                    )
                continue

            # 4. Action / Stage Direction
            current_scene.nodes.append(ScriptNode(type=NodeType.ACTION, content=line))
            i += 1

        if current_scene.nodes or current_scene.heading:
            scenes.append(current_scene)

        return Screenplay(title=title, scenes=scenes)
