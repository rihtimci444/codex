from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class CameraMode(str, Enum):
    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"
    TOP_DOWN = "top_down"
    CINEMATIC = "cinematic"


@dataclass(frozen=True)
class CameraState:
    mode: CameraMode
    position_xyz: Tuple[float, float, float]
    target_xyz: Tuple[float, float, float]
    fov_deg: float
    pitch_deg: float
    yaw_deg: float
    roll_deg: float


@dataclass(frozen=True)
class CameraConstraints:
    min_distance: float
    max_distance: float
    min_pitch: float
    max_pitch: float


def compute_camera_state(
    mode: CameraMode,
    player_position_xyz: Tuple[float, float, float],
    player_velocity_xyz: Tuple[float, float, float],
    dt_s: float,
) -> CameraState:
    """Compute camera transform per frame for selected gameplay mode."""
    raise NotImplementedError


def apply_camera_constraints(
    state: CameraState,
    constraints: CameraConstraints,
) -> CameraState:
    """Clamp and smooth camera parameters for comfort and collision safety."""
    raise NotImplementedError


def build_cinematic_shot_plan(
    poi_positions: Dict[str, Tuple[float, float, float]],
    duration_s: float,
) -> Dict[str, object]:
    """Generate keyframed camera sequence for mission/cutscene moments."""
    raise NotImplementedError
