"""OpenClap Universal AI Film & Screenplay Interchange (.clap) Serializer.

Assimilated from jbilcke-hf/OpenClap-Format standard.
Multi-document YAML stream architecture with multi-track timeline tracks.
"""
from __future__ import annotations

import gzip
from dataclasses import dataclass, field
from typing import Any

import yaml

from nougenscript.core import Screenplay


@dataclass
class ClapDocument:
    header: dict[str, Any]
    meta: dict[str, Any]
    entities: list[dict[str, Any]] = field(default_factory=list)
    scenes: list[dict[str, Any]] = field(default_factory=list)
    segments: list[dict[str, Any]] = field(default_factory=list)


class OpenClapSerializer:
    """Serializes Screenplay AST into OpenClap multi-document YAML or compressed .clap bundle."""

    @staticmethod
    def to_documents(script: Screenplay) -> list[dict[str, Any]]:
        # 1. ClapHeader
        header = {
            "format": "clap-0",
            "entityCount": len({d.character for d in script.dialogue_lines if d.character}),
            "sceneCount": len(script.scenes),
            "segmentCount": len(script.dialogue_lines),
        }

        # 2. ClapMeta
        meta = {
            "id": script.script_hash[:16],
            "title": script.title,
            "author": script.author,
            "engine": "Veo 3.1 / Wan2.1",
            "resolution": "3840x2160",
            "framerate": 24,
        }

        # 3. ClapEntity[]
        characters = sorted({d.character for d in script.dialogue_lines if d.character})
        entities = [
            {
                "id": f"ent_{char.lower()}",
                "name": char,
                "category": "character",
                "identityPrompt": f"Consistent portrait of {char}, hyper-realistic dark cinematic lighting.",
            }
            for char in characters
        ]

        # 4. ClapScene[]
        scenes = [
            {
                "id": s.scene_id,
                "sequence": s.scene_number,
                "heading": s.heading,
                "dialogueCount": len(s.dialogues),
            }
            for s in script.scenes
        ]

        # 5. ClapSegment[] (Multi-Track Timeline Matrix)
        segments: list[dict[str, Any]] = []
        track_time = 0.0
        for s in script.scenes:
            for d in s.dialogues:
                duration = max(2.0, len(d.text.split()) * 0.4)
                seg = {
                    "id": f"seg_{d.node_id}",
                    "sceneId": s.scene_id,
                    "startTime": track_time,
                    "endTime": track_time + duration,
                    "track_video": f"Cinematic shot of {d.character} speaking: {d.text[:40]}...",
                    "track_dialogue": {
                        "speaker": d.character,
                        "utterance": d.text,
                        "parenthetical": d.parenthetical or "",
                    },
                    "track_sound": "Pneumatic airlock hiss, low atmospheric industrial rumble.",
                    "track_music": "Dark ambient drone in D minor.",
                }
                segments.append(seg)
                track_time += duration

        return [header, meta, {"entities": entities}, {"scenes": scenes}, {"segments": segments}]

    @classmethod
    def to_yaml_stream(cls, script: Screenplay) -> str:
        docs = cls.to_documents(script)
        return yaml.dump_all(docs, sort_keys=False)

    @classmethod
    def to_clap_binary(cls, script: Screenplay) -> bytes:
        """Export as gzip compressed .clap package."""
        yaml_text = cls.to_yaml_stream(script)
        return gzip.compress(yaml_text.encode("utf-8"))
