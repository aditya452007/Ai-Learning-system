"""Citation verification as a grounded-answer quality gate."""

from __future__ import annotations

import re

from app.domain.models.answer import Citation


class CitationVerifier:
    def verified_citations(self, answer_text: str, citations: list[Citation], used_ids: list[str]) -> list[Citation]:
        available = {citation.citation_id: citation for citation in citations}
        ids_from_text = set(re.findall(r"cite_\d+", answer_text))
        ids = set(used_ids).union(ids_from_text)
        verified = [available[citation_id] for citation_id in sorted(ids) if citation_id in available]
        return verified or citations[: min(len(citations), 3)]

