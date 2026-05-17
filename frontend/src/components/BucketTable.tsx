import { useMemo } from "react";
import type { District, SenateSeat } from "../types";

// Common row shape — District and SenateSeat both expose these fields.
type BucketRow = { id: string; incumbent: string | null; party: string; projection: number };

type Props = {
  districts?: District[];
  seats?: SenateSeat[];
  onPick?: (id: string) => void;
  title?: string;
};

type Bucket = "tilt" | "lean" | "likely";

function bucketOf(proj: number): Bucket | "safe" {
  const a = Math.abs(proj);
  if (a > 13) return "safe";
  if (a > 7)  return "likely";
  if (a > 3)  return "lean";
  return "tilt";
}

const BUCKET_BG: Record<Bucket, { d: string; r: string }> = {
  likely: { d: "bg-dem4 text-white", r: "bg-rep4 text-white" },
  lean:   { d: "bg-dem3",            r: "bg-rep3 text-white" },
  tilt:   { d: "bg-dem2",            r: "bg-rep2" },
};

const COLS: { side: "D" | "R"; bucket: Bucket; label: string }[] = [
  { side: "D", bucket: "likely", label: "Likely D" },
  { side: "D", bucket: "lean",   label: "Lean D" },
  { side: "D", bucket: "tilt",   label: "Tilt D" },
  { side: "R", bucket: "tilt",   label: "Tilt R" },
  { side: "R", bucket: "lean",   label: "Lean R" },
  { side: "R", bucket: "likely", label: "Likely R" },
];

export function BucketTable({ districts, seats, onPick, title = "Competitive seats by bucket" }: Props) {
  const rows: BucketRow[] = useMemo(() => {
    if (districts) {
      return districts.map((d) => ({ id: d.district, incumbent: d.incumbent ?? null, party: d.party, projection: d.projection }));
    }
    if (seats) {
      return seats.map((s) => ({ id: s.state, incumbent: s.incumbent ?? null, party: s.party, projection: s.projection }));
    }
    return [];
  }, [districts, seats]);

  const grouped = useMemo(() => {
    const out: Record<string, BucketRow[]> = {};
    for (const c of COLS) out[`${c.side}-${c.bucket}`] = [];
    for (const d of rows) {
      const b = bucketOf(d.projection);
      if (b === "safe") continue;
      const side = d.projection > 0 ? "D" : "R";
      out[`${side}-${b}`].push(d);
    }
    // Sort each column: farther from zero at the top, most-marginal at the
    // bottom so adjacent buckets meet at their shared boundary.
    for (const k of Object.keys(out)) {
      out[k].sort((a, b) => Math.abs(b.projection) - Math.abs(a.projection));
    }
    return out;
  }, [rows]);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">{title}</h2>
        <div className="text-xs text-slate-500">
          Click a district to see its breakdown · Tilt ≤3 · Lean 3-7 · Likely 7-13
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-2">
        {COLS.map((c) => {
          const list = grouped[`${c.side}-${c.bucket}`];
          const headerBg = BUCKET_BG[c.bucket][c.side === "D" ? "d" : "r"];
          return (
            <div key={c.label} className="border rounded">
              <div className={`px-2 py-1 text-xs font-semibold ${headerBg}`}>
                {c.label} ({list.length})
              </div>
              <div className="max-h-72 overflow-auto p-1 flex flex-wrap gap-1 content-start">
                {list.length === 0 ? (
                  <div className="px-1 py-1 text-xs text-slate-400 italic">—</div>
                ) : list.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => onPick?.(d.id)}
                    title={`${d.id} · ${d.incumbent ?? ""} · ${d.projection > 0 ? "+" : ""}${d.projection.toFixed(1)}`}
                    className={`font-mono text-[11px] px-1.5 py-0.5 rounded hover:opacity-80 ${
                      d.party === "(D)" ? "bg-blue-700 text-white"
                      : d.party === "(R)" ? "bg-red-700 text-white"
                      : "bg-slate-500 text-white"
                    }`}
                  >
                    {d.id}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
