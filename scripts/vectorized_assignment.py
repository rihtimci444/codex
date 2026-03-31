from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import cProfile
import io
from pathlib import Path
import json
import math
import pstats
import re
import statistics
import time
import tracemalloc
from typing import Any, Dict, Iterable, List, Tuple


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_./-]+")

_JSON_CACHE: Dict[str, Tuple[int, Dict[str, Any]]] = {}
_WRITERS_CACHE: Dict[str, Tuple[int, Dict[str, "Writer"]]] = {}
_BLOCKS_CACHE: Dict[str, Tuple[int, List["Block"]]] = {}
_WEIGHTS_CACHE: Dict[str, Tuple[int, Dict[str, Any]]] = {}
_EMBEDDING_CACHE: Dict[str, Tuple[float, List[float]]] = {}


@dataclass(frozen=True)
class Writer:
    id: str
    specialty: str
    focus_paths: List[str]
    focus_areas: List[str]
    style: str
    max_parallel_tasks: int = 2
    learning_sources: List[str] | None = None


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


def _mtime_ns(path: Path) -> int:
    return path.stat().st_mtime_ns


def _read_json_uncached(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> Dict[str, Any]:
    key = str(path.resolve())
    mtime = _mtime_ns(path)
    cached = _JSON_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    parsed = _read_json_uncached(path)
    _JSON_CACHE[key] = (mtime, parsed)
    return parsed


def load_writers(path: Path) -> Dict[str, Writer]:
    key = str(path.resolve())
    mtime = _mtime_ns(path)
    cached = _WRITERS_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    raw = _read_json(path)
    writers: Dict[str, Writer] = {}
    for item in raw["writers"]:
        writers[item["id"]] = Writer(
            id=item["id"],
            specialty=item["specialty"],
            focus_paths=item["focus_paths"],
            focus_areas=item.get("focus_areas", []),
            style=item["style"],
            max_parallel_tasks=item.get("max_parallel_tasks", 2),
            learning_sources=item.get("learning_sources", []),
        )

    _WRITERS_CACHE[key] = (mtime, writers)
    return writers


def load_blocks(path: Path) -> List[Block]:
    key = str(path.resolve())
    mtime = _mtime_ns(path)
    cached = _BLOCKS_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    raw = _read_json(path)
    blocks: List[Block] = []
    for item in raw.get("blocks", []):
        blocks.append(
            Block(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                tags=item.get("tags", []),
                input_contract=item.get("input_contract", []),
                output_contract=item.get("output_contract", []),
                quality=item.get("quality", {}),
            )
        )

    _BLOCKS_CACHE[key] = (mtime, blocks)
    return blocks


def load_semantic_weights(path: Path) -> Dict[str, Any]:
    key = str(path.resolve())
    mtime = _mtime_ns(path)
    cached = _WEIGHTS_CACHE.get(key)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    raw = _read_json(path)
    weights = raw.get("weights", {})
    result = {
        "weights": {
            "rule": float(weights.get("rule", 0.6)),
            "semantic": float(weights.get("semantic", 0.3)),
            "historical": float(weights.get("historical", 0.1)),
        },
        "top_k_writers": int(raw.get("top_k_writers", 4)),
        "top_k_blocks": int(raw.get("top_k_blocks", 3)),
        "vector_dim": int(raw.get("vector_dim", 256)),
    }
    _WEIGHTS_CACHE[key] = (mtime, result)
    return result


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _hash_vec(tokens: Iterable[str], dim: int = 256) -> List[float]:
    vec = [0.0] * dim
    counts = Counter(tokens)
    for token, freq in counts.items():
        vec[hash(token) % dim] += float(freq)

    norm = math.sqrt(sum(value * value for value in vec))
    if norm > 0:
        return [value / norm for value in vec]
    return vec


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def _node_semantic_text(node: Dict[str, Any]) -> str:
    task_tags = node.get("task_tags", [])
    depends_on = node.get("depends_on", [])
    return " ".join(
        [
            node.get("path", ""),
            " ".join(str(tag) for tag in task_tags if tag is not None),
            " ".join(str(dep) for dep in depends_on if dep is not None),
        ]
    )


def _writer_semantic_text(writer: Writer) -> str:
    learning_sources = writer.learning_sources or []
    return " ".join(
        [
            writer.specialty,
            writer.style,
            " ".join(writer.focus_paths),
            " ".join(writer.focus_areas),
            " ".join(learning_sources),
        ]
    )


def _embedding_cache_key(kind: str, payload: str, vector_dim: int) -> str:
    return f"{kind}:{vector_dim}:{payload}"


def _cached_hash_vec(
    kind: str,
    payload: str,
    vector_dim: int,
    ttl_seconds: int | None = None,
) -> List[float]:
    now = time.time()
    key = _embedding_cache_key(kind, payload, vector_dim)
    cached = _EMBEDDING_CACHE.get(key)
    if cached is not None:
        expires_at, vec = cached
        if ttl_seconds is None or now <= expires_at:
            return vec

    vec = _hash_vec(_tokenize(payload), dim=vector_dim)
    expires_at = float("inf") if ttl_seconds is None else now + ttl_seconds
    _EMBEDDING_CACHE[key] = (expires_at, vec)
    return vec


def semantic_candidates_for_node(
    node: Dict[str, Any],
    writers: Dict[str, Writer],
    top_k: int,
    vector_dim: int = 256,
    cache_ttl_seconds: int | None = None,
) -> List[Tuple[str, float]]:
    """
    Goal:
        Rank writer ids for a node using semantic similarity.

    Input:
        - node: mapping with optional keys path/task_tags/depends_on
        - writers: writer map keyed by writer id
        - top_k: number of results (must be >= 1)
        - vector_dim: embedding dimensionality (must be >= 1)

    Output:
        List[(writer_id, score)] sorted descending by score, length <= top_k.

    Edge cases:
        - empty writers => []
        - top_k <= 0 or vector_dim <= 0 => []
    """
    if top_k <= 0 or vector_dim <= 0 or not writers:
        return []
    node_text = _node_semantic_text(node)
    node_vec = _cached_hash_vec("node", node_text, vector_dim, ttl_seconds=cache_ttl_seconds)
    scored: List[Tuple[str, float]] = []
    for writer in writers.values():
        writer_text = _writer_semantic_text(writer)
        writer_vec = _cached_hash_vec("writer", writer_text, vector_dim, ttl_seconds=cache_ttl_seconds)
        scored.append((writer.id, _cosine(node_vec, writer_vec)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


def recommend_blocks_for_node(
    node: Dict[str, Any],
    blocks: List[Block],
    top_k: int,
    vector_dim: int = 256,
    cache_ttl_seconds: int | None = None,
) -> List[Tuple[str, float]]:
    """
    Goal:
        Recommend reusable block ids for a given node.

    Input:
        - node: mapping with optional path/task_tags/depends_on
        - blocks: block list
        - top_k: number of results (must be >= 1)
        - vector_dim: embedding dimensionality (must be >= 1)

    Output:
        List[(block_id, score)] sorted descending by score, length <= top_k.

    Edge cases:
        - empty blocks => []
        - top_k <= 0 or vector_dim <= 0 => []
    """
    if top_k <= 0 or vector_dim <= 0 or not blocks:
        return []
    node_text = _node_semantic_text(node)
    node_vec = _cached_hash_vec("node", node_text, vector_dim, ttl_seconds=cache_ttl_seconds)
    scored: List[Tuple[str, float]] = []
    for block in blocks:
        block_vec = _cached_hash_vec("block", block.semantic_text(), vector_dim, ttl_seconds=cache_ttl_seconds)
        scored.append((block.id, _cosine(node_vec, block_vec)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]


def build_block_bundle_for_theme(
    requested_tags: List[str],
    blocks: List[Block],
    max_items: int = 8,
) -> List[Dict[str, Any]]:
    """
    Build a ready-to-compose block bundle for a game theme.

    Input:
        - requested_tags: tags such as ["space", "vehicle", "energy"]
        - blocks: reusable blocks
        - max_items: hard cap for bundle size

    Output:
        Ordered bundle of blocks with overlap scores.
    """
    if max_items <= 0 or not blocks:
        return []

    tag_set = {tag.lower() for tag in requested_tags}
    scored: List[Tuple[float, Block]] = []
    for block in blocks:
        block_tags = {tag.lower() for tag in block.tags}
        overlap = len(tag_set & block_tags)
        if overlap > 0:
            scored.append((float(overlap), block))

    scored.sort(key=lambda item: item[0], reverse=True)
    bundle: List[Dict[str, Any]] = []
    for overlap, block in scored[:max_items]:
        bundle.append(
            {
                "id": block.id,
                "name": block.name,
                "tags": block.tags,
                "overlap_score": overlap,
                "input_contract": block.input_contract,
                "output_contract": block.output_contract,
            }
        )
    return bundle


def hybrid_rank_writers_for_node(
    node: Dict[str, Any],
    candidate_writer_ids: List[str],
    writers: Dict[str, Writer],
    weights: Dict[str, float],
    top_k: int,
    vector_dim: int = 256,
    historical_scores: Dict[str, float] | None = None,
    cache_ttl_seconds: int | None = None,
) -> Tuple[List[str], Dict[str, float]]:
    """
    Goal:
        Combine rule rank and semantic scores into a hybrid ranking.

    Output:
        - top writer ids (length <= top_k)
        - per-writer final score table
    """
    if top_k <= 0 or vector_dim <= 0:
        return [], {}
    historical_scores = historical_scores or {}
    semantic = dict(
        semantic_candidates_for_node(
            node,
            writers,
            top_k=len(writers),
            vector_dim=vector_dim,
            cache_ttl_seconds=cache_ttl_seconds,
        )
    )
    rule_rank = {writer_id: rank for rank, writer_id in enumerate(candidate_writer_ids)}

    all_candidates = set(candidate_writer_ids) | set(semantic)
    scored: List[Tuple[str, float]] = []
    detail: Dict[str, float] = {}

    for writer_id in all_candidates:
        if writer_id not in writers:
            continue
        rule_score = 1.0 / (1 + rule_rank.get(writer_id, 999))
        semantic_score = semantic.get(writer_id, 0.0)
        historical_score = historical_scores.get(writer_id, 0.0)

        final_score = (
            weights.get("rule", 0.6) * rule_score
            + weights.get("semantic", 0.3) * semantic_score
            + weights.get("historical", 0.1) * historical_score
        )
        detail[writer_id] = final_score
        scored.append((writer_id, final_score))

    scored.sort(key=lambda item: item[1], reverse=True)
    top = [writer_id for writer_id, _score in scored[:top_k]]
    return top, detail


def build_semantic_assignment_metrics(score_table: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    total_nodes = len(score_table)
    if total_nodes == 0:
        return {"nodes": 0, "mean_top_score": 0.0}

    top_scores = []
    for per_node_scores in score_table.values():
        if per_node_scores:
            top_scores.append(max(per_node_scores.values()))
    if not top_scores:
        return {"nodes": total_nodes, "mean_top_score": 0.0}

    return {
        "nodes": total_nodes,
        "mean_top_score": sum(top_scores) / len(top_scores),
    }


def build_selection_telemetry(
    recommendations: Dict[str, List[str]],
    selected: Dict[str, str],
) -> Dict[str, Any]:
    not_selected: List[Dict[str, str]] = []
    total_recommended = 0
    total_fallback = 0
    confidence_values: List[float] = []

    for node, recs in recommendations.items():
        total_recommended += len(recs)
        chosen = selected.get(node)
        if chosen is None:
            total_fallback += 1
            continue
        if chosen not in recs:
            not_selected.append({"node": node, "chosen": chosen, "top_recommended": recs[0] if recs else ""})

        if recs:
            confidence_values.append(1.0 if chosen == recs[0] else 0.5 if chosen in recs else 0.0)

    coverage = 0.0 if not recommendations else 1 - (total_fallback / len(recommendations))
    mean_confidence = 0.0 if not confidence_values else sum(confidence_values) / len(confidence_values)

    return {
        "coverage": coverage,
        "fallback_rate": 0.0 if not recommendations else total_fallback / len(recommendations),
        "mean_confidence": mean_confidence,
        "recommended_but_not_selected": not_selected,
        "total_recommended": total_recommended,
    }


def calculate_node_latency_metrics(latencies: List[float]) -> Dict[str, float]:
    """Return p50/p95/mean latency metrics in seconds."""
    if not latencies:
        return {"p50": 0.0, "p95": 0.0, "mean": 0.0}
    ordered = sorted(latencies)
    p50_index = min(len(ordered) - 1, int(0.50 * (len(ordered) - 1)))
    p95_index = min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))
    return {
        "p50": ordered[p50_index],
        "p95": ordered[p95_index],
        "mean": statistics.mean(ordered),
    }


def profile_semantic_pipeline(
    nodes: List[Dict[str, Any]],
    writers: Dict[str, Writer],
    blocks: List[Block],
    vector_dim: int,
    top_k: int,
) -> Dict[str, Any]:
    cpu_profiler = cProfile.Profile()
    tracemalloc.start()
    node_latencies: List[float] = []

    def _run() -> None:
        for node in nodes:
            t0 = time.perf_counter()
            semantic_candidates_for_node(node, writers, top_k=top_k, vector_dim=vector_dim, cache_ttl_seconds=300)
            recommend_blocks_for_node(node, blocks, top_k=top_k, vector_dim=vector_dim, cache_ttl_seconds=300)
            node_latencies.append(time.perf_counter() - t0)

    cpu_profiler.enable()
    _run()
    cpu_profiler.disable()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    stream = io.StringIO()
    stats = pstats.Stats(cpu_profiler, stream=stream).sort_stats("cumtime")
    stats.print_stats(10)
    return {
        "latency": calculate_node_latency_metrics(node_latencies),
        "memory_bytes": {"current": current_mem, "peak": peak_mem},
        "cpu_top_functions": stream.getvalue(),
    }


def run_ab_tests(
    nodes: List[Dict[str, Any]],
    writers: Dict[str, Writer],
    blocks: List[Block],
    vector_dims: List[int] | None = None,
    top_ks: List[int] | None = None,
) -> List[Dict[str, Any]]:
    """
    Run matrix A/B tests across vector dimensions and top-k settings.

    Constraints:
        - vector_dims values must be positive integers
        - top_ks values must be positive integers
    """
    vector_dims = vector_dims or [128, 256, 512]
    top_ks = top_ks or [5, 10, 20]
    vector_dims = [value for value in vector_dims if value > 0]
    top_ks = [value for value in top_ks if value > 0]
    if not vector_dims or not top_ks:
        return []

    results: List[Dict[str, Any]] = []
    for vector_dim in vector_dims:
        for top_k in top_ks:
            profile = profile_semantic_pipeline(nodes, writers, blocks, vector_dim=vector_dim, top_k=top_k)
            results.append(
                {
                    "vector_dim": vector_dim,
                    "top_k": top_k,
                    "latency": profile["latency"],
                    "memory_peak_bytes": profile["memory_bytes"]["peak"],
                }
            )
    return results
