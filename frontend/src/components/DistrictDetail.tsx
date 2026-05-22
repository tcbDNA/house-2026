import { useEffect, useState } from "react";
import type { District } from "../types";
import { formatProjection } from "../types";
import { fetchDistrict } from "../api";

type Props = {
  district: District | null;
  onClose: () => void;
  onViewCounties?: (districtId: string) => void;
};

export function DistrictDetail({ district, onClose, onViewCounties }: Props) {
  const [detail, setDetail] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    setDetail(null);
    if (!district) return;
    fetchDistrict(district.district).then(setDetail).catch(console.error);
  }, [district?.district]);

  if (!district) return null;
  const d = detail ?? {};

  return (
    <div className="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white w-full sm:max-w-lg rounded-t-lg sm:rounded-lg shadow-xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold font-mono">{district.district}</h2>
            <div className="text-sm">
              <span className={district.party === "(D)" ? "text-blue-700" : district.party === "(R)" ? "text-red-700" : "text-slate-700"}>
                {district.incumbent}
              </span>{" "}
              <span className="text-slate-400">{district.party}</span>
            </div>
            {district.challenger && (() => {
              const isOpen = (district.incumbent ?? "").startsWith("(open");
              return (
                <div className="text-xs mt-0.5">
                  <span className="text-slate-500">
                    {isOpen ? `${district.challenger_party} nominee: ` : "vs "}
                  </span>
                  <span className={district.challenger_party === "(D)" ? "text-blue-700 font-medium" : district.challenger_party === "(R)" ? "text-red-700 font-medium" : "text-slate-700 font-medium"}>
                    {district.challenger}
                  </span>
                  {!isOpen && (
                    <> <span className="text-slate-400">{district.challenger_party}</span></>
                  )}
                </div>
              );
            })()}
            <div className="text-xs text-slate-500 mt-1">Lines: {district.lines}</div>
          </div>
          <div className="flex items-center gap-2">
            {onViewCounties && (
              <button
                onClick={() => onViewCounties(district.district)}
                className="text-xs px-2 py-1 rounded border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 whitespace-nowrap"
              >
                View county map
              </button>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-700 text-2xl leading-none">×</button>
          </div>
        </div>

        <div className="p-4 space-y-4">
          <section>
            <h3 className="text-xs uppercase text-slate-500 font-semibold mb-1">Projection</h3>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div>
                <div className="text-slate-500 text-xs">2024 margin</div>
                <div className="font-mono">{district.margin_2024?.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-slate-500 text-xs">Base</div>
                <div className="font-mono">{d.base_margin?.toFixed(1)}</div>
              </div>
              <div>
                <div className="text-slate-500 text-xs">Projected</div>
                <div className={`font-mono font-bold ${district.projection > 0 ? "text-blue-700" : "text-red-700"}`}>
                  {formatProjection(district.projection)}
                </div>
              </div>
            </div>
            <div className="mt-2 text-xs text-slate-600">
              Demographic contribution (this scenario):{" "}
              <span className={`font-mono ${district.demo_shift > 0 ? "text-blue-700" : district.demo_shift < 0 ? "text-red-700" : "text-slate-500"}`}>
                {district.demo_shift > 0 ? "+" : ""}{district.demo_shift.toFixed(2)}
              </span>
              {" "}({district.race_shift.toFixed(2)} race + {district.edu_shift.toFixed(2)} edu + {district.age_shift.toFixed(2)} age)
            </div>
          </section>

          <section>
            <h3 className="text-xs uppercase text-slate-500 font-semibold mb-2">Demographics</h3>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
              <DemoRow label="White (NH)" value={d.pct_white_nh} />
              <DemoRow label="Black" value={d.pct_black} />
              <DemoRow label="Hispanic" value={d.pct_hispanic} />
              <DemoRow label="Asian" value={d.pct_asian} />
              <DemoRow label="Other" value={d.pct_other} />
              <DemoRow label="College+" value={d.pct_college} />
              <DemoRow label="W college" value={d.pct_white_nh_college} />
              <DemoRow label="W non-college" value={d.pct_white_nh_non_college} />
              <DemoRow label="NW college" value={d.pct_nonwhite_college} />
              <DemoRow label="NW non-college" value={d.pct_nonwhite_non_college} />
              <DemoRow label="Under 30" value={d.pct_under_30} />
              <DemoRow label="65+" value={d.pct_65_plus} />
              <DemoRow label="Median age" value={d.median_age} suffix=" yrs" />
              <DemoRow label="Median income" value={d.median_income ? `$${Math.round(d.median_income / 1000)}k` : null} />
            </div>
            <div className="text-[10px] text-slate-400 mt-2">
              Source: {d.demo_source || district.demo_source}
              {(district.demo_source || "").endsWith("_old_lines") && (
                <span className="ml-1 italic">(estimated — pre-redistricting lines)</span>
              )}
            </div>
          </section>

          <section>
            <h3 className="text-xs uppercase text-slate-500 font-semibold mb-1">Model inputs</h3>
            <div className="text-xs space-y-1 text-slate-600">
              <div>State 2024 margin: <span className="font-mono">{d.state_margin_2024?.toFixed?.(1)}</span></div>
              <div>
                Relative trend:{" "}
                <span className="font-mono">
                  {(district.rel_trend_applied ?? district.rel_trend ?? 0).toFixed(2)}
                </span>
                {district.rel_trend_applied != null && district.rel_trend != null
                  && Math.abs(district.rel_trend_applied - district.rel_trend) > 1e-6 && (
                  <span className="ml-1 text-[10px] text-slate-400">
                    (raw {district.rel_trend.toFixed(2)} × current discount)
                  </span>
                )}
              </div>
              <div>WAR adj (discounted): <span className="font-mono">{(d.war_adj_discounted ?? 0).toFixed(2)}</span></div>
              <div>Incumbency adj: <span className="font-mono">{(d.incumbency_adj ?? 0).toFixed(2)}</span></div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function DemoRow({ label, value, suffix = "%" }: { label: string; value: number | string | null | undefined; suffix?: string }) {
  if (value == null || value === "") {
    return (
      <div className="flex justify-between border-b border-slate-100 py-0.5">
        <span className="text-slate-500">{label}</span>
        <span className="text-slate-300 text-xs">—</span>
      </div>
    );
  }
  const display = typeof value === "number" ? `${value}${suffix === "%" ? "%" : suffix}` : value;
  return (
    <div className="flex justify-between border-b border-slate-100 py-0.5">
      <span className="text-slate-700">{label}</span>
      <span className="font-mono">{display}</span>
    </div>
  );
}
