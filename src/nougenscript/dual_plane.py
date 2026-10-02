"""Dual-Plane Script Model & Direct Word Re-Anchor Architecture.

Assimilates jlecomte/voice-activated-teleprompter & NouGenQ specs (Shards #30700 & #30701).
Fundamental Invariant: DISPLAY_PLANE != SPEECH_PLANE.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from nougenscript.core import NodeType, Screenplay

_CLEAN_WORDS = re.compile(r"[A-Za-z0-9']+")


@dataclass
class DisplaySpan:
    """Talent/prompter facing visual layout segment."""
    span_id: str
    node_type: NodeType
    rendered_text: str
    character: str | None = None
    is_spoken: bool = False
    speech_token_indices: list[int] = field(default_factory=list)


@dataclass
class SpokenToken:
    """Speech-recognition and phonetic stream token."""
    token_index: int
    raw_word: str
    normalized: str
    character: str
    display_span_id: str
    char_offset_in_span: int


class DualPlaneProjector:
    """Project an authored Screenplay AST bijectively into DisplayPlane and SpeechPlane."""

    @staticmethod
    def project(script: Screenplay) -> tuple[list[DisplaySpan], list[SpokenToken]]:
        display_spans: list[DisplaySpan] = []
        speech_tokens: list[SpokenToken] = []
        token_counter = 0

        for scene_idx, scene in enumerate(script.scenes):
            # Scene Heading span
            h_span_id = f"disp_{scene.scene_id}_heading"
            display_spans.append(
                DisplaySpan(
                    span_id=h_span_id,
                    node_type=NodeType.SCENE_HEADING,
                    rendered_text=scene.heading,
                    is_spoken=False,
                )
            )

            current_char = ""
            for node_idx, node in enumerate(scene.nodes):
                span_id = f"disp_{node.node_id}_{node_idx}"

                if node.type == NodeType.CHARACTER:
                    current_char = node.content.strip()
                    display_spans.append(
                        DisplaySpan(
                            span_id=span_id,
                            node_type=NodeType.CHARACTER,
                            rendered_text=current_char,
                            character=current_char,
                            is_spoken=False,
                        )
                    )
                elif node.type == NodeType.PARENTHETICAL:
                    display_spans.append(
                        DisplaySpan(
                            span_id=span_id,
                            node_type=NodeType.PARENTHETICAL,
                            rendered_text=f"({node.content.strip()})",
                            character=current_char,
                            is_spoken=False,
                        )
                    )
                elif node.type == NodeType.DIALOGUE:
                    text = node.content.strip()
                    span = DisplaySpan(
                        span_id=span_id,
                        node_type=NodeType.DIALOGUE,
                        rendered_text=text,
                        character=current_char,
                        is_spoken=True,
                    )

                    # Extract spoken lexical tokens
                    for match in _CLEAN_WORDS.finditer(text):
                        word = match.group(0)
                        st = SpokenToken(
                            token_index=token_counter,
                            raw_word=word,
                            normalized=word.lower(),
                            character=current_char,
                            display_span_id=span_id,
                            char_offset_in_span=match.start(),
                        )
                        span.speech_token_indices.append(token_counter)
                        speech_tokens.append(st)
                        token_counter += 1

                    display_spans.append(span)
                elif node.type in (NodeType.ACTION, NodeType.DIRECTION, NodeType.CUE, NodeType.TRANSITION):
                    display_spans.append(
                        DisplaySpan(
                            span_id=span_id,
                            node_type=node.type,
                            rendered_text=node.content.strip(),
                            is_spoken=False,
                        )
                    )

        return display_spans, speech_tokens

    @staticmethod
    def reanchor_by_word_index(speech_tokens: list[SpokenToken], clicked_index: int) -> SpokenToken | None:
        """Direct Word Re-Anchor (Shard #30700): instantly reset anchor without restarting session."""
        if 0 <= clicked_index < len(speech_tokens):
            return speech_tokens[clicked_index]
        return None
