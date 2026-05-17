import { useCallback, useEffect, useRef, useState } from "react";
import { SliderPanel } from "./components/SliderPanel";
import { NationalSummary } from "./components/NationalSummary";
import { DistrictTable } from "./components/DistrictTable";
import { BucketTable } from "./components/BucketTable";
import { Methodology } from "./components/Methodology";
import { DistrictDetail } from "./components/DistrictDetail";
import { DistrictMap } from "./components/DistrictMap";
import { SenateSummaryView } from "./components/SenateSummary";
import { SenateTable } from "./components/SenateTable";
import { SenateMap } from "./components/SenateMap";
import { CountyMap } from "./components/CountyMap";
import { fetchProjection, fetchSenate } from "./api";
import { CATALIST_BASELINES, DEFAULT_SLIDERS, SLIDER_DEFS, type District, type ProjectResponse, type SenateResponse, type SliderKey, type SliderValues } from "./types";

type Tab = "house" | "senate";
export type DemoFrame = "race" | "race_edu";

function readUrl(): { tab: Tab; env: number; sliders: SliderValues; trendDiscount: number; frame: DemoFrame } {
  const p = new URLSearchParams(window.location.search);
  const tab: Tab = window.location.hash === "#senate" ? "senate" : "house";
  // Default D+6.3 = current generic-ballot average per Silver Bulletin polling avg
  const env = Number(p.get("env") ?? "6.3");
  const out: SliderValues = { ...DEFAULT_SLIDERS };
  for (const s of SLIDER_DEFS) {
    const v = p.get(s.key);
    if (v != null && !Number.isNaN(Number(v))) out[s.key] = Number(v);
  }
  const tdRaw = p.get("trend");
  let trendDiscount = 0.5;
  if (tdRaw != null) {
    const tv = Number(tdRaw);
    if (!Number.isNaN(tv) && tv >= 0 && tv <= 1) trendDiscount = tv;
  }
  const frame: DemoFrame = p.get("frame") === "race_edu" ? "race_edu" : "race";
  return { tab, env: Number.isNaN(env) ? 6.3 : env, sliders: out, trendDiscount, frame };
}

function writeUrl(tab: Tab, env: number, sliders: SliderValues, trendDiscount: number, frame: DemoFrame) {
  const p = new URLSearchParams();
  if (env !== 6.3) p.set("env", String(env));
  for (const s of SLIDER_DEFS) {
    if (sliders[s.key] !== CATALIST_BASELINES[s.key]) {
      p.set(s.key, String(sliders[s.key]));
    }
  }
  if (trendDiscount !== 0.5) p.set("trend", String(trendDiscount));
  if (frame !== "race") p.set("frame", frame);
  const qs = p.toString();
  const hash = tab === "senate" ? "#senate" : "";
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
  const [houseResult, setHouseResult] = useState<ProjectResponse | null>(null);
  const [senateResult, setSenateResult] = useState<SenateResponse | null>(null);
  const [picked, setPicked] = useState<District | null>(null);
  const [pickedState, setPickedState] = useState<string | null>(null);
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
      } else {
        const r = await fetchSenate(env, s, td, ac.signal);
        setSenateResult(r);
      }
      setError(null);
    } catch (e: any) {
      if (e.name !== "AbortError") setError(e.message);
    }
  }, []);

  useEffect(() => {
    const t = window.setTimeout(() => {
      run(tab, environment, sliders, trendDiscount);
      writeUrl(tab, environment, sliders, trendDiscount, frame);
    }, 80);
    return () => window.clearTimeout(t);
  }, [tab, environment, sliders, trendDiscount, frame, run]);

  const onSlider = (k: SliderKey, v: number) => setSliders((cur) => ({ ...cur, [k]: v }));
  const onReset = () => { setEnvironment(6.3); setSliders(DEFAULT_SLIDERS); setTrendDiscount(0.5); setFrame("race"); };

  // Switching frames: snap the inactive axis's sliders back to baseline so
  // they contribute zero to demographic_shift. Keeps the model honest about
  // which axis is currently "telling the story."
  const onFrameChange = (next: DemoFrame) => {
    const RACE_KEYS: SliderKey[] = ["white_nh", "black", "hispanic", "asian"];
    const EDU_KEYS: SliderKey[] = [
      "white_college", "white_non_college", "nonwhite_college", "nonwhite_non_college",
    ];
    setSliders((cur) => {
      const reset = next === "race" ? EDU_KEYS : RACE_KEYS;
      const out = { ...cur };
      for (const k of reset) out[k] = CATALIST_BASELINES[k];
      return out;
    });
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
        <h1 className="text-2xl font-bold">2026 Scenario Tool</h1>
        <p className="text-sm text-slate-500">
          Demographic-driven projection model
        </p>
      </header>

      <div className="flex gap-1 border-b mb-4">
        {tabBtn("house", "House (435)")}
        {tabBtn("senate", "Senate (35 up)")}
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
            axisWeight={(tab === "house" ? houseResult : senateResult)?.axis_weight ?? 1}
            onEnvironment={setEnvironment}
            onSlider={onSlider}
            onSliders={setSliders}
            onTrendDiscount={setTrendDiscount}
            onFrame={onFrameChange}
            onReset={onReset}
          />
        </div>

        <div className="space-y-4">
          {tab === "house" && houseResult && (
            <>
              <NationalSummary summary={houseResult.summary} />
              <div className="hidden md:block">
                <DistrictMap
                  districts={houseResult.districts}
                  uniformSwing={houseResult.uniform_swing}
                  onPick={(id) => setPicked(houseResult.districts.find((d) => d.district === id) ?? null)}
                  selected={picked?.district ?? null}
                />
              </div>
              <BucketTable
                districts={houseResult.districts}
                onPick={(id) => setPicked(houseResult.districts.find((d) => d.district === id) ?? null)}
              />
              <DistrictTable
                districts={houseResult.districts}
                onPick={(id) => setPicked(houseResult.districts.find((d) => d.district === id) ?? null)}
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

          {tab === "house" && !houseResult && !error && <div className="text-slate-500">Loading…</div>}
          {tab === "senate" && !senateResult && !error && <div className="text-slate-500">Loading…</div>}

          {(houseResult || senateResult) && <Methodology />}
        </div>
      </div>

      <DistrictDetail district={picked} onClose={() => setPicked(null)} />
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
