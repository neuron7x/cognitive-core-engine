"""Network generation helpers for ISR simulations."""
from __future__ import annotations
import numpy as np
import networkx as nx


def ring(n: int) -> np.ndarray:
    """Return adjacency matrix of an n-node ring network."""
    g = nx.cycle_graph(n)
    return nx.to_numpy_array(g)


def random(n: int, p: float = 0.1) -> np.ndarray:
    """Return adjacency matrix of an Erdos-Renyi network."""
    g = nx.erdos_renyi_graph(n, p)
    return nx.to_numpy_array(g)
