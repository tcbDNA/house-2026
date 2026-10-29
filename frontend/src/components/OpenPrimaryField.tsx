import { partyColorClass, type OpenPrimary } from "../types";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// "2026-11-03" -> "Nov 3" (parsed by hand: new Date() would read it as UTC midnight).
export function day(iso: string): string {
  const [, m, d] = iso.split("-").map(Number);
  return `${MONTHS[m - 1]} ${d}`;
}

/** An all-party primary's ballot, grouped by party in ballot order. `short`
 *  shows last names only (for the table). */
export function OpenPrimaryField({ primary, short = false }: { primary: OpenPrimary; short?: boolean }) {
  const groups = new Map<string, string[]>();
  for (const c of primary.candidates) {
    const name = short ? c.name.split(" ").slice(-1)[0] : c.name;
    groups.set(c.party, [...(groups.get(c.party) ?? []), name]);
  }
  const runoff = `If no one wins a majority, the top two meet in a ${day(primary.runoff)} runoff.`;
  return (
    <div className="text-[10px] mt-0.5 text-slate-500" title={`All-party primary, no nominees. ${runoff}`}>
      {day(primary.date)} open primary:{" "}
      {[...groups].map(([party, names], i) => (
        <span key={party}>
          {i > 0 && " · "}
          <span className={partyColorClass(party)}>{names.join(", ")}</span> {party}
        </span>
      ))}
      {!short && <div>{runoff}</div>}
    </div>
  );
}
