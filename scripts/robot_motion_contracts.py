from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple


class DriveType(str, Enum):
    WHEELED = "wheeled"
    TRACKED = "tracked"
    LEGGED = "legged"
    THRUSTER = "thruster"


@dataclass(frozen=True)
class MotorSpec:
    motor_id: str
    torque_nm: float
    max_rpm: float
    efficiency: float
    thermal_limit_c: float


@dataclass(frozen=True)
class RobotChassis:
    robot_id: str
    drive_type: DriveType
    mass_kg: float
    wheel_radius_m: float
    max_payload_kg: float


@dataclass(frozen=True)
class MotionCommand:
    throttle: float
    steering: float
    brake: float
    target_heading_deg: float


@dataclass(frozen=True)
class RobotState:
    position_xy: Tuple[float, float]
    velocity_xy: Tuple[float, float]
    heading_deg: float
    battery_kwh: float
    payload_kg: float


@dataclass(frozen=True)
class TerrainCell:
    friction_coeff: float
    slope_deg: float
    sinkage_factor: float


def compute_drive_force(command: MotionCommand, motor: MotorSpec, chassis: RobotChassis) -> float:
    """Convert motor + command to forward force (N)."""
    raise NotImplementedError


def apply_terrain_response(force_n: float, terrain: TerrainCell, payload_kg: float) -> float:
    """Apply terrain losses/slip and return effective traction force (N)."""
    raise NotImplementedError


def integrate_robot_state(
    state: RobotState,
    effective_force_n: float,
    dt_s: float,
    command: MotionCommand,
) -> RobotState:
    """Advance robot state by one simulation step."""
    raise NotImplementedError


def plan_cargo_robot_routes(
    graph: Dict[str, List[str]],
    cargo_tasks: List[Dict[str, str]],
    robot_count: int,
) -> Dict[str, List[str]]:
    """Route cargo robots between depots/farms/stations with load balancing."""
    raise NotImplementedError


def allocate_robot_fleet_to_jobs(
    fleet: List[RobotChassis],
    jobs: List[Dict[str, float]],
) -> Dict[str, str]:
    """Assign robots to jobs by payload, terrain fit and battery limits."""
    raise NotImplementedError
