from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Protocol, Tuple


class ArchitectureChoice(str, Enum):
    DOMAIN_EVENT_DRIVEN = "domain_event_driven"
    HEXAGONAL = "hexagonal_ports_adapters"
    ECS_RUNTIME = "ecs_runtime"


@dataclass(frozen=True)
class VectorConfig:
    vector_dim: int
    top_k_writers: int
    top_k_blocks: int
    cache_ttl_seconds: int


@dataclass(frozen=True)
class PipelineOutputs:
    writer_contributions: Dict[str, Any]
    coordination_report: Dict[str, Any]
    telemetry: Dict[str, Any]


class EmbeddingProvider(Protocol):
    def embed_text(self, text: str, vector_dim: int) -> List[float]:
        ...


def run_vectorized_assignment_pipeline(config: VectorConfig) -> PipelineOutputs:
    """Main orchestration contract for runtime integration."""
    raise NotImplementedError


def precompute_writer_embeddings(
    writers: Dict[str, Dict[str, Any]],
    vector_dim: int,
    cache_ttl_seconds: int,
) -> Dict[str, List[float]]:
    """Precompute writer embeddings once per run."""
    raise NotImplementedError


def precompute_block_embeddings(
    blocks: List[Dict[str, Any]],
    vector_dim: int,
    cache_ttl_seconds: int,
) -> Dict[str, List[float]]:
    """Precompute block embeddings once per run."""
    raise NotImplementedError


def semantic_candidates_for_nodes(
    nodes: List[Dict[str, Any]],
    writers: Dict[str, Dict[str, Any]],
    config: VectorConfig,
) -> Dict[str, List[Tuple[str, float]]]:
    """Batch writer ranking contract."""
    raise NotImplementedError


def recommend_blocks_for_nodes(
    nodes: List[Dict[str, Any]],
    blocks: List[Dict[str, Any]],
    config: VectorConfig,
) -> Dict[str, List[Tuple[str, float]]]:
    """Batch block recommendation contract."""
    raise NotImplementedError


def build_composition_plan(
    selected_block_ids: List[str],
    dependency_graph: Dict[str, List[str]],
) -> Dict[str, Any]:
    """Composable build-order contract."""
    raise NotImplementedError
