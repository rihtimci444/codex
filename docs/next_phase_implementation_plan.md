# Next Phase Implementation Plan

This plan describes the concrete code to write in the next phase of the vectorized assignment project.

## Phase 1 (High Priority): Integrate with Runtime Outputs

### 1. Add orchestration entrypoint

**File**: `scripts/vectorized_assignment.py`

Add a production entrypoint that wires loaders + scoring + output persistence:

- `run_vectorized_assignment_pipeline(...)`
- Inputs:
  - `issue_page_path`, `code_map_path`, `writers_path`, `block_library_path`, `weights_path`
- Outputs:
  - `writer_contributions.json` with:
    - `recommended_block_ids`
    - `semantic_score`
  - `coordination_report.json` with:
    - `semantic_assignment_metrics`
    - `selection_telemetry`
    - `ab_test_baseline`

### 2. Add config model

**File**: `scripts/vectorized_assignment.py`

Introduce explicit config dataclasses:

- `VectorConfig`:
  - `vector_dim`
  - `top_k_writers`
  - `top_k_blocks`
  - `cache_ttl_seconds`
- `TelemetryConfig`:
  - `enable_recommended_not_selected`
  - `emit_latency_metrics`
  - `emit_profiling_summary`

### 3. Add output schema validators

**Files**:
- `scripts/vectorized_assignment.py`
- `scripts/tests/test_vectorized_assignment.py`

Add lightweight runtime checks for required output keys to avoid schema drift.

## Phase 2 (High Priority): Fast Path Optimization

### 4. Precompute embeddings once per run

**File**: `scripts/vectorized_assignment.py`

Add precomputation helpers:

- `precompute_writer_embeddings(writers, vector_dim, ttl)`
- `precompute_block_embeddings(blocks, vector_dim, ttl)`

Refactor ranking functions to optionally accept precomputed embeddings and avoid repeated hashing per node.

### 5. Batch scoring API

**File**: `scripts/vectorized_assignment.py`

Add:

- `semantic_candidates_for_nodes(nodes, writers, ...)`
- `recommend_blocks_for_nodes(nodes, blocks, ...)`

This will reduce repeated overhead and simplify profiling.

## Phase 3 (Medium Priority): Composition Workflow

### 6. Add composition planner

**File**: `scripts/vectorized_assignment.py`

Implement:

- `build_composition_plan(bundle, dependencies)`

Purpose: combine selected ready blocks (grass/path/road/space systems/etc.) into executable build order with dependency edges.

### 7. Add dependency contracts per block

**File**: `scripts/data/block_library.json`

Add fields:

- `depends_on_blocks`
- `provides_interfaces`

This enables automatic compatibility checks before composition.

## Phase 4 (Medium Priority): Telemetry Feedback Loop

### 8. Historical score updater

**Files**:
- `scripts/vectorized_assignment.py`
- `scripts/data/` (new telemetry store json)

Add:

- `update_historical_scores(selection_telemetry, store_path)`

Use recommended-but-not-selected outcomes to adjust historical scores gradually.

### 9. Confidence and fallback dashboard payload

**File**: `scripts/vectorized_assignment.py`

Emit dashboard-friendly payload:

- `coverage`
- `fallback_rate`
- `mean_confidence`
- `top_missed_recommendations`

## Phase 5 (Low Priority): Developer Experience

### 10. Add CLI wrapper

**File**: `scripts/vectorized_assignment_cli.py`

Commands:

- `run`
- `profile`
- `ab-test`
- `bundle`

### 11. Add golden snapshot tests for outputs

**File**: `scripts/tests/test_vectorized_assignment_outputs.py`

Use fixed fixtures to validate full JSON output shape and stability over time.

---

## Suggested immediate coding order

1. `run_vectorized_assignment_pipeline`
2. precompute writer/block embeddings
3. batch scoring functions
4. composition planner
5. historical score updater

This order gives immediate production value while preparing the block-composition stage.

See also: `docs/space_game_deep_preparation_plan.md` for domain-deep module breakdown
(space farming, construction, driving/repair, shipyard, Earth cargo).
Also see: `docs/pre_coding_architecture_kit.md` and `scripts/pre_coding_contracts.py`
for pre-coding architecture choices, library stack, and function contracts.
