# Plugins

`cognitive-core-engine` can load external plugins that expose an entry point.
Calling `discover()` imports these plugins and registers them automatically.

## pyproject.toml configuration

```toml
[project.entry-points."cognitive_core.plugins"]
math = "my_package.math_plugin:create_plugin"
```

The referenced callable should return a tuple `(plugin, metadata)` where
`metadata` is an instance of `PluginMetadata`.

```python
from cognitive_core.plugins import PluginMetadata

def create_plugin():
    plugin = MathPlugin()
    metadata = PluginMetadata(name="math.dot", version="1.0.0", requirements=[])
    return plugin, metadata
```
