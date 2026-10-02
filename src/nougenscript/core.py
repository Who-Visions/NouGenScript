"""Core AST and structural nodes for NouGenScript."""
from __future__ import annotations

import enum
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any


class NodeType(str, enum.Enum):
    SCENE_HEADING = "SCENE_HEADING"
    ACTION = "ACTION"
    CHARACTER = "CHARACTER"
    PARENTHETICAL = "PARENTHETICAL"
    DIALOGUE = "DIALOGUE"
    TRANSITION = "TRANSITION"
    CUE = "CUE"
    DIRECTION = "DIRECTION"


@dataclass
class ScriptNode:
    type: NodeType
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            canon = f"{self.type.value}:{self.content}:{json.dumps(self.metadata, sort_keys=True)}"
            self.node_id = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]


@dataclass
class Dialogue:
    character: str
    text: str
    parenthetical: str | None = None
    character_id: str | None = None
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            canon = f"{self.character}:{self.text}:{self.parenthetical or ''}"
            self.node_id = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]


@dataclass
class Direction:
    text: str
    kind: str = "stage_direction"  # camera, lighting, audio, blocking
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            self.node_id = hashlib.sha256(f"{self.kind}:{self.text}".encode()).hexdigest()[:12]


@dataclass
class Cue:
    text: str
    target_actor: str | None = None
    emotional_crescendo: float = 0.5  # 0.0 to 1.0
    node_id: str = ""

    def __post_init__(self):
        if not self.node_id:
            self.node_id = hashlib.sha256(f"{self.target_actor}:{self.text}:{self.emotional_crescendo}".encode()).hexdigest()[:12]


@dataclass
class Scene:
    heading: str
    nodes: list[ScriptNode] = field(default_factory=list)
    scene_number: int = 1
    setting: str = ""
    time_of_day: str = ""
    scene_id: str = ""

    def __post_init__(self):
        if not self.scene_id:
            self.scene_id = hashlib.sha256(f"scene_{self.scene_number}:{self.heading}".encode()).hexdigest()[:12]

    @property
    def dialogues(self) -> list[Dialogue]:
        results: list[Dialogue] = []
        current_char = ""
        current_paren = None
        for node in self.nodes:
            if isinstance(node, Dialogue):
                results.append(node)
                continue
            if not hasattr(node, "type"):
                continue
            if node.type == NodeType.CHARACTER:
                current_char = node.content.strip()
                current_paren = None
            elif node.type == NodeType.PARENTHETICAL:
                current_paren = node.content.strip()
            elif node.type == NodeType.DIALOGUE:
                results.append(
                    Dialogue(
                        character=current_char,
                        text=node.content.strip(),
                        parenthetical=current_paren,
                    )
                )
                current_paren = None
        return results


@dataclass
class Screenplay:
    title: str
    author: str = field(default_factory=lambda: os.getenv("NOUGEN_AUTHOR", "Anonymous Author"))
    scenes: list[Scene] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    script_hash: str = ""

    def __post_init__(self):
        if not self.script_hash:
            self.recompute_hash()

    def recompute_hash(self) -> str:
        serialized = json.dumps([asdict(s) for s in self.scenes], sort_keys=True)
        self.script_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return self.script_hash

    @property
    def dialogue_lines(self) -> list[Dialogue]:
        lines: list[Dialogue] = []
        for s in self.scenes:
            lines.extend(s.dialogues)
        return lines

    @classmethod
    def from_fountain(cls, text: str, title: str = "Untitled Screenplay") -> Screenplay:
        from nougenscript.parser import FountainParser
        return FountainParser.parse(text, title=title)


# --------------------------------------------------------------------------- #
# Kaedra Continuity State Machine
# --------------------------------------------------------------------------- #

@dataclass
class ContinuityTracker:
    """Live state machine tracking active plot threads, somatic props, emotions, and locations across scenes."""
    active_threads: list[str] = field(default_factory=list)
    somatic_props: list[str] = field(default_factory=list)
    emotional_state: str = "determined, focused"
    last_location: str = ""
    character_states: dict[str, str] = field(default_factory=dict)

    def update_from_scene(self, scene: Scene):
        """Extracts and updates continuity from scene headings and node contents."""
        self.last_location = scene.heading
        scene_text = scene.heading + " " + " ".join(
            (n.text if hasattr(n, "text") else getattr(n, "content", "")) for n in scene.nodes
        )
        lower = scene_text.lower()

        # Update character states from dialogues
        for d in scene.dialogues:
            if d.parenthetical:
                self.character_states[d.character] = d.parenthetical

        # Auto-detect props and threads
        prop_keywords = ["weapon", "key", "armor", "file", "drive", "device", "token", "serum", "shard", "sword"]
        for p in prop_keywords:
            if p in lower and p not in self.somatic_props:
                self.somatic_props.append(p)

    def context_prompt(self) -> str:
        """Returns dense context string for next scene generation."""
        props_str = ", ".join(self.somatic_props[-4:]) if self.somatic_props else "None"
        threads_str = ", ".join(self.active_threads[-3:]) if self.active_threads else "Standard Progression"
        return (
            f"CONTINUITY CONSTRAINTS:\n"
            f"- Prior Location: {self.last_location or 'Beginning'}\n"
            f"- Somatic Props in Play: {props_str}\n"
            f"- Active Threads: {threads_str}\n"
            f"- Baseline Emotional Cadence: {self.emotional_state}"
        )
