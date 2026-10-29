// Writes public/district_points.json and public/state_points.json: one label
// point per district and state, where the maps' "Shift from 2024" arrows
// start (county points are computed in the browser from the county GeoJSON).
// Re-run after changing districts.geojson or states.geojson:
//   node scripts/build_label_points.ts      (from frontend/)
import { readFileSync, writeFileSync } from "node:fs";
import { labelPoint } from "../src/labelPoint.ts";

for (const [src, out, key] of [
  ["public/districts.geojson", "public/district_points.json", "district"],
  ["public/states.geojson", "public/state_points.json", "state"],
]) {
  const gj = JSON.parse(readFileSync(src, "utf8"));
  const points: Record<string, [number, number]> = {};
  for (const f of gj.features) {
    const p = labelPoint(f.geometry);
    if (p) points[f.properties[key]] = p;
  }
  writeFileSync(out, JSON.stringify(points) + "\n");
  console.log(`${out}: ${Object.keys(points).length} points`);
}
