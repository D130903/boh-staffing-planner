"""Build docs/index.html from data/covers_by_hour.csv and data/roster_by_hour.csv.

The page is self-contained apart from Plotly (CDN). All staffing maths runs in the browser so the
Day and Event-day filters work without a server.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(fn):
    with open(ROOT / "data" / fn, encoding="utf-8") as f:
        return list(csv.DictReader(f))


cov = read("covers_by_hour.csv")
ros = read("roster_by_hour.csv")
roster = {(r["outlet"], r["day"], int(r["hour"])): int(r["boh_staff_rostered"]) for r in ros}

outlets, seen = [], set()
for r in cov:
    if r["outlet"] not in seen:
        seen.add(r["outlet"])
        outlets.append({"name": r["outlet"], "type": r["type"], "std": int(r["covers_per_staff_standard"])})

rows = [[r["outlet"], r["day"], int(r["hour"]), int(r["covers"]), int(r["covers_event_day"]),
         roster[(r["outlet"], r["day"], int(r["hour"]))]] for r in cov]

data = {"outlets": outlets, "rows": rows}
html = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(html, encoding="utf-8")
print("built docs/index.html", len(html) // 1024, "KB")
