"""The one contract every topic-specific engine follows.

To adapt the kit to a new problem statement:
1. Copy engines/example_planner.py to engines/<your_topic>.py
2. Change name, description, sample_input and run()
3. Restart the server. The UI picks the engine up automatically.
"""
from abc import ABC, abstractmethod


class EngineError(ValueError):
    """Raise for bad user input. The API returns it as HTTP 422 with the message."""


class Engine(ABC):
    name = ""
    description = ""

    @abstractmethod
    def sample_input(self) -> dict:
        """Demo-ready input shown in the UI editor."""

    @abstractmethod
    def run(self, data: dict) -> dict:
        """Core logic. Return the result of make_result()."""


def make_result(engine, summary, table=None, series=None, grid=None, log=None):
    """Standard result shape the frontend knows how to render.

    summary: {label: value}              headline numbers (cards)
    table:   [{col: value, ...}, ...]    rows (table + CSV export)
    series:  {"title", "labels", "values"} bar chart
    grid:    {"rows": [str], "path": [[r, c], ...]}  grid/field view
    log:     [str]                       step-by-step explanation
    """
    return {
        "engine": engine,
        "summary": summary,
        "table": table or [],
        "series": series,
        "grid": grid,
        "log": log or [],
    }
