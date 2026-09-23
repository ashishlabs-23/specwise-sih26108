import argparse
import json
from datetime import date
from app.engine import RecommendationEngine
from app.models import AnalysisRequest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--date", default=None)
    p.add_argument("--report", default=None)
    args = p.parse_args()

    request = AnalysisRequest(
        text=args.query,
        tender_date=date.fromisoformat(args.date) if args.date else None
    )
    result = RecommendationEngine().analyze(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(result.report_html or "")
        print(f"Report saved to {args.report}")

if __name__ == "__main__":
    main()
