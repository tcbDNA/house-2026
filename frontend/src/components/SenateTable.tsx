import { useMemo, useState } from "react";
import { partyColorClass, partyTag, type SenateSeat } from "../types";

type Props = {
  seats: SenateSeat[];
  notUpD?: number;  // Senate seats not up in 2026 that are held by D (47-of-100 currently)
};

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13
function bucket(s: SenateSeat): string {
  const proj = s.projection;
  // Independent winners (caucus-with-D) use grey scale; the D-side may be
  // either the incumbent (party "(I)") or the challenger (challenger_party "(I)").
  const indWin = proj > 0 && (s.party === "(I)" || s.challenger_party === "(I)");
  if (indWin) {
    const a = Math.abs(proj);
    if (a > 13) return "bg-ind5 text-white";
    if (a > 7)  return "bg-ind4 text-white";
    if (a > 3)  return "bg-ind3";
    return "bg-ind2";
  }
  if (proj > 13)  return "bg-dem5 text-white";
  if (proj > 7)   return "bg-dem4 text-white";
  if (proj > 3)   return "bg-dem3";
  if (proj > 0)   return "bg-dem2";
  if (proj > -3)  return "bg-rep2";
  if (proj > -7)  return "bg-rep3 text-white";
  if (proj > -13) return "bg-rep4 text-white";
  return "bg-rep5 text-white";
}

type SortKey = "state" | "presidential_margin_2024" | "projection" | "incumbent";

export function SenateTable({ seats, notUpD }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("projection");
  const [asc, setAsc] = useState(true);
  const [filter, setFilter] = useState("");
  const [onlyFlips, setOnlyFlips] = useState(false);
  const [onlyClose, setOnlyClose] = useState(false);

  // Tipping point: the seat at the position that would flip the chamber if it
  // changed hands. Includes the 65 not-up seats (assumed to hold their current
  // party). D needs 51 total → needs (51 - notUpD) wins from the 35 up-seats.
  const tippingPointState = useMemo(() => {
    if (notUpD == null) return null;
    const dSeatsNeeded = 51 - notUpD;
    if (dSeatsNeeded < 1 || dSeatsNeeded > seats.length) return null;
    const sorted = [...seats].sort((a, b) => b.projection - a.projection);
    return sorted[dSeatsNeeded - 1]?.state ?? null;
  }, [seats, notUpD]);

  const rows = useMemo(() => {
    let r = seats;
    if (filter) {
      const q = filter.toLowerCase();
      r = r.filter(
        (s) =>
          s.state.toLowerCase().includes(q) ||
          s.name.toLowerCase().includes(q) ||
          (s.incumbent ?? "").toLowerCase().includes(q),
      );
    }
    if (onlyFlips) r = r.filter((s) => s.flip !== null);
    if (onlyClose) r = r.filter((s) => Math.abs(s.projection) <= 8);
    r = [...r].sort((a, b) => {
      const av: any = a[sortKey];
      const bv: any = b[sortKey];
      if (typeof av === "number" && typeof bv === "number") return asc ? av - bv : bv - av;
      return asc
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av));
    });
    return r;
  }, [seats, filter, onlyFlips, onlyClose, sortKey, asc]);

  function header(label: string, key: SortKey, align: "L" | "R" = "L") {
    const active = sortKey === key;
    return (
      <th
        onClick={() => {
          if (active) setAsc(!asc);
          else { setSortKey(key); setAsc(key === "state" || key === "incumbent"); }
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
          placeholder="filter by state, incumbent, or state name…"
          className="border rounded px-2 py-1 text-sm flex-1 min-w-[160px]"
        />
        <label className="text-xs flex items-center gap-1">
          <input type="checkbox" checked={onlyFlips} onChange={(e) => setOnlyFlips(e.target.checked)} />
          Only flips
        </label>
        <label className="text-xs flex items-center gap-1">
          <input type="checkbox" checked={onlyClose} onChange={(e) => setOnlyClose(e.target.checked)} />
          Only within ±8
        </label>
        <span className="text-xs text-slate-500">{rows.length} of {seats.length}</span>
      </div>
      <div className="overflow-auto max-h-[70vh]">
        <table className="text-sm w-full">
          <thead className="bg-slate-50 text-xs uppercase text-slate-600 sticky top-0">
            <tr>
              {header("State", "state")}
              {header("Incumbent", "incumbent")}
              {header("Pres 2024", "presidential_margin_2024", "R")}
              {header("Proj", "projection", "R")}
              <th className="px-2 py-1 text-left">Flip</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr
                key={s.state}
                className={`border-t hover:bg-slate-50 ${s.state === tippingPointState ? "outline outline-2 outline-amber-500" : ""}`}
                title={s.state === tippingPointState ? "Tipping point — flipping this seat changes the majority" : undefined}
              >
                <td className="px-2 py-1 font-mono">
                  {s.state}
                  {s.seat_type === "special" && (
                    <span className="ml-1 text-[10px] text-slate-400">(special)</span>
                  )}
                </td>
                <td className="px-2 py-1">
                  <span className={partyColorClass(s.party)}>{s.incumbent}</span>{" "}
                  <span className="text-slate-400">{partyTag(s.party, !!s.incumbency_adj || !!s.primary_unresolved)}</span>
                  {s.retiring && <span className="ml-1 text-[10px] text-slate-400 italic">retiring</span>}
                  {s.appointed && <span className="ml-1 text-[10px] text-slate-400 italic">appointed</span>}
                  {s.primary_unresolved && <span className="ml-1 text-[10px] text-slate-400 italic">primary unresolved</span>}
                  {s.challenger && (
                    <div className="text-[10px] mt-0.5">
                      <span className="text-slate-500">
                        {(s.retiring || (s.incumbent ?? "").startsWith("(open")) ? `${s.challenger_party} nominee: ` : "vs "}
                      </span>
                      <span className={partyColorClass(s.challenger_party)}>{s.challenger}</span>
                      {!(s.retiring || (s.incumbent ?? "").startsWith("(open")) && (
                        <> <span className="text-slate-400">{s.challenger_party}</span></>
                      )}
                    </div>
                  )}
                  {s.co_nominee && (
                    <div className="text-[10px] mt-0.5">
                      <span className="text-slate-500">{s.co_nominee_party} nominee: </span>
                      <span className={partyColorClass(s.co_nominee_party)}>{s.co_nominee}</span>
                    </div>
                  )}
                </td>
                <td className="px-2 py-1 text-right font-mono">
                  {s.presidential_margin_2024 !== null
                    ? (s.presidential_margin_2024 > 0 ? "+" : "") + s.presidential_margin_2024.toFixed(1)
                    : "—"}
                </td>
                <td className={`px-2 py-1 text-right font-mono ${bucket(s)}`}>
                  {s.projection > 0 ? "+" : ""}{s.projection.toFixed(1)}
                </td>
                <td className="px-2 py-1 text-xs">
                  {s.flip === "to_D" && <span className="text-blue-700 font-semibold">→ D</span>}
                  {s.flip === "to_R" && <span className="text-red-700 font-semibold">→ R</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
