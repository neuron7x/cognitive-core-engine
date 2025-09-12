from ...app.services import dot
from .. import register


class MathPlugin:
    name = "math.dot"

    def run(self, payload: dict) -> dict:
        a = payload.get("a", [])
        b = payload.get("b", [])
        return {"result": dot(a, b)}


register(MathPlugin())
