from app.models import LifecycleAssessment

def assess(standard, as_of=None):
    reasons = []
    warning = False

    for event in standard.lifecycle_events:
        if event.get("event") == "revision_under_print":
            reasons.append(
                "BIS material lists revision work for this standard; this does not by itself prove withdrawal of the published edition."
            )
        elif event.get("event") == "withdrawn_after_revision":
            warning = True
            reasons.append(
                f"Previous edition withdrawal event recorded after {event.get('date')}."
            )

    return LifecycleAssessment(
        standard_id=standard.standard_id,
        state="warning" if warning else "supported",
        as_of_date=as_of,
        reasons=reasons or ["No contradictory lifecycle event is stored in this prototype record."],
        evidence_ids=standard.evidence_ids,
    )
