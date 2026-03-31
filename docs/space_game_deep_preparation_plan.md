# Space Survival & Industry Game — Deep Preparation Plan

Scope requested:

- space farming
- construction
- car driving
- car repair
- spaceship construction
- ordering cargo from Earth

This plan turns these into concrete code modules, data contracts, and milestones.

## 1) Core Architecture (Code First)

## Services to implement

1. `economy_service.py`
   - price curves
   - budget/liquidity checks
   - imports/exports settlement
2. `logistics_service.py`
   - Earth cargo ordering
   - shipment ETA + risk events
   - docking/port capacity
3. `construction_service.py`
   - base module placement
   - dependency checks (power/air/water)
   - build queue and interruptions
4. `vehicle_service.py`
   - car driving state model
   - vehicle wear/fuel model
   - repair actions and part usage
5. `shipyard_service.py`
   - spaceship blueprint validation
   - module assembly + launch readiness
6. `farming_service.py`
   - hydroponic growth simulation
   - nutrient/light/water loops
   - harvest + spoilage pipeline

## Shared primitives

- `resource_types.py`: water, oxygen, metal, electronics, food, fuel
- `time_system.py`: ticks/day cycles/season-like orbital cycles
- `event_bus.py`: deterministic simulation events

## 2) Data Models to Implement

## Orders and logistics

```python
@dataclass
class CargoOrder:
    order_id: str
    manifest: dict[str, int]
    destination: str
    budget: float
    ordered_at_tick: int
```

```python
@dataclass
class Shipment:
    shipment_id: str
    order_id: str
    eta_tick: int
    risk_flags: list[str]
    status: str  # scheduled|in_transit|delivered|lost
```

## Construction

```python
@dataclass
class BuildTask:
    task_id: str
    blueprint_id: str
    location: str
    required_resources: dict[str, int]
    required_power: float
    status: str  # queued|building|paused|done
```

## Vehicles

```python
@dataclass
class CarState:
    vehicle_id: str
    fuel: float
    durability: float
    speed: float
    position: tuple[float, float]
```

## Farming

```python
@dataclass
class HydroponicBed:
    bed_id: str
    crop_type: str
    growth: float
    nutrient_level: float
    water_level: float
    light_level: float
```

## 3) Gameplay Loops (Must Be Coded)

1. **Earth Cargo Loop**
   - player orders resources
   - budget check
   - ETA + risk simulation
   - arrival/unpack/customs events

2. **Base Construction Loop**
   - choose blueprint
   - verify dependencies/resources
   - enqueue build
   - power/air/water gate checks

3. **Ground Ops Loop (Car Driving + Repair)**
   - route planning on roads/terrain
   - fuel consumption + wear
   - crash/damage events
   - repair bay workflow

4. **Shipyard Loop**
   - blueprint -> modules -> assembly
   - missing part constraints
   - launch readiness checks

5. **Space Farming Loop**
   - environmental control adjustments
   - growth and disease/stress checks
   - harvest and logistics to storage/market

## 4) Dependency Graph (Execution Order)

1. Resource/economy primitives
2. Logistics (Earth cargo)
3. Construction
4. Driving + repair
5. Farming
6. Shipyard
7. Cross-system balancing + telemetry tuning

## 5) Telemetry & Balancing Metrics

- p50/p95 tick processing time by service
- cargo on-time delivery rate
- construction queue utilization
- car failure rate / repair turnaround
- ship build completion time
- farming yield per cycle
- player bankruptcy rate

## 6) Test Plan (Required)

## Unit tests

- economy math
- ETA/risk generator determinism
- construction dependency validation
- vehicle fuel/durability updates
- farming growth equations

## Integration tests

- cargo arrival unblocks construction
- vehicle repair restores mission readiness
- farming output feeds logistics/economy
- shipyard blocked until required modules exist

## Simulation regression tests

- fixed seed, 30/60/120 day runs
- assert no deadlock in build/logistics loops
- assert deterministic totals for resources and money

## 7) Immediate Coding Backlog (2 Sprints)

## Sprint 1

- implement `CargoOrder` + `Shipment` + `logistics_service.py`
- implement `BuildTask` + `construction_service.py`
- add event bus contracts and snapshot tests

## Sprint 2

- implement `CarState` driving + repair
- implement hydroponics growth cycle
- implement shipyard assembly pipeline
- add balancing dashboard payloads

## 8) Content Preparation

Use `scripts/data/block_library.json` starter blocks and extend with:

- multi-tier blueprints for habitats/factories
- regional road kits + vehicle part kits
- cargo catalog from Earth (critical, bulk, luxury)
- ship classes (cargo, scout, mining)
- crop classes (fast, resilient, high-yield)

This provides enough depth to start coding immediately while keeping systems composable.

See also: `docs/spacecraft_design_system.md` for detailed spacecraft design structure,
validation rules, schemas, and implementation flow.
See also: `docs/robot_motion_simulation_tactics.md` and
`scripts/robot_motion_contracts.py` for motor movement simulation and robot fleet tactics.
See also: `docs/story_mission_inventory_camera_plan.md`,
`scripts/story_mission_contracts.py`, and `scripts/camera_system_contracts.py`
for evolving story/mission systems, dynamic lighting, inventory/build recipes, and camera modes.
See also: `docs/game_world_relations_kroki_blender.md` and `scripts/data/world_kroki.json`
for system relation map, camera/route linking, and Blender-oriented asset budgets.
See also: `docs/audio_light_music_timed_effects.md`,
`scripts/audio_timeline_contracts.py`, and `scripts/data/audio_light_timeline.json`
for time-scheduled audio/light/music story effects.
Risk controls: `docs/risk_mitigation_checklist.md`.
