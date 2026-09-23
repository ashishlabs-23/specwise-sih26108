from app.models import Requirement

def validate_requirements(requirements: list[Requirement]):
    issues = []
    seen = set()
    for r in requirements:
        if r.requirement_id in seen:
            issues.append(f"duplicate:{r.requirement_id}")
        seen.add(r.requirement_id)
        if not r.text.strip():
            issues.append(f"empty:{r.requirement_id}")
    return issues
