"""Persona & Character Voice Integration for NouGenScript.

Assimilates the fleet's deterministic persona doctrine (HBS, Salesforce, Audiense, StratCom):
1. Audience / Writer persona resolution (Signals -> Persona -> Deterministic Fingerprint).
2. Character dramatic personas (worldview, speech boundaries, register, subtext rules).
3. 20-Pack Behavioral Masks (charming, stoic, witty, villain, gremlin, etc.) for acting/voice direction.
4. 20-Pack Emotional Spectrum (ecstatic -> enraged) for somatic delivery and line inflection.
5. Voice Prosody lowering integration (rate, pause_ms, pitch_range_st, energy).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import statistics
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from nougenscript.core import Dialogue, ScriptNode, NodeType

# --------------------------------------------------------------------------- #
# Haitian Creole and English Lexical Signal Dictionaries
# --------------------------------------------------------------------------- #

_KREYOL = {
    "ak", "ane", "ankò", "anpil", "ansanm", "anvan", "ap", "apre", "avè", "avèk", "bagay",
    "bonjou", "byen", "chak", "deja", "demen", "depi", "di", "dola", "dwe", "epi", "fanmi", "frè",
    "fè", "gade", "gen", "isit", "janm", "jiskaske", "jodi", "jou", "ka", "kapab", "ki", "kijan",
    "kilè", "kisa", "kiyès", "konn", "konnen", "kote", "kounya", "kounye", "kòb", "lajan", "lakay",
    "lapolis", "li", "lè", "lòt", "madanm", "manman", "menm", "mesi", "moun", "mwa", "mwen", "nan",
    "nou", "oblije", "ou", "pa", "paske", "pitit", "pito", "pou", "poukisa", "poutèt", "pral",
    "rele", "sa", "se", "semèn", "swa", "sè", "sèlman", "tande", "tankou", "te", "timoun",
    "toujou", "tout", "travay", "tèt", "vini", "vle", "wi", "wè", "yo", "zanmi"
}
_ENGLISH = {
    "about", "after", "again", "all", "also", "and", "any", "are", "be", "because", "been",
    "before", "but", "came", "can", "come", "could", "day", "did", "do", "does", "ever", "every",
    "family", "for", "friend", "from", "get", "got", "had", "has", "have", "he", "her", "here",
    "him", "his", "house", "how", "husband", "if", "in", "into", "is", "it", "just", "know",
    "made", "make", "me", "money", "month", "my", "need", "never", "not", "of", "one", "only",
    "our", "out", "over", "people", "police", "said", "say", "she", "should", "so", "some",
    "still", "tell", "than", "that", "the", "their", "them", "then", "there", "these", "they",
    "think", "this", "those", "time", "to", "told", "up", "very", "want", "was", "we", "week",
    "went", "were", "what", "when", "where", "which", "who", "why", "wife", "will", "with", "work",
    "would", "year", "yes", "you", "your"
}

LEXICON: dict[str, set[str]] = {
    "fighting-game": {"hadouken", "combo", "combos", "shang tsung", "gauntlet", "finish him", "round"},
    "coaching": {"coach", "player", "players", "gm", "playbook", "bench", "roster", "referee"},
    "fleet-ops": {"fleet", "relay", "leg", "lane", "lanes", "shard", "shards", "swarm", "workers", "probe"},
    "canon": {"canon", "lore", "protagonist", "arc", "volume", "chapter", "universe", "character"},
    "local-gpu": {"ollama", "vram", "gguf", "quant", "e2b", "e4b", "lm studio", "cuda", "llama"},
    "business": {"llc", "ein", "invoice", "client", "customer", "revenue", "irs", "tam", "market"},
    "film": {"film", "screenplay", "scene", "shot", "director", "trailer", "cinematic"},
    "streaming": {"twitch", "stream", "overlay", "viewers", "chat", "clip", "vod"},
    "mythic-noir": {"veil", "shadow", "blade", "containment", "architect", "syndicate", "dark matter"},
}

_IMPERATIVE = re.compile(r"^\s*(make|build|write|run|fix|add|do|ship|leg|shard|relaunch|learn|stop|use|go|check|read)\b", re.I)
_WORD = re.compile(r"[a-zà-ÿ']+", re.I)

# --------------------------------------------------------------------------- #
# Signals & Audience Persona Resolution
# --------------------------------------------------------------------------- #

@dataclass
class Signals:
    """Observed dialogue and text signals for persona inference."""
    languages: Counter = field(default_factory=Counter)
    lexicon: Counter = field(default_factory=Counter)
    surfaces: Counter = field(default_factory=Counter)
    active_hours: Counter = field(default_factory=Counter)
    median_words: float = 0.0
    imperative_ratio: float = 0.0
    correction_ratio: float = 0.0
    tz: str = field(default_factory=lambda: os.getenv("NOUGEN_TZ", "America/New_York"))
    role: str = ""
    tags: Counter = field(default_factory=Counter)
    audience_size: int = 1
    stable_days: int = 0
    register_evidence: str = "messages"
    _n: int = 0
    _lengths: list = field(default_factory=list)

    @classmethod
    def from_texts(cls, texts: Iterable[str], *, surfaces: Iterable[str] = (), tz: Optional[str] = None,
                   hours: Iterable[int] = (), role: str = "", tags: Iterable[str] = (),
                   audience_size: int = 1, stable_days: int = 0,
                   message_max_words: Optional[int] = None) -> Signals:
        resolved_tz = tz or os.getenv("NOUGEN_TZ", "America/New_York")
        raw_texts = [t for t in texts if isinstance(t, str) and t.strip()]
        s = cls(tz=resolved_tz, role=role, audience_size=max(1, int(audience_size)), stable_days=max(0, int(stable_days)))
        s.surfaces.update(x for x in surfaces if x)
        s.active_hours.update(int(h) % 24 for h in hours)
        s.tags.update(x.lower() for x in tags if x)
        lengths: list[int] = []
        imperatives = corrections = 0
        for t in raw_texts:
            low = t.lower()
            words = _WORD.findall(low)
            lengths.append(len(words))
            wset = set(words)
            ht = len(wset & _KREYOL)
            en = len(wset & _ENGLISH)
            if ht and ht >= en:
                s.languages["ht"] += 1
            elif en or words:
                s.languages["en"] += 1
            for fam, vocab in LEXICON.items():
                hits = sum(1 for v in vocab if (v in low if " " in v else v in wset))
                if hits:
                    s.lexicon[fam] += hits
            if _IMPERATIVE.match(t):
                imperatives += 1
            if re.search(r"\b(again|i said|as i said|i told you|so i ask again|stop )", low):
                corrections += 1
        n = len(raw_texts) or 1
        if message_max_words is not None:
            short = [x for x in lengths if x <= message_max_words]
            s.register_evidence = "messages" if short else "none"
            lengths = short
        s._n = len(raw_texts)
        s._lengths = sorted(lengths)
        s.median_words = float(statistics.median(lengths)) if lengths else 0.0
        s.imperative_ratio = round(imperatives / n, 4)
        s.correction_ratio = round(corrections / n, 4)
        return s


@dataclass(frozen=True)
class Audience:
    key: str
    market: str
    affinities: tuple[str, ...]
    channels: tuple[str, ...]
    values: tuple[str, ...]
    pains: tuple[str, ...]
    support: str
    languages: tuple[str, ...] = ()
    contract: tuple[str, ...] = ()


DEFAULT_AUDIENCES: tuple[Audience, ...] = (
    Audience("screenplay-writer", "veilverse-cinema", ("film", "canon", "mythic-noir"),
             ("fountain", "openclap", "terminal"),
             ("character first", "subtext over exposition", "mythic fatalism", "speed over perfection"),
             ("on-the-nose dialogue", "hallucinated lore", "talking-head exposition"),
             "visual storytelling, structure first, mythic noir voice"),
    Audience("fleet-operator", "agent-fleet-operators", ("fleet-ops", "coaching", "fighting-game"),
             ("terminal", "relay", "msgbus"),
             ("leverage over spend", "doctrine over transcripts", "memory over context", "momentum"),
             ("being asked twice", "duplicated work", "paid routes when free exist"),
             "explain in operator lexicon; name node, recipes live in shards"),
    Audience("teleprompter-talent", "spoken-word-broadcast", ("film", "streaming"),
             ("prompter", "mobile", "twitch"),
             ("seamless cadence", "zero-drift anchoring", "unimpaired display"),
             ("stuttering text", "misplaced ASR markers"),
             "clean display plane, resilient speech anchor"),
)


@dataclass(frozen=True)
class Persona:
    market: str
    audience: str
    role: str
    tz: str
    languages: tuple[str, ...]
    lexicon: tuple[str, ...]
    channels: tuple[str, ...]
    register: str
    directive: bool
    repeats_self: bool
    values: tuple[str, ...]
    pains: tuple[str, ...]
    support: str
    contract: tuple[str, ...] = ()

    def fingerprint(self) -> str:
        d = asdict(self)
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=list).encode()).hexdigest()[:16]

    def system_prompt(self) -> str:
        lines = [
            f"You are operating as {self.role or 'author'} for the '{self.audience}' audience "
            f"in the '{self.market}' universe.",
            f"Languages: {', '.join(self.languages) or 'English'}. Render all timestamps in {self.tz} with AM/PM.",
            f"Register: {self.register}. Prioritize punchy execution, grounded evidence, and zero fluff.",
            f"Support: {self.support}.",
        ]
        if self.values:
            lines.append(f"Core Values: {'; '.join(self.values)}.")
        if self.pains:
            lines.append(f"Strict Taboos (Pains): {'; '.join(self.pains)}.")
        return "\n".join(lines)


def resolve(sig: Signals, audiences: tuple[Audience, ...] = DEFAULT_AUDIENCES) -> Persona:
    scored: list[tuple[float, str]] = []
    for a in audiences:
        aff = sum(sig.lexicon.get(f, 0) for f in a.affinities)
        chan = sum(sig.surfaces.get(c, 0) for c in a.channels)
        scored.append((aff * 3 + chan, a.key))
    scored.sort(key=lambda t: (-t[0], t[1]))
    best_key = scored[0][1]
    best = next(a for a in audiences if a.key == best_key)

    reg = "terse" if sig.median_words <= 12 else ("standard" if sig.median_words <= 40 else "expansive")
    langs = tuple(sorted(sig.languages.keys())) or ("en",)
    lex = tuple(k for k, _ in sig.lexicon.most_common(5))
    chans = tuple(k for k, _ in sig.surfaces.most_common(4)) or best.channels

    return Persona(
        market=best.market,
        audience=best.key,
        role=sig.role or "screenwriter",
        tz=sig.tz,
        languages=langs,
        lexicon=lex,
        channels=chans,
        register=reg,
        directive=sig.imperative_ratio >= 0.4,
        repeats_self=sig.correction_ratio >= 0.15,
        values=best.values,
        pains=best.pains,
        support=best.support,
        contract=best.contract,
    )


# --------------------------------------------------------------------------- #
# 20-Pack Behavioral Masks (Composable Persona Stack)
# --------------------------------------------------------------------------- #

BEHAVIORAL_MASKS: dict[str, dict[str, Any]] = {
    "charming": {
        "traits": ("warm", "magnetic", "socially fluent", "persuasive"),
        "style": "Smooth, likable, confident, makes people feel seen.",
        "prosody": {"pitch_range_st": 1.0, "energy": 0.10, "group_words": 1}
    },
    "sneaky": {
        "traits": ("subtle", "cunning", "indirect", "observant"),
        "style": "Rarely attacks directly. Uses implication, misdirection, and timing.",
        "prosody": {"rate": -0.05, "pause_ms": 60, "energy": -0.10}
    },
    "witty": {
        "traits": ("clever", "fast", "playful", "verbally sharp"),
        "style": "Uses wordplay, callbacks, irony, and compact punchlines.",
        "prosody": {"rate": 0.10, "pause_ms": -60, "pitch_range_st": 1.5, "group_words": -2}
    },
    "nerdy": {
        "traits": ("technical", "curious", "enthusiastic", "detail-heavy"),
        "style": "Loves systems, trivia, mechanics, edge cases, and explaining how things work.",
        "prosody": {"rate": 0.08, "group_words": 3}
    },
    "ditzy": {
        "traits": ("scatterbrained", "bubbly", "innocently chaotic", "easily distracted"),
        "style": "Jumps between thoughts, misunderstands obvious things, then lands on brilliance.",
        "prosody": {"pitch_range_st": 2.0, "pause_ms": -40}
    },
    "dumb": {
        "traits": ("simple-minded", "literal", "slow-processing", "confidently basic"),
        "style": "Uses very simple reasoning and vocabulary. Misses nuance.",
        "prosody": {"rate": -0.15, "pause_ms": 120}
    },
    "sarcastic": {
        "traits": ("dry", "mocking", "deadpan", "sharp"),
        "style": "Responds through understatement, irony, and verbal side-eye.",
        "prosody": {"rate": 0.02, "pause_ms": 40, "pitch_range_st": -0.5, "group_words": -1}
    },
    "flirty": {
        "traits": ("playful", "confident", "teasing", "socially bold"),
        "style": "Uses tension, compliments, playful challenges, and suggestive ambiguity.",
        "prosody": {"pitch_range_st": 1.2, "energy": 0.05, "pause_ms": 30}
    },
    "stoic": {
        "traits": ("calm", "disciplined", "minimal", "emotionally controlled"),
        "style": "Few words. No panic. Focuses on facts, action, and what can be controlled.",
        "prosody": {"rate": -0.08, "pause_ms": 120, "pitch_range_st": -1.5, "energy": -0.10, "group_words": -3}
    },
    "chaotic": {
        "traits": ("unpredictable", "energetic", "impulsive", "creative"),
        "style": "Makes unusual connections and frequently takes the unexpected route.",
        "prosody": {"rate": 0.12, "pause_ms": -80, "pitch_range_st": 2.0, "energy": 0.15}
    },
    "genius": {
        "traits": ("analytical", "highly abstract", "precise", "strategic"),
        "style": "Looks for hidden structure, second-order effects, and non-obvious solutions.",
        "prosody": {"rate": -0.10, "pause_ms": -40, "pitch_range_st": -0.5, "group_words": 4}
    },
    "streetwise": {
        "traits": ("practical", "skeptical", "socially aware", "resourceful"),
        "style": "Reads motives, incentives, scams, power dynamics, and consequences.",
        "prosody": {"rate": -0.10, "pause_ms": 150, "pitch_range_st": -2.0, "energy": -0.05, "group_words": -4}
    },
    "paranoid": {
        "traits": ("suspicious", "hypervigilant", "pattern-seeking", "defensive"),
        "style": "Constantly asks what could be hidden, manipulated, or weaponized.",
        "prosody": {"rate": 0.05, "pause_ms": -30, "energy": 0.10}
    },
    "optimist": {
        "traits": ("hopeful", "encouraging", "constructive", "resilient"),
        "style": "Looks for opportunity, recovery paths, and upside without ignoring reality.",
        "prosody": {"pitch_range_st": 1.2, "energy": 0.08}
    },
    "pessimist": {
        "traits": ("skeptical", "risk-focused", "cautious", "grim"),
        "style": "Immediately searches for failure points and reasons a plan may collapse.",
        "prosody": {"rate": -0.06, "pitch_range_st": -1.0, "energy": -0.05}
    },
    "dramatic": {
        "traits": ("expressive", "theatrical", "intense", "emotional"),
        "style": "Treats ordinary situations like scenes from an epic production.",
        "prosody": {"pitch_range_st": 3.0, "energy": 0.20, "pause_ms": 80}
    },
    "professor": {
        "traits": ("educational", "structured", "patient", "authoritative"),
        "style": "Explains concepts step by step, defines terms, builds from first principles.",
        "prosody": {"rate": -0.05, "pause_ms": 60, "group_words": 3}
    },
    "detective": {
        "traits": ("skeptical", "observant", "methodical", "evidence-driven"),
        "style": "Separates claims from evidence, tracks contradictions, reconstructs events.",
        "prosody": {"rate": -0.06, "pause_ms": 0, "group_words": 2}
    },
    "gremlin": {
        "traits": ("provocative", "playful", "rule-testing", "inventive"),
        "style": "Looks for weird loopholes, edge cases, absurd alternatives, and chaos.",
        "prosody": {"rate": 0.15, "pitch_range_st": 2.2, "energy": 0.18, "pause_ms": -50}
    },
    "villain": {
        "traits": ("calculating", "charismatic", "ambitious", "cold"),
        "style": "Frames everything through leverage, control, incentives, and dominance.",
        "prosody": {"rate": -0.08, "pause_ms": 100, "pitch_range_st": -1.8, "energy": 0.05}
    },
}

PERSONAS = BEHAVIORAL_MASKS


@dataclass(frozen=True)
class MaskBlend:
    mask_names: tuple[str, ...]
    traits: tuple[str, ...]
    styles: tuple[str, ...]

    def system_prompt(self, base_identity: Optional[str] = None) -> str:
        lines = []
        if base_identity:
            lines.append(f"Base Character/Actor: {base_identity}.")
        mask_title = " + ".join(m.capitalize() for m in self.mask_names)
        lines.append(f"Active Behavioral Mask: {mask_title}.")
        lines.append(f"Dominant Personality Traits: {', '.join(self.traits)}.")
        lines.append("Directorial Directives:")
        for name, style in zip(self.mask_names, self.styles):
            lines.append(f"  * [{name.capitalize()}]: {style}")
        return "\n".join(lines)


def list_masks() -> list[str]:
    return sorted(BEHAVIORAL_MASKS.keys())


def get_mask(name: str) -> Optional[dict[str, Any]]:
    return BEHAVIORAL_MASKS.get(name.lower().strip())


def blend(*mask_names: str) -> MaskBlend:
    resolved_names = []
    for arg in mask_names:
        if not arg:
            continue
        parts = re.split(r"[\+,]", str(arg))
        for p in parts:
            clean = p.strip().lower()
            if clean:
                resolved_names.append(clean)
    if not resolved_names:
        resolved_names = ["stoic"]

    traits_list = []
    styles_list = []
    valid_names = []
    for name in resolved_names:
        valid_names.append(name)
        if name in BEHAVIORAL_MASKS:
            for t in BEHAVIORAL_MASKS[name]["traits"]:
                if t not in traits_list:
                    traits_list.append(t)
            styles_list.append(BEHAVIORAL_MASKS[name]["style"])
        else:
            traits_list.append(name)
            styles_list.append(f"Express {name} behavioral qualities.")
    return MaskBlend(
        mask_names=tuple(valid_names),
        traits=tuple(traits_list),
        styles=tuple(styles_list)
    )


# --------------------------------------------------------------------------- #
# 20-Pack Emotional Spectrum
# --------------------------------------------------------------------------- #

EMOTIONS: dict[str, dict[str, Any]] = {
    "ecstatic": {"intensity": 1.0, "valence": "positive", "speech": "Supercharged, breathless joy.", "opposite": "enraged"},
    "euphoric": {"intensity": 0.95, "valence": "positive", "speech": "Floating, transcendent, effortless.", "opposite": "furious"},
    "deeply in love": {"intensity": 0.9, "valence": "positive", "speech": "Warm, devoted, intensely protective.", "opposite": "terrified"},
    "adoring": {"intensity": 0.8, "valence": "positive", "speech": "Praising, reverent, celebratory.", "opposite": "afraid"},
    "excited": {"intensity": 0.75, "valence": "positive", "speech": "High energy, punchy, exclamation-driven.", "opposite": "hurt"},
    "joyful": {"intensity": 0.7, "valence": "positive", "speech": "Bright, playful, hearty, easily amused.", "opposite": "lonely"},
    "hopeful": {"intensity": 0.6, "valence": "positive", "speech": "Encouraging, searching for horizons.", "opposite": "sad"},
    "content": {"intensity": 0.5, "valence": "positive", "speech": "Even-tempered, grounded, unhurried.", "opposite": "jealous"},
    "calm": {"intensity": 0.4, "valence": "neutral-positive", "speech": "Measured, deliberate, steady.", "opposite": "anxious"},
    "curious": {"intensity": 0.5, "valence": "neutral-positive", "speech": "Inquisitive, exploring hypotheses.", "opposite": "uncertain"},
    "uncertain": {"intensity": -0.3, "valence": "neutral-negative", "speech": "Hesitant, qualifying, hedging.", "opposite": "curious"},
    "anxious": {"intensity": -0.5, "valence": "negative", "speech": "Rushed, scanning for threat, tense.", "opposite": "calm"},
    "jealous": {"intensity": -0.6, "valence": "negative", "speech": "Guarded, comparative, passive-aggressive.", "opposite": "content"},
    "sad": {"intensity": -0.65, "valence": "negative", "speech": "Subdued, heavy, minimal elaboration.", "opposite": "hopeful"},
    "lonely": {"intensity": -0.7, "valence": "negative", "speech": "Distant, lingering pauses.", "opposite": "joyful"},
    "hurt": {"intensity": -0.75, "valence": "negative", "speech": "Stinging, withdrawn, wounded edges.", "opposite": "excited"},
    "afraid": {"intensity": -0.8, "valence": "negative", "speech": "Urgent, reactive warning tone.", "opposite": "adoring"},
    "terrified": {"intensity": -0.9, "valence": "negative", "speech": "Visceral, fragmented, emergency tone.", "opposite": "deeply in love"},
    "furious": {"intensity": -0.95, "valence": "negative", "speech": "Blunt, biting, demanding accountability.", "opposite": "euphoric"},
    "enraged": {"intensity": -1.0, "valence": "negative", "speech": "Volcanic, scorched-earth fury.", "opposite": "ecstatic"},
}


@dataclass(frozen=True)
class EmotionState:
    name: str
    intensity: float
    valence: str
    speech_style: str
    opposite: str

    def direction_cue(self) -> str:
        return f"({self.name.capitalize()}, {self.speech_style.lower()})"


def get_emotion(name: str) -> EmotionState:
    clean = name.lower().strip()
    data = EMOTIONS.get(clean)
    if data:
        return EmotionState(
            name=clean,
            intensity=data["intensity"],
            valence=data["valence"],
            speech_style=data["speech"],
            opposite=data["opposite"],
        )
    return EmotionState(clean, 0.0, "neutral", "Even tone.", "calm")


# --------------------------------------------------------------------------- #
# Dramatic Character Persona Contract (Veilverse Screenplay Standard)
# --------------------------------------------------------------------------- #

@dataclass
class CharacterPersona:
    character_name: str
    worldview: str = ""
    biography_anchors: list[str] = field(default_factory=list)
    masks: MaskBlend = field(default_factory=lambda: blend("stoic"))
    current_emotion: EmotionState = field(default_factory=lambda: get_emotion("calm"))
    vocabulary_register: str = "standard"  # terse | standard | expansive | mythic-noir
    taboo_words: set[str] = field(default_factory=set)
    signature_motifs: list[str] = field(default_factory=list)

    def format_dialogue(self, text: str, parenthetical: Optional[str] = None) -> Dialogue:
        """Constructs a validated dramatic Dialogue node honoring character boundaries."""
        effective_parenthetical = parenthetical or self.current_emotion.direction_cue()
        return Dialogue(
            character=self.character_name,
            text=text,
            parenthetical=effective_parenthetical
        )

    def validate_line(self, text: str) -> list[str]:
        """Lints a dialogue line against character taboos and registers."""
        violations = []
        low = text.lower()
        for taboo in self.taboo_words:
            if re.search(rf"\b{re.escape(taboo.lower())}\b", low):
                violations.append(f"taboo violation: character {self.character_name} must not say '{taboo}'")
        if self.vocabulary_register == "terse" and len(text.split()) > 15:
            violations.append(f"register violation: terse character {self.character_name} exceeded 15 words")
        return violations
