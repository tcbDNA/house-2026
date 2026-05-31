"""Bulk-download DRA precinct data + geojson from github.com/dra2020/vtd_data.

For each state: lists files via GitHub API, picks the highest-version
Election_Data_{STATE}.v{NN}.zip and Geojson_{STATE}.v{NN}.zip, downloads,
and extracts to ~/Downloads/ matching the layout that
build_slices_from_github.py expects.

Usage:
  python data/fetch_dra_github.py                 # all 50 states
  python data/fetch_dra_github.py GA TX FL        # subset
"""
from __future__ import annotations
import re
import sys
import time
import urllib.request
import zipfile
import json
from pathlib import Path

REPO = "dra2020/vtd_data"
BRANCH = "main"
# Keep the downloads in-repo (under backend/data/dra_vtd/) so the project is
# self-contained. The raw data is several hundred MB and gitignored; the
# slices JSON produced from it is small enough to commit.
HOME = Path(__file__).resolve().parent / "dra_vtd"

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


def gh_list(state: str) -> list[dict]:
    url = f"https://api.github.com/repos/{REPO}/contents/2020_VTD/{state}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


VERSION_RE = re.compile(r"\.v(\d+)\.zip$")


def latest_file(files: list[dict], prefix: str) -> dict | None:
    candidates = [f for f in files if f["name"].startswith(prefix)
                  and VERSION_RE.search(f["name"])]
    if not candidates:
        return None
    return max(candidates, key=lambda f: int(VERSION_RE.search(f["name"]).group(1)))


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as r, dest.open("wb") as f:
        while True:
            chunk = r.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)


def extract_in_place(zip_path: Path) -> Path:
    """Extract the zip into a sibling directory named after the zip (minus .zip)."""
    extract_dir = zip_path.with_suffix("")
    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_dir)
    return extract_dir


def process_state(state: str) -> bool:
    try:
        files = gh_list(state)
    except Exception as e:
        print(f"  {state}: failed to list ({e})")
        return False

    elec = latest_file(files, f"Election_Data_{state}.v")
    gj = latest_file(files, f"Geojson_{state}.v")
    if not elec or not gj:
        print(f"  {state}: missing files (elec={'OK' if elec else 'MISS'}, gj={'OK' if gj else 'MISS'})")
        return False

    # Skip if extracted directories already present (idempotent re-runs)
    elec_extract = HOME / elec["name"].replace(".zip", "")
    gj_extract = HOME / gj["name"].replace(".zip", "")
    if elec_extract.exists() and any(elec_extract.iterdir()) and \
       gj_extract.exists() and any(gj_extract.iterdir()):
        print(f"  {state}: already extracted ({elec['name']} + {gj['name']}) — skipping")
        return True

    print(f"  {state}: downloading {elec['name']} + {gj['name']} ", end="", flush=True)
    for f in (elec, gj):
        url = f["download_url"]
        dest = HOME / f["name"]
        if not dest.exists():
            download(url, dest)
        extract_in_place(dest)
        print(".", end="", flush=True)
    print(" done")
    return True


def main(argv: list[str]) -> int:
    targets = [s.upper() for s in argv[1:]] if len(argv) > 1 else STATES
    ok = fail = 0
    for state in targets:
        if process_state(state):
            ok += 1
        else:
            fail += 1
        time.sleep(0.3)  # gentle rate-limit
    print(f"\nDone. ok={ok} fail={fail} of {len(targets)} states")
    print(f"Files extracted under {HOME}/")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
