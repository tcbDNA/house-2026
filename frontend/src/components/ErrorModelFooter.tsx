import type { ErrorModel } from "../types";

const GROUP_LABEL: Record<string, string> = {
  white_nh: "white", black: "Black", hispanic: "Hispanic", asian: "Asian",
  white_college: "white college", white_non_college: "white non-college",
  nonwhite_college: "non-white college", nonwhite_non_college: "non-white non-college",
};

// Every error term the simulation actually used (backend
// probability.error_model_summary), so the footer can't drift from the model.
export function ErrorModelFooter({ model }: { model?: ErrorModel }) {
  if (!model) return null;
  const terms: string[] = [`national polling ${model.national}`];
  if (model.composition) terms.push(`composition ${model.composition}`);
  if (model.level) terms.push(`level ${model.level}`);
  terms.push(`region ${model.region}`);
  if (model.state) terms.push(`state ${model.state}`);
  terms.push(`race ${model.race}`);
  terms.push(`+${model.open_seat_extra} open seat`);
  if (model.new_lines_extra) terms.push(`+${model.new_lines_extra} × share new on new lines`);
  const groups = Object.entries(model.groups).filter(([, g]) => g.sigma > 0);
  return (
    <div className="text-[10px] text-slate-400 italic mt-1">
      Monte Carlo ({model.n_sims.toLocaleString()} sims), σ in pts: {terms.join(" · ")}
      {groups.length > 0 && (
        <>
          {" "}· group errors (demeaned; national total unchanged):{" "}
          {groups.map(([g, v]) => `${GROUP_LABEL[g] ?? g} ${v.sigma.toFixed(1)}`).join(", ")}
        </>
      )}
      . Extras for open seats and new lines are added in quadrature.
    </div>
  );
}
