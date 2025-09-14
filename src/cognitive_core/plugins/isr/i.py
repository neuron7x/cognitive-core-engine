from .. import PluginMetadata, register


class IStage:
    """Integration stage."""

    name = "isr.i"

    def run(self, payload: dict) -> dict:
        text = payload.get("text", "")
        text = f"{text} -> I"
        return {"text": text, "logic": 0.2, "semantic": 0.2, "narrative": 0.2}


metadata = PluginMetadata(name="isr.i", version="1.0.0", requirements=[])
register(IStage(), metadata)
