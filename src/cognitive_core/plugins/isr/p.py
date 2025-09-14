from .. import PluginMetadata, register


class PStage:
    """Processing stage."""

    name = "isr.p"

    def run(self, payload: dict) -> dict:
        text = payload.get("text", "")
        text = f"{text} -> P"
        return {"text": text, "logic": 0.3, "semantic": 0.3, "narrative": 0.3}


metadata = PluginMetadata(name="isr.p", version="1.0.0", requirements=[])
register(PStage(), metadata)
