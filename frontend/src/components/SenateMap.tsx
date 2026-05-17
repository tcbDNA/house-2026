import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Popup } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { bucketLabel, partyColorHex, partyTag, type SenateSeat } from "../types";

type Props = {
  seats: SenateSeat[];
  uniformSwing: number;
  onPickState?: (state: string) => void;
};

const BASE_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

const PALETTE = {
  dem5: "#0b3d91", dem4: "#1f6fdc", dem3: "#5aa1ec", dem2: "#a8cbf2",
  rep2: "#f4a8a8", rep3: "#ea6f6f", rep4: "#d33b3b", rep5: "#8c1d1d",
  // Grey ramp used when an Independent (caucusing with D for majority purposes)
  // is the projected winner.
  ind5: "#374151", ind4: "#525252", ind3: "#a3a3a3", ind2: "#d4d4d4",
  notUp: "#d6d6d6",
};

// Independent (caucus-with-D) candidates exist on the D side only in our data.
// They show as grey instead of blue when projected to win.
function isIndependentWinner(s: SenateSeat): boolean {
  if (s.projection <= 0) return false;
  return s.party === "(I)" || s.challenger_party === "(I)";
}

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
function bucketColor(proj: number, indWinner = false): string {
  if (indWinner) {
    const a = Math.abs(proj);
    if (a > 13) return PALETTE.ind5;
    if (a > 7)  return PALETTE.ind4;
    if (a > 3)  return PALETTE.ind3;
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

function buildPopupHtml(s: SenateSeat, uniformSwing: number): string {
  const row = (label: string, value: number | null | undefined, isResult = false) => {
    if (value == null) return "";
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
  const flipRow = s.flip
    ? `<div style="color:${s.flip === "to_D" ? "#1e40af" : "#9b1c1c"};font-weight:600;margin-top:2px">flip → ${s.flip === "to_D" ? "D" : "R"}</div>`
    : "";

  const incColor = partyColorHex(s.party);
  const chColor = partyColorHex(s.challenger_party);
  // Year/geography provenance is internal noise; suppress it. (No special tag
  // surfaces here today — Senate doesn't produce a "skipped" tag.)
  const sourceTag = "";
  // Open seat: both nominees are non-incumbents, so "vs" / "challenger" is the
  // wrong frame. Show the candidate as the party's nominee instead.
  const isOpen = !!(s.retiring || (s.incumbent ?? "").startsWith("(open"));
  const candPrefix = isOpen
    ? `<span style="color:#666">${s.challenger_party ?? ""} nominee: </span>`
    : `<span style="color:#666">vs </span>`;
  const challengerLine = s.challenger
    ? `<div style="margin-bottom:3px">${candPrefix}<b style="color:${chColor}">${s.challenger}</b>${isOpen ? "" : ` <span style="color:#888">${s.challenger_party ?? ""}</span>`}${sourceTag}</div>`
    : "";
  // Optional co-nominee (same-party-as-incumbent nominee on open seats)
  const coNomColor = partyColorHex(s.co_nominee_party);
  // "manual" = no auto-WAR match; for primary-confirmed nominees this is just
  // a "no federal-race record" placeholder, not signal worth surfacing.
  const coNominee = s.co_nominee
    ? `<div style="margin-bottom:3px"><span style="color:#666">${s.co_nominee_party ?? ""} nominee: </span><b style="color:${coNomColor}">${s.co_nominee}</b></div>`
    : "";
  // Always show all rows — keep zeros visible so the projection arithmetic
  // is fully transparent regardless of whether candidate info exists.
  const candidateRowLabel = isOpen ? "+ nominee WAR" : "+ challenger";

  return `<div style="font:11px ui-sans-serif,system-ui;line-height:1.35;min-width:200px">
    <div style="margin-bottom:3px"><b>${s.state}</b> · ${s.name}</div>
    <div style="margin-bottom:3px"><span style="color:${incColor}">${s.incumbent ?? ""}</span> <span style="color:#888">${partyTag(s.party, !!s.incumbency_adj || !!s.primary_unresolved)}</span>${s.appointed ? " · <i style='color:#666'>appointed</i>" : ""}${s.primary_unresolved ? " · <i style='color:#666'>primary unresolved</i>" : ""}</div>
    ${challengerLine}
    ${coNominee}
    ${row("Pres 2024", s.presidential_margin_2024)}
    ${row("+ state trend", s.state_trend_applied ?? s.state_trend)}
    ${row("+ WAR adj", s.war_adj_discounted)}
    ${row("+ incumbency", s.incumbency_adj)}
    ${row(candidateRowLabel, s.challenger_adj)}
    ${row("+ uniform swing", uniformSwing)}
    ${row("+ demographic Δ", s.demo_shift)}
    ${row("= projection", s.projection, true)}
    ${flipRow}
  </div>`;
}

function notUpPopupHtml(state: string, name: string): string {
  return `<div style="font:11px ui-sans-serif,system-ui;line-height:1.35">
    <div><b>${state}</b> · ${name}</div>
    <div style="color:#777">not up for election in 2026</div>
  </div>`;
}

export function SenateMap({ seats, uniformSwing, onPickState }: Props) {
  const onPickStateRef = useRef(onPickState);
  onPickStateRef.current = onPickState;
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MLMap | null>(null);
  const popupRef = useRef<Popup | null>(null);
  const seatsRef = useRef<SenateSeat[]>(seats);
  const swingRef = useRef<number>(uniformSwing);
  const isLoadedRef = useRef(false);

  seatsRef.current = seats;
  swingRef.current = uniformSwing;

  function buildFillColorExpr(): any {
    const expr: any[] = ["match", ["get", "state"]];
    for (const s of seatsRef.current) {
      expr.push(s.state, bucketColor(s.projection, isIndependentWinner(s)));
    }
    expr.push(PALETTE.notUp);
    return expr;
  }

  function buildFlipFilter(): any {
    const ids = seatsRef.current.filter((s) => s.flip).map((s) => s.state);
    if (ids.length === 0) return ["==", ["get", "state"], "__none__"];
    return ["in", ["get", "state"], ["literal", ids]];
  }

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

  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASE_STYLE,
      center: [-96.5, 38.5],
      zoom: 2.8,
      minZoom: 1.5,
      maxZoom: 8,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", () => {
      map.addSource("states", {
        type: "geojson",
        data: "/states.geojson",
        promoteId: "state",
      });

      map.addLayer({
        id: "state-fill",
        type: "fill",
        source: "states",
        paint: {
          "fill-color": buildFillColorExpr(),
          "fill-opacity": 0.7,
        },
      });

      const hashImg = makeHashPattern(14);
      if (!map.hasImage("flip-hash-states")) {
        map.addImage("flip-hash-states", hashImg, { pixelRatio: 2 });
      }
      map.addLayer({
        id: "state-flips",
        type: "fill",
        source: "states",
        paint: { "fill-pattern": "flip-hash-states", "fill-opacity": 0.55 },
        filter: buildFlipFilter(),
      });

      map.addLayer({
        id: "state-line",
        type: "line",
        source: "states",
        paint: { "line-color": "#3a3a3a", "line-width": 0.5 },
      });

      map.addLayer({
        id: "state-hover",
        type: "line",
        source: "states",
        paint: { "line-color": "#111", "line-width": 2 },
        filter: ["==", ["get", "state"], ""],
      });

      isLoadedRef.current = true;
      popupRef.current = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 8,
      });

      map.on("mousemove", "state-fill", (e) => {
        if (!e.features?.length) return;
        const state = e.features[0].properties?.state as string;
        const name = e.features[0].properties?.name as string;
        map.setFilter("state-hover", ["==", ["get", "state"], state]);
        map.getCanvas().style.cursor = "pointer";
        const s = seatsRef.current.find((ss) => ss.state === state);
        if (popupRef.current) {
          popupRef.current
            .setLngLat(e.lngLat)
            .setHTML(s ? buildPopupHtml(s, swingRef.current) : notUpPopupHtml(state, name))
            .addTo(map);
        }
      });

      map.on("mouseleave", "state-fill", () => {
        map.setFilter("state-hover", ["==", ["get", "state"], ""]);
        map.getCanvas().style.cursor = "default";
        popupRef.current?.remove();
      });

      map.on("click", "state-fill", (e) => {
        const state = e.features?.[0]?.properties?.state as string | undefined;
        if (state && onPickStateRef.current) onPickStateRef.current(state);
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

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoadedRef.current) return;
    map.setPaintProperty("state-fill", "fill-color", buildFillColorExpr());
    map.setFilter("state-flips", buildFlipFilter());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seats]);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden relative">
      <div ref={containerRef} className="w-full h-[500px]" />
      <div className="absolute bottom-2 left-2 bg-white/95 rounded shadow px-2 py-1.5 text-[10px] leading-tight font-mono">
        <div className="font-sans font-semibold text-[10px] mb-1">Projected D-R margin</div>
        <div className="flex items-center gap-0">
          {[PALETTE.rep5, PALETTE.rep4, PALETTE.rep3, PALETTE.rep2,
            PALETTE.dem2, PALETTE.dem3, PALETTE.dem4, PALETTE.dem5].map((c, i) => (
            <span key={i} className="inline-block w-5 h-3" style={{ background: c }} />
          ))}
        </div>
        <div className="flex justify-between mt-0.5">
          <span>R+15</span><span>tie</span><span>D+15</span>
        </div>
        <div className="font-sans mt-1.5 flex items-center gap-2 text-[10px]">
          <span className="inline-block w-4 h-3 border border-slate-400"
            style={{ background: PALETTE.notUp }} />
          <span className="text-slate-700">not up 2026</span>
        </div>
        <div className="font-sans mt-1 flex items-center gap-2 text-[10px]">
          <span
            className="inline-block w-4 h-3 border border-slate-400"
            style={{
              backgroundImage:
                "repeating-linear-gradient(45deg, rgba(0,0,0,0.65), rgba(0,0,0,0.65) 1.5px, transparent 1.5px, transparent 4px)",
            }}
          />
          <span className="text-slate-700">flipped seat</span>
        </div>
      </div>
    </div>
  );
}
