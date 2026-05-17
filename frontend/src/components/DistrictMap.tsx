import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { bucketLabel, partyColorHex, partyTag, type District } from "../types";

type Props = {
  districts: District[];
  uniformSwing: number;   // env − HOUSE_2024_POPVOTE, in margin pts
  onPick?: (id: string) => void;
  selected?: string | null;
};

const BASE_STYLE =
  "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

// 8-bucket diverging palette (must match Tailwind theme in tailwind.config.js)
const PALETTE = {
  dem5: "#0b3d91",  // D+15 and up
  dem4: "#1f6fdc",  // D+8..15
  dem3: "#5aa1ec",  // D+3..8
  dem2: "#a8cbf2",  // 0..3
  rep2: "#f4a8a8",  // -3..0
  rep3: "#ea6f6f",  // -8..-3
  rep4: "#d33b3b",  // -15..-8
  rep5: "#8c1d1d",  // worse than -15
};

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
function bucketColor(proj: number): string {
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
  if (n == null) return "0.0";
  const r = Math.round(n * 10) / 10;
  return (r > 0 ? "+" : r < 0 ? "" : "+") + r.toFixed(1);
}

function buildPopupHtml(d: District, uniformSwing: number): string {
  const m24 = d.margin_2024 ?? 0;
  // Use the discounted value so the tooltip reflects the active trend_discount.
  const trend = d.rel_trend_applied ?? d.rel_trend ?? 0;
  const war = d.war_adj_discounted ?? 0;
  const inc = d.incumbency_adj ?? 0;
  const ch = d.challenger_adj ?? 0;
  const demo = d.demo_shift ?? 0;
  const proj = d.projection;

  const row = (label: string, value: number, isResult = false) => {
    const v = signed(value);
    const colored =
      value > 0 ? "color:#1e40af" : value < 0 ? "color:#9b1c1c" : "color:#666";
    const bold = isResult ? "font-weight:700;border-top:1px solid #ccc;padding-top:2px;margin-top:2px;" : "";
    const tag = isResult
      ? `<span style="color:#666;font-weight:500;font-size:10px;margin-left:6px">(${bucketLabel(value)})</span>`
      : "";
    return `<div style="display:flex;justify-content:space-between;gap:8px;${bold}">
              <span style="color:#555">${label}${tag}</span>
              <span style="font-family:ui-monospace,monospace;${colored}">${v}</span>
            </div>`;
  };

  const flipRow = d.flip
    ? `<div style="color:${d.flip === "to_D" ? "#1e40af" : "#9b1c1c"};font-weight:600;margin-top:2px">flip → ${d.flip === "to_D" ? "D" : "R"}</div>`
    : "";

  const incColor = partyColorHex(d.party);
  const chColor = partyColorHex(d.challenger_party);
  // Only show the source tag for special cases ("manual", "skipped ..."):
  // year/geography provenance is internal noise; named-nominee placeholder
  // ("wikipedia") is implicit.
  const src = d.challenger_war_source;
  const showSrc = src && (src === "manual" || src.endsWith("rematch"));
  const sourceTag = showSrc
    ? `<span style="color:#888;font-size:9px"> · ${src}</span>`
    : "";
  // Open seat: no incumbent → reframe "challenger" as the party's nominee
  // (both nominees are non-incumbents in an open race).
  const isOpen = (d.incumbent ?? "").startsWith("(open");
  const candPrefix = isOpen
    ? `<span style="color:#666">${d.challenger_party ?? ""} nominee: </span>`
    : `<span style="color:#666">vs </span>`;
  const challengerLine = d.challenger
    ? `<div style="margin-bottom:3px">${candPrefix}<b style="color:${chColor}">${d.challenger}</b>${isOpen ? "" : ` <span style="color:#888">${d.challenger_party ?? ""}</span>`}${sourceTag}</div>`
    : "";

  // Always show all rows — keep zeros visible so the projection arithmetic
  // is fully transparent regardless of whether candidate info exists.
  const challengerRowLabel = isOpen ? "+ nominee WAR" : "+ challenger";

  return `<div style="font:11px ui-sans-serif,system-ui;line-height:1.35;min-width:180px">
    <div style="margin-bottom:3px"><b>${d.district}</b> · <span style="color:${incColor}">${d.incumbent ?? ""}</span> <span style="color:#888">${partyTag(d.party, !!d.incumbency_adj)}</span></div>
    ${challengerLine}
    ${row("2024 margin", m24)}
    ${row("+ rel. trend", trend)}
    ${row("+ WAR adj", war)}
    ${row("+ incumbency", inc)}
    ${row(challengerRowLabel, ch)}
    ${row("+ uniform swing", uniformSwing)}
    ${row("+ demographic Δ", demo)}
    ${row("= projection", proj, true)}
    ${flipRow}
  </div>`;
}

export function DistrictMap({ districts, uniformSwing, onPick, selected }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MLMap | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const districtsRef = useRef<District[]>(districts);
  const swingRef = useRef<number>(uniformSwing);
  const isLoadedRef = useRef(false);

  districtsRef.current = districts;
  swingRef.current = uniformSwing;

  // Build the data-driven fill-color expression for setPaintProperty
  function buildFillColorExpr(): any {
    const expr: any[] = ["match", ["get", "district"]];
    for (const d of districtsRef.current) {
      expr.push(d.district, bucketColor(d.projection));
    }
    expr.push("#cccccc");
    return expr;
  }

  // Filter expression matching only districts whose flip is non-null
  function buildFlipFilter(): any {
    const ids = districtsRef.current.filter((d) => d.flip).map((d) => d.district);
    if (ids.length === 0) return ["==", ["get", "district"], "__none__"];
    return ["in", ["get", "district"], ["literal", ids]];
  }

  // Build a tile-sized canvas of diagonal hash lines for fill-pattern
  function makeHashPattern(tile = 18): ImageData {
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

  // Init map once
  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASE_STYLE,
      center: [-96.5, 38.5],
      zoom: 3.4,
      minZoom: 2.5,
      maxZoom: 12,
      attributionControl: { compact: true },
    });
    mapRef.current = map;

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", () => {
      map.addSource("districts", {
        type: "geojson",
        data: "/districts.geojson",
        promoteId: "district",
      });

      map.addLayer({
        id: "district-fill",
        type: "fill",
        source: "districts",
        paint: {
          "fill-color": buildFillColorExpr(),
          "fill-opacity": 0.62,
        },
      });

      // Register hash pattern and add the flip overlay layer
      const hashImg = makeHashPattern(18);
      if (!map.hasImage("flip-hash")) {
        map.addImage("flip-hash", hashImg, { pixelRatio: 2 });
      }
      map.addLayer({
        id: "district-flips",
        type: "fill",
        source: "districts",
        paint: {
          "fill-pattern": "flip-hash",
          "fill-opacity": 0.55,
        },
        filter: buildFlipFilter(),
      });

      map.addLayer({
        id: "district-line",
        type: "line",
        source: "districts",
        paint: {
          "line-color": "#3a3a3a",
          "line-width": 0.35,
        },
      });

      // hover highlight (single feature filter)
      map.addLayer({
        id: "district-hover",
        type: "line",
        source: "districts",
        paint: { "line-color": "#111", "line-width": 1.8 },
        filter: ["==", ["get", "district"], ""],
      });

      // selected highlight
      map.addLayer({
        id: "district-selected",
        type: "line",
        source: "districts",
        paint: { "line-color": "#fbbf24", "line-width": 2.5 },
        filter: ["==", ["get", "district"], ""],
      });

      isLoadedRef.current = true;

      // hover popup
      popupRef.current = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 8,
      });
      map.getCanvas().style.cursor = "default";

      map.on("mousemove", "district-fill", (e) => {
        if (!e.features?.length) return;
        const id = e.features[0].properties?.district as string;
        map.setFilter("district-hover", ["==", ["get", "district"], id]);
        map.getCanvas().style.cursor = "pointer";
        const d = districtsRef.current.find((dd) => dd.district === id);
        if (popupRef.current && d) {
          popupRef.current.setLngLat(e.lngLat).setHTML(buildPopupHtml(d, swingRef.current)).addTo(map);
        }
      });

      map.on("mouseleave", "district-fill", () => {
        map.setFilter("district-hover", ["==", ["get", "district"], ""]);
        map.getCanvas().style.cursor = "default";
        popupRef.current?.remove();
      });

      map.on("click", "district-fill", (e) => {
        if (!e.features?.length) return;
        const id = e.features[0].properties?.district as string;
        onPick?.(id);
      });
    });

    return () => {
      popupRef.current?.remove();
      map.remove();
      mapRef.current = null;
      isLoadedRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Update fill colors + flip overlay when projection results change
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current) return;
    map.setPaintProperty("district-fill", "fill-color", buildFillColorExpr());
    map.setFilter("district-flips", buildFlipFilter());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [districts]);

  // Update selected highlight
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current) return;
    map.setFilter("district-selected", ["==", ["get", "district"], selected ?? ""]);
  }, [selected]);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden relative">
      <div ref={containerRef} className="w-full h-[600px]" />
      <div className="absolute bottom-2 left-2 bg-white/95 rounded shadow px-2 py-1.5 text-[10px] leading-tight font-mono">
        <div className="font-sans font-semibold text-[10px] mb-1">Projected D-R margin</div>
        <div className="flex items-center gap-0">
          {Object.values(PALETTE).map((c, i) => (
            <span key={i} className="inline-block w-5 h-3" style={{ background: c }} />
          ))}
        </div>
        <div className="flex justify-between mt-0.5">
          <span>R+15</span><span>tie</span><span>D+15</span>
        </div>
        <div className="font-sans mt-1.5 flex items-center gap-1.5">
          <span
            className="inline-block w-5 h-3 border border-slate-400"
            style={{
              backgroundImage:
                "repeating-linear-gradient(45deg, rgba(0,0,0,0.65), rgba(0,0,0,0.65) 1.5px, transparent 1.5px, transparent 4px)",
            }}
          />
          <span className="text-[10px] text-slate-700">flipped seat</span>
        </div>
      </div>
    </div>
  );
}
