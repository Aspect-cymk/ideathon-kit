"""STARTER FOR A NEW TOPIC. Copy this file to engines/<your_topic>.py, then:
1. Set `name` (this enables the engine) and `description`.
2. Return realistic demo data from sample_input().
3. Put the core logic in run(). Raise EngineError for bad input.
4. Restart the server. The UI lists the engine automatically.

While `name` is empty, this file is ignored by the registry.
"""
from .base import Engine, EngineError, make_result


class TopicEngine(Engine):
    name = ""
    description = "One line describing what this engine does."

    def sample_input(self):
        return {"example": 1}

    def run(self, data):
        if "example" not in data:
            raise EngineError("example is required")
        # ---- core logic goes here ----
        score = data["example"] * 2
        return make_result(
            self.name,
            summary={"score": score},
            table=[{"input": data["example"], "output": score}],
            series={"title": "Demo", "labels": ["in", "out"], "values": [data["example"], score]},
            log=["Replace this with a plain-language explanation of the steps."],
        )
