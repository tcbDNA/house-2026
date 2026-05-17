import type { SenateSummary } from "../types";

export function SenateSummaryView({ summary }: { summary: SenateSummary }) {
  const { final_d, final_r, d_seats_up, r_seats_up, seats_up, tossups_up,
    d_pickups, r_pickups, majority, not_up_d, not_up_r } = summary;
  const total = final_d + final_r;
  const dPct = total ? (final_d / 100) * 100 : 50;

  const majorityLabel = majority === "D"
    ? "Democratic majority"
    : majority === "R"
    ? "Republican majority"
    : majority === "tie"
    ? "50-50 tie (VP breaks)"
    : "No majority";
  const majorityColor =
    majority === "D" ? "text-blue-700" :
    majority === "R" ? "text-red-700" :
    "text-slate-600";

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-3">Senate composition</h2>
      <div className="flex items-end justify-between mb-2">
        <div>
          <div className="text-3xl font-bold text-blue-700">{final_d}</div>
          <div className="text-xs text-slate-500">D</div>
        </div>
        <div className="text-center">
          <div className={`text-sm font-semibold ${majorityColor}`}>{majorityLabel}</div>
          <div className="text-xs text-slate-500">51 needed</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-red-700">{final_r}</div>
          <div className="text-xs text-slate-500">R</div>
        </div>
      </div>
      <div className="h-4 bg-slate-200 rounded overflow-hidden flex">
        <div className="bg-blue-600 h-full" style={{ width: `${dPct}%` }} />
        <div className="bg-red-600 h-full flex-1" />
      </div>
      <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
        <div className="text-slate-600">
          <div><b>{seats_up}</b> seats up · D-held: <b>{d_seats_up}</b> · R-held: <b>{r_seats_up}</b></div>
          <div className="text-slate-500">{tossups_up} within ±3</div>
        </div>
        <div className="text-slate-600 text-right">
          <div>not up: D <b>{not_up_d}</b> · R <b>{not_up_r}</b></div>
        </div>
      </div>

      {(d_pickups.length > 0 || r_pickups.length > 0) && (
        <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
          <div>
            <div className="font-semibold text-blue-700 mb-1">D pickups ({d_pickups.length})</div>
            <div className="font-mono text-[11px] leading-tight">{d_pickups.join(", ") || "—"}</div>
          </div>
          <div>
            <div className="font-semibold text-red-700 mb-1">R pickups ({r_pickups.length})</div>
            <div className="font-mono text-[11px] leading-tight">{r_pickups.join(", ") || "—"}</div>
          </div>
        </div>
      )}

      <div className="text-[10px] text-slate-400 mt-3 italic border-t pt-2">
        Class II seats up 2026 + 2 special elections (OH, FL). Non-up seats assume current party.
      </div>
    </div>
  );
}
