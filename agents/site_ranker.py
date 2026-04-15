from __future__ import annotations

from schemas.site_candidate import VerifiedSiteCandidate


def rank_verified_sites(candidates: list[VerifiedSiteCandidate]) -> list[VerifiedSiteCandidate]:
    ranked: list[VerifiedSiteCandidate] = []
    for candidate in candidates:
        score = (
            0.35 * candidate.discovery_confidence
            + 0.25 * candidate.structural_score
            + 0.20 * candidate.trust_score
            + 0.20 * candidate.verification_confidence
        )
        candidate.overall_site_score = round(score, 4)
        ranked.append(candidate)

    ranked.sort(
        key=lambda row: (row.verified, row.overall_site_score, row.discovery_confidence),
        reverse=True,
    )
    return ranked
