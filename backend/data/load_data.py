"""Merge v18 sensitivity + demographics.csv into a single districts.json
keyed by district ID. Run after fetch_acs.py and build_demographics.py."""

import csv
import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
V18_CSV = DATA_DIR.parent.parent / "national_sensitivity_v20.csv"
DEMOS_CSV = DATA_DIR / "demographics.csv"
OUT_JSON = DATA_DIR / "districts.json"

NUMERIC_V18 = {
    "harris_2024", "trump_2024", "margin_2024",
    "biden_2020", "trump_2020", "margin_2020",
    "state_margin_2020", "state_margin_2024",
    "rel_2020", "rel_2024", "rel_trend",
    "abs_shift", "state_shift",
    "d_war", "d_n", "r_war", "r_n",
    "war", "war_n", "war_adj", "war_adj_discounted",
    "proj", "proj_d2", "proj_d4", "proj_d6", "proj_d8", "proj_d10", "proj_d12",
    "proj_d2_war", "proj_d4_war", "proj_d6_war", "proj_d8_war",
    "proj_d10_war", "proj_d12_war",
    "proj_d2_final", "proj_d4_final", "proj_d6_final", "proj_d8_final",
    "proj_d10_final", "proj_d12_final",
    "proj_d3_final", "proj_d5_final", "proj_d7_final", "proj_d9_final", "proj_d11_final",
}
NUMERIC_DEMOS = {
    "pct_white_nh", "pct_black", "pct_hispanic", "pct_asian", "pct_other",
    "pct_college",
    "pct_white_nh_college", "pct_white_nh_non_college",
    "pct_nonwhite_college", "pct_nonwhite_non_college",
    "pct_under_30", "pct_30_44", "pct_45_64", "pct_65_plus",
    "median_age", "median_income", "total_population",
}


def to_num(s):
    if s is None or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return s  # leave non-numeric strings alone


def parse_incumbent(field: str) -> str | None:
    """Return the bare candidate name from v18's incumbent column, or None
    for open seats. Examples:
      'Claudia Tenney'                 -> 'Claudia Tenney'
      'Henry Cuellar'                  -> 'Henry Cuellar'
      '(open, Evans retiring)'         -> None
      '(open, Donalds→gov)'             -> None
    """
    if not field:
        return None
    s = field.strip()
    if s.startswith("(") or s.lower().startswith("open"):
        return None
    # Trim trailing parenthetical notes "Henry Cuellar (something)"
    s = re.sub(r"\s*\(.*?\)\s*$", "", s).strip()
    return s or None


# Known v18 -> raw_war name aliases (raw data typos / suffix differences)
NAME_ALIASES = {
    "August Pfluger": "August Pfluer",        # raw data typo
    "Rob Menendez": "Rob Menendez Jr.",       # raw uses Jr. suffix
    "Derek Merrin": "Derrick Merrin",         # raw data spells "Derrick"
}

# Manual WAR overrides for cases where the recent-cycle number is distorted
# by a specific opponent or context that won't repeat in 2026. Value is the
# WAR in this candidate's party-perspective (positive = overperform their
# party's baseline). Set to 0.0 to neutralize.
WAR_OVERRIDES = {
    # (district, name) -> war (party-perspective signed value). Applied to BOTH
    # incumbents (via apply_recent_war) AND named challengers (via
    # apply_house_challenger). Each entry must have a documented reason.
    ("AK-AL", "Nick Begich"): 0.0,   # 2024 race vs. Mary Peltola distorts the WAR
    # Ojeda's only race is 2018 WV-03 — out-of-window under any reasonable
    # blend (the auto-match already rejects it on state mismatch), single
    # data point, and the WV-2018 context (coalfield-D pitch, teacher strike,
    # biographical appeal) doesn't transfer to NC-09 2026. Explicit zero
    # documents the model's already-implicit conclusion.
    ("NC-09", "Richard Ojeda"): 0.0,
}

# Incumbent column overrides for cases v20 missed.
# Keyed by district -> {"incumbent": str, "party": "(D)" | "(R)"} (party optional).
INCUMBENT_OVERRIDES = {
    # UT-court redraw: Moore moved from old UT-01 to new UT-02 (same geography).
    # New UT-01 is the post-court SLC-leaning seat with no R incumbent.
    "UT-01": {"incumbent": "(open, post-court redraw)"},
    "UT-02": {"incumbent": "Blake Moore", "party": "(R)"},
    # Crenshaw lost 2026 R primary; Steve Toth is the R nominee.
    # is_incumbent=False suppresses incumbency_adj and WAR (Toth isn't sitting).
    "TX-02": {"incumbent": "Steve Toth", "party": "(R)", "is_incumbent": False},
    # Cohen announced retirement after the TN-2nd-Extraordinary redraw cracked
    # Memphis; the new TN-09 is R-leaning and Cohen is not running.
    "TN-09": {"incumbent": "(open, Cohen retiring)"},
    # NE-02 open (Bacon retiring); Brinker Harding is the R nominee.
    # No federal WAR; is_incumbent=False keeps incumbency_adj at 0.
    "NE-02": {"incumbent": "Brinker Harding", "party": "(R)", "is_incumbent": False},
    # CA-40 under Prop50 lines merged Calvert (old CA-41) and Kim (old CA-40)
    # into a single R-leaning seat — both sitting reps are in the primary.
    "CA-40": {"incumbent": "(open, R primary: Calvert vs Kim)", "party": "(R)"},
    # TX-18: Menefee (sitting since 2025 special after Jackson Lee) defeated
    # Al Green (moved from TX-09 post-redraw) in the May 26 runoff.
    "TX-18": {"incumbent": "Christian Menefee", "party": "(D)"},
    # TX-19: open (Arrington retiring). Sell won R runoff over Enriquez.
    "TX-19": {"incumbent": "Tom Sell", "party": "(R)", "is_incumbent": False},
    # TX-33: incumbent Julie Johnson (moved from TX-32 post-SB4) lost D primary
    # runoff to Colin Allred. Allred is not currently a sitting member.
    "TX-33": {"incumbent": "Colin Allred", "party": "(D)", "is_incumbent": False},
    # TX-35: open (Casar→TX-37). Garcia won D runoff over Galindo.
    "TX-35": {"incumbent": "Johnny Garcia", "party": "(D)", "is_incumbent": False},
    # TX-38: open (Hunt→Senate). Bonck won R runoff over deZevallos.
    "TX-38": {"incumbent": "Jon Bonck", "party": "(R)", "is_incumbent": False},
    # TX-08: open (Luttrell retiring). Steinmann won R primary outright in March.
    "TX-08": {"incumbent": "Jessica Steinmann", "party": "(R)", "is_incumbent": False},
    # TX-09: SB4 redrew this from a D coalition district into an R-leaning seat
    # (Trump won the new lines by ~12pts). Green moved to TX-18. Mealer won R runoff.
    "TX-09": {"incumbent": "Alex Mealer", "party": "(R)", "is_incumbent": False},
    # TX-10: open (McCaul retiring). Gober won R primary outright in March.
    "TX-10": {"incumbent": "Chris Gober", "party": "(R)", "is_incumbent": False},
    # TX-21: open (Roy→AG). Teixeira (Mark, former MLB) won R primary.
    "TX-21": {"incumbent": "Mark Teixeira", "party": "(R)", "is_incumbent": False},
    # TX-22: open (Nehls retiring). Trever Nehls (twin brother) won R primary.
    "TX-22": {"incumbent": "Trever Nehls", "party": "(R)", "is_incumbent": False},
    # TX-30: open (Crockett→Senate). Haynes won D primary outright in March.
    "TX-30": {"incumbent": "Frederick Douglas Haynes III", "party": "(D)", "is_incumbent": False},
    # TX-32: SB4 redrew this from Johnson's D seat into an R-leaning seat
    # (Johnson moved to TX-33). Yarbrough is R nominee (Binkley withdrew from runoff).
    "TX-32": {"incumbent": "Jace Yarbrough", "party": "(R)", "is_incumbent": False},
    # FL-24: Frederica Wilson retiring; D nominee not yet selected. Safe D Miami seat.
    "FL-24": {"incumbent": "(open, Wilson retiring)", "party": "(D)"},
    # === 2026-05-19 primaries ===
    # KY-04: Massie lost R primary to Trump-endorsed Ed Gallrein. No federal WAR for Gallrein;
    # is_incumbent=False zeros incumbency_adj.
    "KY-04": {"incumbent": "Ed Gallrein", "party": "(R)", "is_incumbent": False},
    # GA-01: open (Carter→Senate). Jim Kingston won R primary; D side in runoff.
    "GA-01": {"incumbent": "Jim Kingston", "party": "(R)", "is_incumbent": False},
    # GA-10: open (Collins→Senate). Houston Gaines won R primary.
    "GA-10": {"incumbent": "Houston Gaines", "party": "(R)", "is_incumbent": False},
    # GA-11: open (Loudermilk retiring). Both R and D primaries headed to June 16 runoff.
    "GA-11": {"incumbent": "(open, Loudermilk retiring)", "party": "(R)"},
    # GA-13: open (David Scott died April 2026). Jasmine Clark won D primary;
    # Chavez unopposed R. Heavily D seat.
    "GA-13": {"incumbent": "Jasmine Clark", "party": "(D)", "is_incumbent": False},
    # GA-14: MTG resigned Jan 2026; Clay Fuller won April 7 special by 12pts.
    # is_incumbent=False: only ~6 weeks in office, no full structural incumbency advantage.
    "GA-14": {"incumbent": "Clay Fuller", "party": "(R)", "is_incumbent": False},
    # PA-03: open (Evans retired). Rabb (D) won contested D primary;
    # R primary had only a write-in (William Small) — deep blue Philadelphia seat.
    "PA-03": {"incumbent": "Chris Rabb", "party": "(D)", "is_incumbent": False},
    # TX-23: open after Gonzales dropped out. Herrera (R) is the nominee;
    # is_incumbent=False (no federal record).
    "TX-23": {"incumbent": "Brandon Herrera", "party": "(R)", "is_incumbent": False},
}

# Known House challengers (primaries finished / well-established candidates).
# Model auto-looks-up most-recent WAR from raw_war.csv with state
# disambiguation. The "war" field is a manual fallback only.
#
# To add: HOUSE_CHALLENGERS["XX-NN"] = {
#     "name": "Full Name", "party": "(D)" | "(R)" | "(I)",
#     "war": <manual estimate, in their party-perspective>,
#     "note": "...",
# }
HOUSE_CHALLENGERS: dict[str, dict] = {
    # === North Carolina (primaries 2026-03-03, all decided) ===
    "NC-01": {"name": "Laurie Buckhout", "party": "(R)", "war": 0.0, "note": "ran 2024 NC-01 — auto-WAR"},
    "NC-02": {"name": "Gene Douglass", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NC-03": {"name": "Raymond Smith Jr.", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-04": {"name": "Max Ganorkar", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NC-05": {"name": "Chuck Hubbard", "party": "(D)", "war": 0.0, "note": "ran 2024 NC-05 — auto-WAR"},
    "NC-06": {"name": "Cyril Jefferson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-07": {"name": "Kim Hardy", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-08": {"name": "Colby Watson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-09": {"name": "Richard Ojeda", "party": "(D)", "war": 0.0, "note": "2026 D nominee (former WV state senator)"},
    "NC-10": {"name": "Ashley Bell", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-11": {"name": "Jamie Ager", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-12": {"name": "Jack Codiga", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NC-13": {"name": "Paul Barringer", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NC-14": {"name": "Lakesha Womack", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # === Alabama ===
    "AL-03": {"name": "Lee McInnis", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Arkansas ===
    "AR-01": {"name": "Terri Yarbrough Green", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "AR-02": {"name": "Chris Jones", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "AR-03": {"name": "Robb Ryerse", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "AR-04": {"name": "James Russell", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Georgia (primaries 2026-05-19) ===
    "GA-02": {"name": "Matt Day", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "GA-03": {"name": "Maura Keller", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-04": {"name": "Jim Duffie", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "GA-05": {"name": "John Salvesen", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "GA-06": {"name": "Kevin Martin", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "GA-08": {"name": "Kelly Esti", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-09": {"name": "Caitlyn Gegen", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-10": {"name": "Pamela Delancy", "party": "(D)", "war": 0.0, "note": "2026 D nominee (open seat — Collins→Senate)"},
    "GA-13": {"name": "Jonathan Chavez", "party": "(R)", "war": 0.0, "note": "2026 R nominee (unopposed); open seat after Scott's death"},
    "GA-14": {"name": "Shawn Harris", "party": "(D)", "war": 0.0, "note": "2026 D nominee; also lost April special to Fuller 44-56"},
    # === Kentucky (primaries 2026-05-19) ===
    "KY-04": {"name": "Melissa Strange", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Gallrein in post-Massie open seat)"},
    # === Pennsylvania (primaries 2026-05-19) ===
    "PA-01": {"name": "Bob Harvie", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Fitzpatrick); Bucks Co commissioner"},
    "PA-02": {"name": "Jessica Arriaga", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Boyle)"},
    "PA-04": {"name": "Aurora Stuski", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Dean)"},
    "PA-05": {"name": "Nick Manganaro", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Scanlon)"},
    "PA-06": {"name": "Marty Young", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Houlahan)"},
    "PA-07": {"name": "Bob Brooks", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Mackenzie); former firefighter / union president"},
    "PA-08": {"name": "Paige Cognetti", "party": "(D)", "war": 0.0, "note": "2026 D nominee unopposed (challenger to Bresnahan); Scranton mayor"},
    "PA-09": {"name": "Rachel Wallace", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Meuser)"},
    "PA-10": {"name": "Janelle Stelson", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Perry); ran 2024 PA-10 — auto-WAR"},
    "PA-11": {"name": "Nancy Mannion", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Smucker)"},
    "PA-12": {"name": "James Hayes", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Summer Lee)"},
    "PA-13": {"name": "Beth Farnham", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Joyce); 2022/2024 candidate"},
    "PA-14": {"name": "Alan Bradstock", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Reschenthaler)"},
    "PA-15": {"name": "Ray Bilger", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to GT Thompson)"},
    "PA-16": {"name": "Justin Wagner", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Mike Kelly)"},
    "PA-17": {"name": "Tony Guy", "party": "(R)", "war": 0.0, "note": "2026 R nominee (Beaver Co Sheriff; challenger to Deluzio)"},
    # === Illinois ===
    "IL-01": {"name": "Christian Maxwell", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-02": {"name": "Michael Noack", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-03": {"name": "Angel Oakley", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-04": {"name": "Lupe Castillo", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-05": {"name": "Tommy Hanson", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-06": {"name": "Niki Conforti", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-07": {"name": "Chad Koppie", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-08": {"name": "Jennifer Davis", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-09": {"name": "John Elleson", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-10": {"name": "Carl Lambrecht", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-11": {"name": "Jeff Walter", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-12": {"name": "Julie Fortier", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-13": {"name": "Jeff Wilson", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-14": {"name": "James Marter", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-15": {"name": "Jennifer Todd", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-16": {"name": "Paul Nolley", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IL-17": {"name": "Dillan Vancil", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Indiana ===
    "IN-01": {"name": "Barb Regnitz", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-02": {"name": "Jamee Decio", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-03": {"name": "Kelly Thompson", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-04": {"name": "Drew Cox", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-05": {"name": "J. D. Ford", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-06": {"name": "Cynthia Wirth", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-07": {"name": "Patrick McAuley", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-08": {"name": "Mary Allen", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "IN-09": {"name": "Brad Meyer", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Kentucky ===
    "KY-01": {"name": "Drew Williams", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "KY-05": {"name": "Ned Pillersdorf", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Maryland ===
    "MD-04": {"name": "George McDermott", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "MD-07": {"name": "Scott Collier", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Mississippi ===
    "MS-01": {"name": "Cliff Johnson", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "MS-02": {"name": "Ron Eller", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "MS-03": {"name": "Michael Chiaradio", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "MS-04": {"name": "Jeffrey Hulum III", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Nebraska ===
    "NE-01": {"name": "Chris Backemeyer", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "NE-02": {"name": "Denise Powell", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "NE-03": {"name": "Becky Stille", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === New Mexico ===
    "NM-01": {"name": "Didi Okpareke", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "NM-03": {"name": "Martin Zamora", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Ohio ===
    "OH-01": {"name": "Eric Conroy", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-02": {"name": "Jennifer Mazzuckelli", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-03": {"name": "Cleophus Dulaney", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-04": {"name": "Joshua Kolasinski", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-05": {"name": "Brian Shaver", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-06": {"name": "Elizabeth Kirtley", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-07": {"name": "Brian Poindexter", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-08": {"name": "Vanessa Enoch", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-09": {"name": "Derek Merrin", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-10": {"name": "Kristina Knickerbocker", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-11": {"name": "Mike Kirchner", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-12": {"name": "Jerrad Christian", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-13": {"name": "Carey Coleman", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-14": {"name": "Maria Jukic", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OH-15": {"name": "Don Leonard", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Oregon ===
    "OR-01": {"name": "Barbara J. Kahl", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Bonamici)"},
    "OR-02": {"name": "Chris Beck", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Bentz); former OR state rep"},
    "OR-03": {"name": "Loran Ayles", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "OR-04": {"name": "Monique DeSpain", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Hoyle); also 2024 R nominee — auto-WAR"},
    "OR-05": {"name": "Patti Adair", "party": "(R)", "war": 0.0, "note": "2026 R nominee (Deschutes Co commissioner; challenger to Bynum)"},
    "OR-06": {"name": "David Russ", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Texas ===
    "TX-01": {"name": "Yolanda Prince", "party": "(D)", "war": 0.0, "note": "2026 D runoff winner (def. Alexander 72-28)"},
    "TX-02": {"name": "Shaun Finnie", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-03": {"name": "Evan Hunt", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-04": {"name": "Jason Pearce", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-05": {"name": "Chelsey Hockett", "party": "(D)", "war": 0.0, "note": "2026 D runoff winner (def. Torres 53-47)"},
    "TX-06": {"name": "Danny Minton", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-07": {"name": "Alexander Hale", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Cohen 64-36); challenger to Fletcher"},
    "TX-08": {"name": "Laura Jones", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-10": {"name": "Caitlin Rourk", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-11": {"name": "Claire Reynolds", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-12": {"name": "Angela Rodriguez Prilliman", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-13": {"name": "Mark Nair", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-14": {"name": "Thurman Bartie", "party": "(D)", "war": 0.0, "note": "2026 D runoff winner (def. Davis 51-49); challenger to Weber"},
    "TX-15": {"name": "Bobby Pulido", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-16": {"name": "Adam Bauman", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Barraza 69-31); challenger to Escobar"},
    "TX-17": {"name": "Casey Shepard", "party": "(D)", "war": 0.0, "note": "2026 D runoff winner (def. Flores 60-40); challenger to Sessions"},
    "TX-18": {"name": "Ronald Whitfield", "party": "(R)", "war": 0.0, "note": "2026 R nominee (challenger to Menefee)"},
    "TX-19": {"name": "Kyle Rable", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Sell in open Arrington seat)"},
    "TX-20": {"name": "Edgardo Baez", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-21": {"name": "Kristin Hook", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-22": {"name": "Marquette Greene-Scott", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-23": {"name": "Katy Padilla Stout", "party": "(D)", "war": 0.0, "note": "2026 D nominee (>50% in initial primary, no runoff)"},
    "TX-24": {"name": "Kevin Burge", "party": "(D)", "war": 0.0, "note": "2026 D runoff winner (def. Ware 78-22); challenger to Van Duyne"},
    "TX-25": {"name": "Dione Sims", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Williams)"},
    "TX-26": {"name": "Steven Shook", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-27": {"name": "Tanya Lloyd", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-28": {"name": "Tano Tijerina", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-29": {"name": "Martha Fierro", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-30": {"name": "Everett Jackson", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Daniels 57-43); challenger to open D seat (Crockett→Senate)"},
    "TX-31": {"name": "Justin Early", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-32": {"name": "Dan Barrios", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Yarbrough in SB4-redrawn R-leaning TX-32)"},
    "TX-33": {"name": "Patrick Gillespie", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Sims 57-43); challenger to Allred"},
    "TX-34": {"name": "Eric Flores", "party": "(R)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-35": {"name": "Carlos De La Cruz", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Lujan 58-42); challenger to Garcia in open D seat"},
    "TX-36": {"name": "Rhonda Hart", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "TX-37": {"name": "Lauren Peña", "party": "(R)", "war": 0.0, "note": "2026 R runoff winner (def. Gary 58-42); challenger to Casar"},
    "TX-38": {"name": "Melissa McDonough", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Bonck in open Hunt seat)"},
    # === West Virginia ===
    "WV-01": {"name": "Vince George", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    "WV-02": {"name": "Ace Parsi", "party": "(D)", "war": 0.0, "note": "2026 nominee per Wikipedia"},
    # === Manual additions (primary not yet held / not yet on Wikipedia infobox) ===
    "ME-02": {"name": "Paul LePage", "party": "(R)", "war": 0.0,
              "note": "former Maine governor; no federal-race WAR available"},
    # 2024 rematches the user is near-certain about (primary results pending) —
    # all five have prior House WAR records that will auto-match.
    "WI-03": {"name": "Rebecca Cooke", "party": "(D)", "war": 0.0,
              "note": "2024 rematch vs Van Orden — auto-WAR from 2024 WI-03"},
    "AZ-02": {"name": "Jonathan Nez", "party": "(D)", "war": 0.0,
              "note": "2024 rematch vs Crane — auto-WAR from 2024 AZ-02"},
    "IA-01": {"name": "Christina Bohannan", "party": "(D)", "war": 0.0,
              "note": "2024 rematch vs Miller-Meeks — auto-WAR from 2024 IA-01"},
    "VA-02": {"name": "Elaine Luria", "party": "(D)", "war": 0.0,
              "note": "former VA-02 rep (2019-23), comeback vs Kiggans — auto-WAR from prior runs"},
    "PA-10": {"name": "Janelle Stelson", "party": "(D)", "war": 0.0,
              "note": "2024 rematch vs Perry — auto-WAR from 2024 PA-10"},
    "IA-03": {"name": "Sarah Trone Garriott", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (IA state senator); no federal WAR record"},
}

# Generic incumbency advantage in D-R margin points. Split-Ticket's 2020
# WAR analysis pegs this at 1.7 points
# (https://split-ticket.org/2022/01/12/2020-house-wins-above-replacement-quantifying-the-impacts-of-incumbency-and-spending/).
# Added to base_margin in the incumbent's direction; open seats get zero.
INCUMBENCY_ADV = 1.7


def _strip_suffix(s: str) -> str:
    return re.sub(r"\b(jr|sr|ii|iii|iv)\.?\b", "", s, flags=re.IGNORECASE).strip()


def _last_name(name: str) -> str:
    parts = _strip_suffix(name).split()
    return parts[-1].lower() if parts else ""


RAW_WAR_CSV = DATA_DIR / "raw_war.csv"

# Time-weighting for multi-cycle WAR blend. Per the WAR creator's guidance:
# blend the last three cycles 0.50 / 0.30 / 0.20; zero-fill missing cycles to
# regress toward the mean (so a 1-cycle candidate is heavily mean-reverted).
# Recency weights for the WAR blend. Per-record windowing: each candidate's
# records are sorted by year (most recent first), and the top 3 slot into
# 0.50 / 0.30 / 0.20 — a record's weight depends on its rank among the
# candidate's records of its own office, not the calendar year. This keeps
# recent races from being discarded when the candidate moves between offices.
WAR_WEIGHTS = (0.50, 0.30, 0.20)

# Sample-size shrinkage. Candidates with fewer than 3 surviving records have
# their blended WAR shrunk toward zero by n/(n+k) / (3/(3+k)), normalized so
# 3-cycle candidates are unaffected.
WAR_SHRINK_K = 1.0


def _shrinkage(n: int) -> float:
    """Normalized sample-size factor. n=0→0; n=3→1.0; smaller n → smaller factor."""
    if n <= 0:
        return 0.0
    return (n / (n + WAR_SHRINK_K)) / (3 / (3 + WAR_SHRINK_K))


def time_weighted_war(records: list[dict]) -> float:
    """Per-record positional blend. `records` is the candidate's House cycle
    history, sorted year-desc; top 3 slot at 0.50 / 0.30 / 0.20 by recency
    rank. Sample-size shrinkage applies (3-cycle candidates unaffected;
    n=1 shrinks to 0.667× of blend; missing slots contribute 0)."""
    s = 0.0
    n = 0
    for i, w in enumerate(WAR_WEIGHTS):
        if i < len(records):
            s += w * records[i]["war"]
            n += 1
    return s * _shrinkage(min(n, 3))


def load_recent_war() -> tuple[dict, dict]:
    """Returns two indexes built from raw_war.csv (House only):
      - primary:   (name, party) -> list of records, year desc
      - fallback:  (last_name, party, state) -> list of records, year desc
    Each record carries year, geography, and `war` in the candidate's
    party-perspective (D-positive for D, R-positive for R).
    """
    primary: dict[tuple[str, str], list[dict]] = {}
    by_last_party_state: dict[tuple[str, str, str], list[dict]] = {}
    if not RAW_WAR_CSV.exists():
        return primary, by_last_party_state
    with RAW_WAR_CSV.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("Chamber") != "House":
                continue
            try:
                year = int(r["Year"])
                sortable = float(r["Sortable"])
            except (ValueError, KeyError, TypeError):
                continue
            # No year-based filter: the term-length calendar window in
            # time_weighted_war naturally excludes pre-2020 House cycles.
            geo = (r.get("Geography") or "").strip()
            state = geo.split("-")[0] if "-" in geo else geo
            for party_letter, name_field in (("D", "Democrat"), ("R", "Republican")):
                name = (r.get(name_field) or "").strip()
                if not name:
                    continue
                war_signed = -sortable if party_letter == "D" else +sortable
                rec = {"name": name, "war": war_signed, "year": year, "geography": geo}
                primary.setdefault((name, party_letter), []).append(rec)
                by_last_party_state.setdefault(
                    (_last_name(name), party_letter, state), []
                ).append(rec)
    # Sort each list by year desc so callers can take the top-3 directly.
    for lst in primary.values():
        lst.sort(key=lambda r: r["year"], reverse=True)
    for lst in by_last_party_state.values():
        lst.sort(key=lambda r: r["year"], reverse=True)
    return primary, by_last_party_state


def apply_recent_war(row: dict, primary: dict, fallback: dict) -> dict:
    """Override war / war_adj / war_adj_discounted in `row` using the most
    recent cycle WAR for the incumbent.

    Convention (mirrors v18):
      D incumbent  -> war is D-positive; war_adj = +war
      R incumbent  -> war is R-positive; war_adj = -war
      Open seat    -> all zero
      Discount     -> half if lines != '2024'
    """
    party = (row.get("party") or "").strip()
    is_d = party == "(D)"
    is_r = party == "(R)"

    name = parse_incumbent(row.get("incumbent", ""))
    new_war = 0.0
    new_year = None
    matched = False
    match_type = None

    # Manual override takes precedence
    override = WAR_OVERRIDES.get((row.get("district"), name)) if name else None
    if override is not None and (is_d or is_r):
        new_war = override
        matched = True
        match_type = "manual_override"

    if not matched and name and (is_d or is_r):
        party_letter = "D" if is_d else "R"
        # Try alias first. `primary` is now (name, party) -> list of records desc-sorted.
        alias_name = NAME_ALIASES.get(name, name)
        recs = primary.get((alias_name, party_letter))
        if recs is None and alias_name != name:
            recs = primary.get((name, party_letter))
        if recs:
            match_type = "exact" if recs[0]["name"] == name else "alias"
        else:
            # Fallback: last_name + party + state, BUT require the first name's
            # first letter to match — avoids false matches between same-surname
            # relatives (e.g. Adelita Grijalva vs Raul Grijalva). Pick the
            # most-recent matching record's *exact name*, then pull its full
            # history under that key (handles spelling variants between cycles).
            state = (row.get("state") or row.get("district", "").split("-")[0]).upper()
            candidates = fallback.get((_last_name(name), party_letter, state), [])
            v18_first_initial = (_strip_suffix(name).split() or [""])[0][:1].lower()
            ok = [c for c in candidates
                  if (_strip_suffix(c["name"]).split() or [""])[0][:1].lower() == v18_first_initial]
            if ok:
                # `ok` is year-desc; group by exact name and take the most-recent name's history.
                exact_name = ok[0]["name"]
                recs = [c for c in ok if c["name"] == exact_name]
                match_type = f"last+state ({exact_name})"
        if recs:
            new_war = round(time_weighted_war(recs), 3)
            new_year = recs[0]["year"]
            matched = True

    war_adj = new_war if is_d else -new_war if is_r else 0.0
    discount = 0.5 if (row.get("lines") and row["lines"] != "2024") else 1.0
    war_adj_discounted = round(war_adj * discount, 3)

    row["war"] = round(new_war, 3)
    row["war_n"] = 1 if matched else 0
    row["war_adj"] = round(war_adj, 3)
    row["war_adj_discounted"] = war_adj_discounted
    row["war_year"] = new_year
    row["war_matched"] = matched
    row["war_match_type"] = match_type

    # Generic incumbency advantage: +2 D-favorable if D incumbent,
    # -2 if R, 0 for open seats.
    if name is None or not (is_d or is_r):
        row["incumbency_adj"] = 0.0
    elif is_d:
        row["incumbency_adj"] = INCUMBENCY_ADV
    else:
        row["incumbency_adj"] = -INCUMBENCY_ADV
    return row


def apply_house_challenger(row: dict, primary: dict, fallback: dict) -> dict:
    """Add challenger_adj for a known House challenger, mirroring Senate logic.
    Looks up most-recent WAR via primary_war (name, party) with state
    fallback. Manual estimate in HOUSE_CHALLENGERS is used when no data match."""
    district = row.get("district", "")
    state = district.split("-")[0] if "-" in district else ""
    ch = HOUSE_CHALLENGERS.get(district)
    if ch is None:
        row["challenger"] = None
        row["challenger_party"] = None
        row["challenger_war"] = None
        row["challenger_war_year"] = None
        row["challenger_war_source"] = None
        row["challenger_adj"] = 0.0
        return row

    party = ch.get("party", "")
    # Independents are treated as D-aligned for the WAR-sign convention
    party_letter = "R" if party == "(R)" else "D"

    name = ch["name"]
    # Manual override short-circuits all lookup logic (e.g. Ojeda NC-09 → 0).
    if (district, name) in WAR_OVERRIDES:
        war_signed = float(WAR_OVERRIDES[(district, name)])
        challenger_adj = +war_signed if party != "(R)" else -war_signed
        row["challenger"] = name
        row["challenger_party"] = party
        row["challenger_war"] = round(abs(war_signed), 2)
        row["challenger_war_year"] = None
        row["challenger_war_source"] = "manual_override"
        row["challenger_adj"] = round(challenger_adj, 2)
        return row
    war_year = None
    war_source = None

    # Step 1 — try primary (name, party). Reject if most-recent state mismatch.
    # `primary` is (name, party) -> list of records year-desc.
    recs = primary.get((name, party_letter))
    if recs:
        rec_state = (recs[0].get("geography") or "").split("-")[0]
        if rec_state != state:
            recs = None

    # Step 2 — fallback by (last_name, party, state) for nickname / suffix variants
    if not recs:
        last = _last_name(name)
        first_initial = (_strip_suffix(name).split() or [""])[0][:1].lower()
        candidates = fallback.get((last, party_letter, state), [])
        ok = [c for c in candidates
              if (_strip_suffix(c["name"]).split() or [""])[0][:1].lower() == first_initial]
        if ok:
            exact_name = ok[0]["name"]
            recs = [c for c in ok if c["name"] == exact_name]

    # Step 3 — anti-double-count: any cycle the challenger ran in THIS district
    # against THIS incumbent is already captured by the incumbent's WAR blend.
    # Drop all of the challenger's cycles in this district when the incumbent
    # has a matched WAR. Capture the most-recent dropped year for the "rematch"
    # tooltip — that's the actual year of the head-to-head, which may pre-date
    # the incumbent's most-recent race against a different opponent.
    skipped_same_race = False
    rematch_year: int | None = None
    if recs and row.get("war_matched"):
        dropped = [c for c in recs if c.get("geography") == district]
        if dropped:
            rematch_year = dropped[0]["year"]  # recs are year-desc, dropped preserves order
        filtered = [c for c in recs if c.get("geography") != district]
        skipped_same_race = (len(filtered) == 0 and len(dropped) > 0)
        recs = filtered

    # Step 4 — derive the WAR value via time-weighted blend, or fall back to
    # the manual/wikipedia placeholder.
    if recs:
        war_signed = round(time_weighted_war(recs), 3)
        war_year = recs[0]["year"]
        war_source = f"{recs[0]['year']} House {recs[0]['geography']}"
    else:
        war_signed = float(ch.get("war", 0.0))
        war_year = None
        if skipped_same_race:
            # All of the challenger's cycles were filtered because they were
            # prior matchups against the current incumbent. Label with the
            # actual most-recent shared year (from the dropped records).
            war_source = f"{rematch_year} rematch" if rematch_year else "rematch"
        else:
            war_source = ch.get("source") or ("manual" if war_signed != 0.0 else "wikipedia")

    # war_signed is in the candidate's own party-perspective.
    # D-positive → directly adds to D-margin. R-positive → subtract for D-margin.
    challenger_adj = +war_signed if party != "(R)" else -war_signed

    row["challenger"] = name
    row["challenger_party"] = party
    row["challenger_war"] = round(abs(war_signed), 2)
    row["challenger_war_year"] = war_year
    row["challenger_war_source"] = war_source
    row["challenger_adj"] = round(challenger_adj, 2)
    return row


def main():
    if not DEMOS_CSV.exists():
        sys.exit(f"missing {DEMOS_CSV}. Run fetch_acs.py + build_demographics.py first.")

    primary_war, fallback_war = load_recent_war()
    print(f"loaded recent_war: primary={len(primary_war)} keys; "
          f"fallback index entries={len(fallback_war)}", file=sys.stderr)

    demos = {}
    with DEMOS_CSV.open() as f:
        for r in csv.DictReader(f):
            out = {"district": r["district"], "source": r.get("source") or "UNKNOWN"}
            for k, v in r.items():
                if k in NUMERIC_DEMOS:
                    out[k] = to_num(v)
            demos[r["district"]] = out

    districts = []
    with V18_CSV.open() as f:
        for r in csv.DictReader(f):
            d_id = r["district"]
            row = {"district": d_id}
            for k, v in r.items():
                if k == "district":
                    continue
                row[k] = to_num(v) if k in NUMERIC_V18 else v
            demo = demos.get(d_id)
            if demo:
                for k in NUMERIC_DEMOS:
                    row[k] = demo.get(k)
                row["demo_source"] = demo["source"]
            else:
                for k in NUMERIC_DEMOS:
                    row[k] = None
                row["demo_source"] = "MISSING"
            # Apply manual incumbent overrides BEFORE WAR (since WAR is keyed on incumbent name)
            override = INCUMBENT_OVERRIDES.get(d_id)
            if override:
                if "incumbent" in override:
                    row["incumbent"] = override["incumbent"]
                if "party" in override:
                    row["party"] = override["party"]
            apply_recent_war(row, primary_war, fallback_war)
            # Named-but-not-sitting nominee (e.g. Crenshaw lost primary to Toth):
            # zero out the incumbency / WAR contribution that apply_recent_war
            # added based on the override name.
            if override and override.get("is_incumbent") is False:
                row["incumbency_adj"] = 0.0
                row["war"] = 0.0
                row["war_adj"] = 0.0
                row["war_adj_discounted"] = 0.0
                row["war_matched"] = False
                row["war_match_type"] = None
                row["war_year"] = None
            apply_house_challenger(row, primary_war, fallback_war)
            districts.append(row)

    with OUT_JSON.open("w") as f:
        json.dump({"districts": districts}, f, indent=None)

    n_missing = sum(1 for d in districts if d["demo_source"] == "MISSING")
    n_estimated = sum(1 for d in districts if d["demo_source"].endswith("_old_lines"))
    n_real = len(districts) - n_missing - n_estimated
    size_kb = OUT_JSON.stat().st_size / 1024
    print(f"Wrote {OUT_JSON} ({size_kb:.0f} KB)")
    print(f"  total districts:        {len(districts)}")
    print(f"  demographics (real):    {n_real}")
    print(f"  demographics (est):     {n_estimated}")
    print(f"  demographics (missing): {n_missing}")

    n_war_matched = sum(1 for d in districts if d.get("war_matched"))
    n_war_unmatched = sum(
        1 for d in districts
        if not d.get("war_matched") and parse_incumbent(d.get("incumbent", ""))
    )
    n_war_open = sum(1 for d in districts if not parse_incumbent(d.get("incumbent", "")))
    print(f"  WAR matched:            {n_war_matched}")
    print(f"  WAR unmatched named:    {n_war_unmatched}")
    print(f"  WAR open seats:         {n_war_open}")
    if n_war_unmatched:
        print(f"  (unmatched names get war=0; check load_data output for specifics)")


if __name__ == "__main__":
    main()
