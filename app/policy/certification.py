from datetime import date
from app.models import CertificationResult


class CertificationRepository:
    def __init__(self, rules):
        self.rules = rules

    def lookup(self, standard_id: str, product_text: str) -> CertificationResult:
        for r in self.rules:
            if r.get("standard_id") != standard_id:
                continue
            is_verified = r.get("verified", True)
            if is_verified:
                return CertificationResult(
                    state="verified",
                    rule_type=r.get("rule_type"),
                    description=r.get("description"),
                    effective_date=(
                        date.fromisoformat(r["effective_date"])
                        if r.get("effective_date") else None
                    ),
                    evidence_ids=r.get("evidence_ids", []),
                )
            else:
                # QCO_PROPOSED or other unconfirmed entries: surface the text
                # but do NOT claim the rule is in force.
                return CertificationResult(
                    state="not_verified_in_prototype_corpus",
                    rule_type=r.get("rule_type"),
                    description=r.get("description"),
                    effective_date=None,
                    evidence_ids=r.get("evidence_ids", []),
                )

        return CertificationResult(
            state="not_verified_in_prototype_corpus",
            description=(
                "No verified certification or QCO mapping for this standard "
                "is included in the prototype corpus. "
                "SOURCE ACCESS RESTRICTED — DETAILS NOT VERIFIED."
            ),
        )
