import csv
import io
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import engines, storage
from .config import APP_TITLE, STATIC_DIR


@asynccontextmanager
async def lifespan(app):
    storage.init_db()
    engines.all_engines()
    yield


app = FastAPI(title=APP_TITLE, lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok", "title": APP_TITLE}


@app.get("/api/engines")
def list_engines():
    return [{"name": e.name, "description": e.description} for e in engines.all_engines().values()]


@app.get("/api/engines/{name}/sample")
def sample(name: str):
    eng = engines.get_engine(name)
    if eng is None:
        raise HTTPException(404, f"unknown engine {name!r}")
    return eng.sample_input()


@app.post("/api/run/{name}")
def run(name: str, data: dict = Body(default_factory=dict)):
    eng = engines.get_engine(name)
    if eng is None:
        raise HTTPException(404, f"unknown engine {name!r}")
    try:
        result = eng.run(data)
    except engines.EngineError as e:
        raise HTTPException(422, str(e))
    result["run_id"] = storage.save_run(name, data, result)
    return result


@app.get("/api/runs")
def runs(limit: int = 20):
    return storage.list_runs(min(max(limit, 1), 100))


@app.get("/api/runs/{run_id}")
def run_detail(run_id: int):
    r = storage.get_run(run_id)
    if r is None:
        raise HTTPException(404, "run not found")
    return r


@app.get("/api/runs/{run_id}/csv")
def run_csv(run_id: int):
    r = storage.get_run(run_id)
    if r is None:
        raise HTTPException(404, "run not found")
    table = r["result"].get("table") or []
    buf = io.StringIO()
    if table:
        w = csv.DictWriter(buf, fieldnames=list(table[0].keys()))
        w.writeheader()
        w.writerows(table)
    return PlainTextResponse(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=run_{run_id}.csv"},
    )


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
