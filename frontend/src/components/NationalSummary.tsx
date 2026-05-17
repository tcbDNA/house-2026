import type { Summary } from "../types";

export function NationalSummary({ summary }: { summary: Summary }) {
  const { d_seats, r_seats, tossups, d_pickups, r_pickups, majority, buckets } = summary;
  const total = d_seats + r_seats;
  const dPct = total ? (d_seats / total) * 100 : 50;

  // 435 House seats — segments are widths in %.
  // Order left-to-right: safe D → likely D → lean D → tossup D → tossup R → lean R → likely R → safe R.
  // Falls back to plain D/R if buckets missing (e.g. Senate response shape).
  const segments = buckets ? [
    { count: buckets.d_safe,   className: "bg-dem5", label: "safe D" },
    { count: buckets.d_likely, className: "bg-dem4", label: "likely D" },
    { count: buckets.d_lean,   className: "bg-dem3", label: "lean D" },
    { count: buckets.d_tossup, className: "bg-dem2", label: "tilt D" },
    { count: buckets.r_tossup, className: "bg-rep2", label: "tilt R" },
    { count: buckets.r_lean,   className: "bg-rep3", label: "lean R" },
    { count: buckets.r_likely, className: "bg-rep4", label: "likely R" },
    { count: buckets.r_safe,   className: "bg-rep5", label: "safe R" },
  ] : null;
  const denom = total || 435;

  const majorityLabel = majority === "D"
    ? "Democratic majority"
    : majority === "R"
    ? "Republican majority"
    : "No majority";
  const majorityColor = majority === "D" ? "text-blue-700" : majority === "R" ? "text-red-700" : "text-slate-500";

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold mb-3">National total</h2>
      <div className="flex items-end justify-between mb-2">
        <div>
          <div className="text-3xl font-bold text-blue-700">{d_seats}</div>
          <div className="text-xs text-slate-500">D</div>
        </div>
        <div className="text-center">
          <div className={`text-sm font-semibold ${majorityColor}`}>{majorityLabel}</div>
          <div className="text-xs text-slate-500">218 to flip</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-red-700">{r_seats}</div>
          <div className="text-xs text-slate-500">R</div>
        </div>
      </div>

      <div className="relative h-4 bg-slate-200 rounded overflow-hidden flex">
        {segments
          ? segments.map((s, i) => (
              <div
                key={i}
                className={s.className}
                style={{ width: `${(s.count / denom) * 100}%` }}
                title={`${s.count} ${s.label}`}
              />
            ))
          : (
            <>
              <div className="bg-blue-600 h-full" style={{ width: `${dPct}%` }} />
              <div className="bg-red-600 h-full flex-1" />
            </>
          )}
        {/* 218 majority threshold marker (218 / 435 = 50.11%) */}
        <div
          className="absolute inset-y-0 w-0.5 bg-slate-900"
          style={{ left: `${(218 / 435) * 100}%`, transform: "translateX(-50%)" }}
          title="218 = majority threshold"
        />
      </div>
      <div className="text-xs text-slate-500 mt-2 italic">
        {tossups} seat{tossups === 1 ? "" : "s"} within ±3 (tilt)
      </div>

      {(d_pickups.length > 0 || r_pickups.length > 0) && (
        <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
          <div>
            <div className="font-semibold text-blue-700 mb-1">
              D pickups ({d_pickups.length})
            </div>
            <div className="font-mono text-[11px] leading-tight">{d_pickups.join(", ") || "—"}</div>
          </div>
          <div>
            <div className="font-semibold text-red-700 mb-1">
              R pickups ({r_pickups.length})
            </div>
            <div className="font-mono text-[11px] leading-tight">{r_pickups.join(", ") || "—"}</div>
          </div>
        </div>
      )}

      <div className="text-[10px] text-slate-400 mt-3 italic border-t pt-2">
        Projections within ±3 pts are tilts (very narrow leads). Demographic models are approximations.
      </div>
    </div>
  );
}
