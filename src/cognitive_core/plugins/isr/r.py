from .. import PluginMetadata, register


class RStage:
    """Initial reflection stage."""

    name = "isr.r"

    def run(self, payload: dict) -> dict:
        text = payload.get("text", "")
        text = f"{text} -> R"
        return {"text": text, "logic": 0.1, "semantic": 0.1, "narrative": 0.1}


metadata = PluginMetadata(name="isr.r", version="1.0.0", requirements=[])
register(RStage(), metadata)
