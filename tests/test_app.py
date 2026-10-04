import os
import tempfile

os.environ["IDEATHON_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

import pytest
from fastapi.testclient import TestClient

from app.engines import EngineError, all_engines
from app.main import app


def test_registry_has_examples():
    assert {"priority_planner", "grid_path"} <= set(all_engines())


def test_planner_optimal_beats_or_ties_greedy():
    eng = all_engines()["priority_planner"]
    res = eng.run(eng.sample_input())
    assert res["summary"]["optimal_value"] >= res["summary"]["greedy_value"]
    assert res["summary"]["optimal_value"] == 135  # A + D + E, hand-checked
    assert res["summary"]["greedy_value"] == 125  # E + B + D, hand-checked
    assert res["summary"]["total_value"] == res["summary"]["optimal_value"]


def test_planner_budget_respected():
    eng = all_engines()["priority_planner"]
    res = eng.run({"budget": 3, "strategy": "greedy", "items": [{"name": "x", "value": 5, "cost": 4}]})
    assert res["summary"]["total_value"] == 0


def test_planner_validation():
    eng = all_engines()["priority_planner"]
    with pytest.raises(EngineError):
        eng.run({"budget": "abc", "items": []})
    with pytest.raises(EngineError):
        eng.run({"budget": 5, "items": [{"name": "x", "value": 1, "cost": 0}]})


def test_grid_path_found_and_blocked():
    eng = all_engines()["grid_path"]
    res = eng.run(eng.sample_input())
    assert res["summary"]["path_found"] == "yes"
    assert res["grid"]["path"][0] == [0, 0]
    blocked = eng.run({"grid": ["S#G"]})
    assert blocked["summary"]["path_found"] == "no"


def test_api_flow():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        names = [e["name"] for e in c.get("/api/engines").json()]
        assert "priority_planner" in names
        sample = c.get("/api/engines/priority_planner/sample").json()
        r = c.post("/api/run/priority_planner", json=sample)
        assert r.status_code == 200
        run_id = r.json()["run_id"]
        assert c.get(f"/api/runs/{run_id}").json()["engine"] == "priority_planner"
        assert "name,value,cost" in c.get(f"/api/runs/{run_id}/csv").text
        assert c.post("/api/run/priority_planner", json={"budget": "x"}).status_code == 422
        assert c.post("/api/run/nope", json={}).status_code == 404
        assert c.get("/").status_code == 200
