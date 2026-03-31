# Robot Motor Movement & Cargo Simulation Tactics

Bu doküman, oyunda "her şey robotlarla ilerleyecek" yaklaşımı için hareket simülasyonu kod yapısını tanımlar.

## 1) Robot Hareket Mimarisi

Katmanlar:

1. **Command Layer**
   - oyuncu/AI komutları (`throttle`, `steering`, `brake`)
2. **Motor Layer**
   - tork, rpm, verim, ısıl sınır
3. **Traction Layer**
   - zemin sürtünmesi, eğim, batma/slip
4. **Integration Layer**
   - hız/pozisyon/baş yönü güncellemesi
5. **Fleet Layer**
   - rota planlama + görev atama

Referans kontratlar: `scripts/robot_motion_contracts.py`

## 2) Temel Kod Yapısı

- `compute_drive_force(...)`
  - motor + komuttan ileri kuvvet üretir
- `apply_terrain_response(...)`
  - yüzey kaybı/slip sonrası efektif çekiş hesaplar
- `integrate_robot_state(...)`
  - tek timestep ilerletir
- `plan_cargo_robot_routes(...)`
  - yük taşıma rotalarını çıkarır
- `allocate_robot_fleet_to_jobs(...)`
  - robotları işe dağıtır

## 3) Simülasyon Denklemleri (Basit Başlangıç)

- `wheel_omega = rpm * 2*pi/60`
- `wheel_force = torque / wheel_radius`
- `traction_force = min(wheel_force, mu * normal_force)`
- `acceleration = traction_force / (mass + payload)`
- `v_next = v + a * dt`
- `x_next = x + v_next * dt`

Enerji:

- `power_w = force * speed`
- `battery_delta_kwh = power_w * dt / 3_600_000`

## 4) Uzay Tarımı + Robot Taktiği

Robot tipleri:

- Harvester bot (hasat)
- Carrier bot (depo taşıma)
- Maintenance bot (onarım/sulama)

Önerilen taktık:

1. Hasat penceresini hesapla
2. Harvester botları kritik yataklara ata
3. Carrier botları bottleneck depolarına yönlendir
4. Maintenance botu düşük su/nutrient bölgelerine önceliklendir

## 5) Araba Benzeri Kontrol (Sürüş Hissi)

- PID hız kontrolü
- yaw-rate limitleri
- yüzey tipine göre dinamik sürtünme
- payload arttıkça fren mesafesi artışı

## 6) Yük Taşıma Stratejileri

1. **Milk-run**: tek robot çok durak
2. **Hub-spoke**: merkez depo + çevre görevler
3. **Priority dispatch**: acil görev öncelikli

Gerçek zamanlı kural:

- ETA + enerji + payload uygun değilse rota yeniden planla.

## 7) Test Planı

Unit:

- kuvvet hesabı
- slip/traction sınırları
- enerji tüketimi

Integration:

- tarla -> depo -> üretim hattı akışı
- robot arızasında görev yeniden atama

Simulation:

- 1000 tick deterministik run
- farklı zemin/eğim kombinasyonları
- p95 görev gecikmesi hedefi

## 8) İlk Sprintte Kodlanacaklar

1. `compute_drive_force`
2. `apply_terrain_response`
3. `integrate_robot_state`
4. tek rota planlayıcı (`hub-spoke`)
5. görev atama (payload + battery + terrain)

Bu yapı, araç/robot hareketini tek motor fizik altyapısında birleştirir ve uzay tarımı ile lojistiği aynı simülasyon omurgasında çalıştırır.
