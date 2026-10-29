import type { GeoJSONSource, Map as MLMap } from "maplibre-gl";

// "Shift from 2024" map view, after the New York Times' shift maps: an arrow
// from each district's, state's or county's label point, pointing left (blue)
// for a shift toward Democrats and right (red) toward Republicans, its length
// proportional to the shift (projected 2026 margin − 2024 presidential
// margin). Arrows keep their screen size at every zoom, so the legend's scale
// holds. A view only: no projection changes.

export const SWING_COLORS = { D: "#1f6fdc", R: "#d33b3b" } as const;
export const SWING_CAP = 40;          // longest arrow, in points
export const SWING_FILL = "#eeeeee";  // district/state/county fill in this view
const ANGLE = (40 * Math.PI) / 180;   // above horizontal
const PAD = 3;                        // px around the arrow in each image
const RATIO = 2;                      // image pixel ratio
const STROKE = 1.6;

type Dir = "D" | "R";
export type SwingArrow = { point: [number, number]; shift: number };

// Arrow of `len` px in an image of w × h px, tail at a bottom corner.
function geometry(len: number, dir: Dir) {
  const w = len * Math.cos(ANGLE) + 2 * PAD, h = len * Math.sin(ANGLE) + 2 * PAD;
  const sx = dir === "D" ? -1 : 1;
  const tail = [dir === "D" ? w - PAD : PAD, h - PAD];
  const ux = sx * Math.cos(ANGLE), uy = -Math.sin(ANGLE);
  const tip = [tail[0] + ux * len, tail[1] + uy * len];
  const head = Math.min(5.5, Math.max(3, len * 0.6)), half = head * 0.55;
  const base = [tip[0] - ux * head, tip[1] - uy * head];
  const wing = (s: number) => [base[0] - s * uy * half, base[1] + s * ux * half];
  return { w, h, tail, neck: base, tip, wings: [wing(1), wing(-1)] };
}

function arrowImage(len: number, dir: Dir): ImageData {
  const g = geometry(len, dir);
  const canvas = document.createElement("canvas");
  canvas.width = Math.ceil(g.w * RATIO); canvas.height = Math.ceil(g.h * RATIO);
  const ctx = canvas.getContext("2d")!;
  ctx.scale(RATIO, RATIO);
  ctx.lineCap = "round"; ctx.lineJoin = "round";
  // A white outline first, so overlapping arrows stay legible.
  for (const [color, extra] of [["rgba(255,255,255,0.9)", 2], [SWING_COLORS[dir], 0]] as const) {
    ctx.strokeStyle = color; ctx.fillStyle = color;
    ctx.lineWidth = STROKE + extra;
    ctx.beginPath(); ctx.moveTo(g.tail[0], g.tail[1]); ctx.lineTo(g.neck[0], g.neck[1]); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(g.tip[0], g.tip[1]); ctx.lineTo(g.wings[0][0], g.wings[0][1]); ctx.lineTo(g.wings[1][0], g.wings[1][1]);
    ctx.closePath(); ctx.fill();
    if (extra) ctx.stroke();
  }
  return ctx.getImageData(0, 0, canvas.width, canvas.height);
}

/** Registers the arrow images (one per whole point, 1 to SWING_CAP, each way)
 *  and adds a hidden arrow layer on top of the map's layers. */
export function addSwingLayer(map: MLMap, pxPerPt: number): void {
  for (const dir of ["D", "R"] as const) {
    for (let n = 1; n <= SWING_CAP; n++) {
      const id = `swing-${dir}-${n}`;
      if (!map.hasImage(id)) map.addImage(id, arrowImage(n * pxPerPt, dir), { pixelRatio: RATIO });
    }
  }
  map.addSource("swing", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  map.addLayer({
    id: "swing-arrows",
    type: "symbol",
    source: "swing",
    layout: {
      "icon-image": ["get", "img"],
      // The tail sits on the label point.
      "icon-anchor": ["match", ["get", "dir"], "D", "bottom-right", "bottom-left"],
      "icon-offset": ["match", ["get", "dir"], "D", ["literal", [PAD, PAD]], ["literal", [-PAD, PAD]]],
      "icon-allow-overlap": true,
      "icon-ignore-placement": true,
      // Shorter arrows drawn over longer ones.
      "symbol-sort-key": ["-", 0, ["get", "len"]],
      "visibility": "none",
    },
  });
}

/** Shows these arrows, or hides the layer (null). Shifts under 0.5 points get
 *  no arrow; shifts over SWING_CAP draw at the cap. */
export function setSwingArrows(map: MLMap, arrows: SwingArrow[] | null): void {
  const src = map.getSource("swing") as GeoJSONSource | undefined;
  if (!src || !map.getLayer("swing-arrows")) return;
  map.setLayoutProperty("swing-arrows", "visibility", arrows ? "visible" : "none");
  src.setData({
    type: "FeatureCollection",
    features: (arrows ?? []).flatMap((a) => {
      const n = Math.min(SWING_CAP, Math.round(Math.abs(a.shift)));
      if (n < 1) return [];
      const dir: Dir = a.shift > 0 ? "D" : "R";
      return [{
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: a.point },
        properties: { img: `swing-${dir}-${n}`, dir, len: n },
      }];
    }),
  });
}

/** Precomputed label points (id → [lng, lat]; scripts/build_label_points.ts). */
export async function fetchPoints(url: string): Promise<Map<string, [number, number]>> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} failed: ${res.status}`);
  return new Map(Object.entries(await res.json()) as [string, [number, number]][]);
}

/** Popup row: the shift from 2024, signed and colored like the other rows. */
export function shiftRowHtml(shift: number | null, missing?: string): string {
  if (shift == null) return missing ? `<div style="color:#666">${missing}</div>` : "";
  const r = Math.round(shift * 10) / 10;
  const color = r > 0 ? "#1e40af" : r < 0 ? "#9b1c1c" : "#666";
  const text = r > 0 ? `D+${r.toFixed(1)}` : r < 0 ? `R+${(-r).toFixed(1)}` : "none";
  return `<div style="display:flex;justify-content:space-between;gap:8px;margin-top:2px;padding-top:2px;border-top:1px dashed #ccc">
            <span style="color:#555">shift from 2024 pres.</span>
            <span style="font-family:ui-monospace,monospace;color:${color}">${text}</span>
          </div>`;
}

export function SwingToggle({ on, onChange }: { on: boolean; onChange: (on: boolean) => void }) {
  return (
    <div className="inline-flex rounded shadow border border-slate-300 overflow-hidden text-[11px]">
      {[false, true].map((v) => (
        <button key={String(v)} onClick={() => onChange(v)}
                className={`px-2 py-1 ${on === v ? "bg-slate-800 text-white" : "bg-white/95 text-slate-700 hover:bg-slate-50"}`}>
          {v ? "Shift from 2024" : "Margin"}
        </button>
      ))}
    </div>
  );
}

function ArrowSvg({ len, dir }: { len: number; dir: Dir }) {
  const g = geometry(len, dir);
  const pts = (ps: number[][]) => ps.map((p) => p.join(",")).join(" ");
  return (
    <svg width={g.w} height={g.h} className="shrink-0" aria-hidden>
      <line x1={g.tail[0]} y1={g.tail[1]} x2={g.neck[0]} y2={g.neck[1]}
            stroke={SWING_COLORS[dir]} strokeWidth={STROKE} strokeLinecap="round" />
      <polygon points={pts([g.tip, ...g.wings])} fill={SWING_COLORS[dir]} />
    </svg>
  );
}

/** Legend for the shift view: 10-point sample arrows at the map's scale. */
export function SwingLegend({ pxPerPt, towardD = "D", capped, notes = [] }: {
  pxPerPt: number; towardD?: string; capped: boolean; notes?: string[];
}) {
  return (
    <div className="absolute bottom-2 left-2 bg-white/95 rounded shadow px-2 py-1.5 text-[10px] leading-tight max-w-[260px]">
      <div className="font-semibold mb-1">Shift from the 2024 presidential margin</div>
      <div className="flex items-end gap-4">
        <span className="flex items-end gap-1"><ArrowSvg len={10 * pxPerPt} dir="D" />10 pts toward {towardD}</span>
        <span className="flex items-end gap-1"><ArrowSvg len={10 * pxPerPt} dir="R" />10 pts toward R</span>
      </div>
      <div className="text-slate-500 mt-1">
        Projected 2026 margin minus 2024 (Harris − Trump). No arrow under 0.5 pts
        {capped ? `; arrows stop at ${SWING_CAP} pts (hover for the exact shift)` : ""}.
      </div>
      {notes.map((n) => <div key={n} className="text-slate-500 mt-0.5">{n}</div>)}
    </div>
  );
}
