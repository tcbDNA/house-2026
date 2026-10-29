// Label point of a (multi)polygon: the pole of inaccessibility of its largest
// polygon (the interior point farthest from its edges, after Mapbox's
// polylabel), so a concave or wrap-around district still gets a point inside
// it. Longitudes are scaled by cos(latitude) so distances follow the true
// shape. No imports: scripts/build_label_points.ts runs it under Node.

type Ring = number[][];
type Cell = { x: number; y: number; h: number; d: number; max: number };

export function labelPoint(geometry: { type: string; coordinates: any } | null): [number, number] | null {
  if (!geometry) return null;
  const polys: Ring[][] = geometry.type === "Polygon" ? [geometry.coordinates]
    : geometry.type === "MultiPolygon" ? geometry.coordinates : [];
  if (!polys.length) return null;
  let best = polys[0], bestArea = -1;
  for (const p of polys) {
    const a = Math.abs(ringArea(p[0]));
    if (a > bestArea) { best = p; bestArea = a; }
  }
  let minY = Infinity, maxY = -Infinity;
  for (const [, y] of best[0]) { minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
  const k = Math.cos(((minY + maxY) / 2) * Math.PI / 180);
  const [x, y] = polylabel(best.map((r) => r.map(([px, py]) => [px * k, py])));
  return [Math.round((x / k) * 1e4) / 1e4, Math.round(y * 1e4) / 1e4];
}

function ringArea(ring: Ring): number {
  let a = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    a += (ring[j][0] - ring[i][0]) * (ring[j][1] + ring[i][1]);
  }
  return a / 2;
}

function polylabel(rings: Ring[]): [number, number] {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const [x, y] of rings[0]) {
    minX = Math.min(minX, x); minY = Math.min(minY, y);
    maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
  }
  const w = maxX - minX, h = maxY - minY;
  const size = Math.min(w, h);
  if (size === 0) return [minX, minY];
  const precision = Math.max(w, h) / 200;
  const heap = new MaxHeap();
  for (let x = minX; x < maxX; x += size) {
    for (let y = minY; y < maxY; y += size) heap.push(cell(x + size / 2, y + size / 2, size / 2, rings));
  }
  let best = centroidCell(rings);
  const boxCell = cell(minX + w / 2, minY + h / 2, 0, rings);
  if (boxCell.d > best.d) best = boxCell;
  while (heap.size) {
    const c = heap.pop();
    if (c.d > best.d) best = c;
    if (c.max - best.d <= precision) continue;
    const h2 = c.h / 2;
    heap.push(cell(c.x - h2, c.y - h2, h2, rings));
    heap.push(cell(c.x + h2, c.y - h2, h2, rings));
    heap.push(cell(c.x - h2, c.y + h2, h2, rings));
    heap.push(cell(c.x + h2, c.y + h2, h2, rings));
  }
  return [best.x, best.y];
}

function cell(x: number, y: number, h: number, rings: Ring[]): Cell {
  const d = signedDistance(x, y, rings);
  return { x, y, h, d, max: d + h * Math.SQRT2 };
}

// Area-weighted centroid of the outer ring (the search's first guess).
function centroidCell(rings: Ring[]): Cell {
  const ring = rings[0];
  let area = 0, x = 0, y = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [ax, ay] = ring[i], [bx, by] = ring[j];
    const f = ax * by - bx * ay;
    x += (ax + bx) * f; y += (ay + by) * f; area += f * 3;
  }
  return area === 0 ? cell(ring[0][0], ring[0][1], 0, rings) : cell(x / area, y / area, 0, rings);
}

// Distance from (x, y) to the polygon's edges: positive inside, negative outside.
function signedDistance(x: number, y: number, rings: Ring[]): number {
  let inside = false, minSq = Infinity;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const a = ring[i], b = ring[j];
      if ((a[1] > y) !== (b[1] > y) && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
      minSq = Math.min(minSq, segmentDistSq(x, y, a, b));
    }
  }
  return (inside ? 1 : -1) * Math.sqrt(minSq);
}

function segmentDistSq(px: number, py: number, a: number[], b: number[]): number {
  let x = a[0], y = a[1];
  let dx = b[0] - x, dy = b[1] - y;
  if (dx !== 0 || dy !== 0) {
    const t = ((px - x) * dx + (py - y) * dy) / (dx * dx + dy * dy);
    if (t > 1) { x = b[0]; y = b[1]; } else if (t > 0) { x += dx * t; y += dy * t; }
  }
  dx = px - x; dy = py - y;
  return dx * dx + dy * dy;
}

class MaxHeap {
  private a: Cell[] = [];
  get size(): number { return this.a.length; }
  push(c: Cell): void {
    const a = this.a;
    a.push(c);
    let i = a.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (a[p].max >= a[i].max) break;
      [a[p], a[i]] = [a[i], a[p]]; i = p;
    }
  }
  pop(): Cell {
    const a = this.a, top = a[0], last = a.pop()!;
    if (a.length) {
      a[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let m = i;
        if (l < a.length && a[l].max > a[m].max) m = l;
        if (r < a.length && a[r].max > a[m].max) m = r;
        if (m === i) break;
        [a[m], a[i]] = [a[i], a[m]]; i = m;
      }
    }
    return top;
  }
}
