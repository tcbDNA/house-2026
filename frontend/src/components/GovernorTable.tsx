import { useMemo, useState } from "react";
import { formatProjection, partyColorClass, type GovernorRace } from "../types";

// Buckets: tossup ≤3 | lean 3-7 | likely 7-13 | safe >13 (independent winners in grey)
function bucket(r: GovernorRace): string {
  const p = r.projection;
  if ((p > 0 && r.anti_r_party === "(I)") || (p <= 0 && r.opponent_party === "(I)")) {
    const a = Math.abs(p);
    if (a > 13) return "bg-ind5 text-white";
    if (a > 7) return "bg-ind4 text-white";
    if (a > 3) return "bg-ind3";
    return "bg-ind2";
  }
  if (p > 13) return "bg-dem5 text-white";
  if (p > 7) return "bg-dem4 text-white";
  if (p > 3) return "bg-dem3";
  if (p > 0) return "bg-dem2";
  if (p > -3) return "bg-rep2";
  if (p > -7) return "bg-rep3 text-white";
  if (p > -13) return "bg-rep4 text-white";
  return "bg-rep5 text-white";
}

type SortKey = "state" | "model_projection" | "projection" | "p_d";

export function GovernorTable({ races, onPick }: { races: GovernorRace[]; onPick?: (state: string) => void }) {
  const [sortKey, setSortKey] = useState<SortKey>("projection");
  const [asc, setAsc] = useState(true);
  const [filter, setFilter] = useState("");
  const [onlyClose, setOnlyClose] = useState(false);

  const rows = useMemo(() => {
    let r = races;
    if (filter) {
      const q = filter.toLowerCase();
      r = r.filter((x) => [x.state, x.name, x.d_nominee, x.r_nominee, x.anti_r_candidate, x.opponent]
        .some((v) => (v ?? "").toLowerCase().includes(q)));
    }
    if (onlyClose) r = r.filter((x) => Math.abs(x.projection) <= 8);
    return [...r].sort((a, b) => {
      const av: any = a[sortKey] ?? -999, bv: any = b[sortKey] ?? -999;
      if (typeof av === "number" && typeof bv === "number") return asc ? av - bv : bv - av;
      return asc ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    });
  }, [races, filter, onlyClose, sortKey, asc]);

  const header = (label: string, key: SortKey, align: "L" | "R" = "R") => {
    const active = sortKey === key;
    return (
      <th onClick={() => { if (active) setAsc(!asc); else { setSortKey(key); setAsc(key === "state"); } }}
        className={`px-2 py-1 cursor-pointer select-none ${align === "R" ? "text-right" : "text-left"} ${active ? "bg-slate-100" : ""}`}>
        {label}{active ? (asc ? " ↑" : " ↓") : ""}
      </th>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-3 flex flex-wrap items-center gap-3 border-b">
        <input value={filter} onChange={(e) => setFilter(e.target.value)}
          placeholder="filter by state or candidate…" className="border rounded px-2 py-1 text-sm flex-1 min-w-[160px]" />
        <label className="text-xs flex items-center gap-1">
          <input type="checkbox" checked={onlyClose} onChange={(e) => setOnlyClose(e.target.checked)} />
          Only within ±8
        </label>
        <span className="text-xs text-slate-500">{rows.length} of {races.length}</span>
      </div>
      <div className="overflow-auto max-h-[70vh]">
        <table className="text-sm w-full">
          <thead className="bg-slate-50 text-xs uppercase text-slate-600 sticky top-0">
            <tr>
              {header("State", "state", "L")}
              <th className="px-2 py-1 text-left">Candidates</th>
              {header("Model", "model_projection")}
              <th className="px-2 py-1 text-right">Polls</th>
              <th className="px-2 py-1 text-right">Weight</th>
              {header("Proj", "projection")}
              {header("P(D)", "p_d")}
              <th className="px-2 py-1 text-left">Flags</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.state} className={`border-t hover:bg-slate-50 align-top ${onPick ? "cursor-pointer" : ""}`}
                  onClick={() => onPick?.(r.state)} title={onPick ? "Click for the county map" : undefined}>
                <td className="px-2 py-1 font-mono">{r.state}</td>
                <td className="px-2 py-1">
                  <div>
                    <span className={partyColorClass(r.anti_r_party)}>{r.anti_r_candidate ?? "—"}</span>{" "}
                    <span className="text-slate-400">{r.anti_r_party}</span>
                    <span className="text-slate-400"> vs </span>
                    <span className={partyColorClass(r.opponent_party)}>{r.opponent ?? "—"}</span>{" "}
                    <span className="text-slate-400">{r.opponent_party}</span>
                  </div>
                  <div className="text-[10px] text-slate-500">
                    {r.incumbent ? <>Gov. {r.incumbent} {r.incumbent_party} · {r.incumbent_status}</> : "open"}
                    {r.incumbency_adj !== 0 && <> · incumbency {formatProjection(r.incumbency_adj)}</>}
                    {r.war_effect !== 0 && <> · WAR {formatProjection(r.war_effect)}</>}
                  </div>
                  {(() => {
                    // Other candidates on the ballot: third parties at 10%+ (not the opponent
                    // shown above), and the Republican where the opponent is an independent (RI).
                    const also = r.other_candidates.filter((o) => o.name !== r.opponent)
                      .map((o) => `${o.name} ${o.party}${o.max_poll_share ? ` (up to ${o.max_poll_share}%)` : ""}`);
                    if (r.opponent_party !== "(R)" && r.r_nominee) also.push(`${r.r_nominee} (R)`);
                    return also.length > 0 && <div className="text-[10px] text-slate-500">also: {also.join(", ")}</div>;
                  })()}
                </td>
                <td className="px-2 py-1 text-right font-mono">
                  {r.model_projection != null ? formatProjection(r.model_projection) : <span className="text-slate-400">polls only</span>}
                </td>
                <td className="px-2 py-1 text-right font-mono">
                  {r.poll_average ? <>{formatProjection(r.poll_average.margin)} <span className="text-[10px] text-slate-400">({r.poll_average.n_polls})</span></> : "—"}
                </td>
                <td className="px-2 py-1 text-right font-mono">{r.poll_weight ? r.poll_weight.toFixed(2) : "—"}</td>
                <td className={`px-2 py-1 text-right font-mono ${bucket(r)}`}>{formatProjection(r.projection)}</td>
                <td className="px-2 py-1 text-right font-mono">{r.p_d != null ? `${(r.p_d * 100).toFixed(0)}%` : "—"}</td>
                <td className="px-2 py-1 text-[10px]">
                  {r.flip && <div className="font-semibold">{r.flip === "to_D" ? "→ D" : r.flip === "to_R" ? "→ R" : "→ I"}</div>}
                  {r.model_poll_gap != null && (
                    <div className="text-slate-500" title="Model and polls disagree where polls are sparse: half the gap is added to the race's error.">
                      gap {formatProjection(r.model_poll_gap)}
                    </div>
                  )}
                  {r.flags.map((f) => (
                    <div key={f.code} className={f.risk ? "text-amber-700 font-semibold" : "text-slate-500"} title={f.text}>
                      {f.code === "rcv" ? "ranked choice" : f.code === "runoff" ? (f.risk ? "runoff risk" : "runoff rule") :
                        f.risk ? "legislature may choose" : "legislature rule"}
                    </div>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="p-2 text-[10px] text-slate-400 border-t">
        Click a row (or a state on the map) for its county map. Proj = weight × (polls + scenario change) + (1 − weight) × model; polls older than Oct 5 count half for the
        weight where a race has fewer than three recent polls. P(D) is the chance the Democrat wins (in Rhode Island,
        against independent Ken Block). Hover a flag for details.
      </div>
    </div>
  );
}
