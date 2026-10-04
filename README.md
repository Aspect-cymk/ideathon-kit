# Ideathon Kit

A topic-agnostic software skeleton: **Input -> Engine -> Result**. The web app, API, storage, history, CSV export and charts are done. For a new problem statement you only write one file: the engine.

## Architecture

```
Browser (static HTML/JS/CSS, no build step, no CDN, works offline)
   |  JSON
FastAPI  (app/main.py)
   |-- /api/engines, /api/engines/{name}/sample
   |-- /api/run/{name}  -> Engine.run(data) -> standard result
   |-- /api/runs, /api/runs/{id}, /api/runs/{id}/csv
   |
Engine registry (app/engines/__init__.py)  auto-discovers every Engine subclass
   |-- priority_planner  (budgeted task selection, greedy vs optimal)
   |-- grid_path         (A* on a grid field)
   |-- your_topic        (you add this)
   |
SQLite (data/ideathon.db)  stores every run for the history list
```

Standard result shape (what the UI renders): `summary` (cards), `table` (rows + CSV), `series` (bar chart), `grid` (field view with a path), `log` (explanation lines). Use any subset.

## Setup (once, tonight)

1. Install Python 3.10 or newer.
2. In this folder run `run.bat` (Windows) or `./run.sh` (Linux/macOS). First run creates `.venv` and installs the packages; later runs just start the server.
3. Open http://localhost:8000 and press Run on both sample engines.
4. Run the tests: activate the venv, then `python -m pytest -q`. All 6 should pass.
5. Create a Git repo, push it, and have both teammates clone it and run step 2.

## Adapting it to the real topic (target: 15 minutes)

1. Fill the engine spec note (Obsidian: Template - Hackathon engine spec) with the input, the output and the algorithm.
2. Copy `app/engines/_template.py` to `app/engines/<topic>.py`.
3. Set `name` and `description`, and write `sample_input()` with realistic demo data.
4. Write the logic in `run()`. Return `make_result(...)`.
5. Save. The server reloads; refresh the page and pick your engine in the dropdown.
6. Add one test per engine in `tests/` so you can change code quickly without breaking the demo.
7. Need something the UI cannot show? Add a new key to the result and a small render function in `static/app.js`.

## Compare-two-approaches pattern (strong for "innovation")

Implement a baseline and your improved method in the same engine and report both numbers in `summary`, as `priority_planner` does with greedy vs optimal. Judges see a measured improvement instead of a claim.

## Demo rules

1. Prepare 2 or 3 scripted inputs and rehearse them on the exact laptop you will present from.
2. Run on localhost; do not depend on venue Wi-Fi.
3. Record a backup screen capture of the working demo.
4. Do not add features in the last 45 minutes.
5. Ask the organizers whether AI tools or external APIs are allowed before using them.

## Files

```
app/main.py            routes and static serving
app/config.py          paths, title (env: IDEATHON_TITLE, IDEATHON_DB)
app/storage.py         SQLite run history
app/engines/base.py    Engine contract, EngineError, make_result
app/engines/*.py       your engines (auto-registered)
static/                index.html, app.js, style.css
tests/test_app.py      engine and API tests
```
