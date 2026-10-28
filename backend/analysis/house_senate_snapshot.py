"""Save, or compare, the House and Senate projection responses for a fixed set
of requests, to confirm that work elsewhere (the governors model) leaves them
byte-for-byte unchanged.

Usage (from backend/):
  python3 analysis/house_senate_snapshot.py save <file.json>
  python3 analysis/house_senate_snapshot.py compare <file.json>   # exit 1 on any difference
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402

REQUESTS = {
    "default": {},
    "environment_D+12": {"environment": 12.0},
    "environment_R+2": {"environment": -2.0},
    "hispanic_slider": {"sliders": {"hispanic": 10.0}},
    "race_edu_frame": {"frame": "race_edu"},
    "trend_off": {"trend_discount": 0.0},
    "senate_poll_blend_off": {"settings": {"senate_poll_blend": False}},
    "house_incumbency_1.7": {"settings": {"house_incumbency": 1.7}},
    "group_errors_off": {"settings": {"group_errors": False}},
}
ENDPOINTS = ("/api/project", "/api/senate/project")


def snapshot() -> dict:
    c = TestClient(main.app)
    out = {}
    for name, body in REQUESTS.items():
        for ep in ENDPOINTS:
            r = c.post(ep, json=body)
            r.raise_for_status()
            out[f"{ep} {name}"] = r.json()
    out["GET /api/senate/seats"] = c.get("/api/senate/seats").json()
    out["GET /api/districts"] = c.get("/api/districts").json()
    return out


def main_cli():
    mode, path = sys.argv[1], Path(sys.argv[2])
    snap = snapshot()
    if mode == "save":
        path.write_text(json.dumps(snap, sort_keys=True))
        print(f"saved {len(snap)} responses to {path}")
        return
    old = json.loads(path.read_text())
    diff = [k for k in sorted(set(old) | set(snap))
            if json.dumps(old.get(k), sort_keys=True) != json.dumps(snap.get(k), sort_keys=True)]
    print(f"{len(snap)} responses compared; {len(diff)} differ" + (": " + ", ".join(diff) if diff else ""))
    sys.exit(1 if diff else 0)


if __name__ == "__main__":
    main_cli()
