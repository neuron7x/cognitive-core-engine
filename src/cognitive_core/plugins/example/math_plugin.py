from ...app.services import dot
from .. import PluginMetadata, register


class MathPlugin:
    name = "math.dot"

    def run(self, payload: dict) -> dict:
        a = payload.get("a", [])
        b = payload.get("b", [])
        return {"result": dot(a, b)}


metadata = PluginMetadata(name="math.dot", version="1.0.0", requirements=[])
register(MathPlugin(), metadata)
