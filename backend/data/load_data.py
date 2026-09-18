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
    # TX-09: redistricted open R-leaning seat (Al Green moved to TX-18).
    # Mealer is the R nominee — non-sitting, so is_incumbent=False zeros out the
    # ±1.7 structural incumbency bonus. D nominee (Gutierrez) is in HOUSE_CHALLENGERS.
    "TX-09": {"incumbent": "Alex Mealer", "party": "(R)", "is_incumbent": False},
    # CA-40 under Prop50 lines merged Calvert (old CA-41) and Kim (old CA-40)
    # into a single R-leaning seat — both sitting reps are in the primary.
    "CA-40": {"incumbent": "(open, R primary: Calvert vs Kim)", "party": "(R)"},
    # CA-41 under Prop50 was redrawn from Calvert's Riverside seat into a D-leaning
    # South LA County / N Orange County seat (Downey/Norwalk/Whittier). Linda Sánchez
    # (formerly CA-38) moved her reelection bid here when Prop50 passed.
    "CA-41": {"incumbent": "Linda Sánchez", "party": "(D)"},
    # CA-03 under Prop50 was redrawn from Kiley's Trump+3 district to a
    # Harris-by-double-digits district. Ami Bera (formerly CA-06) moved his
    # reelection bid here. Won D primary June 2, 2026.
    "CA-03": {"incumbent": "Ami Bera", "party": "(D)"},
    # CA-06 under Prop50 is a Sacramento-area Rocklin/Roseville/Citrus Heights
    # seat that includes Kiley's home. He moved here from old CA-03 AND switched
    # from R to Independent (NPP) on March 9, 2026 (became the only I in the
    # House, still caucuses with R Conference). Party=(I) → incumbency_adj=0
    # since the model only gives the structural ±1.7 to D/R caucus.
    "CA-06": {"incumbent": "Kevin Kiley", "party": "(I)"},
    # === CA top-two primary lockouts (general election is intra-party) ===
    # Projection is forced to ±100 because the party is guaranteed to hold the seat.
    "CA-04":  {"incumbent": "Mike Thompson",         "party": "(D)",
               "lockout": "D", "lockout_opponent": "Eric Jones"},
    "CA-07":  {"incumbent": "Doris Matsui",          "party": "(D)",
               "lockout": "D", "lockout_opponent": "Mai Vang"},
    "CA-11":  {"incumbent": "Scott Wiener",          "party": "(D)", "is_incumbent": False,
               "lockout": "D", "lockout_opponent": "Connie Chan"},
    "CA-12":  {"incumbent": "Lateefah Simon",        "party": "(D)",
               "lockout": "D", "lockout_opponent": "Jamie Joyce"},
    "CA-14":  {"incumbent": "Aisha Wahab",           "party": "(D)", "is_incumbent": False,
               "lockout": "D", "lockout_opponent": "Melissa Hernandez"},
    "CA-29":  {"incumbent": "Luz Rivas",             "party": "(D)",
               "lockout": "D", "lockout_opponent": "Angélica Dueñas"},
    "CA-34":  {"incumbent": "Jimmy Gomez",           "party": "(D)",
               "lockout": "D", "lockout_opponent": "Angela Gonzales-Torres"},
    "CA-37":  {"incumbent": "Sydney Kamlager-Dove",  "party": "(D)",
               "lockout": "D", "lockout_opponent": "Samantha Mota"},
    "CA-40":  {"incumbent": "Ken Calvert", "party": "(R)", "is_incumbent": False,
               "lockout": "R", "lockout_opponent": "Young Kim"},
    # CA-48 under Prop50: Issa retired. Jim Desmond (R, sitting San Diego County
    # Supervisor) won R primary; Marni von Wilpert (D) advanced as D challenger.
    "CA-48": {"incumbent": "Jim Desmond", "party": "(R)", "is_incumbent": False},
    # CA-01: LaMalfa vacated; James Gallagher (R, sitting assemblymember) won
    # R primary, Mike McGuire (D, state Senate Pro Tem) advanced as D.
    "CA-01": {"incumbent": "James Gallagher", "party": "(R)", "is_incumbent": False},
    # CA-26 post-Prop50: Jacqui Irwin (D, sitting CA-26 rep) advanced.
    "CA-26": {"incumbent": "Jacqui Irwin", "party": "(D)"},
    # CA-38 post-Prop50: Linda Sánchez moved to CA-41. Hilda Solis (former HHS
    # Sec / LA County Supervisor) won D primary for the redrawn seat.
    "CA-38": {"incumbent": "Hilda Solis", "party": "(D)", "is_incumbent": False},
    # === 2026-06-09 primaries ===
    # NV-02: open (Amodei retiring). Flippo (Trump-endorsed) won R primary over
    # establishment pick Settelmeyer (backed by Gov. Lombardo + Amodei).
    "NV-02": {"incumbent": "David Flippo", "party": "(R)", "is_incumbent": False},
    # === Summer/fall 2026 primaries (post-June) ===
    # SC-05: Norman ran for Senate (lost), seat is open. Wes Climer (R state sen) unopposed.
    "SC-05": {"incumbent": "Wes Climer", "party": "(R)", "is_incumbent": False},
    # CO-01: DeGette LOST D primary (major upset). Melat Kiros (D) is nominee.
    "CO-01": {"incumbent": "Melat Kiros", "party": "(D)", "is_incumbent": False},
    # FL-07: Mills LOST R primary amid ethics/DoJ probes. Ryan Elijah (R) is nominee.
    "FL-07": {"incumbent": "Ryan Elijah", "party": "(R)", "is_incumbent": False},
    # FL-19: open (Byron Donalds→gov). Strada (R) won primary.
    "FL-19": {"incumbent": "J. Strada", "party": "(R)", "is_incumbent": False},
    # FL-20: WS beat Cherfilus-McCormick + Holness + Manley + Luther Campbell in D primary — kept as inc.
    # FL-24: open (Wilson retiring/displaced by new FL map). Oliver Gilbert III (D) nominee.
    "FL-24": {"incumbent": "Oliver Gilbert III", "party": "(D)", "is_incumbent": False},
    # MI-10: open (John James→gov). Bouchard (R, Trump-endorsed, 72%) vs Hines (D).
    "MI-10": {"incumbent": "Mike Bouchard", "party": "(R)", "is_incumbent": False},
    # MI-11: open (Haley Stevens→Senate). Jeremy Moss (D state sen) is nominee.
    "MI-11": {"incumbent": "Jeremy Moss", "party": "(D)", "is_incumbent": False},
    # MI-13: Thanedar LOST D primary. Donavan McKinney (D state rep) is nominee.
    "MI-13": {"incumbent": "Donavan McKinney", "party": "(D)", "is_incumbent": False},
    # NH-01: open (Pappas→Senate). Stefany Shaheen (D, Jeanne Shaheen's granddaughter) is nominee.
    "NH-01": {"incumbent": "Stefany Shaheen", "party": "(D)", "is_incumbent": False},
    # NY-07: open (Velázquez retiring). Claire Valdez (D, DSA/Mamdani-backed).
    "NY-07": {"incumbent": "Claire Valdez", "party": "(D)", "is_incumbent": False},
    # NY-10: Goldman LOST D primary 62-38. Brad Lander (D, NYC comptroller) is nominee.
    "NY-10": {"incumbent": "Brad Lander", "party": "(D)", "is_incumbent": False},
    # NY-12: open (Nadler retiring). Micah Lasher (D state assembly) is nominee.
    "NY-12": {"incumbent": "Micah Lasher", "party": "(D)", "is_incumbent": False},
    # NY-13: Espaillat LOST D primary. Darializa Avila Chevalier (D) is nominee.
    "NY-13": {"incumbent": "Darializa Avila Chevalier", "party": "(D)", "is_incumbent": False},
    # NY-21: open (Stefanik→gov). Gendebien (D) vs Constantino (R, Trump-endorsed) → R stays R here.
    "NY-21": {"incumbent": "Anthony Constantino", "party": "(R)", "is_incumbent": False},
    # WA-04: open (Newhouse retiring). Amanda McKinney (R state sen, 34.9%) won top-two.
    "WA-04": {"incumbent": "Amanda McKinney", "party": "(R)", "is_incumbent": False},
    # WI-07: open (Tiffany→gov). Michael Alfonso (R, Duffy's son-in-law, Trump-endorsed).
    "WI-07": {"incumbent": "Michael Alfonso", "party": "(R)", "is_incumbent": False},
    # CT-01: Larson LOST D primary (major upset). Luke Bronin (D, ex-Hartford mayor).
    "CT-01": {"incumbent": "Luke Bronin", "party": "(D)", "is_incumbent": False},
    # MA-06: open (Moulton→Senate). Dan Koh (D) is nominee.
    "MA-06": {"incumbent": "Dan Koh", "party": "(D)", "is_incumbent": False},
    # OK-01: open (Hern→Senate). Mark Tedford (R) is nominee.
    "OK-01": {"incumbent": "Mark Tedford", "party": "(R)", "is_incumbent": False},
    # TN-05: Ogles LOST R primary despite Trump endorsement. Charlie Hatcher (R, 53.2%).
    "TN-05": {"incumbent": "Charlie Hatcher", "party": "(R)", "is_incumbent": False},
    # TN-06: open (John Rose→gov). Johnny Garrett (R state rep).
    "TN-06": {"incumbent": "Johnny Garrett", "party": "(R)", "is_incumbent": False},
    # TN-09: open (Cohen retired after TN redistricting split Memphis). Brent Taylor (R state sen).
    "TN-09": {"incumbent": "Brent Taylor", "party": "(R)", "is_incumbent": False},
    # WY-AL: open (Hageman→Senate). Chuck Gray (R Sec of State).
    "WY-AL": {"incumbent": "Chuck Gray", "party": "(R)", "is_incumbent": False},
    # MO-06: open (Sam Graves retiring after 13 terms). Chris Stigall (R).
    "MO-06": {"incumbent": "Chris Stigall", "party": "(R)", "is_incumbent": False},
    # AZ-05: open (Biggs→gov). Mark Lamb (R, former Pinal Co sheriff).
    "AZ-05": {"incumbent": "Mark Lamb", "party": "(R)", "is_incumbent": False},
    # UT-01: court-redraw made this a new D-leaning SLC seat. Ben McAdams (D, former US Rep) won D primary 60%.
    "UT-01": {"incumbent": "Ben McAdams", "party": "(D)", "is_incumbent": False},
    # UT-04: open (Burgess Owens retired). Mike Kennedy (R) moved from old UT-03.
    "UT-04": {"incumbent": "Mike Kennedy", "party": "(R)", "is_incumbent": False},
    # MN-02: open (Craig→Senate). Matt Little (D) vs Eric Pratt (R).
    "MN-02": {"incumbent": "Matt Little", "party": "(D)", "is_incumbent": False},
    # AZ-01: already open (Schweikert→gov). Jay Feely (R, Trump-endorsed) won R primary.
    "AZ-01": {"incumbent": "Jay Feely", "party": "(R)", "is_incumbent": False},
    # MD-05: open (Hoyer retiring). Adrian Boafo (D).
    "MD-05": {"incumbent": "Adrian Boafo", "party": "(D)", "is_incumbent": False},
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
    # LA-06: post-redraw the seat is R-leaning (R+32 pres). Cleo Fields keeps the
    # incumbent label as a placeholder but is unlikely to run; is_incumbent=False
    # zeros the +1.7 D incumbency boost that he won't actually carry into a hostile seat.
    "LA-06": {"incumbent": "Cleo Fields", "party": "(D)", "is_incumbent": False},
    # === 2026-06-02 primaries ===
    # IA-02: open (Hinson→Senate). Trump-endorsed Mitchell won R primary.
    "IA-02": {"incumbent": "Joe Mitchell", "party": "(R)", "is_incumbent": False},
    # IA-04: open (Feenstra→gov). McGowan won R primary.
    "IA-04": {"incumbent": "Chris McGowan", "party": "(R)", "is_incumbent": False},
    # MT-01: open (Zinke retiring). Trump-endorsed Flint (veteran/radio host) won R primary.
    "MT-01": {"incumbent": "Aaron Flint", "party": "(R)", "is_incumbent": False},
    # NJ-12: open (Watson Coleman retiring). Hamawy won crowded 13-way D primary.
    "NJ-12": {"incumbent": "Adam Hamawy", "party": "(D)", "is_incumbent": False},
    # SD-AL: open (Johnson→gov). State AG Jackley won R primary.
    "SD-AL": {"incumbent": "Marty Jackley", "party": "(R)", "is_incumbent": False},
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
    # === 2026-06-02 primaries ===
    "IA-02": {"name": "Lindsay James", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (IA state rep); challenger to Mitchell in open Hinson seat"},
    "IA-04": {"name": "Dave Dawson", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee; challenger to McGowan in open Feenstra seat (heavily R)"},
    "MT-01": {"name": "Sam Forstag", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (called after late count; Busse fell short)"},
    "MT-02": {"name": "Brian Miller", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (Helena attorney); challenger to Downing"},
    "NJ-02": {"name": "Zack Mullock", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee; challenger to Van Drew"},
    "NJ-03": {"name": "Michael McGuire", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (Marine vet, ex-NYPD officer); challenger to Conaway"},
    "NJ-04": {"name": "Rachel Peace", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee; challenger to Chris Smith"},
    "NJ-07": {"name": "Rebecca Bennett", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (former Navy helicopter pilot); challenger to Tom Kean Jr"},
    "NM-02": {"name": "Greg Cunningham", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (retired police officer); challenger to Vasquez"},
    "NV-02": {"name": "Teresa Benitez-Thompson", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (former Assembly Majority Leader, AG chief of staff); challenger to Flippo"},
    "NV-04": {"name": "Cody Whipple", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (rancher); challenger to Horsford"},
    # NV remaining
    "NV-01": {"name": "Carrie Buck", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (NV state senator, Trump-endorsed); challenger to Titus"},
    "NV-03": {"name": "Marty O'Donnell", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (composer, Trump+Lombardo-endorsed); challenger to Susie Lee"},
    # CA non-lockout competitive seats (advancing 1 D + 1 R per June 2 SoS results)
    "CA-06": {"name": "Richard Pan", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (former state senator); challenger to Kiley (I) in post-Prop50 Sacramento seat"},
    "CA-13": {"name": "Kevin Lincoln", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee (former Stockton mayor); challenger to Adam Gray"},
    "CA-22": {"name": "Randy Villegas", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee; challenger to Valadao"},
    "CA-27": {"name": "Jason Gibbs", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Whitesides"},
    "CA-41": {"name": "Mitch Clemmons", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Sánchez in post-Prop50 LA County seat"},
    "CA-45": {"name": "Chuong V. Vo", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Tran"},
    "CA-47": {"name": "Jenny Rae Le Roux", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Min"},
    "CA-48": {"name": "Marni von Wilpert", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (San Diego city council); challenger to Desmond in open Issa seat"},
    "CA-49": {"name": "Armen Kurdian", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Levin"},
    "CA-50": {"name": "Steve Cohen", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee; challenger to Peters"},
    # CA remaining (safe seats, completing the slate from June 2 SoS results)
    "CA-01": {"name": "Mike McGuire", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "CA-03": {"name": "Robb Tucker", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Bera in post-Prop50 D-leaning seat"},
    "CA-02": {"name": "Robin Littau", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-05": {"name": "Michael Masuda", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "CA-08": {"name": "Rudy Recile", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-09": {"name": "John McBride", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-10": {"name": "Jeff Frese", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-15": {"name": "Charles Hoelter", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-16": {"name": "Peter Sundin Soulé", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-17": {"name": "Ritesh Tandon", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-18": {"name": "Shane Lewis", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-19": {"name": "Peter Coe Verbica", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-20": {"name": "Sandra Van Scotter", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "CA-21": {"name": "Kyle Kirkland", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-23": {"name": "Tessa Lynn Hodge", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "CA-24": {"name": "Bob Smith", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-25": {"name": "Joe Males", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-26": {"name": "Sam Gallucci", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-28": {"name": "April A. Verlato", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-30": {"name": "Scott Alan Meyers", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-31": {"name": "Eric Ching", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-32": {"name": "Larry Thompson", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-33": {"name": "Stephanie M. Vargas", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-35": {"name": "Mike Cargile", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-36": {"name": "Houston Brignano", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-38": {"name": "Pedro Antonio Casas", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-39": {"name": "Steve Manos", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-42": {"name": "Brian Burley", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-43": {"name": "Cristian Morales", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-44": {"name": "Genevieve Angel", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-46": {"name": "David Pan", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-51": {"name": "Ricardo Cabrera", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CA-52": {"name": "Jeff Belle", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # === Summer/fall 2026 primary results ===
    # AZ
    "AZ-01": {"name": "Amish Shah", "party": "(D)", "war": 0.0, "note": "2026 D nominee (2024 rematch — auto-WAR)"},
    "AZ-06": {"name": "JoAnna Mendoza", "party": "(D)", "war": 0.0, "note": "2026 D nominee (Marine vet); challenger to Ciscomani"},
    "AZ-09": {"name": "Dani Sterbinsky", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Gosar"},
    # CO
    "CO-03": {"name": "Dwayne Romero", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Hurd"},
    "CO-04": {"name": "Eileen Laubacher", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Boebert"},
    "CO-05": {"name": "Jessica Killin", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Crank"},
    "CO-08": {"name": "Manny Rutinel", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Evans — top toss-up"},
    # FL competitive races (map redraw pending review — see NOTE)
    "FL-14": {"name": "Kathy Castor", "party": "(D)", "war": 0.0, "note": "Castor (D-inc) vs R nominee in new Trump+11 seat post-FL redraw"},
    # MI
    "MI-03": {"name": "Terri DeBoer", "party": "(R)", "war": 0.0, "note": "2026 R nominee (former TV meteorologist); challenger to Scholten"},
    "MI-04": {"name": "Sean McCann", "party": "(D)", "war": 0.0, "note": "2026 D nominee (state senator, Whitmer-endorsed); challenger to Huizenga"},
    "MI-07": {"name": "Will Lawrence", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Barrett"},
    "MI-08": {"name": "Tom Smith", "party": "(R)", "war": 0.0, "note": "2026 R nominee (upset Trump-endorsed Amir Hassan); challenger to McDonald Rivet"},
    "MI-10": {"name": "Christina Hines", "party": "(D)", "war": 0.0, "note": "2026 D nominee (former asst US attorney); challenger to Bouchard in open James seat"},
    "MI-13": {"name": "TP Nykoriak", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # MN
    "MN-01": {"name": "Jake Johnson", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Finstad"},
    "MN-02": {"name": "Eric Pratt", "party": "(R)", "war": 0.0, "note": "2026 R nominee (state senator); challenger to Little in open Craig seat"},
    "MN-03": {"name": "Tyler Bass", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Morrison"},
    # MO
    "MO-02": {"name": "Fred Wellman", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Wagner (2024 lines restored)"},
    "MO-05": {"name": "Rick Brattin", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Cleaver (seat safe D again after map reverted)"},
    "MO-06": {"name": "Josh Smead", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Stigall in open Graves seat"},
    # NH
    "NH-01": {"name": "Anthony DiLorenzo", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Stefany Shaheen in open Pappas seat"},
    # NY competitive
    "NY-17": {"name": "Cait Conley", "party": "(D)", "war": 0.0, "note": "2026 D nominee (Army vet); challenger to Lawler"},
    "NY-18": {"name": "Sharanjit Thind", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Ryan"},
    "NY-19": {"name": "Peter Oberacker", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Riley"},
    "NY-21": {"name": "Blake Gendebien", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Constantino in open Stefanik seat"},
    "NY-22": {"name": "Kailee Buller", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Mannion"},
    "NY-24": {"name": "Alissa J. Ellman", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Tenney"},
    "NY-23": {"name": "Aaron Gies", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Langworthy"},
    # WA competitive
    "WA-03": {"name": "John Braun", "party": "(R)", "war": 0.0, "note": "2026 R nominee (state Sen Minority Leader, Trump-backed); challenger to Gluesenkamp Perez"},
    "WA-04": {"name": "John Duresky", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to McKinney in open Newhouse seat"},
    "WA-05": {"name": "Carmela Conroy", "party": "(D)", "war": 0.0, "note": "2026 D nominee (2024 rematch); challenger to Baumgartner"},
    # WI competitive
    "WI-01": {"name": "Mitchell Berman", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Steil"},
    "WI-03": {"name": "Rebecca Cooke", "party": "(D)", "war": 0.0, "note": "2026 D nominee (2024 rematch — auto-WAR); challenger to Van Orden"},
    "WI-07": {"name": "Fred Clark", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Alfonso in open Tiffany seat"},
    # TN post-redraw
    "TN-09": {"name": "Justin J. Pearson", "party": "(D)", "war": 0.0, "note": "2026 D nominee ('TN Three' state rep); challenger to Taylor in open Cohen seat"},
    # SC
    "SC-05": {"name": "Mallory Dittmer", "party": "(D)", "war": 0.0, "note": "2026 D nominee (55.5% in primary); challenger to Climer in open Norman seat"},
    # UT
    "UT-01": {"name": "Riley Owen", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to McAdams in new D-lean SLC seat"},
    "UT-02": {"name": "Peter Crosby", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Moore"},
    "UT-03": {"name": "Caroline Gleich", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Maloy"},
    "UT-04": {"name": "Jonny Larsen", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Kennedy in open Owens seat"},
    # WY, KS, MS, OK, MA (safe-seat challengers)
    "WY-AL": {"name": "Lisa F. Kinney", "party": "(D)", "war": 0.0, "note": "2026 D nominee (ex-state Sen minority leader); challenger to Gray in open Hageman seat"},
    "KS-01": {"name": "Lauren Reinhold", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "KS-02": {"name": "Don Coover", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "KS-03": {"name": "Eric Jenkins", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Davids"},
    "KS-04": {"name": "Katy Tyndell", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MA-06": {"name": "Micah Jones", "party": "(R)", "war": 0.0, "note": "2026 R nominee (Army vet); challenger to Koh in open Moulton seat"},
    "OK-01": {"name": "John Croisant", "party": "(D)", "war": 0.0, "note": "2026 D nominee; challenger to Tedford in open Hern seat"},
    "OK-05": {"name": "Jena Nelson", "party": "(D)", "war": 0.0, "note": "2026 D nominee (beat Trey Martin); challenger to Bice"},
    # CT
    "CT-01": {"name": "Amy Chai", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Bronin in open Larson seat"},
    # DE
    "DE-AL": {"name": "Joseph Arminio", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to McBride"},
    # MD-06
    "MD-06": {"name": "Robin Ficker", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to McClain Delaney"},
    # === Additional safe-seat challengers from June-Sept primaries ===
    # CO safe/second-tier
    "CO-02": {"name": "Kelley Dennison", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CO-06": {"name": "Jason Clark", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Crow"},
    # FL — deep-red R holds getting sacrificial D challengers
    "FL-02": {"name": "A. Green", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-03": {"name": "S. Harp", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-04": {"name": "L. Holloway", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-05": {"name": "R. Grage", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-06": {"name": "E. Yonce", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-07": {"name": "B. Dalton", "party": "(D)", "war": 0.0, "note": "2026 D nominee (challenger to Elijah in open Mills seat)"},
    "FL-12": {"name": "Christopher Irizarry", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-22": {"name": "Casey Askar", "party": "(R)", "war": 0.0,
              "note": "2026 R nominee for redrawn FL-22 (now R-leaning open seat). D nominee: Pia Dandiya."},
    "FL-26": {"name": "Nicole Locklin", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-27": {"name": "Rodriguez", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # MI additional
    "MI-09": {"name": "Ray Pooley", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MI-12": {"name": "James D. Hooper", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # MN additional
    "MN-04": {"name": "Paul Wikstrom", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MN-05": {"name": "John Nagel", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MN-06": {"name": "Doug Chapin", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MN-07": {"name": "Erik Osberg", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MN-08": {"name": "Trina Swanson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # MO additional (post-map-revert)
    "MO-01": {"name": "Paul Berry", "party": "(R)", "war": 0.0, "note": "2026 R nominee; challenger to Bell (who beat Cori Bush in D primary)"},
    "MO-03": {"name": "Bethany Mann", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MO-04": {"name": "Jordan Herrera", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MO-07": {"name": "Missi Hesketh", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MO-08": {"name": "Cody Reichard", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # NY safe D + swing
    "NY-01": {"name": "Christopher J. Gallant", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NY-02": {"name": "Jessica N. Murphy", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NY-03": {"name": "Michael LiPetri", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-04": {"name": "Jeanine C. Driscoll", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-11": {"name": "Mike DeCillis", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # CT
    "CT-02": {"name": "George Austin", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CT-03": {"name": "Chris Lancia", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CT-04": {"name": "Michael Goldstein", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "CT-05": {"name": "Chris Shea", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # MD
    "MD-01": {"name": "Dan Schwartz", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MD-02": {"name": "Dave Wallace", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MD-03": {"name": "Berney Flowers", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MD-08": {"name": "Cheryl Riley", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # MS
    "MS-01": {"name": "Cliff Johnson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MS-02": {"name": "Ron Eller", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MS-03": {"name": "Michael Chiaradio", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # OK
    "OK-02": {"name": "Brandon Wade", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "OK-03": {"name": "Suzie Byrd", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "OK-04": {"name": "Mitchell Jacob", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # RI
    "RI-01": {"name": "Kellie Keenan", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "RI-02": {"name": "Victor Mellor", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # TN
    "TN-01": {"name": "Kristi Burke", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-04": {"name": "Victoria Broderick", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-08": {"name": "Lynnette Williams", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # WA
    "WA-01": {"name": "Mary Silva", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-02": {"name": "Edwin H. Feller", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-06": {"name": "Teresa Fox", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-07": {"name": "Nirav Sheth", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-08": {"name": "Spencer Meline", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-09": {"name": "Doug Basler", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WA-10": {"name": "Chris Chung", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # WI
    "WI-04": {"name": "Tim Rogers", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "WI-05": {"name": "Andrew Beck", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    # MA safe D — mostly token opposition
    "MA-01": {"name": "R token", "party": "(R)", "war": 0.0, "note": "2026 R token opposition (safe D)"},
    "MA-03": {"name": "Gary Grossi", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # KY (post-May primary — leftover safe seats)
    "KY-02": {"name": "D token", "party": "(D)", "war": 0.0, "note": "2026 D token (safe R)"},
    "KY-03": {"name": "R token", "party": "(R)", "war": 0.0, "note": "2026 R token (safe D — Morgan McGarvey seat)"},
    "KY-06": {"name": "D token", "party": "(D)", "war": 0.0, "note": "2026 D token; challenger to Barr's successor"},
    # === Named 2026 cross-party nominees from Ballotpedia (primaries complete) ===
    "AK-AL": {"name": "Eric Hafner", "party": "(D)", "war": 0.0, "note": "2026 D nominee (top-4 primary)"},
    "AL-01": {"name": "Clyde Jones", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "AL-02": {"name": "Rhett Marques", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "AL-04": {"name": "Amanda Pusczek", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "AL-05": {"name": "Andrew Sneed", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "AL-06": {"name": "Maurice Mercer", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "AL-07": {"name": "Ammie Akin", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "AZ-03": {"name": "Jacob Parkman", "party": "(R)", "war": 0.0, "note": "2026 R write-in nominee"},
    "AZ-04": {"name": "Zuhdi Jasser", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "AZ-05": {"name": "Elizabeth Lee", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "AZ-07": {"name": "Daniel Butierez Sr.", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "AZ-08": {"name": "Bernadette Greene-Placentia", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "CO-01": {"name": "Christy Peterson", "party": "(R)", "war": 0.0, "note": "2026 R nominee; note DeGette lost D primary to Melat Kiros"},
    "CO-07": {"name": "Timothy Bennett", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "FL-01": {"name": "Gay Valimont", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-08": {"name": "Jennifer Jenkins", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-09": {"name": "Dan Green", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # FL-10: Frost (D) uncontested — no R filed. No entry (challenger stays null).
    "FL-11": {"name": "James Pericola", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-13": {"name": "Leela Gray", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-15": {"name": "Robert People", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-16": {"name": "Kelly Kirschner", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-17": {"name": "Matthew Montavon", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-18": {"name": "Curtis Gibson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-19": {"name": "Victor Arias", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-20": {"name": "Brent Andersen", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "FL-21": {"name": "James Martin", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "FL-23": {"name": "Deborah Adeimy", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "FL-24": {"name": "Mayonna Te Brown", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "FL-25": {"name": "Scott Singer", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "FL-28": {"name": "Phil Ehr", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-01": {"name": "Amanda Hollowell", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-07": {"name": "Anthony Kozycki", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-11": {"name": "Chris Harden", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "GA-12": {"name": "Ceretta Smith", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "HI-01": {"name": "Maxwell Frazier", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "HI-02": {"name": "Brenton Awa", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "ID-01": {"name": "Kaylee Peterson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "ID-02": {"name": "Elinor Gilbreath", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "LA-01": {"name": "Lauren Jewett", "party": "(D)", "war": 0.0, "note": "2026 D nominee (LA jungle primary)"},
    # LA-02: no R filed — Libertarian only opposition. Uncontested by R.
    "LA-03": {"name": "John Day", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "LA-04": {"name": "Conrad Cable", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "LA-05": {"name": "Patricia \"Pat\" Moore", "party": "(D)", "war": 0.0,
              "note": "Leading D in LA jungle primary (state rep HD-17). Open seat (Letlow→Senate)."},
    "LA-06": {"name": "Blake Miguez", "party": "(R)", "war": 0.0, "note": "2026 R nominee; Fields withdrew after redraw"},
    # MA-02: uncontested by R.
    "MA-04": {"name": "Tom Stalcup", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MA-05": {"name": "Derek Fleming", "party": "(I)", "war": 0.0, "note": "2026 I candidate; no R filed"},
    "MA-07": {"name": "Kelechi Linardon", "party": "(I)", "war": 0.0, "note": "2026 I candidate; no R filed"},
    "MA-08": {"name": "Robert Burke", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MA-09": {"name": "Robert MacAllister", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MD-05": {"name": "Chris Chaffee", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "ME-01": {"name": "Ron Russell", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MI-01": {"name": "Callie Barr", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MI-02": {"name": "Ben Ambrose", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MI-05": {"name": "Christian Vukasovich", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "MI-06": {"name": "Heather Smiley", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "MI-11": {"name": "Ethan Baker", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "ND-AL": {"name": "Trygve Hammer", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "NH-02": {"name": "Lily Tang Williams", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-01": {"name": "Damon Galdo", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-05": {"name": "Sean Kirrane", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-06": {"name": "Hillary Herzig", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-08": {"name": "Aristotle Eliopoulos", "party": "(I)", "war": 0.0, "note": "2026 I candidate; no R filed (GOP-aligned)"},
    "NJ-09": {"name": "Rosie Pino", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-10": {"name": "Carmen Bucco", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-11": {"name": "Joe Hathaway", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NJ-12": {"name": "Gregg Mele", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-05": {"name": "George Marsh", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-06": {"name": "Joseph Chou", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-07": {"name": "Melvin Rivera", "party": "(R)", "war": 0.0, "note": "2026 R nominee (open — Velázquez retired)"},
    "NY-08": {"name": "Lewis Mizrahi", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-09": {"name": "Joel Anabilah-Azumah", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-10": {"name": "Jennifer Moore", "party": "(R)", "war": 0.0, "note": "2026 R nominee (open — Goldman lost D primary)"},
    "NY-12": {"name": "Caroline Shinkle", "party": "(R)", "war": 0.0, "note": "2026 R nominee (open — Nadler retired)"},
    "NY-13": {"name": "Jomo M. Williams", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-14": {"name": "Diamant Hysenaj", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-15": {"name": "Stylo Sapaskis", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-16": {"name": "Joseph Cinquemani", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-20": {"name": "Ralph Ambrosio", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-25": {"name": "Virginia McIntyre", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "NY-26": {"name": "Dennis Hannon", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # PA-03: uncontested by R (Evans open seat; only independent opposition).
    "SC-01": {"name": "Nancy Lacore", "party": "(D)", "war": 0.0, "note": "2026 D nominee (open — Mace ran for governor; Jenny Costa Honeycutt won R runoff)"},
    "SC-02": {"name": "Zyon Khalifa", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "SC-03": {"name": "Eunice Lehmacher", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "SC-04": {"name": "Courtney McClain", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "SC-06": {"name": "John Peterson", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "SC-07": {"name": "John Gregory Vincent", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "SD-AL": {"name": "Nikki Gronli", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-02": {"name": "Michaela Barnett", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-03": {"name": "Anna Golladay", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-05": {"name": "Chaz Molder", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-06": {"name": "Mike Croley", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TN-07": {"name": "Darden Copeland", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "TX-09": {"name": "Leticia Gutierrez", "party": "(D)", "war": 0.0,
              "note": "2026 D nominee (won D primary March 3 outright with 53.6% in 6-way field). "
                      "TX-09 is a redistricted open R-leaning seat; Al Green moved to TX-18."},
    "VA-01": {"name": "Shannon Taylor", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "VA-03": {"name": "Edwin Rivera", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "VA-04": {"name": "Robert Murray", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "VA-05": {"name": "Tom Perriello", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "VA-06": {"name": "Beth Macy", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "VA-07": {"name": "Doug Ollivant", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "VA-08": {"name": "Tony Sabio", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "VA-09": {"name": "Joy Powers", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "VA-10": {"name": "Dave Beckwith", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    "VA-11": {"name": "Arthur Purves", "party": "(R)", "war": 0.0, "note": "2026 R nominee (Walkinshaw is now incumbent, won July 2025 special)"},
    "VT-AL": {"name": "Gerald Malloy", "party": "(R)", "war": 0.0, "note": "2026 R nominee"},
    # WI-02: uncontested by R (Pocan).
    "WI-06": {"name": "Brad Smith", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
    "WI-08": {"name": "Rick Crosson", "party": "(D)", "war": 0.0, "note": "2026 D nominee"},
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
            # Lockout: top-two primary advanced two same-party candidates.
            # Override the challenger field with the intra-party opponent and
            # zero out challenger_adj (no cross-party math applies).
            if override and "lockout" in override:
                row["lockout"] = override["lockout"]
                row["challenger"] = override.get("lockout_opponent")
                row["challenger_party"] = override["party"]
                row["challenger_adj"] = 0.0
                row["challenger_war"] = None
                row["challenger_war_year"] = None
                row["challenger_war_source"] = None
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
