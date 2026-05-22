export type SliderKey =
  | "white_nh"
  | "black"
  | "hispanic"
  | "asian"
  | "white_college"
  | "white_non_college"
  | "nonwhite_college"
  | "nonwhite_non_college"
  | "under_30"
  | "age_30_44"
  | "age_45_64"
  | "age_65_plus";

export type SliderValues = Record<SliderKey, number>;

// Electorate composition uses Catalist 2022 shares (midterm-electorate proxy
// for 2026); group margins below use Catalist 2024 values (the most recent
// signal on how each group is voting). This mix matches the user's modeling
// choice: who shows up in a midterm comes from 2022, how they vote comes from
// 2024.
// Source: Catalist "What Happened 2024" national crosstabs Excel
// (https://catalist.us/whathappened2024/).
export const CATALIST_ELECTORATE_SHARES_RACE: Record<
  "white_nh" | "black" | "hispanic" | "asian" | "other", number
> = {
  white_nh: 0.7581,
  black:    0.0959,
  hispanic: 0.0804,
  asian:    0.0365,
  other:    0.0292,
};

// Catalist 2022 race × edu shares. nonwhite cells = Black + Latino + AAPI + Other.
export const CATALIST_ELECTORATE_SHARES_EDU: Record<
  "white_college" | "white_non_college" | "nonwhite_college" | "nonwhite_non_college", number
> = {
  white_college:        0.3351,
  white_non_college:    0.4230,
  nonwhite_college:     0.1010,   // Black 3.67 + Latino 3.17 + AAPI 1.96 + Other 1.30
  nonwhite_non_college: 0.1409,   // Black 5.92 + Latino 4.86 + AAPI 1.70 + Other 1.61
};

// Catalist 2022 age-bracket shares.
export const CATALIST_ELECTORATE_SHARES_AGE: Record<
  "under_30" | "age_30_44" | "age_45_64" | "age_65_plus", number
> = {
  under_30:    0.1000,
  age_30_44:   0.2001,
  age_45_64:   0.3652,
  age_65_plus: 0.3347,
};

// "Other" race (AIAN / NHPI / two-or-more-races, 3.05% of electorate).
// Catalist 2024: two-way D 53.53% → margin +7.06.
export const OTHER_RACE_BASELINE = 7.06;

// Catalist 2024 "What Happened" published D-R margins — the slider zero-point.
// Matches the 2024 presidential spine the rest of the model is built on:
// parking sliders here means "group voted the same as 2024 = zero demographic
// deviation from the baseline." Moving a slider models that group voting
// differently than 2024.
export const CATALIST_BASELINES: SliderValues = {
  white_nh:               -15.24,
  black:                   70.80,
  hispanic:                 8.46,
  asian:                   21.38,
  white_college:            1.90,
  white_non_college:      -27.28,
  nonwhite_college:        36.82,
  nonwhite_non_college:    31.85,
  under_30:                10.52,
  age_30_44:                4.70,
  age_45_64:               -8.64,
  age_65_plus:             -4.02,
};

// Per-cycle Catalist D-R margins. Used to populate slider presets so users
// can model "what if Hispanic / white / etc. voted like 2020 (or 2022)".
// The model baseline stays at 2024 — selecting an older preset moves the
// sliders away from baseline, generating a demographic_shift delta.
export const CATALIST_PRESETS: Record<"2020" | "2022" | "2024", SliderValues> = {
  // 2020 (presidential) — Catalist exact margins from 2024 report's revised
  // 2020 column. Biden coalition peak; pres popvote D+4.5.
  "2020": {
    white_nh:               -11.66,
    black:                   77.34,
    hispanic:                26.56,
    asian:                   30.46,
    white_college:            8.18,
    white_non_college:      -24.54,
    nonwhite_college:        46.17,
    nonwhite_non_college:    46.07,
    under_30:                22.72,
    age_30_44:               13.18,
    age_45_64:               -3.26,
    age_65_plus:             -2.76,
  },
  // 2022 (US House popular vote) — Catalist exact margins. Midterm with
  // post-Dobbs youth surge; House popvote R+2.9.
  "2022": {
    white_nh:               -15.76,
    black:                   76.22,
    hispanic:                21.64,
    asian:                   24.80,
    white_college:           -2.20,
    white_non_college:      -26.50,
    nonwhite_college:        43.70,
    nonwhite_non_college:    41.78,
    under_30:                29.62,
    age_30_44:               14.26,
    age_45_64:               -9.24,
    age_65_plus:            -12.16,
  },
  // 2024 (presidential) — Catalist exact margins. Pres popvote R-2.0
  // (Harris 49.26% two-way).
  "2024": {
    white_nh:               -15.24,
    black:                   70.80,
    hispanic:                 8.46,
    asian:                   21.38,
    white_college:            1.90,
    white_non_college:      -27.28,
    nonwhite_college:        36.82,
    nonwhite_non_college:    31.85,
    under_30:                10.52,
    age_30_44:                4.70,
    age_45_64:               -8.64,
    age_65_plus:             -4.02,
  },
};

export const SLIDER_DEFS: { key: SliderKey; label: string; min: number; max: number; axis: "race" | "edu" | "age" }[] = [
  { key: "hispanic",              label: "Hispanic",              min: -100, max: 100, axis: "race" },
  { key: "black",                 label: "Black",                 min: -100, max: 100, axis: "race" },
  { key: "asian",                 label: "Asian",                 min: -100, max: 100, axis: "race" },
  { key: "white_nh",              label: "White (non-Hisp.)",     min: -100, max: 100, axis: "race" },
  { key: "white_college",         label: "White, college",        min: -100, max: 100, axis: "edu"  },
  { key: "white_non_college",     label: "White, non-college",    min: -100, max: 100, axis: "edu"  },
  { key: "nonwhite_college",      label: "Non-white, college",    min: -100, max: 100, axis: "edu"  },
  { key: "nonwhite_non_college",  label: "Non-white, non-college", min: -100, max: 100, axis: "edu" },
  { key: "under_30",              label: "Under 30",              min: -100, max: 100, axis: "age"  },
  { key: "age_30_44",             label: "30-44",                 min: -100, max: 100, axis: "age"  },
  { key: "age_45_64",             label: "45-64",                 min: -100, max: 100, axis: "age"  },
  { key: "age_65_plus",           label: "65+",                   min: -100, max: 100, axis: "age"  },
];

export const DEFAULT_SLIDERS: SliderValues = { ...CATALIST_BASELINES };

export function formatMargin(v: number): string {
  if (v === 0) return "tie";
  return v > 0 ? `D+${v}` : `R+${-v}`;
}

// Signed projection like "+1.2" / "-3.4". When the 1-decimal value would round
// to 0.0, expand to 2 decimals so the sign and direction stay visible.
export function formatProjection(v: number): string {
  const digits = Math.abs(v) < 0.05 ? 2 : 1;
  const sign = v > 0 ? "+" : "";
  return `${sign}${v.toFixed(digits)}`;
}

/** Convert a D-R margin into a two-party D% vs R% breakdown (rounded to 0.5).
 *  e.g., +6 -> "53D-47R", -14 -> "43D-57R". */
export function formatPartySplit(v: number): string {
  const d = (100 + v) / 2;
  const r = 100 - d;
  const fmt = (x: number) => (Math.round(x * 10) / 10).toFixed(x % 1 === 0 ? 0 : 1);
  return `${fmt(d)}D-${fmt(r)}R`;
}

/** Returns a Tailwind text-color class for a candidate's party. */
export function partyColorClass(party: string | null | undefined): string {
  if (party === "(D)") return "text-blue-700";
  if (party === "(R)") return "text-red-700";
  return "text-slate-500"; // I, null, "(open, ...)" etc.
}

/** Returns a hex color suitable for inline styles (e.g., MapLibre tooltip HTML). */
export function partyColorHex(party: string | null | undefined): string {
  if (party === "(D)") return "#1d4ed8";
  if (party === "(R)") return "#b91c1c";
  return "#64748b";
}

/** Tag a party label with "-Inc" when the candidate is a sitting incumbent.
 *  Pass `true` for any candidate who currently holds the seat — including
 *  those whose primary is unresolved (Cassidy LA, Cornyn TX). Pass `false`
 *  for open seats and named-but-not-sitting nominees (TX-02 Toth). */
export function partyTag(
  party: string | null | undefined,
  isIncumbent: boolean,
): string {
  if (!party) return "";
  if (!isIncumbent) return party;
  return party.replace(/^\((.+)\)$/, "($1-Inc)");
}

/** Bucket label for a projection margin (D-positive). Thresholds match the
 *  rest of the app: tilt ≤3 | lean 3-7 | likely 7-13 | safe >13. */
export function bucketLabel(proj: number): string {
  const a = Math.abs(proj);
  const side = proj > 0 ? "D" : "R";
  if (a > 13) return `safe ${side}`;
  if (a > 7)  return `likely ${side}`;
  if (a > 3)  return `lean ${side}`;
  return `tilt ${side}`;
}

export type District = {
  district: string;
  incumbent: string;
  party: "(D)" | "(R)" | string;
  state: string;
  lines: string;
  margin_2024: number;
  rel_trend?: number | null;
  rel_trend_applied?: number | null;
  war_adj_discounted?: number | null;
  incumbency_adj?: number | null;
  war_year?: number | null;
  war_match_type?: string | null;
  challenger?: string | null;
  challenger_party?: string | null;
  challenger_adj?: number | null;
  challenger_war?: number | null;
  challenger_war_year?: number | null;
  challenger_war_source?: string | null;
  projection: number;
  demo_shift: number;
  race_shift: number;
  edu_shift: number;
  age_shift: number;
  is_tossup: boolean;
  flip: "to_D" | "to_R" | null;
  demo_source: string;
};

export type Summary = {
  d_seats: number;
  r_seats: number;
  tossups: number;
  d_pickups: string[];
  r_pickups: string[];
  majority: "D" | "R" | "none";
  buckets?: {
    d_safe: number; d_likely: number; d_lean: number; d_tossup: number;
    r_tossup: number; r_lean: number; r_likely: number; r_safe: number;
  };
};

export type ProjectResponse = {
  environment: number;
  sliders: SliderValues;
  axis_weight: number;
  uniform_swing: number;
  trend_discount: number;
  summary: Summary;
  districts: District[];
};

// ── Senate types ──
export type SenateSeat = {
  state: string;
  name: string;
  incumbent: string | null;
  party: string;
  retiring: boolean;
  appointed?: boolean;
  primary_unresolved?: boolean;
  seat_type: "regular" | "special" | null;
  presidential_margin_2024: number | null;
  state_trend: number | null;
  state_trend_applied?: number | null;
  war_adj_discounted: number | null;
  incumbency_adj: number | null;
  challenger: string | null;
  challenger_party: string | null;
  challenger_adj: number | null;
  challenger_war?: number | null;
  challenger_war_year?: number | null;
  challenger_war_source?: string | null;
  co_nominee?: string | null;
  co_nominee_party?: string | null;
  co_nominee_adj?: number | null;
  co_nominee_war?: number | null;
  co_nominee_war_year?: number | null;
  co_nominee_war_source?: string | null;
  projection: number;
  demo_shift: number;
  race_shift: number;
  edu_shift: number;
  age_shift: number;
  is_tossup: boolean;
  flip: "to_D" | "to_R" | null;
};

export type SenateSummary = {
  seats_up: number;
  d_seats_up: number;
  r_seats_up: number;
  tossups_up: number;
  not_up_d: number;
  not_up_r: number;
  final_d: number;
  final_r: number;
  majority: "D" | "R" | "tie" | "none";
  d_pickups: string[];
  r_pickups: string[];
};

export type SenateResponse = {
  environment: number;
  sliders: SliderValues;
  axis_weight: number;
  uniform_swing: number;
  trend_discount: number;
  summary: SenateSummary;
  seats: SenateSeat[];
};
