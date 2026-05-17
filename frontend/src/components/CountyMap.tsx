import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl, { Map as MLMap, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { fetchCounties, fetchCountyGeoJSON, type CountyResponse } from "../api";
import { bucketLabel, type SliderValues } from "../types";

type Props = {
  state: string;
  environment: number;
  sliders: SliderValues;
  trendDiscount: number;
  indWinner?: boolean;
  onClose: () => void;
};

const BASE_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

const PALETTE = {
  dem5: "#0b3d91", dem4: "#1f6fdc", dem3: "#5aa1ec", dem2: "#a8cbf2",
  rep2: "#f4a8a8", rep3: "#ea6f6f", rep4: "#d33b3b", rep5: "#8c1d1d",
  // Grey scale for Independent winners (caucus-with-D). Applied to D-leaning
  // counties when the seat-level winner is an Independent.
  ind5: "#374151", ind4: "#525252", ind3: "#a3a3a3", ind2: "#d4d4d4",
  empty: "#d6d6d6",
};

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
function bucketColor(proj: number, indWinner = false): string {
  if (indWinner && proj > 0) {
    if (proj > 13) return PALETTE.ind5;
    if (proj > 7)  return PALETTE.ind4;
    if (proj > 3)  return PALETTE.ind3;
    return PALETTE.ind2;
  }
  if (proj > 13)  return PALETTE.dem5;
  if (proj > 7)   return PALETTE.dem4;
  if (proj > 3)   return PALETTE.dem3;
  if (proj > 0)   return PALETTE.dem2;
  if (proj > -3)  return PALETTE.rep2;
  if (proj > -7)  return PALETTE.rep3;
  if (proj > -13) return PALETTE.rep4;
  return PALETTE.rep5;
}

function signed(n: number | null | undefined): string {
  if (n == null) return "—";
  const r = Math.round(n * 10) / 10;
  return (r > 0 ? "+" : r < 0 ? "" : "+") + r.toFixed(1);
}

function popupHtml(c: CountyResponse["counties"][number]): string {
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
  return `<div style="font:11px ui-sans-serif,system-ui;line-height:1.35;min-width:200px">
    <div style="margin-bottom:3px"><b>${c.name}</b> · <span style="color:#777">${c.state}</span></div>
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

export function CountyMap({ state, environment, sliders, trendDiscount, indWinner, onClose }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MLMap | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const [data, setData] = useState<CountyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const isLoadedRef = useRef(false);
  // The map's load callback is registered once but may fire before or after
  // the first data fetch resolves. Keep a ref so the callback always reads
  // the latest counties when building the fill-color expression.
  const dataRef = useRef<CountyResponse | null>(null);
  dataRef.current = data;

  // Fetch projection data on slider/env change
  useEffect(() => {
    const ac = new AbortController();
    fetchCounties(state, environment, sliders, trendDiscount, ac.signal)
      .then(setData)
      .catch((e) => { if (e.name !== "AbortError") setError(e.message); });
    return () => ac.abort();
  }, [state, environment, sliders, trendDiscount]);

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
    expr.push(PALETTE.empty);
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
          paint: { "fill-color": buildFillColorExpr(), "fill-opacity": 0.75 },
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
        // Fit to state bounds
        const bounds = new maplibregl.LngLatBounds();
        for (const f of gj.features) {
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
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current || !data) return;
    if (map.getLayer("county-fill")) {
      map.setPaintProperty("county-fill", "fill-color", buildFillColorExpr());
    }
    if (map.getLayer("county-flips")) {
      map.setFilter("county-flips", buildFlipFilter());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, indWinner]);

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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold">{state} · County projections</h2>
            {summary && (
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
                  <span className="text-blue-700 font-mono">{summary.d_total.toLocaleString()} D</span>
                  <span className="text-slate-400"> vs </span>
                  <span className="text-red-700 font-mono">{summary.r_total.toLocaleString()} R</span>
                  <span className={`ml-2 font-mono font-semibold ${summary.state_margin > 0 ? "text-blue-700" : summary.state_margin < 0 ? "text-red-700" : "text-slate-700"}`}>
                    ({summary.state_margin > 0 ? "D+" : "R+"}{Math.abs(summary.state_margin).toFixed(1)})
                  </span>
                  <span className="text-slate-400 ml-1">· total ~{summary.turnout_total.toLocaleString()} votes</span>
                </div>
              </>
            )}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-2xl leading-none">×</button>
        </div>
        {error && <div className="m-3 p-3 bg-red-100 text-red-800 text-sm rounded">{error}</div>}
        {data?.unavailable_reason && (
          <div className="m-3 p-3 bg-amber-50 text-amber-900 text-sm rounded border border-amber-200">
            {data.unavailable_reason}
          </div>
        )}
        <div ref={containerRef} className="flex-1 min-h-[60vh]" />
      </div>
    </div>
  );
}
