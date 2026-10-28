import type { GovernorSummary } from "../types";
import { ErrorModelFooter } from "./ErrorModelFooter";

export function GovernorSummaryView({ summary }: { summary: GovernorSummary }) {
  const { races_up, d_up, r_up, i_up, not_up_d, not_up_r, not_up_i,
    d_pickups, r_pickups, i_pickups, governorships: g } = summary;
  const finalD = d_up + not_up_d;
  const finalR = r_up + not_up_r;
  const finalI = i_up + not_up_i;
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-3">Governorships after the election</h2>
      <div className="flex items-end justify-between mb-2">
        <div>
          <div className="text-3xl font-bold text-blue-700">{finalD}</div>
          <div className="text-xs text-slate-500">D</div>
        </div>
        <div className="text-center">
          {finalI > 0 && <div className="text-sm font-semibold text-slate-600">{finalI} independent</div>}
          <div className="text-xs text-slate-500">projected winners · 26 is a majority of 50</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-red-700">{finalR}</div>
          <div className="text-xs text-slate-500">R</div>
        </div>
      </div>
      <div className="h-4 bg-slate-200 rounded overflow-hidden flex">
        <div className="bg-blue-600 h-full" style={{ width: `${(finalD / 50) * 100}%` }} />
        <div className="bg-slate-400 h-full" style={{ width: `${(finalI / 50) * 100}%` }} />
        <div className="bg-red-600 h-full flex-1" />
      </div>
      <div className="grid grid-cols-2 gap-3 mt-3 text-xs text-slate-600">
        <div><b>{races_up}</b> races · projected D <b>{d_up}</b>{i_up > 0 && <> · I <b>{i_up}</b></>} · R <b>{r_up}</b></div>
        <div className="text-right">not up: D <b>{not_up_d}</b> · R <b>{not_up_r}</b>{not_up_i > 0 && <> · I <b>{not_up_i}</b></>}</div>
      </div>
      {(d_pickups.length > 0 || r_pickups.length > 0 || i_pickups.length > 0) && (
        <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
          <div>
            <div className="font-semibold text-blue-700 mb-1">D pickups ({d_pickups.length})</div>
            <div className="font-mono text-[11px] leading-tight">{d_pickups.join(", ") || "—"}</div>
            {i_pickups.length > 0 && (
              <div className="mt-1 text-slate-600">Independent pickups: <span className="font-mono">{i_pickups.join(", ")}</span></div>
            )}
          </div>
          <div>
            <div className="font-semibold text-red-700 mb-1">R pickups ({r_pickups.length})</div>
            <div className="font-mono text-[11px] leading-tight">{r_pickups.join(", ") || "—"}</div>
          </div>
        </div>
      )}
      {g && (
        <div className="mt-3 pt-3 border-t border-slate-200 text-xs">
          <div className="flex items-baseline justify-between mb-1">
            <span className="font-semibold text-slate-700">P(Democrats hold a majority of governorships)</span>
            <span className={`font-bold text-lg ${g.p_d_majority >= 0.5 ? "text-blue-700" : "text-red-700"}`}>
              {(g.p_d_majority * 100).toFixed(1)}%
            </span>
          </div>
          <div className="text-slate-500">
            D governorships: median <b>{g.d_median}</b> · 80% range <b>[{g.d_p10}, {g.d_p90}]</b>
          </div>
          <div className="text-slate-500">
            R governorships: median <b>{g.r_median}</b> · 80% range <b>[{g.r_p10}, {g.r_p90}]</b>
          </div>
          <ErrorModelFooter model={summary.error_model} />
          <div className="text-[10px] text-slate-400 mt-1">
            Governor races share the Senate's simulations: a state's Senate and governor races miss together.
            Partisan slope {summary.slope.toFixed(2)}.
          </div>
        </div>
      )}
      <div className="text-[10px] text-slate-400 mt-3 italic border-t pt-2">
        36 governorships up in 2026. The 14 not up keep their current party.
      </div>
    </div>
  );
}
