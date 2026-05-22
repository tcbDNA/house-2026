import {
  CATALIST_BASELINES, CATALIST_ELECTORATE_SHARES_AGE,
  CATALIST_ELECTORATE_SHARES_EDU, CATALIST_ELECTORATE_SHARES_RACE,
  CATALIST_PRESETS, OTHER_RACE_BASELINE, formatMargin, formatPartySplit,
  SLIDER_DEFS, type SliderKey, type SliderValues,
} from "../types";

type DemoFrame = "race" | "race_edu";

type Props = {
  environment: number;
  sliders: SliderValues;
  trendDiscount: number;
  frame: DemoFrame;
  axisWeight: number;
  onEnvironment: (v: number) => void;
  onSlider: (k: SliderKey, v: number) => void;
  onSliders: (v: SliderValues) => void;
  onTrendDiscount: (v: number) => void;
  onFrame: (f: DemoFrame) => void;
  onReset: () => void;
};

// Cycle preset UI disabled — kept here in case we want to bring it back.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _CYCLE_PRESETS_UNUSED: { key: "2024" | "2022" | "2020"; label: string; hint: string }[] = [
  { key: "2024", label: "2024", hint: "Trump coalition — Hispanic R-shift complete (default baseline)" },
  { key: "2022", label: "2022", hint: "Midterm — post-Dobbs youth surge, partial Hispanic R-shift" },
  { key: "2020", label: "2020", hint: "Biden coalition peak — strong Hispanic/Asian/youth D margins" },
];

// Implied national environment from each axis = electorate share × group margin,
// summed. Computed independently per axis. The two values should be roughly
// equal in any sensible scenario — divergence signals an internally-inconsistent
// slider set (e.g. moving white_nh sharply R but leaving white-edu cells alone).
function impliedEnvRace(s: SliderValues): number {
  const sh = CATALIST_ELECTORATE_SHARES_RACE;
  return (
    sh.white_nh * s.white_nh +
    sh.black    * s.black    +
    sh.hispanic * s.hispanic +
    sh.asian    * s.asian    +
    sh.other    * OTHER_RACE_BASELINE
  );
}

function impliedEnvEdu(s: SliderValues): number {
  const sh = CATALIST_ELECTORATE_SHARES_EDU;
  return (
    sh.white_college        * s.white_college        +
    sh.white_non_college    * s.white_non_college    +
    sh.nonwhite_college     * s.nonwhite_college     +
    sh.nonwhite_non_college * s.nonwhite_non_college
  );
}

function impliedEnvAge(s: SliderValues): number {
  const sh = CATALIST_ELECTORATE_SHARES_AGE;
  return (
    sh.under_30    * s.under_30 +
    sh.age_30_44   * s.age_30_44 +
    sh.age_45_64   * s.age_45_64 +
    sh.age_65_plus * s.age_65_plus
  );
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function _activePreset_unused(sliders: SliderValues, frame: DemoFrame): "2020" | "2022" | "2024" | null {
  // Only compare sliders that are actually editable under the current frame.
  // Inactive-axis sliders are pinned at baseline and irrelevant to "which cycle preset is on."
  const ageKeys: SliderKey[] = ["under_30", "age_30_44", "age_45_64", "age_65_plus"];
  const keysToCheck: SliderKey[] = frame === "race"
    ? ["white_nh", "black", "hispanic", "asian", ...ageKeys]
    : ["white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college", ...ageKeys];
  for (const k of ["2024", "2022", "2020"] as const) {
    const preset = CATALIST_PRESETS[k];
    const match = keysToCheck.every(
      (key) => Math.abs(preset[key] - sliders[key]) < 1e-6,
    );
    if (match) return k;
  }
  return null;
}

const TREND_PRESETS: { value: number; label: string; hint: string }[] = [
  { value: 1.0, label: "Full",    hint: "trends persist at full strength (default)" },
  { value: 0.5, label: "Partial", hint: "50% mean-reversion — useful for >1 cycle out" },
  { value: 0.0, label: "None",    hint: "pure structural baseline — no trend term" },
];

const axisLabel: Record<"race" | "edu" | "age", string> = {
  race: "Race / ethnicity",
  edu: "Race × education",
  age: "Age",
};

export function SliderPanel({
  environment, sliders, trendDiscount, frame, axisWeight,
  onEnvironment, onSlider, onSliders, onTrendDiscount, onFrame, onReset,
}: Props) {
  // Cycle preset disabled — baseline is fixed at Catalist 2024.
  // const preset = activePreset(sliders, frame);

  // Compositional shift is the DELTA from the Catalist 2024 baseline implied
  // env. At default sliders both deltas are 0. Moving sliders shifts each
  // axis's implied popvote; the delta is what the model adds to projections.
  const impliedDemoNow      = frame === "race" ? impliedEnvRace(sliders)           : impliedEnvEdu(sliders);
  const impliedDemoBaseline = frame === "race" ? impliedEnvRace(CATALIST_BASELINES) : impliedEnvEdu(CATALIST_BASELINES);
  const impliedAgeNow       = impliedEnvAge(sliders);
  const impliedAgeBaseline  = impliedEnvAge(CATALIST_BASELINES);
  const impliedDemo = impliedDemoNow - impliedDemoBaseline;
  const impliedAge  = impliedAgeNow  - impliedAgeBaseline;

  // Anti-double-count: race-or-edu axis and the age axis describe the same
  // voters. Backend halves the contribution when both are moved; display
  // matches.
  const ageKeysForCheck: SliderKey[] = ["under_30", "age_30_44", "age_45_64", "age_65_plus"];
  const demoKeysForCheck: SliderKey[] = frame === "race"
    ? ["white_nh", "black", "hispanic", "asian"]
    : ["white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college"];
  const isAxisMoved = (ks: SliderKey[]) => ks.some((k) => Math.abs(sliders[k] - CATALIST_BASELINES[k]) > 1e-6);
  const demoMoved = isAxisMoved(demoKeysForCheck);
  const ageMoved = isAxisMoved(ageKeysForCheck);
  const compositionalWeight = demoMoved && ageMoved ? 0.5 : 1.0;
  const implied = compositionalWeight * (impliedDemo + impliedAge);
  // Cycle preset disabled — kept for future re-enable.
  // const applyPreset = (cycleKey: "2020" | "2022" | "2024") => {
  //   const preset = CATALIST_PRESETS[cycleKey];
  //   const out: SliderValues = { ...sliders };
  //   const ageKeys: SliderKey[] = ["under_30", "age_30_44", "age_45_64", "age_65_plus"];
  //   const activeKeys: SliderKey[] = frame === "race"
  //     ? ["white_nh", "black", "hispanic", "asian", ...ageKeys]
  //     : ["white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college", ...ageKeys];
  //   for (const k of activeKeys) out[k] = preset[k];
  //   onSliders(out);
  // };
  // Race axis = the 4 race sliders. Edu axis = the 4 race×edu cells. Only one
  // is active at a time (Option 2 / "Demographic frame" toggle), to eliminate
  // the race ↔ race×edu double-count problem. Age is independent and always shown.
  const grouped = {
    race: frame === "race"     ? SLIDER_DEFS.filter((s) => s.axis === "race") : [],
    edu:  frame === "race_edu" ? SLIDER_DEFS.filter((s) => s.axis === "edu")  : [],
    age:  SLIDER_DEFS.filter((s) => s.axis === "age"),
  };

  const envSign = environment >= 0 ? "D" : "R";
  const envMag = Math.abs(environment).toFixed(1);

  // A slider is "moved" only when it's pushed off its Catalist baseline.
  const isMoved = (k: SliderKey) => Math.abs(sliders[k] - CATALIST_BASELINES[k]) > 1e-6;

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Scenario</h2>
        <button
          onClick={onReset}
          className="text-xs px-2 py-1 bg-slate-100 hover:bg-slate-200 rounded"
        >
          Reset
        </button>
      </div>

      <div className="bg-slate-50 rounded p-3 space-y-2">
        <div className="flex items-baseline justify-between">
          <h3 className="text-xs font-semibold uppercase text-slate-500">National environment</h3>
          <span
            className={`text-sm font-mono font-semibold ${
              environment + implied > 0
                ? "text-blue-700"
                : environment + implied < 0
                ? "text-red-700"
                : "text-slate-700"
            }`}
            title="Total = Uniform wave (slider below) + Compositional shift (from demographic sliders)"
          >
            Total: {formatMargin(Math.round((environment + implied) * 10) / 10)}
          </span>
        </div>

        <div>
          <div className="flex items-baseline justify-between text-xs mb-0.5">
            <span className="text-slate-600">Uniform wave (unattributed)</span>
            <span className="font-mono">{envSign}+{envMag}</span>
          </div>
          <input
            type="range"
            min={-20}
            max={20}
            step={0.1}
            value={environment}
            onChange={(e) => onEnvironment(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
            <span>R+20</span><span>R+10</span><span>tie</span><span>D+10</span><span>D+20</span>
          </div>
        </div>

        <div
          className="pt-1 border-t border-slate-200 space-y-0.5 text-xs"
          title="Compositional shift (delta from 2024 baseline) attributable to your demographic sliders. Each axis is a separate reconstruction of the same electorate; when both are moved they're half-weighted to avoid double-counting."
        >
          <div className="flex justify-between">
            <span className="text-slate-600">
              {frame === "race" ? "Race shift" : "Race × Edu shift"}
            </span>
            <span className={`font-mono ${impliedDemo > 0 ? "text-blue-700" : impliedDemo < 0 ? "text-red-700" : "text-slate-500"}`}>
              {formatMargin(Math.round(impliedDemo * 10) / 10)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-600">Age shift</span>
            <span className={`font-mono ${impliedAge > 0 ? "text-blue-700" : impliedAge < 0 ? "text-red-700" : "text-slate-500"}`}>
              {formatMargin(Math.round(impliedAge * 10) / 10)}
            </span>
          </div>
          {compositionalWeight < 1 && (
            <div className="text-[10px] text-slate-400 italic pt-0.5">
              Both axes moved → 0.5× weighting applied to total (anti-double-count).
            </div>
          )}
        </div>
      </div>

      <div>
        <div className="flex items-baseline justify-between mb-1">
          <h3 className="text-xs font-semibold uppercase text-slate-500">
            Demographic frame
          </h3>
          <span className="text-[10px] text-slate-400">
            {frame === "race" ? "race axis" : "race × education"} · default: 2024
          </span>
        </div>
        <div className="flex gap-1">
          {([
            { key: "race",     label: "Race",         hint: "Adjust by racial group (white-NH / Black / Hispanic / Asian). Defaults parked at Catalist 2024 baselines; race×edu cells stay at 2024." },
            { key: "race_edu", label: "Race × Edu",   hint: "Adjust by race × education cells (white-college / white-non-college / etc.). Defaults parked at Catalist 2024 baselines; race sliders stay at 2024." },
          ] as const).map((opt) => {
            const active = frame === opt.key;
            return (
              <button
                key={opt.key}
                onClick={() => onFrame(opt.key)}
                title={opt.hint}
                className={`flex-1 text-xs py-1 px-2 rounded border transition-colors ${
                  active
                    ? "bg-slate-800 text-white border-slate-800"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
        <div className="text-[10px] text-slate-500 mt-1 italic">
          Sliders default to Catalist 2024 D-R margins (matching the 2024
          presidential baseline the rest of the model is built on). Move a slider
          away from default to model the group voting differently than 2024.
          Only one demographic axis active at a time to avoid double-counting.
        </div>
      </div>

      {/* Cycle preset (2020/2022/2024) UI removed — current baselines are
          locked to Catalist 2024. To re-enable historical scenario snap-in,
          restore this block and uncomment the related logic above. */}

      {(Object.keys(grouped) as ("race" | "edu" | "age")[])
        .filter((axis) => grouped[axis].length > 0)
        .map((axis) => (
        <div key={axis}>
          <h3 className="text-xs font-semibold uppercase text-slate-500 mb-2">{axisLabel[axis]}</h3>
          <div className="space-y-2">
            {grouped[axis].map((s) => {
              const v = sliders[s.key];
              const base = CATALIST_BASELINES[s.key];
              const moved = isMoved(s.key);
              const colorClass = v > 0 ? "text-blue-700" : v < 0 ? "text-red-700" : "text-slate-500";
              return (
                <div key={s.key}>
                  <div className="flex justify-between items-baseline text-xs mb-0.5">
                    <span>{s.label}</span>
                    <span className={`font-mono ${colorClass} ${moved ? "font-bold" : "opacity-70"}`}>
                      {formatMargin(v)}
                      <span className="ml-1 text-[10px] text-slate-400 font-normal">
                        ({formatPartySplit(v)})
                      </span>
                      {moved && (
                        <span className="ml-1 text-[10px] text-slate-400 font-normal">
                          · 2024: {formatMargin(base)}
                        </span>
                      )}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={s.min}
                    max={s.max}
                    step={1}
                    value={v}
                    onChange={(e) => onSlider(s.key, Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              );
            })}
          </div>
        </div>
      ))}

      <div className="border-t pt-2">
        <div className="flex items-baseline justify-between mb-1">
          <h3 className="text-xs font-semibold uppercase text-slate-500">
            Trend persistence
          </h3>
          <span className="text-[10px] text-slate-400">advanced</span>
        </div>
        <div className="flex gap-1">
          {TREND_PRESETS.map((p) => {
            const active = Math.abs(p.value - trendDiscount) < 1e-6;
            return (
              <button
                key={p.value}
                onClick={() => onTrendDiscount(p.value)}
                title={p.hint}
                className={`flex-1 text-xs py-1 px-2 rounded border transition-colors ${
                  active
                    ? "bg-slate-800 text-white border-slate-800"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                }`}
              >
                {p.label}
                <span className="block text-[9px] opacity-70 font-mono">
                  {p.value.toFixed(1)}×
                </span>
              </button>
            );
          })}
        </div>
        <div className="text-[10px] text-slate-500 mt-1 italic">
          Multiplies rel_trend (House) / state_trend (Senate). Default 1.0
          assumes 2020→2024 trends repeat in 2026.
        </div>
      </div>

      {axisWeight < 1 && (
        <div className="text-xs text-slate-500 italic border-t pt-2">
          Multiple axes (race / education / age) active: each axis is half-weighted
          to avoid double-counting voters.
        </div>
      )}
    </div>
  );
}
