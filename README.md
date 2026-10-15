# Back-of-House Staffing Planner

An interactive dashboard that shows which Crown Melbourne outlets are busy at which times, and where the
back-of-house (kitchen and stewarding) roster falls short, so shifts can be rostered to match demand.

> **Sample data.** Outlet names are real Crown venues. Covers, staffing standards and the roster are modelled
> for demonstration and are not Crown figures.

## What it shows
- **When each outlet is busy:** hour-by-hour busyness for 10 outlets, for any day of the week
- **Where we're short-staffed:** staff needed (from covers) minus staff rostered, for every outlet and hour
- **Needed vs rostered across the resort**, and short vs spare staff-hours for every day of the week
- **Roster changes to make:** start staff later where they are spare in the afternoon, move kitchen hands and
  stewards across from quiet outlets, and only then add short shifts
- **Big event day** toggle (Australian Open, AFL finals, Melbourne Cup) to plan event rosters

## How it works
`staff needed = ceil(covers per hour ÷ covers one BOH staff member can handle per hour)`, minimum 1 when open.
`gap = needed − rostered`. The sample roster uses the same 4-hour shift blocks every day, sized for the busiest
hour of an average day. That's how a flat roster behaves: weekends run short and early week runs heavy.

## Use it with real data
1. Export covers by hour from the outlet POS / reservations system into `data/covers_by_hour.csv`
   (`outlet,type,day,hour,covers,covers_event_day,covers_per_staff_standard`)
2. Export the BOH roster into `data/roster_by_hour.csv` (`outlet,day,hour,boh_staff_rostered`)
3. `python src/build_dashboard.py` and open `docs/index.html`

To regenerate the sample data: `python src/generate_sample_data.py`.

Built with Python and Plotly.
