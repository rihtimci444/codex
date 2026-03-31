from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CueType(str, Enum):
    MUSIC = "music"
    AMBIENT = "ambient"
    SFX = "sfx"
    LIGHTING = "lighting"


@dataclass(frozen=True)
class TimelineCue:
    cue_id: str
    cue_type: CueType
    start_tick: int
    duration_ticks: int
    intensity: float
    target: str


@dataclass(frozen=True)
class StoryMoodState:
    phase: str
    tension: float
    hope: float
    danger: float


def build_story_timeline_cues(
    story_phase: str,
    mission_state: Dict[str, str],
    mood: StoryMoodState,
) -> List[TimelineCue]:
    """Generate time-scheduled audio/light cues for current story context."""
    raise NotImplementedError


def apply_timeline_cues(
    current_tick: int,
    cues: List[TimelineCue],
) -> Dict[str, List[str]]:
    """Return active audio/light actions at current tick."""
    raise NotImplementedError


def validate_cue_conflicts(cues: List[TimelineCue]) -> List[str]:
    """Detect overlapping/conflicting cues (same target, incompatible types)."""
    raise NotImplementedError
