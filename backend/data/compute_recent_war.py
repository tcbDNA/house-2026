"""Compute most-recent-cycle WAR per candidate from raw_war.csv,
mirroring v18's conventions:

  d_war = -Sortable_most_recent (D-positive: +X means D overperforms)
  r_war = +Sortable_most_recent (R-positive: +X means R overperforms)

Writes recent_war.csv keyed by candidate name with party and year.
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
RAW = DATA_DIR / "raw_war.csv"
OUT = DATA_DIR / "recent_war.csv"


def main():
    if not RAW.exists():
        sys.exit(f"missing {RAW}")

    by_candidate: dict[tuple[str, str], dict] = {}  # (name, party) -> most-recent record

    with RAW.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("Chamber") != "House":
                continue
            try:
                year = int(r["Year"])
                sortable = float(r["Sortable"])
            except (ValueError, KeyError, TypeError):
                continue

            for party_letter, name_field in (("D", "Democrat"), ("R", "Republican")):
                name = (r.get(name_field) or "").strip()
                if not name:
                    continue
                key = (name, party_letter)
                cur = by_candidate.get(key)
                if cur is None or year > cur["year"]:
                    by_candidate[key] = {
                        "year": year,
                        "geography": r.get("Geography", ""),
                        "sortable": sortable,
                        "war_text": r.get("WAR", ""),
                    }

    rows = []
    for (name, party), v in by_candidate.items():
        if party == "D":
            war_signed = -v["sortable"]   # D-positive
        else:
            war_signed = +v["sortable"]   # R-positive
        rows.append({
            "name": name,
            "party": party,
            "year": v["year"],
            "geography": v["geography"],
            "war": round(war_signed, 2),
            "war_text": v["war_text"],
        })

    rows.sort(key=lambda r: (r["name"], r["party"]))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "party", "year", "geography", "war", "war_text"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT} with {len(rows)} candidate-party rows", file=sys.stderr)


if __name__ == "__main__":
    main()
