from __future__ import annotations

from typing import Any, Iterable

from .models import DecisionRequest, ModelRunResult


_EVIDENCE_KEYS = ("evidenceRefs", "counterEvidenceRefs", "supportingEvidenceRefs", "evidence_refs")


class EvidenceVerifier:
    """Fail-closed reference verifier for the first runtime slice.

    Models may cite only evidence references supplied in the frozen DecisionRequest.
    Later resolvers can additionally verify file/URL/clause contents.
    """

    def verify(self, request: DecisionRequest, runs: Iterable[ModelRunResult]) -> dict[str, Any]:
        allowed = set(request.evidence_refs)
        cited: set[str] = set()
        for run in runs:
            cited.update(_extract_refs(run.parsed))

        unsupported = sorted(ref for ref in cited if ref not in allowed)
        supported = sorted(ref for ref in cited if ref in allowed)
        missing_usage = sorted(ref for ref in allowed if ref not in cited)
        coverage = 1.0 if not allowed and not unsupported else (len(supported) / len(allowed) if allowed else 0.0)
        return {
            "allowedEvidenceRefs": sorted(allowed),
            "citedEvidenceRefs": sorted(cited),
            "supportedRefs": supported,
            "unsupportedRefs": unsupported,
            "providedButUnusedRefs": missing_usage,
            "evidenceCoverage": round(coverage, 4),
            "pass": not unsupported,
        }


def _extract_refs(payload: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in _EVIDENCE_KEYS:
                if isinstance(value, str):
                    refs.add(value)
                elif isinstance(value, list):
                    refs.update(str(x) for x in value if x)
            else:
                refs.update(_extract_refs(value))
    elif isinstance(payload, list):
        for item in payload:
            refs.update(_extract_refs(item))
    return refs
