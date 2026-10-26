"""Minimal .xlsx reader (standard library only): rows of one worksheet as
lists of strings, so source spreadsheets saved under data/sources/ can be
read directly instead of retyping their numbers."""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _col_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_sheet(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.iter(f"{REL_NS}Relationship")}
        sheet = next(s for s in wb.find("m:sheets", NS) if s.get("name") == sheet_name)
        target = targets[sheet.get(f"{{{NS['r']}}}id")].lstrip("/")
        xml = ET.fromstring(z.read(target if target.startswith("xl/") else f"xl/{target}"))
        rows = []
        for row in xml.find("m:sheetData", NS):
            out: list[str] = []
            for c in row.findall("m:c", NS):
                i = _col_index(c.get("r"))
                v = c.find("m:v", NS)
                if c.get("t") == "s" and v is not None:
                    val = shared[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(t.text or "" for t in c.iter(f"{{{NS['m']}}}t"))
                else:
                    val = v.text if v is not None else ""
                out.extend([""] * (i - len(out)))
                out.append(val)
            rows.append(out)
        return rows
