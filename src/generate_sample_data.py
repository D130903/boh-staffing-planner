"""Generate an ILLUSTRATIVE week of back-of-house (BOH) demand and roster data for Crown Melbourne outlets.

No real Crown data is used. Outlet names are public venues; covers per hour, staffing standards and the roster
are modelled assumptions so the dashboard can be demonstrated. Replace data/covers_by_hour.csv and
data/roster_by_hour.csv with real POS / roster exports (same columns) and re-run build_dashboard.py.
"""
import csv
import math
import random
from pathlib import Path

random.seed(7)
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_MULT = {"Mon": 0.70, "Tue": 0.75, "Wed": 0.85, "Thu": 0.95, "Fri": 1.25, "Sat": 1.40, "Sun": 1.10}
HOURS = list(range(7, 25))  # 7:00 .. 24:00 (24 = midnight-1am)

# name, type, open hour, close hour, meal peaks {hour: share of peak}, peak covers/hour,
# covers one BOH staff member can support per hour (staffing standard), event-day uplift
OUTLETS = [
    ("Conservatory", "Buffet", 7, 22, {7: .5, 8: .9, 9: .8, 10: .4, 12: .9, 13: 1, 14: .5, 18: .9, 19: 1, 20: .8, 21: .4}, 220, 30, 1.30),
    ("Nobu", "Fine dining", 12, 23, {12: .5, 13: .6, 14: .3, 18: .7, 19: 1, 20: .95, 21: .6, 22: .3}, 90, 10, 1.25),
    ("Koko", "Fine dining", 12, 22, {12: .4, 13: .5, 14: .2, 18: .7, 19: 1, 20: .8, 21: .4}, 60, 10, 1.20),
    ("Ging Thai", "Casual", 11, 23, {12: .7, 13: .8, 14: .4, 17: .5, 18: .9, 19: 1, 20: .8, 21: .5, 22: .3}, 80, 20, 1.35),
    ("88 Noodle Bar", "Casual", 11, 25, {12: .6, 13: .7, 14: .4, 18: .8, 19: .9, 20: .8, 21: .7, 22: .8, 23: 1, 24: .7}, 120, 22, 1.45),
    ("Mr Hive", "Casual", 12, 23, {12: .5, 13: .6, 17: .5, 18: .9, 19: 1, 20: .8, 21: .5}, 70, 18, 1.30),
    ("Fidels", "Casual", 11, 24, {12: .6, 13: .7, 18: .8, 19: 1, 20: .9, 21: .7, 22: .5, 23: .3}, 100, 22, 1.70),
    ("The Pub", "Pub dining", 11, 25, {12: .7, 13: .8, 14: .5, 17: .6, 18: .9, 19: 1, 20: .9, 21: .8, 22: .7, 23: .5, 24: .3}, 110, 25, 1.80),
    ("Room Service", "Hotel", 7, 25, {7: .7, 8: 1, 9: .7, 12: .4, 13: .4, 18: .5, 19: .7, 20: .8, 21: .9, 22: .8, 23: .6, 24: .4}, 45, 12, 1.40),
    ("Banquets", "Events", 7, 24, {7: .2, 8: .3, 12: .5, 13: .5, 18: .6, 19: 1, 20: 1, 21: .6, 22: .3}, 400, 40, 1.50),
]
# Banquets only run big dinners Thu-Sat in a normal week
BANQUET_DAY = {"Mon": .3, "Tue": .3, "Wed": .5, "Thu": 1.0, "Fri": 1.1, "Sat": 1.2, "Sun": .4}


def covers(outlet, day, hour, event=False):
    name, _t, op, cl, peaks, peak, _std, uplift = outlet
    if not (op <= hour < cl):
        return 0
    base = peaks.get(hour, 0.25)
    mult = BANQUET_DAY[day] if name == "Banquets" else DAY_MULT[day]
    if event:
        mult *= uplift
    noise = random.uniform(0.92, 1.08)
    return round(peak * base * mult * noise)


def needed(outlet, c):
    if c == 0:
        return 0
    return max(1, math.ceil(c / outlet[6]))


rows_c, rows_r = [], []
need_by = {}
for o in OUTLETS:
    for d in DAYS:
        for h in HOURS:
            c = covers(o, d, h)
            ce = covers(o, d, h, event=True)
            rows_c.append({"outlet": o[0], "type": o[1], "day": d, "hour": h, "covers": c, "covers_event_day": ce,
                           "covers_per_staff_standard": o[6]})
            need_by[(o[0], d, h)] = needed(o, c)

# Typical roster: the same 4-hour shift blocks every day, sized for the busiest hour of an AVERAGE day.
# This mirrors a flat roster that does not follow demand: weekends run short, early week runs heavy.
for o in OUTLETS:
    for d in DAYS:
        for h in HOURS:
            if not (o[2] <= h < o[3]):
                staff = 0
            else:
                blk = [x for x in HOURS if (x - 7) // 4 == (h - 7) // 4 and o[2] <= x < o[3]]
                # staff the block for its busiest hour on an average day
                avg_peak = max(sum(need_by[(o[0], dd, x)] for dd in DAYS) / len(DAYS) for x in blk)
                staff = max(1, round(avg_peak))
            rows_r.append({"outlet": o[0], "day": d, "hour": h, "boh_staff_rostered": staff})

for fn, rows in (("covers_by_hour.csv", rows_c), ("roster_by_hour.csv", rows_r)):
    with open(OUT / fn, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
print(f"wrote {len(rows_c)} covers rows and {len(rows_r)} roster rows to {OUT}")
