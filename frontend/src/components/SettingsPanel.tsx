import { MODEL_DEFAULTS } from "../types";

// Model settings (backend config.Settings). Each model-v4 change sits behind
// a toggle so it can be compared on and off. Changing a setting resets the
// scenario sliders to that setting's defaults (App re-fetches /api/defaults).

type Settings = Record<string, unknown>;

type Props = {
  settings: Settings;                 // overrides of the defaults
  onSettings: (next: Settings) => void;
};

type Toggle = { key: string; label: string; hint: string };

const GROUPS: { title: string; toggles: Toggle[] }[] = [
  {
    title: "Electorate composition (item 1)",
    toggles: [
      { key: "white_share_enabled", label: "2026 white-share target",
        hint: "Off: Catalist's 2022 midterm composition (white 75.8%)." },
    ],
  },
  {
    title: "Trend (item 2)",
    toggles: [
      { key: "trend_remove_demographic", label: "Remove demographic part",
        hint: "Remove the part of the 2020→2024 trend the electorate shares explain (the sliders model that movement)." },
      { key: "trend_remove_battleground", label: "Remove battleground part",
        hint: "Remove the 2024 battleground-state part of the trend. Off by default: all seven battlegrounds have a 2026 Senate or governor's race." },
      { key: "trend_center_states", label: "Center state trends nationally",
        hint: "Center the Senate's carried state trends on their 2024-vote-weighted national mean." },
      { key: "core_retention_scaling", label: "Scale new-lines rules by core retention",
        hint: "Scale the incumbent WAR discount and new-lines error by the share of the district that is new, instead of all-or-nothing." },
    ],
  },
  {
    title: "Group shifts (item 3)",
    toggles: [
      { key: "subgroup_n_weights", label: "Weight polls by subgroup size",
        hint: "Weight each poll's group margin by √(subgroup n) rather than √(total n)." },
      { key: "crosstab_white_only_polls", label: "Count white-only crosstabs",
        hint: "Include polls that report race only as White vs Non-white (Marist) in the white groups' averages. Off: only polls with Black or Hispanic crosstabs (D+8.8 instead of D+9.5)." },
      { key: "pollster_matched_shifts", label: "Pollster-matched pattern",
        hint: "Take the pattern across groups from each pollster's 2026 vs final-2024 change, net of its topline change. Off: 2026 poll average minus the 2024 baseline." },
      { key: "matched_inverse_variance", label: "Inverse-variance pooling",
        hint: "Combine pollsters' changes with 1/SE² weights rather than √n_eff." },
      { key: "matched_median_fallback", label: "Leave-one-out median rule",
        hint: "If dropping one pollster moves a group's average by more than 1.5 pts, use the weighted median." },
    ],
  },
  {
    title: "Error model (item 4)",
    toggles: [
      { key: "group_errors", label: "Group errors",
        hint: "Correlated misses by demographic group across districts and states (national total unchanged)." },
      { key: "national_extra_errors", label: "Composition + level errors",
        hint: "Two national terms, σ 1.0 each: who turns out, and crosstab measurement / 2024 baseline." },
    ],
  },
  {
    title: "County overlay (item 7)",
    toggles: [
      { key: "overlay_slice_projections", label: "Slice-level projections",
        hint: "Project each county slice from its own margin, demographic shift and shrunk residual trend, then one reconciling shift. Off: every slice shifted by the same amount. Map shading only — no projection changes." },
      { key: "overlay_raked_slices", label: "Raked 2024 slices (12 states)",
        hint: "In AK AR CT ID ME MI ND NJ OK OR PA SD (no 2024 precinct results), estimate each split county's slices by raking their 2020 D and R votes to the actual 2024 county and district totals. Off: 2020 margin + the district's 2020→2024 shift. Map shading only." },
    ],
  },
];

export function SettingsPanel({ settings, onSettings }: Props) {
  const defaults = MODEL_DEFAULTS.settings;
  const value = (k: string) => (k in settings ? settings[k] : defaults[k]);
  const set = (k: string, v: unknown) => {
    const next = { ...settings };
    if (v === defaults[k]) delete next[k]; else next[k] = v;
    onSettings(next);
  };
  const changed = Object.keys(settings).length;
  const whiteShare = Number(value("white_share") ?? 0.74);
  const incumbency = Number(value("house_incumbency") ?? 3.0);

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Model settings</h2>
        {changed > 0 && (
          <button onClick={() => onSettings({})}
                  className="text-xs px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded">
            Reset ({changed})
          </button>
        )}
      </div>
      <div className="text-[10px] text-slate-400 italic -mt-2">
        Changing a setting resets the sliders to that setting's defaults.
      </div>

      <div>
        <div className="flex items-baseline justify-between">
          <span className="text-slate-600">2026 white share of the electorate</span>
          <span className="font-mono">{(whiteShare * 100).toFixed(1)}%</span>
        </div>
        <input type="range" min={0.72} max={0.76} step={0.005} value={whiteShare}
               disabled={value("white_share_enabled") === false}
               onChange={(e) => set("white_share", Number(e.target.value))}
               className="w-full" aria-label="2026 white share" />
        <div className="flex justify-between text-[10px] text-slate-400">
          <span>72% (2024)</span><span>74% (default)</span><span>76% (2022)</span>
        </div>
      </div>

      <div>
        <div className="flex items-baseline justify-between">
          <span className="text-slate-600">House incumbency bonus</span>
          <span className="font-mono">±{incumbency.toFixed(1)}</span>
        </div>
        <input type="range" min={0} max={4} step={0.1} value={incumbency}
               onChange={(e) => set("house_incumbency", Number(e.target.value))}
               className="w-full" aria-label="House incumbency bonus" />
        <div className="flex gap-1 mt-0.5">
          {[{ v: 1.7, l: "1.7 (Split Ticket 2020)" }, { v: 3.0, l: "3.0 (2024, default)" }].map((p) => (
            <button key={p.v} onClick={() => set("house_incumbency", p.v)}
                    className={`flex-1 text-[10px] py-0.5 rounded border ${
                      Math.abs(incumbency - p.v) < 1e-6 ? "bg-slate-800 text-white border-slate-800"
                                                        : "bg-white text-slate-700 border-slate-300"}`}>
              {p.l}
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="flex items-baseline justify-between">
          <span className="text-slate-600">2024 group baseline</span>
          <select value={String(value("group_baseline") ?? "catalist")}
                  onChange={(e) => set("group_baseline", e.target.value)}
                  className="border border-slate-300 rounded px-1 py-0.5 text-xs">
            <option value="catalist">Catalist (default)</option>
            <option value="pew_validated">Pew validated voters</option>
          </select>
        </div>
      </div>

      <div>
        <div className="flex items-baseline justify-between">
          <span className="text-slate-600" title="County residual trends are shrunk toward the district's / state's with weight votes / (votes + k), 2024 votes.">
            Overlay trend shrinkage k (votes)
          </span>
          <input type="number" min={0} step={5000} value={Number(value("overlay_shrink_k") ?? 25000)}
                 onChange={(e) => { const v = Number(e.target.value); if (!Number.isNaN(v) && v >= 0) set("overlay_shrink_k", v); }}
                 className="w-20 text-right border border-slate-300 rounded px-1 py-0.5 font-mono text-xs" />
        </div>
      </div>

      {GROUPS.map((g) => (
        <div key={g.title} className="border-t pt-2">
          <div className="font-semibold uppercase text-[10px] text-slate-500 mb-1">{g.title}</div>
          {g.toggles.map((t) => (
            <label key={t.key} className="flex items-center gap-2 py-0.5 cursor-pointer" title={t.hint}>
              <input type="checkbox" checked={value(t.key) === true}
                     onChange={(e) => set(t.key, e.target.checked)} />
              <span className={k(t.key, settings)}>{t.label}</span>
            </label>
          ))}
        </div>
      ))}
    </div>
  );
}

// Highlight settings changed from their defaults.
function k(key: string, settings: Settings): string {
  return key in settings ? "text-amber-700 font-semibold" : "text-slate-700";
}
