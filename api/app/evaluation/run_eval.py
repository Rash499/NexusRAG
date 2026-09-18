import json
import asyncio
from pathlib import Path
import sys

# Allow execution with: python -m app.evaluation.run_eval
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services import retrieve

async def main():
    dataset = json.loads(
        Path("/app/data/evaluation.json").read_text(encoding="utf-8")
    )

    total = len(dataset)
    passed = 0

    for item in dataset:
        points, _ = await retrieve(item["question"], 3)
        titles = [p.payload.get("title") for p in points if p.payload]
        expected = set(item["expected_sources"])
        hit = bool(expected.intersection(titles))

        print(
            f"{'PASS' if hit else 'FAIL'} | "
            f"{item['question']} | retrieved={titles}"
        )

        if hit:
            passed += 1

    precision = passed / total if total else 0
    print(f"\nRetrieval source-hit rate: {precision:.2%}")

    # CI quality gate. Adjust after establishing a baseline.
    if precision < 0.70:
        raise SystemExit(1)

if __name__ == "__main__":
    asyncio.run(main())
