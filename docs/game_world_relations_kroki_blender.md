# Oyun Sistem İlişkileri + Harita Krokisi + Blender 3D Üretim Planı

Bu doküman, projedeki yapıları (motorlar/nesneler/hareketler/kamera/efekt/tasarım)
birbirine bağlar ve harita krokisini + 3D üretim bütçelerini verir.

## 1) Sistem İlişki Matrisi

| Sistem | İlişkili Motor/Fonksiyon | İlişkili Nesneler | Kamera | Efekt |
|---|---|---|---|---|
| Robot Sürüş | `compute_drive_force`, `apply_terrain_response`, `integrate_robot_state` | `MotorSpec`, `RobotState`, `TerrainCell` | third-person / first-person | toz, teker izleri, süspansiyon shake |
| Uzay Tarımı | `compute_dynamic_lighting`, `allocate_robot_fleet_to_jobs` | `HydroponicBed`, `InventoryItem` | top-down / cinematic | nem, sis, büyüme ışığı |
| Kargo Lojistik | `plan_cargo_robot_routes`, story mission fonksiyonları | cargo manifest, shipment nesneleri | third-person / cinematic | iniş kalkış partikülleri |
| Shipyard | `build_composition_plan`, `validate_blueprint` | `ShipBlueprint`, `ShipModule` | top-down / cinematic | kaynak kıvılcımı, motor test alevi |
| Ev/Üs İnşası | `validate_build_recipe`, `build_inventory_slots` | yapı tarifleri, malzeme listeleri | top-down / third-person | kaynak, toz, inşaat hologramı |

## 2) Harita Krokisi (Top-Down)

Referans veri: `scripts/data/world_kroki.json`

```text
                          [Mining Ridge z_mining]
                                   *
                                   |
                     * [Shipyard z_shipyard]
                         \        |
                          \       |
 [Cargo Port z_logistics]--*--[Landing z_landing]--*--[Habitat z_habitat]--*--[Greenhouse z_greenhouse]
                                |
                                *
                       [Repair Bay z_repair]
```

Ana akış:

- Landing -> Habitat (ilk kurulum)
- Habitat -> Greenhouse (tarım)
- Habitat -> Cargo Port (Earth lojistik)
- Habitat -> Shipyard (uzay aracı üretim)
- Habitat -> Repair Bay (araç bakım)

## 3) Kamera Açı Stratejisi

1. **Top-Down**
   - üs kurma, tarım ve lojistik planlama ekranları
2. **Third-Person**
   - araç sürüş, robot takip, görev yürütme
3. **First-Person**
   - ince tamir, iç mekan etkileşim
4. **Cinematic**
   - kargo inişi, fırlatma, kritik görev geçişi

Kamera POI’leri `world_kroki.json.camera_pois` alanı ile bağlanır.

## 4) Blender 3D Üretim Bütçesi (Performans + Zorluk)

### LOD hedefleri (tek asset)

- LOD0: 20k–60k tri (hero nesneler: gemi, ana araç)
- LOD1: 8k–20k tri
- LOD2: 2k–8k tri
- LOD3: 300–2k tri (uzak görünüm)

### Sınıf bazlı tri bütçesi

- Robot/araç: 15k–40k (LOD0)
- Uzay gemisi: 40k–120k (LOD0)
- Yapılar (modüler): parça başına 2k–15k
- Ortam props: 300–8k

### Texture hedefleri

- Hero asset: 2K–4K
- Standart: 1K–2K
- Uzak/prop: 512–1K

## 5) Zorluk ve Oyun Ağırlığı (Balancing)

Zorluk eksenleri:

1. Enerji kıtlığı
2. Lojistik gecikme (Earth cargo ETA)
3. Mekanik arıza oranı (araç/robot)
4. İklim/ışık etkisi (tarım verimi)

Önerilen başlangıç eğrisi:

- Erken oyun: düşük arıza, yüksek kaynak erişimi
- Orta oyun: enerji + taşıma darboğazı
- Geç oyun: çoklu sistem optimizasyonu (shipyard + farming + logistics)

## 6) Üretim Sırası (Blender + Kod)

1. Harita bloklama (kroki koordinatlarıyla)
2. Yol ve rota mesh’leri
3. Robot/araç base rig
4. Habitat + greenhouse modülleri
5. Shipyard seti + gemi iskeleti
6. LOD ve collision pass
7. Kamera POI yerleşimi
8. Efekt pass (toz, kaynak, motor alevi)

## 7) Kabul Kriterleri

- Harita zoneleri + rota grafı JSON’da tanımlı
- Kamera modları POI’lerle eşlenmiş
- Hero assetlerde LOD zinciri hazır
- Sürüş/tarım/lojistik için en az 1 dikey dilim oynanabilir
- p95 frame ve görev gecikme hedefleri raporlanabilir
