from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class StoryArc:
    arc_id: str
    title: str
    phase: str
    unlock_conditions: List[str]


@dataclass(frozen=True)
class Mission:
    mission_id: str
    arc_id: str
    title: str
    objectives: List[str]
    rewards: Dict[str, Any]
    time_limit_ticks: int | None = None


@dataclass(frozen=True)
class LightingState:
    sun_angle_deg: float
    ambient_intensity: float
    shadow_strength: float
    weather_factor: float


@dataclass(frozen=True)
class InventoryItem:
    item_id: str
    category: str
    weight_kg: float
    stack_limit: int


@dataclass(frozen=True)
class BuildRecipe:
    recipe_id: str
    structure_type: str
    materials: Dict[str, int]
    required_tools: List[str]


def advance_story_state(
    current_phase: str,
    completed_missions: List[str],
    world_flags: Dict[str, bool],
) -> str:
    """Advance narrative phase according to mission progression and world state."""
    raise NotImplementedError


def generate_missions_for_phase(
    phase: str,
    player_level: int,
    colony_state: Dict[str, Any],
) -> List[Mission]:
    """Create mission set for current story phase and colony conditions."""
    raise NotImplementedError


def compute_dynamic_lighting(
    tick: int,
    orbital_period_ticks: int,
    weather_factor: float,
) -> LightingState:
    """Compute time-evolving lighting values for gameplay and visuals."""
    raise NotImplementedError


def build_inventory_slots(
    capacity_kg: float,
    items: List[InventoryItem],
) -> Dict[str, Any]:
    """Create constrained inventory layout and aggregate capacity metrics."""
    raise NotImplementedError


def validate_build_recipe(
    recipe: BuildRecipe,
    available_materials: Dict[str, int],
    available_tools: List[str],
) -> Dict[str, Any]:
    """Validate if a home/base recipe can be built with current resources."""
    raise NotImplementedError
