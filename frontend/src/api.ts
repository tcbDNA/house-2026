import type { ProjectResponse, SenateResponse, SliderValues } from "./types";

export async function fetchProjection(
  environment: number,
  sliders: SliderValues,
  trendDiscount: number,
  signal?: AbortSignal,
): Promise<ProjectResponse> {
  const res = await fetch("/api/project", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ environment, sliders, trend_discount: trendDiscount }),
    signal,
  });
  if (!res.ok) throw new Error(`projection failed: ${res.status}`);
  return res.json();
}

export async function fetchDistrict(id: string): Promise<Record<string, unknown>> {
  const res = await fetch(`/api/district/${id}`);
  if (!res.ok) throw new Error(`district ${id} failed: ${res.status}`);
  return res.json();
}

export type CountyResponse = {
  environment: number;
  state: string;
  uniform_swing: number;
  trend_discount: number;
  axis_weight: number;
  turnout_ratio_2026: number;
  unavailable_reason?: string;
  counties: Array<{
    fips: string;
    state: string;
    name: string;
    margin_2024: number;
    margin_2020: number;
    rel_trend: number;
    rel_trend_applied: number;
    total_2024: number | null;
    estimated_turnout_2026: number;
    estimated_d_votes: number;
    estimated_r_votes: number;
    projection: number;
    demo_shift: number;
    race_shift: number;
    edu_shift: number;
    age_shift: number;
    is_tossup: boolean;
  }>;
};

export async function fetchCounties(
  state: string,
  environment: number,
  sliders: SliderValues,
  trendDiscount: number,
  signal?: AbortSignal,
): Promise<CountyResponse> {
  const res = await fetch(`/api/state/${state}/counties`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ environment, sliders, trend_discount: trendDiscount }),
    signal,
  });
  if (!res.ok) throw new Error(`county projection failed: ${res.status}`);
  return res.json();
}

export async function fetchCountyGeoJSON(state: string): Promise<any> {
  const res = await fetch(`/api/state/${state}/county_geojson`);
  if (!res.ok) throw new Error(`county geojson failed: ${res.status}`);
  return res.json();
}

export type DistrictCountyResponse = {
  district: string;
  state: string;
  district_projection: number;
  candidate_adj: number;
  reconcile: number;
  counties: Array<CountyResponse["counties"][number] & {
    overlap_fraction: number;
    fully_contained: boolean;
  }>;
};

export async function fetchDistrictCounties(
  districtId: string,
  environment: number,
  sliders: SliderValues,
  trendDiscount: number,
  signal?: AbortSignal,
): Promise<DistrictCountyResponse> {
  const res = await fetch(`/api/district/${districtId}/counties`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ environment, sliders, trend_discount: trendDiscount }),
    signal,
  });
  if (!res.ok) throw new Error(`district county overlay failed: ${res.status}`);
  return res.json();
}

export async function fetchSenate(
  environment: number,
  sliders: SliderValues,
  trendDiscount: number,
  signal?: AbortSignal,
): Promise<SenateResponse> {
  const res = await fetch("/api/senate/project", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ environment, sliders, trend_discount: trendDiscount }),
    signal,
  });
  if (!res.ok) throw new Error(`senate projection failed: ${res.status}`);
  return res.json();
}
