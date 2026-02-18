from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from .bo_formatter import format_bo, _normalize_relation
from .config import config


def get_context(bo_name: str) -> str:
    """Extract context from BO name: 'logistics_allparts' → 'logistics'."""
    return bo_name.split("_")[0] if "_" in bo_name else bo_name


def _build_fk_graph(raw: dict) -> dict[str, set[str]]:
    """Build a bidirectional adjacency graph from FK relations."""
    graph: dict[str, set[str]] = defaultdict(set)
    for bo in raw.get("boNames", []):
        bo_name = bo["name"]
        for rel in bo.get("relations", []):
            norm = _normalize_relation(rel)
            if norm and norm["target_bo"]:
                graph[bo_name].add(norm["target_bo"])
                graph[norm["target_bo"]].add(bo_name)  # bidirectional
    return graph


def select_bos_for_context(raw: dict, target_context: str) -> dict:
    """Select all BOs for a context + FK-reachable BOs from other contexts.

    Algorithm:
        1. Seed = all BOs whose context matches target_context
        2. BFS through the FK graph (bidirectional edges)
        3. Collect every reachable BO (same or different context)

    Returns a new raw dict (with enums) containing only the selected BOs.
    """
    all_bo_names = {bo["name"] for bo in raw.get("boNames", [])}
    graph = _build_fk_graph(raw)

    # Seed: all BOs with the target context
    seed = {name for name in all_bo_names if get_context(name) == target_context}

    # BFS from seed through FK edges
    visited = set(seed)
    queue = deque(seed)
    while queue:
        current = queue.popleft()
        for neighbor in graph.get(current, set()):
            if neighbor not in visited and neighbor in all_bo_names:
                visited.add(neighbor)
                queue.append(neighbor)

    # Build filtered raw dict (preserve original order)
    selected = [bo for bo in raw.get("boNames", []) if bo["name"] in visited]

    return {
        "enums": raw.get("enums", {}),
        "boNames": selected,
    }


def get_schema_for_module(
    all_bos_raw: dict,
    detected_module: str,
    fmt: str = "create_table",
) -> str:
    """Drop-in replacement for the old get_schema_for_module().

    Args:
        all_bos_raw: The full business-objects.json dict (all modules).
        detected_module: Persian module name, e.g. "انبار", "فروش".
        fmt: Output format (create_table, yaml_grouped, etc.)

    Returns:
        Schema string for the prompt, containing all BOs of that module
        plus any FK-reachable BOs from other modules.
    """
    module_to_context = config.get("schema", {}).get("module_to_context", {})
    context = module_to_context.get(detected_module.strip())
    if context is None:
        # Unknown module → return all BOs
        return format_bo(all_bos_raw, fmt)

    filtered = select_bos_for_context(all_bos_raw, context)
    return format_bo(filtered, fmt)