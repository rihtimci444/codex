# Story, Mission, Lighting, Inventory, Building Materials, Camera Plan

Bu plan, oyuna zamanla gelişen hikaye/görev sistemi, dinamik ışıklandırma, envanter,
ev yapımı malzeme listeleri ve kamera açı fonksiyon yapıları eklemek için hazırlanmıştır.

## 1) Hikaye ve Görev Yapısı

Veri kaynağı:

- `scripts/data/story_arcs.json`

Kod kontratları:

- `advance_story_state(...)`
- `generate_missions_for_phase(...)`

Tasarım:

- Story arc -> phase -> mission template akışı
- Her phase bir altyapı eşiğiyle açılır (ör. greenhouse, cargo port, factory)
- Görevler ödül olarak kredi, reputation, yeni robot/modül açar

## 2) Zamanla Gelişen Işıklandırma

Kod kontratı:

- `compute_dynamic_lighting(tick, orbital_period_ticks, weather_factor)`

Hedef:

- gün/gece ve orbital döngü etkisini oyuna yansıtmak
- ambient/shadow değerleriyle görsel + oynanış etkisini birleştirmek

## 3) Envanter Yapısı

Kod kontratı:

- `build_inventory_slots(capacity_kg, items)`

Kural seti:

- ağırlık limiti
- stack limiti
- kategori bazlı düzen (structure/energy/farming/logistics)

## 4) Ev Yapımı Malzemeleri ve Tarifler

Veri kaynağı:

- `scripts/data/building_materials.json`

İçerik:

- materyal listesi (çelik, panel, izolasyon, cam, kablo, boru, filtre, pil, hidroponik tepsi)
- tarifler:
  - `home.habitat.mk1`
  - `home.greenhouse.mk1`

Kod kontratı:

- `validate_build_recipe(recipe, available_materials, available_tools)`

## 5) Kamera Açı Fonksiyonları

Kod kontratları:

- `compute_camera_state(...)`
- `apply_camera_constraints(...)`
- `build_cinematic_shot_plan(...)`

Modlar:

- first person
- third person
- top down
- cinematic

## 6) Robotlar ile Taşıma ve Görev İlerlemesi

- Mission objective’ler robot işlerine çevrilir (harvest, carry, maintain, build)
- Fleet allocation motoru görev yoğunluğuna göre robot dağıtır
- Kamera modu görev tipine göre değişebilir (construction => top-down, driving => third-person)

## 7) Sprint Sırası

1. story arc + mission template yükleme
2. inventory + build recipe validation
3. dynamic lighting hesaplama
4. camera state/constraint sistemi
5. story-mission-progress + robot görev entegrasyonu

## 8) Başlangıç Kabul Kriterleri

- en az 3 story arc phase geçişi çalışıyor
- 2 ev/sera tarifi materyal kontrolü ile doğrulanıyor
- envanter ağırlık/stack ihlallerini yakalıyor
- kamera modları arası geçiş hatasız
- lighting tick bazlı deterministik değişiyor
