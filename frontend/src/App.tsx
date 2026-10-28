import { useCallback, useEffect, useRef, useState } from "react";
import { SliderPanel } from "./components/SliderPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { NationalSummary } from "./components/NationalSummary";
import { DistrictTable } from "./components/DistrictTable";
import { BucketTable } from "./components/BucketTable";
import { Methodology } from "./components/Methodology";
import { DistrictMap } from "./components/DistrictMap";
import { SenateSummaryView } from "./components/SenateSummary";
import { SenateTable } from "./components/SenateTable";
import { SenateMap } from "./components/SenateMap";
import { GovernorSummaryView } from "./components/GovernorSummary";
import { GovernorTable } from "./components/GovernorTable";
import { GovernorMap } from "./components/GovernorMap";
import { CountyMap } from "./components/CountyMap";
import { fetchDefaults, fetchGovernors, fetchProjection, fetchSenate, setRequestContext } from "./api";
import {
  AXIS_KEYS, CATALIST_BASELINES, DEFAULT_SLIDERS, EDU_FRAME_DEFAULTS, MODEL_DEFAULTS, SLIDER_DEFS,
  applyModelDefaults, compositionalShift,
  type GovernorResponse, type ProjectResponse, type SenateResponse, type SliderKey, type SliderValues,
} from "./types";

type Tab = "house" | "senate" | "governors";
export type DemoFrame = "race" | "race_edu";

// Defaults (uniform wave, slider positions, national shares) come from the
// backend's /api/defaults (environment.default_scenario), installed in
// main.tsx before the first render: the wave is the 2024 level plus the
// "other" race group's shift, and the race sliders carry each group's shift
// since 2024 at its poll-average margin.

// Slider defaults per frame. The inactive demographic axis sits at its 2024
// baseline so the two frames never double-count.
function frameDefaults(frame: DemoFrame): SliderValues {
  if (frame === "race") return DEFAULT_SLIDERS;
  const out: SliderValues = { ...DEFAULT_SLIDERS, ...EDU_FRAME_DEFAULTS };
  for (const k of AXIS_KEYS.race) out[k] = CATALIST_BASELINES[k];
  return out;
}

// Uniform wave that gives the same national total in either frame.
function frameDefaultEnv(frame: DemoFrame): number {
  if (frame === "race") return MODEL_DEFAULTS.wave;
  const total = MODEL_DEFAULTS.wave + compositionalShift(DEFAULT_SLIDERS);
  return total - compositionalShift(frameDefaults(frame));
}

function readUrl(): { tab: Tab; env: number; sliders: SliderValues; trendDiscount: number; frame: DemoFrame } {
  const p = new URLSearchParams(window.location.search);
  const h = window.location.hash;
  const tab: Tab = h === "#senate" ? "senate" : h === "#governors" ? "governors" : "house";
  const frame: DemoFrame = p.get("frame") === "race_edu" ? "race_edu" : "race";
  const env = Number(p.get("env") ?? frameDefaultEnv(frame));
  const out: SliderValues = { ...frameDefaults(frame) };
  for (const s of SLIDER_DEFS) {
    const v = p.get(s.key);
    if (v != null && !Number.isNaN(Number(v))) out[s.key] = Number(v);
  }
  const tdRaw = p.get("trend");
  let trendDiscount = MODEL_DEFAULTS.trend;
  if (tdRaw != null) {
    const tv = Number(tdRaw);
    if (!Number.isNaN(tv) && tv >= -1 && tv <= 1) trendDiscount = tv;
  }
  return { tab, env: Number.isNaN(env) ? frameDefaultEnv(frame) : env, sliders: out, trendDiscount, frame };
}

function writeUrl(tab: Tab, env: number, sliders: SliderValues, trendDiscount: number, frame: DemoFrame) {
  const p = new URLSearchParams();
  if (env !== frameDefaultEnv(frame)) p.set("env", String(env));
  const defaults = frameDefaults(frame);
  for (const s of SLIDER_DEFS) {
    if (sliders[s.key] !== defaults[s.key]) {
      p.set(s.key, String(sliders[s.key]));
    }
  }
  if (trendDiscount !== MODEL_DEFAULTS.trend) p.set("trend", String(trendDiscount));
  if (frame !== "race") p.set("frame", frame);
  const qs = p.toString();
  const hash = tab === "house" ? "" : `#${tab}`;
  const next = (qs ? `?${qs}` : window.location.pathname) + hash;
  window.history.replaceState(null, "", next);
}

export default function App() {
  const initial = readUrl();
  const [tab, setTab] = useState<Tab>(initial.tab);
  const [environment, setEnvironment] = useState<number>(initial.env);
  const [sliders, setSliders] = useState<SliderValues>(initial.sliders);
  const [trendDiscount, setTrendDiscount] = useState<number>(initial.trendDiscount);
  const [frame, setFrame] = useState<DemoFrame>(initial.frame);
  // Model-settings overrides (config.Settings); not kept in the URL.
  const [settings, setSettings] = useState<Record<string, unknown>>({});
  const [houseResult, setHouseResult] = useState<ProjectResponse | null>(null);
  const [senateResult, setSenateResult] = useState<SenateResponse | null>(null);
  const [governorResult, setGovernorResult] = useState<GovernorResponse | null>(null);
  const [pickedState, setPickedState] = useState<string | null>(null);
  const [pickedDistrictCounties, setPickedDistrictCounties] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const run = useCallback(async (currentTab: Tab, env: number, s: SliderValues, td: number) => {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    try {
      if (currentTab === "house") {
        const r = await fetchProjection(env, s, td, ac.signal);
        setHouseResult(r);
      } else if (currentTab === "senate") {
        const r = await fetchSenate(env, s, td, ac.signal);
        setSenateResult(r);
      } else {
        const r = await fetchGovernors(env, s, td, ac.signal);
        setGovernorResult(r);
      }
      setError(null);
    } catch (e: any) {
      if (e.name !== "AbortError") setError(e.message);
    }
  }, []);

  useEffect(() => {
    setRequestContext({ frame, settings });
    const t = window.setTimeout(() => {
      run(tab, environment, sliders, trendDiscount);
      writeUrl(tab, environment, sliders, trendDiscount, frame);
    }, 80);
    return () => window.clearTimeout(t);
  }, [tab, environment, sliders, trendDiscount, frame, settings, run]);

  // New settings change the default scenario (wave, slider positions, shares):
  // fetch it and reset the sliders to it.
  const onSettings = async (next: Record<string, unknown>) => {
    try {
      const d = await fetchDefaults(next);
      applyModelDefaults(d);
      setSettings(next);
      setEnvironment(frameDefaultEnv(frame));
      setSliders({ ...frameDefaults(frame) });
      setError(null);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const onSlider = (k: SliderKey, v: number) => setSliders((cur) => ({ ...cur, [k]: v }));
  const onReset = () => { setEnvironment(MODEL_DEFAULTS.wave); setSliders({ ...DEFAULT_SLIDERS }); setTrendDiscount(MODEL_DEFAULTS.trend); setFrame("race"); };

  // Switching frames: the axis being left snaps back to its 2024 baseline (so
  // it contributes zero to demographic_shift) and the axis being entered
  // starts at its poll-average defaults. The uniform wave absorbs the
  // difference so the national total doesn't change.
  const onFrameChange = (next: DemoFrame) => {
    if (next === frame) return;
    const entering = next === "race" ? AXIS_KEYS.race : AXIS_KEYS.edu;
    const leaving = next === "race" ? AXIS_KEYS.edu : AXIS_KEYS.race;
    const defaults = frameDefaults(next);
    const out = { ...sliders };
    for (const k of leaving) out[k] = CATALIST_BASELINES[k];
    for (const k of entering) out[k] = defaults[k];
    const total = environment + compositionalShift(sliders);
    setEnvironment(total - compositionalShift(out));
    setSliders(out);
    setFrame(next);
  };

  const tabBtn = (id: Tab, label: string) => (
    <button
      onClick={() => setTab(id)}
      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
        tab === id
          ? "border-slate-800 text-slate-900"
          : "border-transparent text-slate-500 hover:text-slate-700"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen p-3 sm:p-6 max-w-7xl mx-auto">
      <header className="mb-3">
        <h1 className="text-2xl font-bold">2026 US Midterm Election Predictions</h1>
      </header>

      <div className="flex gap-1 border-b mb-4">
        {tabBtn("house", "House (435)")}
        {tabBtn("senate", "Senate (35 up)")}
        {tabBtn("governors", "Governors (36 up)")}
      </div>

      {error && (
        <div className="mb-3 p-3 bg-red-100 text-red-800 text-sm rounded">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-4">
        <div className="space-y-4">
          <SliderPanel
            environment={environment}
            sliders={sliders}
            trendDiscount={trendDiscount}
            frame={frame}
            onEnvironment={setEnvironment}
            onSlider={onSlider}
            onSliders={setSliders}
            onTrendDiscount={setTrendDiscount}
            onFrame={onFrameChange}
            onReset={onReset}
          />
          <SettingsPanel settings={settings} onSettings={onSettings} />
        </div>

        <div className="space-y-4">
          {tab === "house" && houseResult && (
            <>
              <NationalSummary summary={houseResult.summary} nationalMargin={houseResult.national_margin} />
              <div className="hidden md:block">
                <DistrictMap
                  districts={houseResult.districts}
                  uniformSwing={houseResult.uniform_swing}
                  onPick={(id) => setPickedDistrictCounties(id)}
                  selected={pickedDistrictCounties}
                />
              </div>
              <BucketTable
                districts={houseResult.districts}
                onPick={(id) => setPickedDistrictCounties(id)}
              />
              <DistrictTable
                districts={houseResult.districts}
                onPick={(id) => setPickedDistrictCounties(id)}
              />
            </>
          )}

          {tab === "senate" && senateResult && (
            <>
              <SenateSummaryView summary={senateResult.summary} />
              <div className="hidden md:block">
                <SenateMap
                  seats={senateResult.seats}
                  uniformSwing={senateResult.uniform_swing}
                  onPickState={setPickedState}
                />
              </div>
              <BucketTable seats={senateResult.seats} title="Competitive Senate seats by bucket" />
              <SenateTable seats={senateResult.seats} notUpD={senateResult.summary.not_up_d} />
            </>
          )}

          {tab === "governors" && governorResult && (
            <>
              <GovernorSummaryView summary={governorResult.summary} />
              <div className="hidden md:block">
                <GovernorMap races={governorResult.races} />
              </div>
              <GovernorTable races={governorResult.races} />
            </>
          )}

          {tab === "house" && !houseResult && !error && <div className="text-slate-500">Loading…</div>}
          {tab === "governors" && !governorResult && !error && <div className="text-slate-500">Loading…</div>}
          {tab === "senate" && !senateResult && !error && <div className="text-slate-500">Loading…</div>}

          {(houseResult || senateResult || governorResult) && <Methodology />}
        </div>
      </div>

      {pickedDistrictCounties && (
        <CountyMap
          state={pickedDistrictCounties.split("-")[0]}
          district={pickedDistrictCounties}
          environment={environment}
          sliders={sliders}
          trendDiscount={trendDiscount}
          onClose={() => setPickedDistrictCounties(null)}
        />
      )}
      {pickedState && (() => {
        const seat = senateResult?.seats.find((s) => s.state === pickedState);
        const indWinner = !!seat && seat.projection > 0
          && (seat.party === "(I)" || seat.challenger_party === "(I)");
        return (
          <CountyMap
            state={pickedState}
            environment={environment}
            sliders={sliders}
            trendDiscount={trendDiscount}
            indWinner={indWinner}
            onClose={() => setPickedState(null)}
          />
        );
      })()}
    </div>
  );
}
