import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl, { Map as MLMap, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { fetchCounties, fetchCountyGeoJSON, fetchDistrict, fetchDistrictCounties, type CountyResponse } from "../api";
import { bucketLabel, formatProjection, type SliderValues } from "../types";

type DistrictExtras = { overlap_fraction: number; fully_contained: boolean };

type Props = {
  state: string;
  environment: number;
  sliders: SliderValues;
  trendDiscount: number;
  indWinner?: boolean;
  onClose: () => void;
  /** District-mode: when set, only show counties touching this district,
   *  with partial counties (overlap < 99%) rendered at reduced opacity and
   *  labeled with their overlap fraction in the popup. */
  district?: string;
};

const BASE_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

// County-level palette is share-based, mirroring Wikipedia's US-election maps:
// ColorBrewer "Blues" and "Reds" 5-class sequential ramps. Tiers by winner's
// vote share:
//   50-60% → tier 1 (lightest)   |margin| 0-20
//   60-70% → tier 2              |margin| 20-40
//   70-80% → tier 3              |margin| 40-60
//   80-90% → tier 4              |margin| 60-80
//   >90%   → tier 5 (darkest)    |margin| >80
const PALETTE = {
  // Blues (D ramp) — share bins 50-60 → 90-100
  dem1: "#7996e2", dem2: "#6674de", dem3: "#584cde", dem4: "#3933e5", dem5: "#0d0596",
  // Reds (R ramp) — share bins 50-60 → 90-100
  rep1: "#e27f7f", rep2: "#d75d5d", rep3: "#d72f30", rep4: "#c21b18", rep5: "#a80000",
  // Grey ramp for Independent winners (caucus-with-D).
  ind1: "#d9d9d9", ind2: "#bdbdbd", ind3: "#737373", ind4: "#525252", ind5: "#252525",
  empty: "#d6d6d6",
};

function bucketColor(proj: number, indWinner = false): string {
  const a = Math.abs(proj);
  if (indWinner && proj > 0) {
    if (a > 80) return PALETTE.ind5;
    if (a > 60) return PALETTE.ind4;
    if (a > 40) return PALETTE.ind3;
    if (a > 20) return PALETTE.ind2;
    return PALETTE.ind1;
  }
  if (proj > 0) {
    if (a > 80) return PALETTE.dem5;
    if (a > 60) return PALETTE.dem4;
    if (a > 40) return PALETTE.dem3;
    if (a > 20) return PALETTE.dem2;
    return PALETTE.dem1;
  }
  if (a > 80) return PALETTE.rep5;
  if (a > 60) return PALETTE.rep4;
  if (a > 40) return PALETTE.rep3;
  if (a > 20) return PALETTE.rep2;
  return PALETTE.rep1;
}

function signed(n: number | null | undefined): string {
  if (n == null) return "—";
  const r = Math.round(n * 10) / 10;
  return (r > 0 ? "+" : r < 0 ? "" : "+") + r.toFixed(1);
}

function popupHtml(c: CountyResponse["counties"][number] & Partial<DistrictExtras>): string {
  const row = (label: string, value: number | null | undefined, bold = false) => {
    if (value == null) return "";
    const v = signed(value);
    const colored = (value as number) > 0 ? "color:#1e40af" : (value as number) < 0 ? "color:#9b1c1c" : "color:#666";
    const style = bold ? "font-weight:700;border-top:1px solid #ccc;padding-top:2px;margin-top:2px;" : "";
    const tag = bold
      ? `<span style="color:#666;font-weight:500;font-size:10px;margin-left:6px">(${bucketLabel(value)})</span>`
      : "";
    return `<div style="display:flex;justify-content:space-between;gap:8px;${style}"><span style="color:#555">${label}${tag}</span><span style="font-family:ui-monospace,monospace;${colored}">${v}</span></div>`;
  };
  const fmtN = (n: number) => n.toLocaleString();
  const partialBadge = (c.fully_contained === false && c.overlap_fraction != null)
    ? `<div style="color:#92400e;font-size:10px;margin-bottom:2px;background:#fef3c7;border:1px solid #fde68a;padding:1px 4px;border-radius:3px;display:inline-block">partial — ${(c.overlap_fraction * 100).toFixed(0)}% of county area in district</div>`
    : "";
  return `<div style="font:11px ui-sans-serif,system-ui;line-height:1.35;min-width:200px">
    <div style="margin-bottom:3px"><b>${c.name}</b> · <span style="color:#777">${c.state}</span></div>
    ${partialBadge}
    ${row("2024 margin", c.margin_2024)}
    ${row("+ rel. trend", c.rel_trend_applied)}
    ${row("+ demographic Δ", c.demo_shift)}
    ${row("= projection", c.projection, true)}
    <div style="margin-top:4px;padding-top:3px;border-top:1px solid #ccc;font-size:10px">
      <div style="color:#555;margin-bottom:1px">Estimated 2026 vote</div>
      <div style="display:flex;justify-content:space-between;gap:8px;">
        <span style="color:#1e40af">D ${fmtN(c.estimated_d_votes)}</span>
        <span style="color:#9b1c1c">R ${fmtN(c.estimated_r_votes)}</span>
      </div>
      <div style="color:#888">turnout ~${fmtN(c.estimated_turnout_2026)} (2024 was ${fmtN(c.total_2024 ?? 0)})</div>
    </div>
  </div>`;
}

export function CountyMap({ state, environment, sliders, trendDiscount, indWinner, onClose, district }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MLMap | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const [data, setData] = useState<CountyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showLabels, setShowLabels] = useState(false);
  const [districtDetail, setDistrictDetail] = useState<Record<string, any> | null>(null);
  const [showDetails, setShowDetails] = useState(true);
  const isLoadedRef = useRef(false);
  // The map's load callback is registered once but may fire before or after
  // the first data fetch resolves. Keep a ref so the callback always reads
  // the latest counties when building the fill-color expression.
  const dataRef = useRef<CountyResponse | null>(null);
  dataRef.current = data;

  // Fetch projection data on slider/env change. Branch to district endpoint
  // when in district mode so we only get counties touching that district.
  useEffect(() => {
    const ac = new AbortController();
    const fetcher = district
      ? fetchDistrictCounties(district, environment, sliders, trendDiscount, ac.signal)
          .then((d) => ({
            ...d,
            // Reshape so the rest of the map machinery (which expects CountyResponse)
            // works unchanged.
            uniform_swing: 0, axis_weight: 0, turnout_ratio_2026: 0,
          }) as unknown as CountyResponse)
      : fetchCounties(state, environment, sliders, trendDiscount, ac.signal);
    fetcher
      .then(setData)
      .catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ac.abort();
  }, [state, environment, sliders, trendDiscount, district]);

  // Fetch district detail (demographics, model inputs) when in district mode.
  useEffect(() => {
    setDistrictDetail(null);
    if (!district) return;
    fetchDistrict(district).then(setDistrictDetail).catch(console.error);
  }, [district]);

  // Build fips → county lookup for color expression
  const byFips = useMemo(() => {
    const m = new Map<string, CountyResponse["counties"][number]>();
    if (data) for (const c of data.counties) m.set(c.fips, c);
    return m;
  }, [data]);

  function buildFillColorExpr(): any {
    const d = dataRef.current;
    if (!d) return PALETTE.empty;
    const expr: any[] = ["match", ["get", "fips"]];
    for (const c of d.counties) {
      expr.push(c.fips, bucketColor(c.projection, indWinner));
    }
    // In district mode, counties not in the district stay grey instead of fading
    // into the state baseline; in state mode this branch never fires because
    // every county appears in d.counties.
    expr.push(PALETTE.empty);
    return expr;
  }

  // In district mode, fade out counties not in the district (so the district
  // shape is visually obvious) and reduce opacity for partial-overlap counties
  // proportionally to how little of them sits in the district.
  function buildFillOpacityExpr(): any {
    const d = dataRef.current;
    if (!d || !district) return 0.75;
    const expr: any[] = ["match", ["get", "fips"]];
    for (const c of d.counties as Array<CountyResponse["counties"][number] & Partial<DistrictExtras>>) {
      // Fully contained → full opacity; partials scale to 0.25..0.6 based on share.
      const op = c.fully_contained
        ? 0.78
        : Math.max(0.28, Math.min(0.65, (c.overlap_fraction ?? 0.5) * 0.7 + 0.18));
      expr.push(c.fips, op);
    }
    expr.push(0.05);  // out-of-district counties: nearly invisible
    return expr;
  }

  function buildLabelExpr(): any {
    const d = dataRef.current;
    if (!d) return "";
    const expr: any[] = ["match", ["get", "fips"]];
    for (const c of d.counties) {
      const r = Math.round(c.projection);
      const label = r > 0 ? `D+${r}` : r < 0 ? `R+${-r}` : "EVEN";
      expr.push(c.fips, label);
    }
    expr.push("");
    return expr;
  }

  function buildFlipFilter(): any {
    const d = dataRef.current;
    if (!d) return ["==", ["get", "fips"], "__none__"];
    const flipped = d.counties
      .filter((c) => {
        const m = c.margin_2024 ?? 0;
        return (c.projection > 0 && m < 0) || (c.projection < 0 && m > 0);
      })
      .map((c) => c.fips);
    if (flipped.length === 0) return ["==", ["get", "fips"], "__none__"];
    return ["in", ["get", "fips"], ["literal", flipped]];
  }

  function makeHashPattern(tile = 18): ImageData {
    // Softer hatch than the Senate map: single diagonal stripe per tile,
    // thinner line, lower opacity. The layer's fill-opacity is also reduced.
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = tile;
    const ctx = canvas.getContext("2d")!;
    ctx.clearRect(0, 0, tile, tile);
    ctx.strokeStyle = "rgba(0,0,0,0.30)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-2, tile + 2); ctx.lineTo(tile + 2, -2);
    ctx.stroke();
    return ctx.getImageData(0, 0, tile, tile);
  }

  // Initialize map once
  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASE_STYLE,
      center: [-96.5, 38.5],
      zoom: 3.5,
      minZoom: 1.5,
      maxZoom: 12,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", async () => {
      try {
        const gj = await fetchCountyGeoJSON(state);
        map.addSource("counties", { type: "geojson", data: gj, promoteId: "fips" });
        map.addLayer({
          id: "county-fill",
          type: "fill",
          source: "counties",
          paint: { "fill-color": buildFillColorExpr(), "fill-opacity": buildFillOpacityExpr() },
        });
        // Crosshatch overlay for flipped counties (projection sign ≠ 2024 margin sign).
        const hashImg = makeHashPattern(14);
        if (!map.hasImage("flip-hash-counties")) {
          map.addImage("flip-hash-counties", hashImg, { pixelRatio: 2 });
        }
        map.addLayer({
          id: "county-flips",
          type: "fill",
          source: "counties",
          paint: { "fill-pattern": "flip-hash-counties", "fill-opacity": 0.55 },
          filter: buildFlipFilter(),
        });
        map.addLayer({
          id: "county-border",
          type: "line",
          source: "counties",
          paint: { "line-color": "#1f2937", "line-width": 0.8, "line-opacity": 0.85 },
        });
        map.addLayer({
          id: "county-labels",
          type: "symbol",
          source: "counties",
          layout: {
            "text-field": buildLabelExpr(),
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-size": ["interpolate", ["linear"], ["zoom"], 4, 9, 6, 11, 8, 13, 10, 15],
            "text-allow-overlap": false,
            "text-ignore-placement": false,
            "symbol-placement": "point",
            "visibility": showLabelsRef.current ? "visible" : "none",
          },
          paint: {
            "text-color": "#ffffff",
            "text-halo-color": "rgba(0,0,0,0.55)",
            "text-halo-width": 1.2,
          },
        });
        // Fit to bounds — in district mode, fit only the in-district counties;
        // in state mode fit the whole state.
        const inDistrictFips = district && dataRef.current
          ? new Set(dataRef.current.counties.map((c) => c.fips))
          : null;
        const bounds = new maplibregl.LngLatBounds();
        for (const f of gj.features) {
          if (inDistrictFips && !inDistrictFips.has((f.properties as any).fips)) continue;
          const geom = f.geometry;
          const coords = geom.type === "Polygon" ? geom.coordinates : geom.coordinates.flat();
          for (const ring of coords) {
            for (const [lng, lat] of ring) bounds.extend([lng, lat]);
          }
        }
        if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 30, animate: false });

        map.on("mousemove", "county-fill", (e) => {
          if (!e.features?.[0]) return;
          map.getCanvas().style.cursor = "pointer";
          const fips = (e.features[0].properties as any).fips;
          const c = byFipsRef.current.get(fips);
          if (!c) return;
          if (!popupRef.current) popupRef.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
          popupRef.current.setLngLat(e.lngLat).setHTML(popupHtml(c)).addTo(map);
        });
        map.on("mouseleave", "county-fill", () => {
          map.getCanvas().style.cursor = "";
          popupRef.current?.remove();
        });
        isLoadedRef.current = true;
        // Safety re-apply in case data arrived during load.
        if (dataRef.current && map.getLayer("county-fill")) {
          map.setPaintProperty("county-fill", "fill-color", buildFillColorExpr());
          map.setFilter("county-flips", buildFlipFilter());
          map.setLayoutProperty("county-labels", "text-field", buildLabelExpr());
        }
      } catch (e: any) {
        setError(e.message);
      }
    });

    return () => { map.remove(); mapRef.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  // Refresh fill colors when data changes
  const byFipsRef = useRef(byFips);
  byFipsRef.current = byFips;
  const showLabelsRef = useRef(showLabels);
  showLabelsRef.current = showLabels;
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current || !data) return;
    if (map.getLayer("county-fill")) {
      map.setPaintProperty("county-fill", "fill-color", buildFillColorExpr());
      map.setPaintProperty("county-fill", "fill-opacity", buildFillOpacityExpr());
    }
    if (map.getLayer("county-flips")) {
      map.setFilter("county-flips", buildFlipFilter());
    }
    if (map.getLayer("county-labels")) {
      map.setLayoutProperty("county-labels", "text-field", buildLabelExpr());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, indWinner]);

  // Toggle label visibility without rebuilding the layer
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current) return;
    if (map.getLayer("county-labels")) {
      map.setLayoutProperty("county-labels", "visibility", showLabels ? "visible" : "none");
    }
  }, [showLabels]);

  // Summary stats — aggregate county vote estimates into a statewide projection.
  const summary = useMemo(() => {
    if (!data) return null;
    const d_counties = data.counties.filter((c) => c.projection > 0).length;
    const r_counties = data.counties.length - d_counties;
    const flips_to_d_names = data.counties
      .filter((c) => c.projection > 0 && (c.margin_2024 ?? 0) <= 0)
      .map((c) => c.name);
    const flips_to_r_names = data.counties
      .filter((c) => c.projection < 0 && (c.margin_2024 ?? 0) > 0)
      .map((c) => c.name);
    const d_total = data.counties.reduce((s, c) => s + (c.estimated_d_votes || 0), 0);
    const r_total = data.counties.reduce((s, c) => s + (c.estimated_r_votes || 0), 0);
    const turnout_total = d_total + r_total;
    const state_margin = turnout_total > 0 ? 100 * (d_total - r_total) / turnout_total : 0;
    return {
      total: data.counties.length, d_counties, r_counties,
      flips_to_d_names, flips_to_r_names,
      d_total, r_total, turnout_total, state_margin,
    };
  }, [data]);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className={`bg-white rounded-lg shadow-xl w-full ${district ? "max-w-6xl" : "max-w-5xl"} max-h-[90vh] flex flex-col`} onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold">{district ? `${district} · County overlay` : `${state} · County projections`}</h2>
            {district && districtDetail && (
              <div className="text-xs mt-0.5">
                <span className={districtDetail.party === "(D)" ? "text-blue-700" : districtDetail.party === "(R)" ? "text-red-700" : "text-slate-600"}>
                  {districtDetail.incumbent}
                </span>{" "}
                <span className="text-slate-400">{districtDetail.party}</span>
                {(data as any)?.district_projection != null && (
                  <span className="ml-2">
                    <span className="text-slate-500">· projection </span>
                    <span className={`font-mono font-semibold ${(data as any).district_projection > 0 ? "text-blue-700" : "text-red-700"}`}>
                      {formatProjection((data as any).district_projection)}
                    </span>
                  </span>
                )}
              </div>
            )}
            {!district && summary && (
              <>
                <div className="text-xs text-slate-500 mt-0.5">
                  {summary.total} counties · <span className="text-blue-700">{summary.d_counties} D</span> · <span className="text-red-700">{summary.r_counties} R</span>
                  {summary.flips_to_d_names.length > 0 && (
                    <> · <span className="text-blue-700">{summary.flips_to_d_names.length} flip→D ({summary.flips_to_d_names.join(", ")})</span></>
                  )}
                  {summary.flips_to_r_names.length > 0 && (
                    <> · <span className="text-red-700">{summary.flips_to_r_names.length} flip→R ({summary.flips_to_r_names.join(", ")})</span></>
                  )}
                </div>
                <div className="text-xs mt-1">
                  <span className="text-slate-500">Statewide estimate: </span>
                  <span className="text-blue-700 font-mono">
                    {summary.d_total.toLocaleString()} D
                    {summary.turnout_total > 0 && ` (${(100 * summary.d_total / summary.turnout_total).toFixed(1)}%)`}
                  </span>
                  <span className="text-slate-400"> vs </span>
                  <span className="text-red-700 font-mono">
                    {summary.r_total.toLocaleString()} R
                    {summary.turnout_total > 0 && ` (${(100 * summary.r_total / summary.turnout_total).toFixed(1)}%)`}
                  </span>
                  <span className={`ml-2 font-mono font-semibold ${summary.state_margin > 0 ? "text-blue-700" : summary.state_margin < 0 ? "text-red-700" : "text-slate-700"}`}>
                    ({summary.state_margin > 0 ? "D+" : "R+"}{Math.abs(summary.state_margin).toFixed(1)})
                  </span>
                  <span className="text-slate-400 ml-1">· total ~{summary.turnout_total.toLocaleString()} votes</span>
                </div>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {district && (
              <button
                onClick={() => setShowDetails((v) => !v)}
                className="text-xs px-2 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-700"
              >
                {showDetails ? "Hide details" : "Show details"}
              </button>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-2xl leading-none">×</button>
          </div>
        </div>
        {error && <div className="m-3 p-3 bg-red-100 text-red-800 text-sm rounded">{error}</div>}
        {data?.unavailable_reason && (
          <div className="m-3 p-3 bg-amber-50 text-amber-900 text-sm rounded border border-amber-200">
            {data.unavailable_reason}
          </div>
        )}
        <div className={`flex-1 min-h-[60vh] flex ${district && showDetails ? "flex-row" : ""}`}>
        <div className="relative flex-1 min-h-[60vh]">
          <div ref={containerRef} className="absolute inset-0" />
          {/* Margin-label toggle */}
          <button
            onClick={() => setShowLabels((v) => !v)}
            className={`absolute top-2 left-2 px-2 py-1 text-[11px] rounded shadow border ${
              showLabels
                ? "bg-slate-800 text-white border-slate-800"
                : "bg-white/95 text-slate-700 border-slate-300 hover:bg-slate-50"
            }`}
          >
            {showLabels ? "Hide margins" : "Show margins"}
          </button>
          {/* Legend: diverging 5-tier ramp keyed to winner vote share. */}
          <div className="absolute bottom-2 left-2 bg-white/95 border rounded shadow px-2 py-1.5 text-[10px] pointer-events-none">
            <div className="flex items-center gap-px">
              {[PALETTE.rep5, PALETTE.rep4, PALETTE.rep3, PALETTE.rep2, PALETTE.rep1,
                PALETTE.dem1, PALETTE.dem2, PALETTE.dem3, PALETTE.dem4, PALETTE.dem5]
                .map((c, i) => (
                  <span key={i} style={{ background: c }} className="inline-block w-5 h-3" />
                ))}
            </div>
            <div className="flex justify-between mt-0.5 font-mono text-slate-600">
              <span>R&gt;90</span>
              <span className="text-red-700">·</span>
              <span>R 50</span>
              <span className="text-blue-700">·</span>
              <span>D 50</span>
              <span className="text-blue-700">·</span>
              <span>D&gt;90</span>
            </div>
            <div className="text-slate-500 mt-0.5">
              Bands: 50-60 · 60-70 · 70-80 · 80-90 · &gt;90 vote share
            </div>
            {indWinner && (
              <div className="flex items-center gap-1 mt-1 pt-1 border-t text-slate-600">
                {[PALETTE.ind1, PALETTE.ind2, PALETTE.ind3, PALETTE.ind4, PALETTE.ind5]
                  .map((c, i) => (
                    <span key={i} style={{ background: c }} className="inline-block w-5 h-3" />
                  ))}
                <span className="ml-1 text-[9px]">Independent-winning counties</span>
              </div>
            )}
          </div>
        </div>
        {district && showDetails && (
          <DistrictDetailPanel
            district={district}
            detail={districtDetail}
            districtProjection={(data as any)?.district_projection}
            trendDiscount={trendDiscount}
          />
        )}
        </div>
      </div>
    </div>
  );
}

function DistrictDetailPanel({
  district, detail, districtProjection, trendDiscount,
}: {
  district: string;
  detail: Record<string, any> | null;
  districtProjection: number | undefined;
  trendDiscount: number;
}) {
  const d = detail ?? {};
  const m24 = d.margin_2024 ?? 0;
  const relTrendRaw = d.rel_trend ?? 0;
  const relTrendApplied = relTrendRaw * trendDiscount;
  const war = d.war_adj_discounted ?? 0;
  const inc = d.incumbency_adj ?? 0;
  const chal = d.challenger_adj ?? 0;
  const demo = d.demo_shift ?? 0;
  // Uniform swing is whatever's left after the additive components — derived
  // from the projection so we don't have to know the model's popvote constant.
  const uniformSwing = districtProjection != null
    ? districtProjection - (m24 + relTrendApplied + war + inc + chal + demo)
    : null;
  return (
    <div className="w-72 shrink-0 border-l overflow-y-auto bg-slate-50 p-3 space-y-3 text-xs">
      <div>
        <div className="font-mono font-bold text-base">{district}</div>
        {d.challenger && (() => {
          const isOpen = (d.incumbent ?? "").startsWith("(open");
          return (
            <div className="mt-0.5">
              <span className="text-slate-500">
                {isOpen ? `${d.challenger_party} nominee: ` : "vs "}
              </span>
              <span className={d.challenger_party === "(D)" ? "text-blue-700 font-medium" : d.challenger_party === "(R)" ? "text-red-700 font-medium" : "text-slate-700 font-medium"}>
                {d.challenger}
              </span>
            </div>
          );
        })()}
        <div className="text-slate-500 mt-1">Lines: {d.lines ?? "—"}</div>
      </div>

      <section>
        <h3 className="uppercase text-[10px] tracking-wide text-slate-500 font-semibold mb-1">Projection breakdown</h3>
        <div className="space-y-0.5 font-mono">
          <SignedRow label="2024 margin" value={m24} leading />
          <SignedRow
            label={`Rel. trend × ${trendDiscount.toFixed(1)}`}
            value={relTrendApplied}
            note={Math.abs(trendDiscount - 1) > 1e-6 ? `raw ${relTrendRaw.toFixed(2)}` : undefined}
          />
          <SignedRow label="WAR" value={war} />
          <SignedRow label="Incumbency" value={inc} />
          <SignedRow label="Challenger" value={chal} />
          <SignedRow label="Demo shift" value={demo} />
          {uniformSwing != null && (
            <SignedRow label="Uniform swing (env)" value={uniformSwing} />
          )}
          {districtProjection != null && (
            <div className="flex justify-between border-t border-slate-300 pt-1 mt-1 font-semibold">
              <span className="text-slate-700 font-sans">= Projection</span>
              <span className={districtProjection > 0 ? "text-blue-700" : districtProjection < 0 ? "text-red-700" : "text-slate-700"}>
                {formatProjection(districtProjection)}
              </span>
            </div>
          )}
        </div>
      </section>

      <section>
        <h3 className="uppercase text-[10px] tracking-wide text-slate-500 font-semibold mb-1">Demographics</h3>
        <div className="space-y-0.5 font-mono">
          <Row label="White (NH)" value={d.pct_white_nh} suffix="%" />
          <Row label="Black" value={d.pct_black} suffix="%" />
          <Row label="Hispanic" value={d.pct_hispanic} suffix="%" />
          <Row label="Asian" value={d.pct_asian} suffix="%" />
          <Row label="College+" value={d.pct_college} suffix="%" />
          <Row label="W college" value={d.pct_white_nh_college} suffix="%" />
          <Row label="W non-college" value={d.pct_white_nh_non_college} suffix="%" />
          <Row label="NW college" value={d.pct_nonwhite_college} suffix="%" />
          <Row label="NW non-college" value={d.pct_nonwhite_non_college} suffix="%" />
          <Row label="Under 30" value={d.pct_under_30} suffix="%" />
          <Row label="65+" value={d.pct_65_plus} suffix="%" />
          <Row label="Median age" value={d.median_age} suffix=" yr" />
          {d.median_income != null && (
            <div className="flex justify-between border-b border-slate-200 py-0.5">
              <span className="text-slate-600">Median income</span>
              <span>${Math.round(d.median_income / 1000)}k</span>
            </div>
          )}
        </div>
        <div className="text-[10px] text-slate-400 mt-1">
          Source: {d.demo_source ?? "—"}
        </div>
      </section>
    </div>
  );
}

function SignedRow({ label, value, leading, note }: {
  label: string; value: number; leading?: boolean; note?: string;
}) {
  // `leading` row: 2024 margin — show as +12.3 / -12.3 with no operator prefix.
  // Other rows: show as "+ 1.20" / "− 1.20" with the operator separated for clarity.
  const abs = Math.abs(value);
  const color = value > 0 ? "text-blue-700" : value < 0 ? "text-red-700" : "text-slate-500";
  if (leading) {
    return (
      <div className="flex justify-between py-0.5">
        <span className="text-slate-700 font-sans">{label}</span>
        <span className={color}>{(value > 0 ? "+" : value < 0 ? "−" : "")}{abs.toFixed(2)}</span>
      </div>
    );
  }
  const op = value >= 0 ? "+" : "−";
  return (
    <div className="flex justify-between py-0.5">
      <span className="text-slate-600 font-sans">
        {label}
        {note && <span className="text-[10px] text-slate-400 ml-1 font-mono">({note})</span>}
      </span>
      <span className={color}>{op} {abs.toFixed(2)}</span>
    </div>
  );
}

function Row({ label, value, suffix }: { label: string; value: number | null | undefined; suffix?: string }) {
  if (value == null) {
    return (
      <div className="flex justify-between border-b border-slate-200 py-0.5">
        <span className="text-slate-600">{label}</span>
        <span className="text-slate-300">—</span>
      </div>
    );
  }
  const display = suffix === "%" ? `${value}%`
    : suffix ? `${value}${suffix}`
    : (value > 0 ? "+" : "") + value.toFixed(2);
  const color = !suffix
    ? (value > 0 ? "text-blue-700" : value < 0 ? "text-red-700" : "text-slate-700")
    : "text-slate-700";
  return (
    <div className="flex justify-between border-b border-slate-200 py-0.5">
      <span className="text-slate-600 font-sans">{label}</span>
      <span className={color}>{display}</span>
    </div>
  );
}
