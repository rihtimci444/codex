# Görev Bazlı Detaylı Sıralama (Fonksiyon + Nesne + Ortam + Kamera + Zaman + Eylem)

Bu doküman kısa sıralamayı detaylandırır. Her görev için:

- kullanılacak fonksiyonlar
- ilişkili nesneler
- ortamlar
- kamera açıları
- zaman pencereleri
- eylemler
- dünya nesneleri

Veri kaynağı: `scripts/data/task_playbooks.json`

## Sıra-1: Habitat Bootstrap

- Fonksiyonlar: `validate_build_recipe`, `build_inventory_slots`, `compute_dynamic_lighting`
- İlişkili nesneler: `BuildRecipe`, `InventoryItem`, `LightingState`
- Ortamlar: `planet_surface`, `habitat_interior`
- Kamera: `top_down`, `third_person`
- Zaman: `day_cycle`, `construction_window`
- Eylemler: malzeme toplama, modül yerleştirme, yaşam desteği açma

## Sıra-2: Space Farming Robot Loop

- Fonksiyonlar: `compute_dynamic_lighting`, `allocate_robot_fleet_to_jobs`, `plan_cargo_robot_routes`
- İlişkili nesneler: `HydroponicBed`, `RobotChassis`, `MotionCommand`
- Ortamlar: `greenhouse`, `storage_depot`
- Kamera: `top_down`, `cinematic`
- Zaman: `grow_cycle`, `harvest_cycle`
- Eylemler: ekim, hasat, depoya taşıma

## Sıra-3: Earth Cargo Delivery

- Fonksiyonlar: `advance_story_state`, `generate_missions_for_phase`, `build_cinematic_shot_plan`
- İlişkili nesneler: `StoryArc`, `Mission`, `CameraState`
- Ortamlar: `cargo_port`, `orbit_dock`, `earth_link_terminal`
- Kamera: `third_person`, `cinematic`
- Zaman: sipariş, ETA, teslim pencereleri
- Eylemler: sipariş, takip, gümrük, boşaltma

## Sıra-4: Vehicle Drive + Repair

- Fonksiyonlar: `compute_drive_force`, `apply_terrain_response`, `integrate_robot_state`
- İlişkili nesneler: `MotorSpec`, `RobotState`, `TerrainCell`
- Ortamlar: `road_network`, `offroad_zone`, `repair_bay`
- Kamera: `third_person`, `first_person`
- Zaman: `mission_timer`, `repair_window`
- Eylemler: sürüş, yakıt tüketimi, arıza tanılama, onarım

## Sıra-5: Shipyard Launch Readiness

- Fonksiyonlar: `build_composition_plan`, `validate_blueprint`, `compute_launch_readiness`
- İlişkili nesneler: `ShipBlueprint`, `ShipModule`, `ShipValidationReport`
- Ortamlar: `shipyard_factory`, `launch_pad`, `orbital_gate`
- Kamera: `top_down`, `cinematic`, `third_person`
- Zaman: `assembly_window`, `launch_window`
- Eylemler: modül montajı, validasyon, fırlatma testi

## Uygulama Notu

Bu görevler "tek seferde" değil, bağımlılık ve etki skoruna göre sprintlere bölünerek yürütülmelidir.
Öncelik sıralaması için `scripts/task_scheduler.py` + `scripts/data/implementation_tasks.json` kullanılır.
