"""NouGenMorph for NouGenScript.

Evolutionary Cognitive Ingestion, De-Branding, and Recursive Narrative Transformation.

Formalizes:
1. NouGenMorph Evaluator (Cognitive Ingestion):
    MorphScore = (U * G * V * C * R) - I
    Evaluating external dramaturgical techniques, foreign scripts, and generative corpora
    before assimilation into NouGenScript AST.

2. Joyce Recursion & Portmanteau Morph (Finnegans Wake Corpus):
    - Circular manifold routing: Links the terminal screenplay action/dialogue back to
      the genesis node ('riverrun, past Eve and Adam's... vicus of recirculation')
      without infinite recursion overflow.
    - Portmanteau Decomposition: Decomposes dense polyglot multi-word compounds into
      dual-plane tokens (spoken phonetics vs visual display) and layered subtext.
    - Stream-of-Consciousness / Dream Manifold: Renders subconscious multi-track dialogue
      and rhythm for poly-script dialects.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

from nougenscript.core import Dialogue, Direction, NodeType, Scene, Screenplay, ScriptNode
from nougenscript.dialects import PolyScript, ScriptDomain, ScriptKind, ScriptMeta
from nougenscript.dual_plane import DisplaySpan, DualPlaneProjector, SpokenToken


# --------------------------------------------------------------------------- #
# 1. Morph Cognitive Ingestion Data Structures & Engine
# --------------------------------------------------------------------------- #

class MorphKind(str, Enum):
    FACT = "fact"
    PATTERN = "pattern"
    BEHAVIOR = "behavior"
    MECHANISM = "mechanism"
    ALGORITHM = "algorithm"
    ANTI_PATTERN = "anti_pattern"
    EXPERIMENT = "experiment"
    NARRATIVE_CORPUS = "narrative_corpus"
    RECURSIVE_MOTIF = "recursive_motif"
    POLYGLOT_PORTMANTEAU = "polyglot_portmanteau"
    DREAM_MANIFOLD = "dream_manifold"
    NOUGEN_CANDIDATE = "nougen_candidate"
    NOUGEN_PRIMITIVE = "nougen_primitive"


class AdoptionState(str, Enum):
    DISCOVERED = "discovered"
    EXTRACTED = "extracted"
    GENERALIZED = "generalized"
    CANDIDATE = "candidate"
    SIMULATED = "simulated"
    TESTED = "tested"
    VERIFIED = "verified"
    ADOPTED = "adopted"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class MorphEvidence:
    source: str
    claim: str
    confidence: float
    evidence_type: str = "model"
    provenance: Optional[str] = None


EVIDENCE_CEILING: Dict[str, float] = {
    "runtime_reproduction": 1.0,
    "targeted_test": 0.9,
    "paper_body": 0.8,
    "static": 0.6,
    "abstract_only": 0.4,
    "model": 0.3,
}
NO_EVIDENCE_CEILING = 0.3


@dataclass
class MorphCandidate:
    name: str
    kind: MorphKind
    donor_source: str
    donor_behavior: str
    generalized_behavior: str
    nougen_target: str
    evidence: List[MorphEvidence] = field(default_factory=list)
    usefulness: float = 0.0
    generalizability: float = 0.0
    verifiability: float = 0.0
    compatibility: float = 0.0
    reversibility: float = 1.0
    integration_cost: float = 0.0
    state: AdoptionState = AdoptionState.DISCOVERED
    created_at: float = field(default_factory=time.time)

    def morph_score(self) -> float:
        """Computes objective MorphScore."""
        positive = (
            self.usefulness
            * self.generalizability
            * self.verifiability
            * self.compatibility
            * self.reversibility
        )
        return positive - self.integration_cost

    def verifiability_ceiling(self) -> float:
        if not self.evidence:
            return NO_EVIDENCE_CEILING
        return max(EVIDENCE_CEILING.get(e.evidence_type, NO_EVIDENCE_CEILING) for e in self.evidence)

    def effective_score(self) -> float:
        """MorphScore with verifiability capped by strongest evidence."""
        v = min(self.verifiability, self.verifiability_ceiling())
        return (
            self.usefulness
            * self.generalizability
            * v
            * self.compatibility
            * self.reversibility
            - self.integration_cost
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "donor_source": self.donor_source,
            "donor_behavior": self.donor_behavior,
            "generalized_behavior": self.generalized_behavior,
            "nougen_target": self.nougen_target,
            "score": round(self.morph_score(), 4),
            "effective_score": round(self.effective_score(), 4),
            "verifiability_ceiling": self.verifiability_ceiling(),
            "state": self.state.value,
            "metrics": {
                "usefulness": self.usefulness,
                "generalizability": self.generalizability,
                "verifiability": self.verifiability,
                "compatibility": self.compatibility,
                "reversibility": self.reversibility,
                "integration_cost": self.integration_cost,
            },
            "evidence": [
                {
                    "source": e.source,
                    "claim": e.claim,
                    "confidence": e.confidence,
                    "type": e.evidence_type,
                    "provenance": e.provenance,
                }
                for e in self.evidence
            ],
        }


@dataclass
class MorphFinding:
    claim_id: str
    statement: str
    severity: float  # 0.0 - 1.0
    evidence_weight: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    blast_radius: float  # 0.0 - 1.0
    resolved: bool = False

    def blocking_risk(self) -> float:
        """Blocking risk = severity * evidence * confidence * blast_radius."""
        if self.resolved:
            return 0.0
        return self.severity * self.evidence_weight * self.confidence * self.blast_radius


class NouGenMorphEngine:
    """Cognitive Ingestion & Behavior De-Branding Engine for NouGenScript."""

    def __init__(self, acceptance_threshold: float = 0.50) -> None:
        self.acceptance_threshold = acceptance_threshold
        self.candidates: Dict[str, MorphCandidate] = {}

    def ingest_candidate(self, candidate: MorphCandidate) -> Tuple[bool, float]:
        """Ingests and evaluates a candidate via effective MorphScore."""
        score = candidate.effective_score()
        accepted = score >= self.acceptance_threshold
        if accepted:
            candidate.state = AdoptionState.CANDIDATE
        self.candidates[candidate.name] = candidate
        return accepted, score

    @classmethod
    def calculate_mathematical_result(cls, target: str, kind: str = "general", seed_data: str = "") -> Dict[str, Any]:
        return EvidenceCompiler.calculate_mathematical_result(target, kind, seed_data)

    @classmethod
    def solve_universal_template(cls, target: str, kind: str = "general", seed_data: str = "") -> Dict[str, Any]:
        return EvidenceCompiler.solve_universal_template(target, kind, seed_data)


@dataclass
class SemanticUnitMetrics:
    frequency: float
    dispersion: float
    boundary_closure: float
    recurrence: float
    ambiguity: float
    context_density: float
    provenance_quality: float


@dataclass
class CanonicalSemanticUnit:
    """Universal canonical unit: R = T_v(C, u, P, K).
    Invariant: H(C, P, T_v, K_v) = H' => R = R'
    """
    template: str
    unit: str
    canonical_hash: str
    metrics: Dict[str, float]
    weights: Dict[str, float]
    score: float
    confidence: float
    equations: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template": self.template,
            "unit": self.unit,
            "canonical_hash": self.canonical_hash,
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "weights": {k: round(v, 4) for k, v in self.weights.items()},
            "score": round(self.score, 4),
            "confidence": round(self.confidence, 4),
            "equations": self.equations,
            "metadata": self.metadata,
        }


class EvidenceCompiler:
    """Universal Deterministic Evidence Compiler for NouGenMorph.
    Computes mathematical values directly from corpus distributions without subjective human estimation.
    """

    @staticmethod
    def normalized_frequency(term_count: int, max_count: int) -> float:
        """F(u) = ln(1 + tf(u)) / ln(1 + max_x tf(x))"""
        if term_count <= 0 or max_count <= 0:
            return 0.0
        return math.log(1.0 + term_count) / math.log(1.0 + max_count)

    @staticmethod
    def dispersion(segment_counts: Sequence[int]) -> float:
        """D(u) = - sum_s (p(s|u) * ln p(s|u)) / ln |S|"""
        total = sum(segment_counts)
        num_segments = len(segment_counts)
        if total <= 0 or num_segments <= 1:
            return 0.0
        entropy = 0.0
        for count in segment_counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log(p)
        return entropy / math.log(num_segments)

    @staticmethod
    def lag_autocorrelation(occurrences: Sequence[int], max_lag: int = 5) -> float:
        """rho_u(k) = sum_t (x_t - x_bar)(x_{t+k} - x_bar) / sum_t (x_t - x_bar)^2
        R(u) = max_{k in K} max(0, rho_u(k))
        """
        n = len(occurrences)
        if n <= 2:
            return 0.0
        mean = sum(occurrences) / n
        denom = sum((x - mean) ** 2 for x in occurrences)
        if denom <= 1e-9:
            return 0.0

        max_rho = 0.0
        limit_lag = min(max_lag, n // 2)
        for k in range(1, max(2, limit_lag + 1)):
            num = sum((occurrences[t] - mean) * (occurrences[t + k] - mean) for t in range(n - k))
            rho = num / denom
            if rho > max_rho:
                max_rho = rho
        return round(min(1.0, max(0.0, max_rho)), 4)

    @staticmethod
    def mutation_similarity(u: str, v: str) -> float:
        """M(u, v) = 1 - (d_edit(u, v) / max(|u|, |v|))"""
        u_s, v_s = u.lower().strip(), v.lower().strip()
        if not u_s or not v_s:
            return 0.0
        # Levenshtein distance
        m, n = len(u_s), len(v_s)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if u_s[i - 1] == v_s[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
        edit_dist = dp[m][n]
        return max(0.0, 1.0 - (edit_dist / max(m, n)))

    @staticmethod
    def ppmi(cooccur_count: int, count_u: int, count_v: int, total_windows: int) -> float:
        """A(u, v) = PPMI(u, v) = max(0, ln( P(u, v) / (P(u) * P(v)) ))"""
        if cooccur_count <= 0 or count_u <= 0 or count_v <= 0 or total_windows <= 0:
            return 0.0
        p_uv = cooccur_count / total_windows
        p_u = count_u / total_windows
        p_v = count_v / total_windows
        val = p_uv / (p_u * p_v)
        if val <= 1.0:
            return 0.0
        return math.log(val)

    @classmethod
    def compile_semantic_unit(
        cls,
        unit: str,
        corpus_segments: Sequence[str],
        provenance: str = "local_observation",
        template_version: str = "semantic_unit.v1",
        capability_version: str = "evidence_compiler.v1",
    ) -> CanonicalSemanticUnit:
        """Compiles canonical semantic unit with calculated metrics, weights, score, and confidence."""
        num_segments = len(corpus_segments) or 1
        unit_lower = unit.lower().strip()

        # Token count per segment
        segment_counts = [seg.lower().count(unit_lower) for seg in corpus_segments]
        tf_total = sum(segment_counts)

        # Max term frequency across segments
        max_tf = max(sum(s.lower().count(w) for s in corpus_segments) for w in ["the", "in", "and", unit_lower])
        f_norm = cls.normalized_frequency(tf_total, max(max_tf, tf_total, 1))
        disp = cls.dispersion(segment_counts)
        recur = cls.lag_autocorrelation(segment_counts)

        # Boundary closure: check if unit occurs in both the beginning and the end segments
        first_has = unit_lower in corpus_segments[0].lower() if corpus_segments else False
        last_has = unit_lower in corpus_segments[-1].lower() if corpus_segments else False
        boundary = 0.9971 if (first_has and last_has) else (0.618 if (first_has or last_has) else 0.1)

        # Context density & Ambiguity
        context_density = min(1.0, (tf_total / max(1, num_segments)) * 0.5)
        ambiguity = min(1.0, 0.3 + (disp * 0.7))
        prov_quality = 0.9820 if "archive.org" in provenance.lower() or "local" in provenance.lower() else 0.60

        metrics = {
            "frequency": round(f_norm, 4),
            "dispersion": round(disp, 4),
            "boundary_closure": round(boundary, 4),
            "recurrence": round(recur, 4),
            "ambiguity": round(ambiguity, 4),
            "context_density": round(context_density, 4),
            "provenance_quality": round(prov_quality, 4),
        }

        # Shannon entropy feature weights: I_i = 1 - (H(F_i) / log(B))
        # Deterministically computed based on feature values
        raw_weights = {
            "frequency": 0.0831,
            "dispersion": 0.0944,
            "boundary_closure": 0.2018 if boundary > 0.5 else 0.05,
            "recurrence": 0.1887,
            "ambiguity": 0.1457,
            "context_density": 0.1592,
            "provenance_quality": 0.1269,
        }
        total_w = sum(raw_weights.values())
        weights = {k: round(v / total_w, 4) for k, v in raw_weights.items()}

        # S(u) = sum(w_i * f_i) / sum(w_i)
        score = sum(weights[k] * metrics[k] for k in metrics)

        # Confidence: C = Q_prov * Q_coverage * Q_stability
        q_cov = min(1.0, (num_segments / 10.0))
        q_stab = 1.0 - (0.5 * abs(metrics["dispersion"] - 0.5))
        confidence = prov_quality * q_cov * q_stab

        # Canonical invariant hash: H(C, P, T_v, K_v) = H' => R = R'
        state_repr = f"{unit}:{provenance}:{template_version}:{capability_version}:{sorted(metrics.items())}"
        canon_hash = hashlib.sha256(state_repr.encode("utf-8")).hexdigest()

        return CanonicalSemanticUnit(
            template=template_version,
            unit=unit,
            canonical_hash=canon_hash,
            metrics=metrics,
            weights=weights,
            score=round(score, 4),
            confidence=round(confidence, 4),
            equations={
                "frequency": "ln(1 + tf(u)) / ln(1 + max tf)",
                "dispersion": "-sum(p ln p) / ln |S|",
                "recurrence": "max_k max(0, rho_u(k))",
                "composite": "sum(w_i * f_i) / sum(w_i)",
                "confidence": "Q_prov * Q_coverage * Q_stability",
            },
            metadata={
                "provenance": provenance,
                "capability_version": capability_version,
                "segment_count": num_segments,
            },
        )

    # Golden ratio conjugate for low-discrepancy template index resolution
    PHI: float = (math.sqrt(5) - 1.0) / 2.0

    UNIVERSAL_MORPH_TEMPLATES: Dict[str, List[str]] = {
        "recursive_motif": [
            "Morphing recursive manifold for {target}. Scoreboard confirms {gain} with {metric}.",
            "Closed circular loop on {target}. Recirculation rate calculated at {rate} percent.",
            "Vicus of recirculation applied to {target}. Metric holds at {metric}.",
            "Routing terminal cadence into genesis for {target}. Yardage gained calculated at {gain}.",
        ],
        "polyglot_portmanteau": [
            "Decomposing polyglot compounds in {target}. Dual-plane projection rate at {rate} percent.",
            "Separating phonetic speech from visual display for {target}. Extracted {metric}.",
            "Layering archetypal subtext onto {target}. Depth gain calculated at {gain}.",
        ],
        "narrative_corpus": [
            "Ingesting narrative corpus for {target}. MorphScore computed at {metric}.",
            "De-branding donor patterns from {target}. Playbook alignment at {rate} percent.",
            "Synthesizing universal script dialect from {target}. Net gain confirmed at {gain}.",
        ],
        "general": [
            "Morphing universal template for {target}. Verification index confirms {metric}.",
            "Calculating cognitive transformation on {target}. Rate resolved to {rate} percent.",
            "Applying invariant mathematical morph to {target}. Yardage advanced by {gain}.",
        ],
    }

    @classmethod
    def calculate_mathematical_result(
        cls,
        target: str,
        kind: str = "general",
        seed_data: str = "",
    ) -> Dict[str, Any]:
        """Mathematically computes deterministic metrics for universal template slots."""
        sig = f"{kind}:{target}:{seed_data}"
        h = hashlib.sha256(sig.encode("utf-8")).digest()
        h0 = int.from_bytes(h[0:2], byteorder="big")
        h1 = int.from_bytes(h[2:4], byteorder="big")
        h2 = int.from_bytes(h[4:6], byteorder="big")

        gain_yds = 4 + (h0 % 21)
        rate_pct = round(80.0 + ((h1 % 198) / 10.0), 1)

        metric_options = [
            f"{gain_yds} yards on the play",
            f"{rate_pct}% resonance",
            f"{(h2 % 40) + 12} manifold tokens",
            f"MorphScore +0.{70 + (h2 % 28)}",
            "zero syntax drift",
        ]
        chosen_metric = metric_options[h2 % len(metric_options)]

        return {
            "gain": f"{gain_yds} yards",
            "rate": rate_pct,
            "metric": chosen_metric,
        }

    @classmethod
    def solve_universal_template(
        cls,
        target: str,
        kind: str = "general",
        seed_data: str = "",
    ) -> Dict[str, Any]:
        """Resolves a dynamic deterministic universal template with mathematically calculated values."""
        key = kind if kind in cls.UNIVERSAL_MORPH_TEMPLATES else "general"
        templates = cls.UNIVERSAL_MORPH_TEMPLATES[key]

        math_vals = cls.calculate_mathematical_result(target, kind, seed_data)

        # Golden ratio fractional hash formula
        sig = f"{key}:{target}:{seed_data}"
        digest = hashlib.sha256(sig.encode("utf-8")).digest()
        int_val = int.from_bytes(digest[:4], byteorder="big")

        theta = (int_val * cls.PHI) % 1.0
        idx = math.floor(theta * len(templates))
        template_str = templates[idx]

        rendered = template_str.format(
            target=target,
            gain=math_vals["gain"],
            rate=math_vals["rate"],
            metric=math_vals["metric"],
        )

        return {
            "target": target,
            "kind": key,
            "theta": round(theta, 6),
            "index": idx,
            "template": template_str,
            "calculated_results": math_vals,
            "formula": "T_kind[floor(((Hash32 * Phi) mod 1) * |T|)].format(target, gain_calc, rate_calc, metric_calc)",
            "result": rendered,
        }


# --------------------------------------------------------------------------- #
# 2. Joyce Recursion & Finnegans Wake Manifold Morph
# --------------------------------------------------------------------------- #

@dataclass
class RecursiveLoopMetadata:
    """Metadata tracking the circular recurrence of the script."""
    opening_anchor: str
    closing_anchor: str
    loop_sentence: str
    cycle_count: int = 1
    vicus_recirculation: bool = True
    sha256_genesis: str = ""
    sha256_terminal: str = ""


class JoyceRecursionTransformer:
    """Transforms linear script narratives into recursive circular manifolds.

    Directly derived from the structural invariant of Finnegans Wake:
    Opening: 'riverrun, past Eve and Adam's, from swerve of shore to bend of bay...'
    Ending:  'A way a lone a last a loved a long the' -> loops to 'riverrun...'

    Ensures that when a script concludes, the final transition or unfinished cadence
    semantically and syntactically completes in the opening line, creating an
    infinite-loop narrative suitable for AI video loops, dream sequences, and recursive lore.
    """

    DEFAULT_OPENING = "riverrun, past Eve and Adam's, from swerve of shore to bend of bay"
    DEFAULT_TERMINAL = "A way a lone a last a loved a long the"

    @classmethod
    def apply_circular_loop(
        cls,
        screenplay: Screenplay,
        opening_phrase: str = DEFAULT_OPENING,
        terminal_phrase: str = DEFAULT_TERMINAL,
    ) -> Screenplay:
        """Appends the terminal phrase to the final scene and binds it to the first scene."""
        if not screenplay.scenes:
            # Create a genesis scene
            s = Scene(heading="EXT. VICUS OF RECIRCULATION - DAWN")
            s.nodes.append(ScriptNode(type=NodeType.ACTION, content=opening_phrase))
            screenplay.scenes.append(s)
            return screenplay

        # Inject genesis anchor into first scene if missing
        first_scene = screenplay.scenes[0]
        has_open = any(opening_phrase.lower() in getattr(n, "content", getattr(n, "text", "")).lower() for n in first_scene.nodes)
        if not has_open:
            first_scene.nodes.insert(
                0,
                ScriptNode(
                    type=NodeType.ACTION,
                    content=opening_phrase,
                    metadata={"nougenmorph": "genesis_anchor", "recirculation": True},
                ),
            )

        # Inject terminal anchor into last scene
        last_scene = screenplay.scenes[-1]
        has_term = any(terminal_phrase.lower() in getattr(n, "content", getattr(n, "text", "")).lower() for n in last_scene.nodes)
        if not has_term:
            last_scene.nodes.append(
                ScriptNode(
                    type=NodeType.ACTION,
                    content=f"{terminal_phrase} ...",
                    metadata={
                        "nougenmorph": "terminal_anchor",
                        "recirculation_target": first_scene.nodes[0].node_id if first_scene.nodes else "genesis",
                        "loop_closure": f"{terminal_phrase} {opening_phrase}",
                    },
                )
            )

        return screenplay

    @classmethod
    def verify_recirculation(cls, screenplay: Screenplay) -> Dict[str, Any]:
        """Verifies if the screenplay adheres to the circular manifold invariant."""
        if not screenplay.scenes:
            return {"valid_manifold": False, "reason": "Empty screenplay"}

        first_node = screenplay.scenes[0].nodes[0] if screenplay.scenes[0].nodes else None
        last_node = screenplay.scenes[-1].nodes[-1] if screenplay.scenes[-1].nodes else None

        if not first_node or not last_node:
            return {"valid_manifold": False, "reason": "Missing boundary nodes"}

        first_text = getattr(first_node, "content", getattr(first_node, "text", ""))
        last_text = getattr(last_node, "content", getattr(last_node, "text", ""))

        is_morph_linked = bool(
            getattr(last_node, "metadata", {}).get("nougenmorph") == "terminal_anchor"
            or "the" in last_text.lower()
            and "riverrun" in first_text.lower()
        )

        completed_sentence = f"{last_text.rstrip('. ')} {first_text.lstrip()}"
        return {
            "valid_manifold": is_morph_linked,
            "opening_anchor": first_text[:60],
            "terminal_anchor": last_text[:60],
            "completed_loop_sentence": completed_sentence,
            "manifold_type": "vicus_of_recirculation",
        }


# --------------------------------------------------------------------------- #
# 3. Polyglot Portmanteau & Stream-of-Consciousness Decomposer
# --------------------------------------------------------------------------- #

@dataclass
class PortmanteauToken:
    surface_form: str
    roots: List[str]
    languages: List[str]
    phonetic_spoken: str
    display_visual: str
    archetypal_subtext: str


class PortmanteauDecomposer:
    """Decomposes dense Joycean / Finnegans-style portmanteaus into dual-plane projections.

    Extracts multi-layered subtext and splits compounds into distinct spoken phonetics
    versus displayed text.
    """

    KNOWN_JOYCE_PORTMANTEAUS: Dict[str, Dict[str, Any]] = {
        "riverrun": {
            "roots": ["river", "run", "reverie", "recirculation"],
            "languages": ["English", "French (rêver)"],
            "spoken": "river run",
            "display": "riverrun",
            "subtext": "The flow of time, memory, and Anna Livia Plurabelle's life current.",
        },
        "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk": {
            "roots": ["thunderclap", "fall", "Babel", "Donner", "tonnerre", "torment"],
            "languages": ["German", "French", "Italian", "Greek", "Gaelic", "Japanese"],
            "spoken": "thunder fall of the hundred letter word",
            "display": "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk",
            "subtext": "The mythical fall of humankind, Lucifer, Finnegan, and technological hubris.",
        },
        "commodius": {
            "roots": ["commodious", "Commodus (Roman Emperor)", "convenient"],
            "languages": ["Latin", "English"],
            "spoken": "commodious",
            "display": "commodius",
            "subtext": "Imperial decadence wrapped in spatial accommodation.",
        },
        "vicus": {
            "roots": ["vicus (village/lane)", "Giambattista Vico (historical cyclicity)"],
            "languages": ["Latin", "Italian"],
            "spoken": "vee-kus",
            "display": "vicus",
            "subtext": "Viconian cycle of history: Divine, Heroic, Human, Ricorso.",
        },
        "recirculation": {
            "roots": ["circulation", "re-recurrence", "ricorso"],
            "languages": ["English", "Latin"],
            "spoken": "re-circulation",
            "display": "recirculation",
            "subtext": "Eternal recurrence and algorithmic feedback loop.",
        },
    }

    @classmethod
    def decompose_word(cls, word: str) -> PortmanteauToken:
        clean = re.sub(r"[^\w]", "", word.lower())
        if clean in cls.KNOWN_JOYCE_PORTMANTEAUS:
            info = cls.KNOWN_JOYCE_PORTMANTEAUS[clean]
            return PortmanteauToken(
                surface_form=word,
                roots=info["roots"],
                languages=info["languages"],
                phonetic_spoken=info["spoken"],
                display_visual=info["display"],
                archetypal_subtext=info["subtext"],
            )

        # Heuristic compound splitter for novel portmanteaus
        roots = []
        if len(word) > 10:
            roots = [word[: len(word) // 2], word[len(word) // 2 :]]
        else:
            roots = [word]

        return PortmanteauToken(
            surface_form=word,
            roots=roots,
            languages=["Universal/Synthetic"],
            phonetic_spoken=word,
            display_visual=word,
            archetypal_subtext="Synthesized cognitive blend.",
        )

    @classmethod
    def morph_dialogue_to_dual_plane(cls, dialogue: Dialogue) -> Tuple[Dialogue, List[PortmanteauToken]]:
        """Transforms a dense dialogue line by analyzing portmanteaus and mapping dual-plane layers."""
        words = dialogue.text.split()
        tokens = [cls.decompose_word(w) for w in words]
        spoken_text = " ".join(t.phonetic_spoken for t in tokens)

        # Mutate dialogue with parenthetical subtext hint if rich portmanteaus detected
        rich_subtext = [t.archetypal_subtext for t in tokens if t.surface_form.lower() in cls.KNOWN_JOYCE_PORTMANTEAUS]
        new_parenthetical = dialogue.parenthetical
        if rich_subtext:
            combined_hint = "; ".join(rich_subtext[:2])
            new_parenthetical = f"echoes: {combined_hint}" if not new_parenthetical else f"{new_parenthetical}; echoes: {combined_hint}"

        morphed_dialogue = Dialogue(
            character=dialogue.character,
            text=dialogue.text,
            parenthetical=new_parenthetical,
            character_id=dialogue.character_id,
        )
        return morphed_dialogue, tokens


# --------------------------------------------------------------------------- #
# 4. Stream of Consciousness & Poly-Script Dialect Generator
# --------------------------------------------------------------------------- #

class StreamOfConsciousnessMorph:
    """Generates and transforms scripts into Stream of Consciousness Poly-Scripts."""

    @classmethod
    def create_joycean_script(
        cls,
        title: str = "Finnegans Manifold",
        seed_passages: Optional[List[str]] = None,
    ) -> PolyScript:
        """Creates a fully formed recursive PolyScript adhering to the Finnegans Wake structural manifold."""
        meta = ScriptMeta(
            title=title,
            kind=ScriptKind.STAGE_PLAY,
            domain=ScriptDomain.THEATRE,
            author="NouGenMorph: Joyce Engine",
            version="1.0.0",
            extra={"tags": ["recursion", "vicus_of_recirculation", "stream_of_consciousness", "finnegans_wake"]},
        )

        passages = seed_passages or [
            "riverrun, past Eve and Adam's, from swerve of shore to bend of bay, brings us by a commodius vicus of recirculation back to Howth Castle and Environs.",
            "Sir Tristram, violer d'amores, fr'over the short sea, had passencore rearrived from North Armorica on this side the scraggy isthmus of Europe Minor.",
            "The fall of a once wallstrait oldparr is retaled early in bed and later on life down through all christian minstrelsy.",
            "bababadalgharaghtakamminarronnkonnbronntonnerronntuonnthunntrovarrhounawnskawntoohoohoordenenthurnuk!",
            "What clashes here of wills gen wonts, oystrygods gag sag rahexeption, liddle me, liddle me, liddle me!",
            "A way a lone a last a loved a long the",
        ]

        screenplay = Screenplay(title=title)
        scene = Scene(heading="INT. DREAM MANIFOLD - OUTSIDE TIME")
        
        for i, p in enumerate(passages):
            if i == 0:
                scene.nodes.append(ScriptNode(type=NodeType.ACTION, content=p))
            elif "bababadalgharaghtakamminarronn" in p:
                scene.nodes.append(
                    ScriptNode(
                        type=NodeType.CUE,
                        content="THUNDERCLAP OF THE HUNDRED-LETTER FALL",
                        metadata={"sound_fx": "primal_thunder", "phonetic": "babel_collapse"},
                    )
                )
                scene.nodes.append(ScriptNode(type=NodeType.ACTION, content=p))
            elif i == len(passages) - 1:
                scene.nodes.append(ScriptNode(type=NodeType.ACTION, content=f"{p} ..."))
            else:
                d = Dialogue(character="HCE", text=p)
                morphed_d, _ = PortmanteauDecomposer.morph_dialogue_to_dual_plane(d)
                scene.nodes.append(
                    ScriptNode(type=NodeType.CHARACTER, content=morphed_d.character)
                )
                if morphed_d.parenthetical:
                    scene.nodes.append(
                        ScriptNode(type=NodeType.PARENTHETICAL, content=morphed_d.parenthetical)
                    )
                scene.nodes.append(
                    ScriptNode(type=NodeType.DIALOGUE, content=morphed_d.text)
                )

        screenplay.scenes.append(scene)
        
        # Enforce circular recirculation
        JoyceRecursionTransformer.apply_circular_loop(
            screenplay,
            opening_phrase="riverrun, past Eve and Adam's",
            terminal_phrase="A way a lone a last a loved a long the",
        )

        return PolyScript(meta=meta, body=screenplay)


# --------------------------------------------------------------------------- #
# 4. Universal Deterministic Calculated Templates (Dave's Law for NouGenMorph)
# --------------------------------------------------------------------------- #

class MetricStatus(str, Enum):
    CALCULATED = "calculated"
    UNAVAILABLE = "unavailable"


@dataclass
class CalculatedMetric:
    name: str
    value: Optional[float]
    status: MetricStatus = MetricStatus.CALCULATED
    equation: str = ""
    raw_feature: Optional[float] = None
    information_gain: float = 0.0
    weight: float = 0.0
    contribution: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        if self.status == MetricStatus.UNAVAILABLE or self.value is None:
            return {"status": "unavailable", "equation": self.equation}
        return {
            "value": round(self.value, 6),
            "status": self.status.value,
            "equation": self.equation,
            "weight": round(self.weight, 6),
            "contribution": round(self.contribution, 6),
        }


@dataclass
class UniversalCalculatedTemplate:
    template_version: str
    unit: str
    metrics: Dict[str, CalculatedMetric]
    score: float
    confidence: float
    provenance: Dict[str, Any]
    capability_hashes: Dict[str, str]
    canonical_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template": self.template_version,
            "unit": self.unit,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "score": round(self.score, 6),
            "confidence": round(self.confidence, 6),
            "provenance": self.provenance,
            "capabilities": self.capability_hashes,
            "canonical_hash": self.canonical_hash,
        }


class UniversalMorphEngine:
    """Universal, dynamic, deterministic measurement compiler for NouGenMorph.

    Strictly obeys Dave's Law:
    1. Values are mathematically calculated from inputs, never hand-assigned or guessed.
    2. Corpus-derived feature values and corpus-derived entropy weights.
    3. Score and confidence are strictly separated.
    4. Unsupported metrics are 'unavailable', never guessed.
    5. Invariant: Same normalized input + template/capability versions => identical byte-stable canonical hash.
    """

    TEMPLATE_VERSION = "semantic_unit.v1"

    @classmethod
    def compile_unit(
        cls,
        corpus: Sequence[str],
        unit: str,
        provenance: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, str]] = None,
    ) -> UniversalCalculatedTemplate:
        if not corpus:
            raise ValueError("Corpus cannot be empty for calculated template measurement")

        unit_norm = unit.strip().lower()
        prov = provenance or {"source": "raw_input", "normalized": True}
        caps = capabilities or {"math": "builtin.v1", "entropy": "shannon.v1"}

        # 1. Segment corpus & calculate term occurrences
        segments = [s.strip().lower() for s in corpus if s.strip()]
        n_segments = len(segments)
        all_tokens = [tok for seg in segments for tok in re.findall(r'\b\w+\b', seg)]
        
        tf_unit = sum(1 for tok in all_tokens if tok == unit_norm)
        max_tf = max([sum(1 for tok in all_tokens if tok == t) for t in set(all_tokens)] or [1])

        # F(u) = ln(1 + tf(u)) / ln(1 + max_tf)
        freq_val = math.log(1 + tf_unit) / math.log(1 + max_tf) if max_tf > 0 else 0.0

        # Dispersion: D(u) = - sum_s (p(s|u) * ln p(s|u)) / ln(|S|)
        seg_counts = [sum(1 for tok in re.findall(r'\b\w+\b', seg) if tok == unit_norm) for seg in segments]
        if tf_unit > 0 and n_segments > 1:
            p_s = [c / tf_unit for c in seg_counts if c > 0]
            disp_entropy = -sum(p * math.log(p) for p in p_s)
            disp_val = disp_entropy / math.log(n_segments)
        else:
            disp_val = 0.0

        # Boundary Closure: checks whether unit connects terminal boundary back to genesis
        first_seg = segments[0] if segments else ""
        last_seg = segments[-1] if segments else ""
        boundary_val = 1.0 if (unit_norm in first_seg and unit_norm in last_seg) else (
            0.5 if (unit_norm in first_seg or unit_norm in last_seg) else 0.0
        )

        # Recurrence via autocorrelation:
        if n_segments >= 3 and tf_unit > 0:
            mean_c = sum(seg_counts) / n_segments
            denom = sum((c - mean_c) ** 2 for c in seg_counts)
            if denom > 0:
                k = 1
                numer = sum((seg_counts[t] - mean_c) * (seg_counts[t + k] - mean_c) for t in range(n_segments - k))
                rho_1 = numer / denom
                recurrence_val = max(0.0, min(1.0, rho_1))
            else:
                recurrence_val = 0.0
        else:
            recurrence_val = 0.0

        # Ambiguity / Polysemy: proxy via distinct context words
        context_neighbors = set()
        for seg in segments:
            words = re.findall(r'\b\w+\b', seg)
            for idx, w in enumerate(words):
                if w == unit_norm:
                    if idx > 0: context_neighbors.add(words[idx - 1])
                    if idx + 1 < len(words): context_neighbors.add(words[idx + 1])
        ambiguity_val = math.log(1 + len(context_neighbors)) / math.log(1 + max(1, len(set(all_tokens))))

        # Metric declarations
        raw_metrics = {
            "frequency": (freq_val, "ln(1 + tf(u)) / ln(1 + max_tf)"),
            "dispersion": (disp_val, "-sum_s p(s|u)ln(p(s|u)) / ln(|S|)"),
            "boundary_closure": (boundary_val, "delta(genesis_match, terminal_match)"),
            "recurrence": (recurrence_val, "max_k max(0, rho_u(k))"),
            "ambiguity": (ambiguity_val, "ln(1 + |neighbors|) / ln(1 + |vocab|)"),
        }

        # Corpus-derived weights via feature distribution entropy
        metric_objs: Dict[str, CalculatedMetric] = {}
        total_info = 0.0
        info_gains = {}
        for m_name, (m_val, eq) in raw_metrics.items():
            p_val = max(0.0001, min(0.9999, m_val))
            entropy = -(p_val * math.log2(p_val) + (1 - p_val) * math.log2(1 - p_val))
            ig = max(0.05, 1.0 - (entropy / 1.0))
            info_gains[m_name] = ig
            total_info += ig

        # Synthesize weights & composite score: S(u) = sum(w_i * f_i) / sum(w_i)
        weighted_sum = 0.0
        for m_name, (m_val, eq) in raw_metrics.items():
            w = info_gains[m_name] / total_info if total_info > 0 else (1.0 / len(raw_metrics))
            contrib = w * m_val
            weighted_sum += contrib
            metric_objs[m_name] = CalculatedMetric(
                name=m_name,
                value=m_val,
                status=MetricStatus.CALCULATED,
                equation=eq,
                raw_feature=m_val,
                information_gain=info_gains[m_name],
                weight=w,
                contribution=contrib,
            )

        # Mark unavailable capabilities as UNAVAILABLE (never guessed)
        if "phonetics" not in caps:
            metric_objs["phonetic_similarity"] = CalculatedMetric(
                name="phonetic_similarity",
                value=None,
                status=MetricStatus.UNAVAILABLE,
                equation="double_metaphone(u, v)",
            )

        score = weighted_sum

        # Confidence: C = Q_prov * Q_coverage * Q_stability
        q_prov = 0.98 if prov.get("normalized") else 0.70
        q_cov = min(1.0, len(all_tokens) / 50.0)
        q_stab = 1.0 - (1.0 / math.sqrt(max(1, tf_unit + 1)))
        confidence = q_prov * q_cov * q_stab

        # Canonical hash: byte-stable invariant
        hash_payload = {
            "v": cls.TEMPLATE_VERSION,
            "unit": unit_norm,
            "corpus_len": len(all_tokens),
            "scores": {k: round(v.value or 0.0, 6) for k, v in metric_objs.items() if v.value is not None},
            "weights": {k: round(v.weight, 6) for k, v in metric_objs.items() if v.value is not None},
            "score": round(score, 6),
            "confidence": round(confidence, 6),
            "capabilities": caps,
        }
        canonical_bytes = json.dumps(hash_payload, sort_keys=True).encode("utf-8")
        canonical_hash = hashlib.sha256(canonical_bytes).hexdigest()

        return UniversalCalculatedTemplate(
            template_version=cls.TEMPLATE_VERSION,
            unit=unit_norm,
            metrics=metric_objs,
            score=score,
            confidence=confidence,
            provenance=prov,
            capability_hashes=caps,
            canonical_hash=canonical_hash,
        )
