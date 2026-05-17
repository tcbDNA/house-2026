import { useMemo, useState } from "react";
import { partyColorClass, partyTag, type District } from "../types";

type Props = {
  districts: District[];
  onPick?: (id: string) => void;
};

type SortKey = "district" | "margin_2024" | "projection" | "demo_shift" | "incumbent";

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
function bucket(proj: number): string {
  if (proj > 13)  return "bg-dem5 text-white";
  if (proj > 7)   return "bg-dem4 text-white";
  if (proj > 3)   return "bg-dem3";
  if (proj > 0)   return "bg-dem2";
  if (proj > -3)  return "bg-rep2";
  if (proj > -7)  return "bg-rep3 text-white";
  if (proj > -13) return "bg-rep4 text-white";
  return "bg-rep5 text-white";
}

export function DistrictTable({ districts, onPick }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("projection");
  const [asc, setAsc] = useState(true);
  const [filter, setFilter] = useState("");
  const [onlyFlips, setOnlyFlips] = useState(false);
  const [onlyClose, setOnlyClose] = useState(false);

  // Tipping point: seat at position 218 when all 435 districts are sorted by
  // projection desc. If this seat flipped, the majority would change.
  const tippingPointId = useMemo(() => {
    if (districts.length < 218) return null;
    const sorted = [...districts].sort((a, b) => b.projection - a.projection);
    return sorted[217]?.district ?? null;
  }, [districts]);

  const rows = useMemo(() => {
    let r = districts;
    if (filter) {
      const q = filter.toLowerCase();
      r = r.filter(
        (d) =>
          d.district.toLowerCase().includes(q) ||
          (d.incumbent || "").toLowerCase().includes(q) ||
          (d.state || "").toLowerCase().includes(q),
      );
    }
    if (onlyFlips) r = r.filter((d) => d.flip !== null);
    if (onlyClose) r = r.filter((d) => Math.abs(d.projection) <= 5);
    r = [...r].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === "number" && typeof bv === "number") return asc ? av - bv : bv - av;
      return asc
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av));
    });
    return r;
  }, [districts, filter, onlyFlips, onlyClose, sortKey, asc]);

  function header(label: string, key: SortKey, align: "L" | "R" = "L") {
    const active = sortKey === key;
    return (
      <th
        onClick={() => {
          if (active) setAsc(!asc);
          else { setSortKey(key); setAsc(key === "district" || key === "incumbent"); }
        }}
        className={`px-2 py-1 cursor-pointer select-none ${align === "R" ? "text-right" : "text-left"} ${active ? "bg-slate-100" : ""}`}
      >
        {label}{active ? (asc ? " ↑" : " ↓") : ""}
      </th>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-3 flex flex-wrap items-center gap-3 border-b">
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="filter by district, incumbent, or state…"
          className="border rounded px-2 py-1 text-sm flex-1 min-w-[160px]"
        />
        <label className="text-xs flex items-center gap-1">
          <input type="checkbox" checked={onlyFlips} onChange={(e) => setOnlyFlips(e.target.checked)} />
          Only flips
        </label>
        <label className="text-xs flex items-center gap-1">
          <input type="checkbox" checked={onlyClose} onChange={(e) => setOnlyClose(e.target.checked)} />
          Only within ±5
        </label>
        <span className="text-xs text-slate-500">{rows.length} of {districts.length}</span>
      </div>
      <div className="overflow-auto max-h-[70vh]">
        <table className="text-sm w-full">
          <thead className="bg-slate-50 text-xs uppercase text-slate-600 sticky top-0">
            <tr>
              {header("District", "district")}
              {header("Incumbent", "incumbent")}
              {header("2024 m", "margin_2024", "R")}
              {header("Proj", "projection", "R")}
              {header("Demo Δ", "demo_shift", "R")}
              <th className="px-2 py-1 text-left">Flip</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr
                key={d.district}
                onClick={() => onPick?.(d.district)}
                className={`border-t hover:bg-slate-50 cursor-pointer ${d.district === tippingPointId ? "outline outline-2 outline-amber-500" : ""}`}
                title={d.district === tippingPointId ? "Tipping point — the 218th-most-D seat" : undefined}
              >
                <td className="px-2 py-1 font-mono">{d.district}</td>
                <td className="px-2 py-1">
                  <span className={partyColorClass(d.party)}>{d.incumbent}</span>{" "}
                  <span className="text-slate-400">{partyTag(d.party, !!d.incumbency_adj)}</span>
                  {d.challenger && (
                    <div className="text-[10px] mt-0.5">
                      <span className="text-slate-500">
                        {(d.incumbent ?? "").startsWith("(open") ? `${d.challenger_party} nominee: ` : "vs "}
                      </span>
                      <span className={partyColorClass(d.challenger_party)}>{d.challenger}</span>
                      {!(d.incumbent ?? "").startsWith("(open") && (
                        <> <span className="text-slate-400">{d.challenger_party}</span></>
                      )}
                    </div>
                  )}
                </td>
                <td className="px-2 py-1 text-right font-mono">{d.margin_2024?.toFixed(1)}</td>
                <td className={`px-2 py-1 text-right font-mono ${bucket(d.projection)}`}>
                  {d.projection > 0 ? "+" : ""}{d.projection.toFixed(1)}
                </td>
                <td className={`px-2 py-1 text-right font-mono text-xs ${d.demo_shift > 0 ? "text-blue-700" : d.demo_shift < 0 ? "text-red-700" : "text-slate-400"}`}>
                  {d.demo_shift > 0 ? "+" : ""}{d.demo_shift.toFixed(1)}
                </td>
                <td className="px-2 py-1 text-xs">
                  {d.flip === "to_D" && <span className="text-blue-700 font-semibold">→ D</span>}
                  {d.flip === "to_R" && <span className="text-red-700 font-semibold">→ R</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
