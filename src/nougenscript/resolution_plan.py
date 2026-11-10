"""Build value-free, deterministic resolution plans from explicit UDCT policies."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nougenscript.dynamic_suggestions import resolution_for_path
from nougenscript.sources import audit_dynamic_source


@dataclass(frozen=True)
class ResolutionPlan:
    path: str
    line: int
    column: int
    rule_id: str
    slot: str
    resolution: str | None
    required_import: str | None
    rationale: str
    review_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "rule_id": self.rule_id,
            "slot": self.slot,
            "resolution": self.resolution,
            "required_import": self.required_import,
            "rationale": self.rationale,
            "review_required": self.review_required,
        }


def plan_dynamic_resolutions(
    source: str | Path,
    policy: str | Path = ".udct-policy.json",
    ref: str | None = None,
) -> list[ResolutionPlan]:
    """Map policy matches to reviewable language expressions without changing source."""
    findings = audit_dynamic_source(source, policy, ref)
    plans = []
    for finding in findings:
        resolution, required_import = resolution_for_path(finding.path, finding.slot)
        plans.append(ResolutionPlan(
            path=finding.path,
            line=finding.line,
            column=finding.column,
            rule_id=finding.rule_id,
            slot=finding.slot,
            resolution=resolution,
            required_import=required_import,
            rationale=finding.rationale,
        ))
    return plans
