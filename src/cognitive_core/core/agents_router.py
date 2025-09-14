from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None

from ..domain.agents import AgentConfig, DebateRound, Role
from ..llm.provider import get_provider


class AgentsRouter:
    """Utility to run multiple roles against a prompt sequentially or concurrently."""

    def __init__(self, config_dir: str | Path = "config/agents"):
        self.config_dir = Path(config_dir)
        self.provider = get_provider()

    # ------------------------------------------------------------------
    # Configuration helpers
    def load_role(self, name: str) -> AgentConfig:
        """Load a role configuration from YAML."""

        path = self.config_dir / f"{name}.yaml"
        with path.open() as f:
            if yaml:
                data = yaml.safe_load(f) or {}
            else:  # very small YAML subset parser
                data = {}
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if ":" in line:
                        k, v = line.split(":", 1)
                        data[k.strip()] = v.strip().strip('"').strip("'")
        role = Role(name=data.get("name", name), system_prompt=data.get("system_prompt", ""))
        model = data.get("model", "mock")
        return AgentConfig(role=role, model=model)

    def _prepare_prompt(self, cfg: AgentConfig, prompt: str) -> str:
        return f"{cfg.role.system_prompt}\n\n{prompt}" if cfg.role.system_prompt else prompt

    # ------------------------------------------------------------------
    # Execution
    def run(self, prompt: str, roles: Iterable[str], *, concurrent: bool = False) -> DebateRound:
        configs = [self.load_role(r) for r in roles]
        if concurrent:
            return asyncio.run(self._run_concurrent(prompt, configs))
        return self._run_sequential(prompt, configs)

    def _run_sequential(self, prompt: str, configs: List[AgentConfig]) -> DebateRound:
        round = DebateRound(prompt=prompt)
        for cfg in configs:
            r = self.provider.run(self._prepare_prompt(cfg, prompt))
            round.responses[cfg.role.name] = r.get("text", "")
        return round

    async def _run_concurrent(self, prompt: str, configs: List[AgentConfig]) -> DebateRound:
        round = DebateRound(prompt=prompt)

        async def call(cfg: AgentConfig) -> None:
            r = await asyncio.to_thread(self.provider.run, self._prepare_prompt(cfg, prompt))
            round.responses[cfg.role.name] = r.get("text", "")

        await asyncio.gather(*(call(cfg) for cfg in configs))
        return round
