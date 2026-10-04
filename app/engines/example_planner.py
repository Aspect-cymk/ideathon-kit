"""EXAMPLE ENGINE 1: choose the best set of tasks under a budget.

Pattern that fits many problems: limited resource (time, battery, money, points
budget) and many candidate actions with value and cost. Compares a fast greedy
strategy against the exact optimum, which gives a measurable improvement
number for the pitch.
"""
from .base import Engine, EngineError, make_result

MAX_ITEMS = 200
MAX_BUDGET = 100000


def _parse(data):
    try:
        budget = int(round(float(data.get("budget"))))
    except (TypeError, ValueError):
        raise EngineError("budget must be a number")
    if budget < 0 or budget > MAX_BUDGET:
        raise EngineError(f"budget must be between 0 and {MAX_BUDGET}")
    raw = data.get("items")
    if not isinstance(raw, list) or not raw:
        raise EngineError("items must be a non-empty list")
    if len(raw) > MAX_ITEMS:
        raise EngineError(f"at most {MAX_ITEMS} items")
    items = []
    for i, it in enumerate(raw):
        try:
            name = str(it["name"])
            value = float(it["value"])
            cost = int(round(float(it["cost"])))
        except (KeyError, TypeError, ValueError):
            raise EngineError(f"item {i} needs name, numeric value and numeric cost")
        if value < 0 or cost <= 0:
            raise EngineError(f"item {name!r}: value must be >= 0 and cost must be > 0")
        items.append({"name": name, "value": value, "cost": cost})
    return budget, items


def _greedy(budget, items):
    order = sorted(range(len(items)), key=lambda i: items[i]["value"] / items[i]["cost"], reverse=True)
    chosen, left = [], budget
    for i in order:
        if items[i]["cost"] <= left:
            chosen.append(i)
            left -= items[i]["cost"]
    return chosen


def _optimal(budget, items):
    n = len(items)
    best = [[0.0] * (budget + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        v, c = items[i - 1]["value"], items[i - 1]["cost"]
        for b in range(budget + 1):
            best[i][b] = best[i - 1][b]
            if c <= b and best[i - 1][b - c] + v > best[i][b]:
                best[i][b] = best[i - 1][b - c] + v
    chosen, b = [], budget
    for i in range(n, 0, -1):
        if best[i][b] != best[i - 1][b]:
            chosen.append(i - 1)
            b -= items[i - 1]["cost"]
    return chosen[::-1]


def _total(items, idx, key):
    return sum(items[i][key] for i in idx)


class PriorityPlanner(Engine):
    name = "priority_planner"
    description = "Pick the best tasks under a budget (greedy vs optimal)."

    def sample_input(self):
        return {
            "budget": 10,
            "strategy": "optimal",
            "items": [
                {"name": "Task A", "value": 60, "cost": 5},
                {"name": "Task B", "value": 50, "cost": 4},
                {"name": "Task C", "value": 70, "cost": 6},
                {"name": "Task D", "value": 30, "cost": 3},
                {"name": "Task E", "value": 45, "cost": 2},
            ],
        }

    def run(self, data):
        budget, items = _parse(data)
        strategy = data.get("strategy", "optimal")
        if strategy not in ("greedy", "optimal"):
            raise EngineError("strategy must be 'greedy' or 'optimal'")
        greedy = _greedy(budget, items)
        optimal = _optimal(budget, items)
        chosen = optimal if strategy == "optimal" else greedy
        g_val, o_val = _total(items, greedy, "value"), _total(items, optimal, "value")
        gap = round((o_val - g_val) / o_val * 100, 1) if o_val else 0.0
        picked = set(chosen)
        table = [
            {
                "name": it["name"],
                "value": it["value"],
                "cost": it["cost"],
                "value_per_cost": round(it["value"] / it["cost"], 2),
                "selected": "yes" if i in picked else "no",
            }
            for i, it in enumerate(items)
        ]
        sel = [items[i] for i in chosen]
        return make_result(
            self.name,
            summary={
                "strategy": strategy,
                "total_value": _total(items, chosen, "value"),
                "budget_used": f"{_total(items, chosen, 'cost')}/{budget}",
                "greedy_value": g_val,
                "optimal_value": o_val,
                "greedy_gap_%": gap,
            },
            table=table,
            series={"title": "Value of selected tasks", "labels": [s["name"] for s in sel], "values": [s["value"] for s in sel]},
            log=[
                f"Greedy picks by value/cost ratio and reaches {g_val}.",
                f"Dynamic programming finds the exact optimum {o_val}.",
                f"Greedy is {gap}% below optimal on this input.",
                "Costs are rounded to whole numbers for the exact solver.",
            ],
        )
