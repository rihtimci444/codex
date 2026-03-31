# Uzay Aracı Tasarım Yapıları (Game Design + Tech Design)

Bu doküman, oyunda "uzay aracı nasıl tasarlanır" sorusuna hem tasarım (gameplay) hem teknik (kod) bakışından net bir yapı sunar.

## 1) Tasarım Katmanları

Uzay aracı tasarımını 4 katmanda düşünün:

1. **Role (Rol)**
   - Cargo (yük)
   - Scout (keşif)
   - Mining (madencilik)
   - Combat (güvenlik/koruma)

2. **Hull (Gövde Sınıfı)**
   - Hafif / Orta / Ağır
   - Slot kapasitesi (engine, reactor, cargo, utility)

3. **Subsystems (Alt Sistemler)**
   - Engine
   - Reactor / Power
   - Fuel tank
   - Life support
   - Navigation / Sensors
   - Cargo bay / Drone bay

4. **Loadout (Yükleme Konfigürasyonu)**
   - Modül kombinasyonu
   - Yakıt/enerji dengesi
   - Görev odaklı tuning

## 2) Kod Yapısı (Önerilen)

### Domain modelleri

- `ShipBlueprint`
- `ShipHull`
- `ShipModule`
- `ShipAssemblyState`
- `ShipValidationReport`

### Servisler

- `ship_blueprint_service.py`
  - blueprint oluşturma/sürümleme
- `ship_validation_service.py`
  - slot/enerji/kütle/uyumluluk kontrolü
- `ship_assembly_service.py`
  - üretim kuyruğu + montaj
- `ship_performance_service.py`
  - hız, menzil, taşıma kapasitesi

### Event’ler

- `ship.blueprint.created`
- `ship.validation.failed`
- `ship.assembly.started`
- `ship.assembly.completed`
- `ship.launch.ready`

## 3) Zorunlu Kurallar (Validation)

1. Slot uyumu
   - Her modül doğru slot tipine takılmalı.
2. Enerji dengesi
   - `power_generation >= power_consumption`
3. Kütle limiti
   - `total_mass <= hull.max_mass`
4. Yakıt menzil eşiği
   - Göreve uygun minimum menzil sağlanmalı.
5. Güvenlik eşiği
   - Yaşam destek + acil durum sistemleri zorunlu.

## 4) Örnek Veri Şeması

```json
{
  "blueprint_id": "ship.cargo.mk1",
  "role": "cargo",
  "hull": "medium",
  "modules": [
    {"slot": "engine", "module_id": "engine.ion.m2"},
    {"slot": "reactor", "module_id": "reactor.fusion.s1"},
    {"slot": "cargo", "module_id": "cargo.bay.l2"},
    {"slot": "utility", "module_id": "nav.long_range.r1"}
  ]
}
```

## 5) Performans Formülleri (Basit Başlangıç)

- `thrust_to_mass = total_thrust / total_mass`
- `range = (fuel_capacity * engine_efficiency) / mass_factor`
- `cargo_efficiency = cargo_capacity / total_mass`

Bunları önce basit tutun, telemetry ile iteratif kalibre edin.

## 6) Oyun Döngüsüne Entegrasyon

1. Oyuncu blueprint seçer veya oluşturur.
2. Sistem validation raporu üretir.
3. Eksik modül/parça varsa Earth cargo siparişi tetiklenir.
4. Parçalar gelince montaj kuyruğu çalışır.
5. Montaj tamamlanınca launch readiness hesaplanır.
6. Uçuş testi / görev simülasyonu ile kalite kapısı geçilir.

## 7) UI Akışı (Ekranlar)

- Blueprint Editor
- Validation Panel (hata/uyarı)
- Assembly Queue
- Flight Readiness Dashboard
- Mission Fit Score (cargo/scout/mining/combat)

## 8) Test Stratejisi

### Unit
- modül-slot doğrulama
- enerji/kütle denklemi
- menzil hesabı

### Integration
- cargo siparişi -> montaj -> launch hazır akışı
- hatalı blueprint’in doğrulama panelinde doğru hata üretmesi

### Simulation
- 100 farklı blueprint seed ile denge testi
- görev başarısına etkilerin ölçümü

## 9) İlk Kodlanacak Fonksiyonlar

- `validate_blueprint(blueprint, module_catalog, hull_catalog) -> ShipValidationReport`
- `estimate_ship_stats(blueprint, module_catalog, hull_catalog) -> dict`
- `build_assembly_plan(blueprint, inventory_state) -> list[BuildStep]`
- `compute_launch_readiness(validation_report, assembly_state) -> float`

Bu yapı ile tasarım ekibi ve yazılım ekibi aynı sözlükle ilerler; hem oynanış hem teknik borç yönetilebilir kalır.
