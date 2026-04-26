from __future__ import annotations

from urllib.parse import urlparse

from schemas.site_candidate import SiteCandidate, VerifiedSiteCandidate


INVALID_HOST_TOKENS = {"google.", "bing.", "yahoo.", "doubleclick.", "facebook.com/l.php"}


def _looks_invalid(url: str | None) -> bool:
    if not url:
        return True
    lowered = url.lower()
    return any(token in lowered for token in INVALID_HOST_TOKENS)


def _normalize_domain(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    domain = parsed.netloc or parsed.path
    return domain.lower().removeprefix("www.").strip("/")


def _domain_matches(candidate_domain: str, actual_domain: str) -> bool:
    if not candidate_domain or not actual_domain:
        return False
    return actual_domain == candidate_domain or actual_domain.endswith(f".{candidate_domain}")


def verify_site_candidates(candidates: list[SiteCandidate]) -> list[VerifiedSiteCandidate]:
    verified: list[VerifiedSiteCandidate] = []

    for candidate in candidates:
        notes: list[str] = []
        url = candidate.candidate_search_url or candidate.base_url
        parsed = urlparse(url)
        ok = True

        if parsed.scheme != "https":
            ok = False
            notes.append("search_url_not_https")
        if _looks_invalid(url):
            ok = False
            notes.append("search_url_invalid_or_redirect_like")
        if not parsed.netloc:
            ok = False
            notes.append("missing_netloc")

        normalized_domain = _normalize_domain(url)
        expected_domain = _normalize_domain(candidate.base_domain or candidate.base_url)
        if expected_domain and normalized_domain and not _domain_matches(expected_domain, normalized_domain):
            ok = False
            notes.append("search_url_domain_mismatch")

        if candidate.candidate_listing_url:
            listing_domain = _normalize_domain(candidate.candidate_listing_url)
            if expected_domain and listing_domain and not _domain_matches(expected_domain, listing_domain):
                ok = False
                notes.append("listing_url_domain_mismatch")

        trust_score = 0.85 if any(tok in normalized_domain for tok in ["edu", "campus", "housing", "ohana"]) else 0.70
        structural_score = 0.80 if candidate.candidate_listing_url else 0.55
        verification_confidence = 0.90 if ok else 0.25

        verified.append(
            VerifiedSiteCandidate(
                **candidate.model_dump(),
                verified=ok,
                verified_search_url=url if ok else None,
                normalized_base_domain=normalized_domain or candidate.base_domain,
                verification_notes=notes,
                verification_confidence=verification_confidence,
                structural_score=structural_score,
                trust_score=trust_score,
            )
        )

    return verified
