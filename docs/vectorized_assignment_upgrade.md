# Vectorized Writer Assignment and Reusable Game-Design Blocks

This document provides a concrete, drop-in upgrade path for the editorial orchestration app shared in chat.

## Goals

- Add semantic matching (vector similarity) on top of existing rule-based assignment.
- Add a reusable block library for common game-design building blocks.
- Keep compatibility with the current output schema while adding new recommendation fields.

## New Data Files

Add these files under `editorial/`:

- `block_library.json`: reusable game-design blocks.
- `semantic_weights.json`: weights for hybrid scoring.

### `block_library.json` shape

```json
{
  "blocks": [
    {
      "id": "block.enemy-aggro-fsm.v1",
      "name": "Enemy Aggro FSM",
      "description": "State machine for idle/alert/chase/attack transitions.",
      "tags": ["ai", "combat", "mechanics"],
      "input_contract": ["sight_events", "distance", "cooldown"],
      "output_contract": ["state", "intent", "attack_window"],
      "quality": {
        "test_pass_rate": 0.98,
        "perf_cost": "low"
      }
    }
  ]
}
```

### `semantic_weights.json` shape

```json
{
  "weights": {
    "rule": 0.6,
    "semantic": 0.3,
    "historical": 0.1
  },
  "top_k_writers": 4,
  "top_k_blocks": 3
}
```

## Drop-in Python Additions

Use deterministic local vectors (hashing trick) so the feature works without external model services.

```python
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Any, Dict, Iterable, List, Tuple


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_./-]+")


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _hash_vec(tokens: Iterable[str], dim: int = 256) -> List[float]:
    vec = [0.0] * dim
    counts = Counter(tokens)
    for token, freq in counts.items():
        idx = hash(token) % dim
        vec[idx] += float(freq)
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


@dataclass(frozen=True)
class Block:
    id: str
    name: str
    description: str
    tags: List[str]
    input_contract: List[str]
    output_contract: List[str]
    quality: Dict[str, Any]

    def semantic_text(self) -> str:
        return " ".join(
            [
                self.name,
                self.description,
                " ".join(self.tags),
                " ".join(self.input_contract),
                " ".join(self.output_contract),
            ]
        )


def _node_semantic_text(node: Dict[str, Any]) -> str:
    return " ".join(
        [
            node.get("path", ""),
            " ".join(node.get("task_tags", [])),
            " ".join(node.get("depends_on", [])),
        ]
    )


def _writer_semantic_text(writer: Writer) -> str:
    return " ".join(
        [
            writer.specialty,
            writer.style,
            " ".join(writer.focus_paths),
            " ".join(writer.focus_areas),
            " ".join(writer.learning_sources or []),
        ]
    )


def semantic_candidates_for_node(
    node: Dict[str, Any],
    writers: Dict[str, Writer],
    top_k: int,
) -> List[Tuple[str, float]]:
    node_vec = _hash_vec(_tokenize(_node_semantic_text(node)))
    scored: List[Tuple[str, float]] = []
    for writer in writers.values():
        w_vec = _hash_vec(_tokenize(_writer_semantic_text(writer)))
        scored.append((writer.id, _cosine(node_vec, w_vec)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def recommend_blocks_for_node(
    node: Dict[str, Any],
    blocks: List[Block],
    top_k: int,
) -> List[Tuple[str, float]]:
    node_vec = _hash_vec(_tokenize(_node_semantic_text(node)))
    scored: List[Tuple[str, float]] = []
    for block in blocks:
        b_vec = _hash_vec(_tokenize(block.semantic_text()))
        scored.append((block.id, _cosine(node_vec, b_vec)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
```

## Hybrid Scoring in `assign_writers`

Keep existing rule-based logic. Add semantic score and combine:

```python
# after current owner candidate collection and dedup
rule_rank = {writer_id: i for i, writer_id in enumerate(unique_owners)}
semantic = dict(semantic_candidates_for_node(node, writers, top_k=weights["top_k_writers"]))

combined: List[Tuple[str, float]] = []
for writer_id in set(unique_owners) | set(semantic):
    # Higher rank gets higher rule score.
    rr = 1.0 / (1 + rule_rank.get(writer_id, 999))
    ss = semantic.get(writer_id, 0.0)
    hs = 0.0  # optional: fill from historical success table
    score = w_rule * rr + w_semantic * ss + w_historical * hs
    combined.append((writer_id, score))

combined.sort(key=lambda x: x[1], reverse=True)
assignment[node_path] = [writer_id for writer_id, _ in combined[:weights["top_k_writers"]]]
```

## Output Extensions

Add fields without breaking existing consumers:

- `writer_contributions.json`
  - `recommended_block_ids`: list of block ids
  - `semantic_score`: per writer-node score
- `coordination_report.json`
  - `semantic_assignment_metrics`
  - `block_reuse_plan`

## Validation

- Add deterministic tests for vector functions (`_hash_vec`, `_cosine`)
- Add assignment regression tests:
  - same input should produce stable top-K ordering
  - requested specialties still respected
- Add block recommendation tests:
  - combat-tagged nodes should rank combat blocks above unrelated blocks

## Migration Sequence

1. Add new JSON files and loaders (`load_blocks`, `load_semantic_weights`).
2. Implement deterministic vector helpers.
3. Add semantic scoring to `assign_writers`.
4. Extend `generate_contributions` with `recommended_block_ids`.
5. Extend `coordination_report` with semantic metrics.
6. Run integration tests and compare assignment quality before/after.

## Operational Optimization Additions

The implementation now also includes:

- A/B testing helper for `vector_dim` and `top_k` matrices.
- Built-in CPU + memory profiling for semantic pipeline runs.
- Precompute embedding cache with configurable TTL.
- Telemetry helpers for:
  - recommended-but-not-selected signals
  - coverage/fallback/confidence summaries
- Node latency helper for p50/p95/mean reporting.

## Automated Checks

Run these regularly to keep behavior stable:

- `python -m unittest scripts.tests.test_vectorized_assignment`
- `python - <<'PY' ... run_ab_tests(...) ... PY` for scenario-specific A/B matrices.

## Ready Game Blocks (Composable)

A starter reusable library now exists at:

- `scripts/data/block_library.json`

It includes ready blocks for:

- grass biomes
- paths
- roads
- airplanes
- spaceships
- planets
- fuel stations
- solar energy
- alien factions
- space farming

These are designed to be combined later into larger gameplay flows.
