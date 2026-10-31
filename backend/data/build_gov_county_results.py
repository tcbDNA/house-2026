"""County results of each running incumbent governor's last governor race -> gov_county_results.csv.

For the governor county maps (main._state_counties_overlay, setting governor_county_incumbent_map):
an incumbent running again who has won a governor's race gets each county's position relative to the
state from that race instead of from the 2024 presidential map. Sixteen races (South Dakota's Rhoden has
never won a governor's race, so South Dakota keeps the presidential map):

  2022: AZ AR CT HI ID IL MD MA NE NV NY OR PA TX      2024: NH VT

Sources (sources/gov_county_results/README.md has the URLs):
  * Dave's Redistricting precinct data (data/dra_vtd/Election_Data_<ST>.v07, github.com/dra2020/vtd_data),
    E_22_GOV / E_24_GOV summed to counties by the first five digits of GEOID20: AZ HI IL NV NY TX NH VT.
  * MIT Election Data and Science Lab 2022 precinct returns (sources/gov_county_results/medsl_2022/,
    github.com/MEDSL/2022-elections-official): CT MA MD NE OR PA. Office "GOVERNOR"; every vote mode
    summed; undervote, overvote and blank rows dropped; a nominee's votes on every ballot line counted
    (Lamont's Working Families and Independent Party lines). Connecticut's towns go to its nine planning
    regions with the Census town crosswalk (sources/ct_planning_regions/).
  * Arkansas: the state's official results system by county (sources/gov_county_results/
    ar_2022_governor_by_county.json); MIT's Arkansas file has no Phillips County.
  * Idaho: the Secretary of State's official county canvass (sources/gov_results/official/
    2022_id_governor_by_county.csv); MIT's Idaho file counts many precincts twice.
Each state's county sum is checked against the official statewide result in
sources/gov_results/official_overrides.csv and printed.

Margins are total-vote, 100 x (D - R) / total, like every margin in the model.
Usage (from backend/data/): python3 build_gov_county_results.py
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent
SRC = DATA / "sources" / "gov_county_results"
OUT = DATA / "gov_county_results.csv"

RACES = {   # state -> (year, incumbent, source)
    "AZ": (2022, "Katie Hobbs", "dra"), "HI": (2022, "Josh Green", "dra"), "IL": (2022, "JB Pritzker", "dra"),
    "NV": (2022, "Joe Lombardo", "dra"), "NY": (2022, "Kathy Hochul", "dra"), "TX": (2022, "Greg Abbott", "dra"),
    "NH": (2024, "Kelly Ayotte", "dra"), "VT": (2024, "Phil Scott", "dra"),
    "AR": (2022, "Sarah Huckabee Sanders", "ar_official"), "CT": (2022, "Ned Lamont", "medsl"),
    "MA": (2022, "Maura Healey", "medsl"), "MD": (2022, "Wes Moore", "medsl"), "NE": (2022, "Jim Pillen", "medsl"),
    "OR": (2022, "Tina Kotek", "medsl"), "PA": (2022, "Josh Shapiro", "medsl"),
    "ID": (2022, "Brad Little", "id_official"),
}
DROP = {"UNDERVOTES", "UNDER VOTES", "OVERVOTES", "OVER VOTES", "BLANK", "BLANKS", "BLANK VOTES"}


def dra(st: str, year: int) -> dict[str, list[float]]:
    d = next(p for p in sorted((DATA / "dra_vtd").glob(f"Election_Data_{st}.v*")) if p.is_dir())
    f = next(d.glob("*.csv"))
    yy = str(year)[2:]
    out = defaultdict(lambda: [0.0, 0.0, 0.0])
    for r in csv.DictReader(f.open(encoding="utf-8-sig")):
        if not r["GEOID20"][:5].isdigit():
            continue
        c = out[r["GEOID20"][:5]]
        c[0] += float(r[f"E_{yy}_GOV_Dem"] or 0); c[1] += float(r[f"E_{yy}_GOV_Rep"] or 0)
        c[2] += float(r[f"E_{yy}_GOV_Total"] or 0)
    return out


def ct_regions() -> dict[str, str]:
    """Connecticut town name (upper case) -> planning region FIPS."""
    import supplement_ct_pres
    return {t.upper(): "09" + row["NEW_COUNTYFP"] for t, row in supplement_ct_pres.town_crosswalk().items()}


def medsl(st: str) -> dict[str, list[float]]:
    z = zipfile.ZipFile(SRC / "medsl_2022" / f"2022-{st.lower()}-local-precinct-general.zip")
    rows = [r for r in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", newline=""))
            if r["office"].strip().upper() == "GOVERNOR" and r["candidate"].strip().upper() not in DROP]
    by_cand = defaultdict(float)
    for r in rows:
        by_cand[(r["candidate"], r["party_simplified"])] += float(r["votes"] or 0)
    dem = max((k for k in by_cand if k[1] == "DEMOCRAT"), key=by_cand.get)[0]
    rep = max((k for k in by_cand if k[1] == "REPUBLICAN"), key=by_cand.get)[0]
    regions = ct_regions() if st == "CT" else None
    out = defaultdict(lambda: [0.0, 0.0, 0.0])
    for r in rows:
        if regions is not None:
            key = regions[r["jurisdiction_name"].strip().upper()]
        else:
            key = r["county_fips"].zfill(5)
        v = float(r["votes"] or 0)
        c = out[key]
        c[0] += v if r["candidate"] == dem else 0.0
        c[1] += v if r["candidate"] == rep else 0.0
        c[2] += v
    return out


def ar_official() -> dict[str, list[float]]:
    d = json.loads((SRC / "ar_2022_governor_by_county.json").read_text())["response"]
    out = {}
    for fips, loc in d["locations"].items():
        v = {c["choiceID"]: float(c["totalVotes"]) for c in loc["choices"]}
        out[fips] = [v["528"], v["530"], float(loc["totalVotes"])]   # 528 Chris Jones (D), 530 Sarah Huckabee Sanders (R)
    return out


def id_official(fips_by_name: dict[str, str]) -> dict[str, list[float]]:
    rows = list(csv.reader((DATA / "sources" / "gov_results" / "official" / "2022_id_governor_by_county.csv").open()))
    hdr = rows[0]
    di = next(i for i, h in enumerate(hdr) if "Democratic" in h); ri = next(i for i, h in enumerate(hdr) if "Republican" in h)
    ti = hdr.index("Total Votes Cast")
    num = lambda s: float(s.replace(",", "") or 0)
    out = {}
    for r in rows[1:]:
        if not r or r[0] in ("Totals", ""):
            continue
        out[fips_by_name[r[0].strip().upper()]] = [num(r[di]), num(r[ri]), num(r[ti])]
    return out


def main() -> None:
    counties = json.loads((DATA / "counties.json").read_text())["counties"]
    names = {c["fips"]: c["name"] for c in counties}
    official = {(r["year"], r["state"]): r for r in csv.DictReader((DATA / "sources" / "gov_results" / "official_overrides.csv").open())}
    # The race's largest third candidate (gov_results.csv, the table behind the governor WAR records), so
    # the overlay can skip races a third candidate distorted, as the WAR records do (over 5%).
    third = {(r["year"], r["state"]): (r["other_candidate"], float(r["other_pct"] or 0))
             for r in csv.DictReader((DATA / "sources" / "gov_results" / "gov_results.csv").open()) if r["special"] == "no"}
    out_rows = []
    for st, (year, inc, src) in sorted(RACES.items()):
        model_fips = {c["fips"] for c in counties if c["state"] == st}
        if src == "dra":
            res = dra(st, year)
        elif src == "medsl":
            res = medsl(st)
        elif src == "ar_official":
            res = ar_official()
        else:
            res = id_official({c["name"].upper().replace(" COUNTY", ""): c["fips"] for c in counties if c["state"] == st})
        extra = sorted(set(res) - model_fips)
        if extra == ["15005"] and st == "HI":      # Kalawao: no presidential row of its own, part of Maui's
            for i in range(3):
                res["15009"][i] += res["15005"][i]
            del res["15005"]
            extra = []
        assert not extra and set(res) == model_fips, (st, extra, sorted(model_fips - set(res)))
        d, r, t = (sum(v[i] for v in res.values()) for i in range(3))
        o = official[(str(year), st)]
        od, orr, ot = float(o["d_votes"]), float(o["r_votes"]), float(o["total_votes"])
        tc, tp = third.get((str(year), st), ("", 0.0))
        print(f"{st} {year} {inc:24s} {src:12s} third {tc[:14]:14s} {tp:5.2f}  counties {len(res):3d}  D {d:10,.0f} ({d - od:+7,.0f})  R {r:10,.0f} "
              f"({r - orr:+7,.0f})  total {t:10,.0f} ({t - ot:+7,.0f})  margin {100 * (d - r) / t:+6.2f} "
              f"(official {100 * (od - orr) / ot:+6.2f})")
        for fips in sorted(res):
            dv, rv, tv = res[fips]
            tc, tp = third.get((str(year), st), ("", 0.0))
            out_rows.append({"state": st, "year": year, "incumbent": inc, "fips": fips, "county": names[fips],
                             "dem": round(dv), "rep": round(rv), "total": round(tv),
                             "margin": round(100 * (dv - rv) / tv, 2) if tv else "", "source": src,
                             "third_candidate": tc, "third_candidate_pct": tp})
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(out_rows)
    print(f"wrote {OUT.name}: {len(out_rows)} counties in {len(RACES)} states")


if __name__ == "__main__":
    main()
