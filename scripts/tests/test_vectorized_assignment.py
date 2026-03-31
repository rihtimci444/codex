from __future__ import annotations

from pathlib import Path
import json
import importlib
import os
import tempfile
import time
import unittest

from scripts.vectorized_assignment import (
    Block,
    Writer,
    _cached_hash_vec,
    _cosine,
    _hash_vec,
    _read_json,
    build_block_bundle_for_theme,
    build_selection_telemetry,
    calculate_node_latency_metrics,
    hybrid_rank_writers_for_node,
    load_blocks,
    load_semantic_weights,
    recommend_blocks_for_node,
    profile_semantic_pipeline,
    run_ab_tests,
    semantic_candidates_for_node,
)


class VectorizedAssignmentTests(unittest.TestCase):
    def test_robot_motion_contracts_module_imports(self) -> None:
        module = importlib.import_module("scripts.robot_motion_contracts")
        self.assertTrue(hasattr(module, "MotorSpec"))
        story_module = importlib.import_module("scripts.story_mission_contracts")
        self.assertTrue(hasattr(story_module, "Mission"))
        camera_module = importlib.import_module("scripts.camera_system_contracts")
        self.assertTrue(hasattr(camera_module, "CameraState"))
        audio_module = importlib.import_module("scripts.audio_timeline_contracts")
        self.assertTrue(hasattr(audio_module, "TimelineCue"))

    def test_hash_vec_is_unit_norm(self) -> None:
        vec = _hash_vec(["combat", "combat", "ai"], dim=64)
        norm = sum(v * v for v in vec) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=7)

    def test_cosine_identical_and_orthogonal(self) -> None:
        self.assertAlmostEqual(_cosine([1.0, 0.0], [1.0, 0.0]), 1.0)
        self.assertAlmostEqual(_cosine([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_semantic_candidates(self) -> None:
        node = {"path": "ai/enemy/aggro.py", "task_tags": ["ai", "combat"], "depends_on": []}
        writers = {
            "w_ai": Writer("w_ai", "ai", ["ai/"], ["combat", "fsm"], "concise"),
            "w_tools": Writer("w_tools", "tools", ["tools/"], ["pipeline"], "verbose"),
        }
        candidates = semantic_candidates_for_node(node, writers, top_k=1, vector_dim=128)
        self.assertEqual(candidates[0][0], "w_ai")

    def test_block_recommendations(self) -> None:
        node = {"path": "combat/hit.py", "task_tags": ["combat", "mechanics"], "depends_on": []}
        blocks = [
            Block("combat-block", "Hit Reaction", "combat mechanics reaction", ["combat", "mechanics"], [], [], {}),
            Block("ui-block", "HUD Theme", "ui color theme", ["ui"], [], [], {}),
        ]
        top = recommend_blocks_for_node(node, blocks, top_k=1, vector_dim=128)
        self.assertEqual(top[0][0], "combat-block")

    def test_hybrid_rank_preserves_rule_weight_influence(self) -> None:
        node = {"path": "net/repl.py", "task_tags": ["network", "latency"], "depends_on": []}
        writers = {
            "w_net": Writer("w_net", "network", ["net/"], ["latency", "prediction"], "direct"),
            "w_ai": Writer("w_ai", "ai", ["ai/"], ["behavior"], "concise"),
        }
        top, scores = hybrid_rank_writers_for_node(
            node=node,
            candidate_writer_ids=["w_net", "w_ai"],
            writers=writers,
            weights={"rule": 0.8, "semantic": 0.2, "historical": 0.0},
            top_k=1,
            vector_dim=128,
        )
        self.assertEqual(top, ["w_net"])
        self.assertGreater(scores["w_net"], scores["w_ai"])

    def test_tokenizer_and_cache_handle_empty_payload(self) -> None:
        vec = _cached_hash_vec("writer", "", vector_dim=32, ttl_seconds=1)
        self.assertEqual(len(vec), 32)
        self.assertTrue(all(value == 0 for value in vec))

    def test_mtime_cache_invalidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            path.write_text(json.dumps({"k": 1}), encoding="utf-8")
            first = _read_json(path)
            self.assertEqual(first["k"], 1)

            time.sleep(0.02)
            path.write_text(json.dumps({"k": 2}), encoding="utf-8")
            st = path.stat()
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
            second = _read_json(path)
            self.assertEqual(second["k"], 2)

    def test_loaders_parse_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocks_path = Path(tmp) / "block_library.json"
            blocks_path.write_text(
                json.dumps(
                    {
                        "blocks": [
                            {
                                "id": "b1",
                                "name": "Enemy Aggro FSM",
                                "description": "state machine",
                                "tags": ["ai"],
                                "input_contract": ["sight"],
                                "output_contract": ["state"],
                                "quality": {"test_pass_rate": 0.95},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            weights_path = Path(tmp) / "semantic_weights.json"
            weights_path.write_text(
                json.dumps({"weights": {"rule": 0.5, "semantic": 0.4, "historical": 0.1}, "top_k_writers": 5}),
                encoding="utf-8",
            )

            blocks = load_blocks(blocks_path)
            weights = load_semantic_weights(weights_path)

            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0].id, "b1")
            self.assertEqual(weights["top_k_writers"], 5)
            self.assertEqual(weights["vector_dim"], 256)

    def test_selection_telemetry_tracks_not_selected(self) -> None:
        recommendations = {"n1": ["w1", "w2"], "n2": ["w3"]}
        selected = {"n1": "w2", "n2": "w4"}
        telemetry = build_selection_telemetry(recommendations, selected)
        self.assertAlmostEqual(telemetry["coverage"], 1.0)
        self.assertEqual(len(telemetry["recommended_but_not_selected"]), 1)
        self.assertEqual(telemetry["recommended_but_not_selected"][0]["node"], "n2")

    def test_latency_metrics_and_ab(self) -> None:
        latency = calculate_node_latency_metrics([0.2, 0.1, 0.3, 0.4])
        self.assertGreaterEqual(latency["p95"], latency["p50"])
        node = {"path": "ai/enemy/aggro.py", "task_tags": ["ai", "combat"], "depends_on": []}
        writers = {
            "w_ai": Writer("w_ai", "ai", ["ai/"], ["combat", "fsm"], "concise"),
            "w_tools": Writer("w_tools", "tools", ["tools/"], ["pipeline"], "verbose"),
        }
        blocks = [Block("b1", "Enemy Aggro", "aggro logic", ["ai"], ["sight"], ["state"], {})]
        results = run_ab_tests(
            [node],
            writers,
            blocks,
            vector_dims=[32],
            top_ks=[1, 2],
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["vector_dim"], 32)

    def test_invalid_top_k_and_vector_dim_are_handled(self) -> None:
        node = {"path": "ai/enemy/aggro.py", "task_tags": ["ai"], "depends_on": []}
        writers = {"w_ai": Writer("w_ai", "ai", ["ai/"], ["combat"], "concise")}
        blocks = [Block("b1", "Enemy Aggro", "aggro logic", ["ai"], [], [], {})]
        self.assertEqual(semantic_candidates_for_node(node, writers, top_k=0), [])
        self.assertEqual(recommend_blocks_for_node(node, blocks, top_k=-1), [])
        top, scores = hybrid_rank_writers_for_node(
            node=node,
            candidate_writer_ids=["w_ai"],
            writers=writers,
            weights={"rule": 1.0},
            top_k=0,
        )
        self.assertEqual(top, [])
        self.assertEqual(scores, {})
        self.assertEqual(run_ab_tests([node], writers, blocks, vector_dims=[0, -1], top_ks=[0]), [])

    def test_profile_semantic_pipeline_shape(self) -> None:
        node = {"path": "ai/enemy/aggro.py", "task_tags": ["ai"], "depends_on": []}
        writers = {"w_ai": Writer("w_ai", "ai", ["ai/"], ["combat"], "concise")}
        blocks = [Block("b1", "Enemy Aggro", "aggro logic", ["ai"], [], [], {})]
        profile = profile_semantic_pipeline([node], writers, blocks, vector_dim=32, top_k=1)
        self.assertIn("latency", profile)
        self.assertIn("memory_bytes", profile)
        self.assertIn("cpu_top_functions", profile)
        self.assertIn("p50", profile["latency"])

    def test_build_block_bundle_for_theme(self) -> None:
        blocks = [
            Block("space-ship", "Ship", "space travel", ["space", "spaceship"], [], [], {}),
            Block("road", "Road", "road network", ["road", "terrain"], [], [], {}),
        ]
        bundle = build_block_bundle_for_theme(["space", "vehicle"], blocks, max_items=5)
        self.assertEqual(bundle[0]["id"], "space-ship")
        self.assertGreater(bundle[0]["overlap_score"], 0)

    def test_real_block_library_contains_requested_domains(self) -> None:
        root = Path(__file__).resolve().parents[2]
        blocks = load_blocks(root / "scripts" / "data" / "block_library.json")
        tags = {tag for block in blocks for tag in block.tags}
        self.assertIn("grass", tags)
        self.assertIn("path", tags)
        self.assertIn("road", tags)
        self.assertIn("airplane", tags)
        self.assertIn("spaceship", tags)
        self.assertIn("planet", tags)
        self.assertIn("fuel", tags)
        self.assertIn("solar", tags)
        self.assertIn("alien", tags)
        self.assertIn("farming", tags)
        self.assertIn("construction", tags)
        self.assertIn("car", tags)
        self.assertIn("repair", tags)
        self.assertIn("cargo", tags)

    def test_story_and_building_data_files_parse(self) -> None:
        root = Path(__file__).resolve().parents[2]
        story_data = json.loads((root / "scripts" / "data" / "story_arcs.json").read_text(encoding="utf-8"))
        building_data = json.loads((root / "scripts" / "data" / "building_materials.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(story_data.get("arcs", [])), 3)
        self.assertGreaterEqual(len(story_data.get("mission_templates", [])), 1)
        self.assertGreaterEqual(len(building_data.get("materials", [])), 5)
        self.assertGreaterEqual(len(building_data.get("recipes", [])), 1)

    def test_algorithmic_task_schedule_parses_and_orders(self) -> None:
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / "scripts" / "data" / "implementation_tasks.json").read_text(encoding="utf-8"))
        scheduler = importlib.import_module("scripts.task_scheduler")
        Task = getattr(scheduler, "Task")
        schedule_tasks = getattr(scheduler, "schedule_tasks")
        tasks = [
            Task(
                task_id=item["task_id"],
                files=item["files"],
                depends_on=item["depends_on"],
                impact=item["impact"],
                urgency=item["urgency"],
                effort=item["effort"],
                risk=item["risk"],
            )
            for item in data["tasks"]
        ]
        ordered = schedule_tasks(tasks)
        self.assertEqual(len(ordered), len(tasks))
        self.assertEqual(ordered[0].task_id, "task.foundation.domain-contracts")

    def test_task_playbooks_have_required_fields(self) -> None:
        root = Path(__file__).resolve().parents[2]
        payload = json.loads((root / "scripts" / "data" / "task_playbooks.json").read_text(encoding="utf-8"))
        playbooks = payload.get("playbooks", [])
        self.assertGreaterEqual(len(playbooks), 3)
        required = {
            "task_id",
            "functions",
            "related_objects",
            "environments",
            "camera_angles",
            "time_windows",
            "actions",
            "world_objects",
        }
        for playbook in playbooks:
            self.assertTrue(required.issubset(playbook.keys()))

    def test_world_kroki_has_zones_routes_and_camera_pois(self) -> None:
        root = Path(__file__).resolve().parents[2]
        payload = json.loads((root / "scripts" / "data" / "world_kroki.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(payload.get("zones", [])), 5)
        self.assertGreaterEqual(len(payload.get("routes", [])), 5)
        self.assertGreaterEqual(len(payload.get("camera_pois", [])), 2)

    def test_audio_light_timeline_has_phase_cues(self) -> None:
        root = Path(__file__).resolve().parents[2]
        payload = json.loads((root / "scripts" / "data" / "audio_light_timeline.json").read_text(encoding="utf-8"))
        phases = payload.get("phases", [])
        self.assertGreaterEqual(len(phases), 3)
        for phase in phases:
            self.assertIn("phase", phase)
            self.assertGreaterEqual(len(phase.get("cues", [])), 1)


if __name__ == "__main__":
    unittest.main()
