import { MODEL_DEFAULTS, formatMargin, type Summary } from "../types";
import { ErrorModelFooter } from "./ErrorModelFooter";

export function NationalSummary({ summary, nationalMargin }: { summary: Summary; nationalMargin?: number }) {
  const { d_seats, r_seats, tossups, d_pickups, r_pickups, majority, buckets, seat_distribution } = summary;
  // Headline: the simulated median of D seats (what the probabilities are
  // built on). The count of projected leads is a secondary line.
  const dMedian = seat_distribution?.d_median ?? d_seats;
  const rMedian = 435 - dMedian;
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
      <div className="flex items-end justify-between mb-1">
        <div>
          <div className="text-3xl font-bold text-blue-700">{dMedian}</div>
          <div className="text-xs text-slate-500">D (simulated median)</div>
        </div>
        <div className="text-center">
          <div className={`text-sm font-semibold ${dMedian >= 218 ? "text-blue-700" : "text-red-700"}`}>
            {dMedian >= 218 ? "Democratic majority" : "Republican majority"}
          </div>
          <div className="text-xs text-slate-500">218 to flip</div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-red-700">{rMedian}</div>
          <div className="text-xs text-slate-500">R</div>
        </div>
      </div>
      <div className="text-xs text-slate-500 mb-2">
        Projected leads: <b className="text-blue-700">{d_seats} D</b> – <b className="text-red-700">{r_seats} R</b>
        {" "}<span className={majorityColor}>({majorityLabel.toLowerCase()})</span>
      </div>
      {nationalMargin !== undefined && (
        <div className="text-xs text-slate-600 mb-2 border-t pt-2">
          <div className="flex justify-between">
            <span>National House margin</span>
            <b className="font-mono">{formatMargin(Math.round(nationalMargin * 10) / 10)}</b>
          </div>
          {MODEL_DEFAULTS.pollToplineAverage !== null && (
            <ComparisonRow label="Topline avg of included polls" margin={MODEL_DEFAULTS.pollToplineAverage}
                           national={nationalMargin} />
          )}
          {MODEL_DEFAULTS.publicAverages.map((a) => (
            <ComparisonRow key={a.source} label={`${a.source} (${a.as_of})`} margin={a.margin}
                           national={nationalMargin} href={a.url} />
          ))}
        </div>
      )}

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

      {seat_distribution && (
        <div className="mt-3 pt-3 border-t border-slate-200 text-xs">
          <div className="flex items-baseline justify-between mb-1">
            <span className="font-semibold text-slate-700">P(D majority)</span>
            <span className={`font-bold text-lg ${seat_distribution.p_d_majority >= 0.5 ? "text-blue-700" : "text-red-700"}`}>
              {(seat_distribution.p_d_majority * 100).toFixed(1)}%
            </span>
          </div>
          <div className="text-slate-500">
            D seats: median <b>{seat_distribution.d_median}</b>{" "}
            · 80% CI <b>[{seat_distribution.d_p10}, {seat_distribution.d_p90}]</b>
          </div>
          <ErrorModelFooter model={summary.error_model} />
        </div>
      )}

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

// One public-average line: its margin and the gap (model − average).
function ComparisonRow({ label, margin, national, href }:
    { label: string; margin: number; national: number; href?: string }) {
  const gap = national - margin;
  return (
    <div className="flex justify-between text-slate-500">
      <span>{href ? <a href={href} target="_blank" rel="noreferrer" className="underline">{label}</a> : label}</span>
      <span className="font-mono">
        {formatMargin(Math.round(margin * 10) / 10)}{" "}
        <span className="text-slate-400">(gap {gap >= 0 ? "+" : ""}{gap.toFixed(1)})</span>
      </span>
    </div>
  );
}
