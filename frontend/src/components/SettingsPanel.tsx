import { useEffect, useState, type ReactNode } from "react";
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
    title: "District weights",
    toggles: [
      { key: "district_weights_2024_votes", label: "2024 votes in all 435 districts",
        hint: "Weight districts by 2024 presidential votes everywhere (correction, Oct 27). Off: 2020 votes in AK AR CT ID ME MI ND NJ OK OR PA SD, the old weights." },
      { key: "la_enacted_demographics", label: "Louisiana demographics on the enacted map",
        hint: "Louisiana's district demographics from the Legislature's block file for the enacted map (correction, Oct 29). Off: the old values, built from a different plan (LA-06 58% Black, LA-02 70% white)." },
      { key: "acs_2020_2024", label: "2020–2024 Census ACS demographics",
        hint: "District, state and county demographics from the ACS 2020–2024 5-year estimates, on the 2024 district lines (update, Oct 29). Off: 2019–2023, whose district tables put Georgia's districts on the pre-2024 map (GA-06 64% white, 9% Black)." },
    ],
  },
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
        hint: "Include polls that report race only as White vs Non-white (Marist) in the white groups' averages. Off: only polls with Black or Hispanic crosstabs (D+9.5 instead of D+9.9)." },
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
    title: "Governors",
    toggles: [
      { key: "governor_poll_blend", label: "Blend governor polls",
        hint: "Projection = w × (polling average + scenario change) + (1 − w) × model, w 0.79 with 3+ polls. Off: the model alone." },
      { key: "governor_war_single_record_full", label: "Full weight on a single governor record",
        hint: "A candidate whose only governor record is one race gets full weight on it instead of half (governors only; the 2018/2022 calibration fits better with it)." },
      { key: "governor_war_drop_rematch", label: "Rematches: the incumbent keeps the record",
        hint: "Drop a challenger's governor record from an earlier race against the sitting incumbent (MD Cox, IL Bailey, OR Drazan), as the House model does." },
      { key: "governor_war_exclude_third_candidate", label: "Leave out third-candidate records",
        hint: "Computed governor records from races where a third candidate won over 5% (e.g. OR 2022, Betsy Johnson) are left out." },
      { key: "governor_param_draws", label: "Slope and incumbency uncertainty",
        hint: "Each simulation draws one partisan slope and one incumbency bonus (the calibration's standard errors), shared by every governor race." },
      { key: "governor_three_way", label: "Three-way odds in Rhode Island",
        hint: "Each simulation also draws the Republican's margin over independent Ken Block around its polling average (same error size, correlation 0.5), and the candidate with the most votes wins. Off: Foulkes vs Block only." },
    ],
  },
  {
    title: "County overlay (item 7)",
    toggles: [
      { key: "overlay_slice_projections", label: "Slice-level projections",
        hint: "Project each county slice from its own margin, demographic shift and shrunk residual trend, then one reconciling shift. Off: every slice shifted by the same amount. Map shading only — no projection changes." },
      { key: "overlay_raked_slices", label: "Raked 2024 slices (12 states)",
        hint: "In AK AR CT ID ME MI ND NJ OK OR PA SD (no 2024 precinct results), estimate each split county's slices by raking their 2020 D and R votes to the actual 2024 county and district totals. Off: 2020 margin + the district's 2020→2024 shift. Map shading only." },
      { key: "overlay_estimated_slice_trends", label: "County trends in those 12 states",
        hint: "Give their slices their county's own residual trend, shrunk toward the district's as elsewhere (the county results are real). Alaska keeps the district's: its borough results are estimated. Off: every slice takes the district's residual. Map shading only." },
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

      <SettingSlider label="2026 white share of the electorate" ariaLabel="2026 white share"
                     value={whiteShare} min={0.72} max={0.76} step={0.005}
                     format={(v) => `${(v * 100).toFixed(1)}%`}
                     disabled={value("white_share_enabled") === false}
                     onCommit={(v) => set("white_share", v)}>
        <div className="flex justify-between text-[10px] text-slate-400">
          <span>72% (2024)</span><span>74% (default)</span><span>76% (2022)</span>
        </div>
      </SettingSlider>

      <SettingSlider label="House incumbency bonus" ariaLabel="House incumbency bonus"
                     value={incumbency} min={0} max={4} step={0.1}
                     format={(v) => `±${v.toFixed(1)}`}
                     onCommit={(v) => set("house_incumbency", v)}>
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
      </SettingSlider>

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

// A slider for a numeric setting. A settings change refetches the default
// scenario and reruns the model (seconds on the server), so the slider shows
// the dragged value at once but applies it only on release (pointer up, key up
// or blur), once, and keeps showing it until the new setting arrives.
function SettingSlider({ label, ariaLabel, value, min, max, step, format, disabled, onCommit, children }: {
  label: string; ariaLabel: string; value: number; min: number; max: number; step: number;
  format: (v: number) => string; disabled?: boolean; onCommit: (v: number) => void; children?: ReactNode;
}) {
  const [draft, setDraft] = useState<number | null>(null);
  const [pending, setPending] = useState(false);
  useEffect(() => { setDraft(null); setPending(false); }, [value]);
  const shown = draft ?? value;
  const commit = () => {
    if (draft == null || pending) return;
    if (Math.abs(draft - value) < 1e-9) { setDraft(null); return; }
    setPending(true);
    onCommit(draft);
  };
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-slate-600">{label}</span>
        <span className="font-mono">
          {pending && <span className="text-[10px] text-slate-400 mr-1">applying…</span>}
          {format(shown)}
        </span>
      </div>
      <input type="range" min={min} max={max} step={step} value={shown} disabled={disabled}
             onChange={(e) => { setPending(false); setDraft(Number(e.target.value)); }}
             onPointerUp={commit} onKeyUp={commit} onBlur={commit}
             className="w-full" aria-label={ariaLabel} />
      {children}
    </div>
  );
}

// Highlight settings changed from their defaults.
function k(key: string, settings: Settings): string {
  return key in settings ? "text-amber-700 font-semibold" : "text-slate-700";
}
