"""Download Census cb_2024_us_cd119_500k shapefile and emit a simplified
GeoJSON keyed by district ID matching v18 (e.g. TX-28, WY-AL).

Output: frontend/public/districts.geojson
"""

import io
import json
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen

import shapefile  # pyshp

DATA_DIR = Path(__file__).resolve().parent
CACHE = DATA_DIR / "cache"
CACHE.mkdir(exist_ok=True)
OUT = DATA_DIR.parent.parent / "frontend" / "public" / "districts.geojson"

CENSUS_URL = (
    "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_cd119_5m.zip"
)
STATE_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}
AT_LARGE = {"AK", "DE", "ND", "SD", "VT", "WY"}

COORD_PRECISION = 5  # ~1 meter at the equator — far smaller than 1:500k accuracy


def round_coords(coords, geom_type):
    p = COORD_PRECISION
    if geom_type == "Polygon":
        return [[[round(x, p), round(y, p)] for x, y in ring] for ring in coords]
    if geom_type == "MultiPolygon":
        return [[[[round(x, p), round(y, p)] for x, y in ring] for ring in poly] for poly in coords]
    return coords


def cd_label(state_fips: str, cd_code: str) -> str | None:
    state = STATE_FIPS.get(state_fips)
    if state is None:
        return None
    if cd_code in ("ZZ", "98", "99"):
        return None
    if state in AT_LARGE:
        return f"{state}-AL"
    try:
        return f"{state}-{int(cd_code):02d}"
    except ValueError:
        return None


def main():
    zip_path = CACHE / "cb_2024_us_cd119_5m.zip"
    if not zip_path.exists():
        print(f"downloading {CENSUS_URL}", file=sys.stderr)
        with urlopen(CENSUS_URL, timeout=120) as r:
            zip_path.write_bytes(r.read())

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        shp = next(n for n in names if n.endswith(".shp"))
        shx = next(n for n in names if n.endswith(".shx"))
        dbf = next(n for n in names if n.endswith(".dbf"))
        reader = shapefile.Reader(
            shp=z.open(shp), shx=z.open(shx), dbf=z.open(dbf)
        )
        fields = [f[0] for f in reader.fields[1:]]  # skip deletion flag
        si = fields.index("STATEFP")
        ci = fields.index("CD119FP") if "CD119FP" in fields else fields.index("CDFP")

        features = []
        for sr in reader.iterShapeRecords():
            rec = sr.record
            state_fips = rec[si]
            cd_code = rec[ci]
            label = cd_label(state_fips, cd_code)
            if label is None:
                continue
            geo = sr.shape.__geo_interface__
            # __geo_interface__ returns tuples; cast to lists so JSON encoding is plain arrays
            if geo["type"] == "Polygon":
                geo["coordinates"] = [list(ring) for ring in geo["coordinates"]]
            elif geo["type"] == "MultiPolygon":
                geo["coordinates"] = [[list(ring) for ring in poly] for poly in geo["coordinates"]]
            geo["coordinates"] = round_coords(geo["coordinates"], geo["type"])
            features.append({
                "type": "Feature",
                "id": label,
                "properties": {"district": label, "state": label.split("-")[0]},
                "geometry": geo,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fc = {"type": "FeatureCollection", "features": features}
    OUT.write_text(json.dumps(fc, separators=(",", ":")))
    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"wrote {OUT} with {len(features)} districts ({size_mb:.2f} MB)", file=sys.stderr)


if __name__ == "__main__":
    main()
