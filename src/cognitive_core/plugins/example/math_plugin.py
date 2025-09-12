from .. import register
from ...app.services import dot

class MathPlugin:
    name = "math.dot"
    def run(self, payload: dict) -> dict:
        a = payload.get("a", [])
        b = payload.get("b", [])
        return {"result": dot(a,b)}

register(MathPlugin())
