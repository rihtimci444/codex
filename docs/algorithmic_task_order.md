# Algoritmik Görev Sıralaması (Hedefe Yönelik Kodlama)

İstek: Tek seferde değil, görev bazlı ve hedef odaklı ilerleme.

Bu doküman görevleri bağımlılık + etki skoruyla sıralar ve ilk oluşturulacak dosyaları net verir.

## 1) Sıralama Algoritması

Kural:

1. Bağımlılıkları olmayan görevler hazır kuyruğa alınır.
2. Hazır kuyruğu şu skora göre sıralanır:

`priority = (impact * urgency) / (effort + risk)`

3. En yüksek skor seçilir, tamamlanır, bağımlı görevler açılır.
4. Döngü varsa (cycle) kalan görevler skora göre fallback sıralanır.

Referans kod: `scripts/task_scheduler.py`

## 2) İlk Oluşturulacak Dosyalar (Sıralı)

### Adım 1 — Domain contracts (temel sözlük)

1. `scripts/pre_coding_contracts.py`
2. `scripts/story_mission_contracts.py`
3. `scripts/robot_motion_contracts.py`
4. `scripts/camera_system_contracts.py`

### Adım 2 — Statik veri kaynakları

5. `scripts/data/block_library.json`
6. `scripts/data/story_arcs.json`
7. `scripts/data/building_materials.json`

### Adım 3 — Çekirdek semantic pipeline

8. `scripts/vectorized_assignment.py`

### Adım 4 — Dikey entegrasyonlar

9. Story + inventory + camera entegrasyonu
10. Robot motion + cargo route entegrasyonu

### Adım 5 — Doğrulama

11. `scripts/tests/test_vectorized_assignment.py`

### Adım 6 — Dokümantasyon kapanışı

12. `docs/next_phase_implementation_plan.md`
13. `docs/space_game_deep_preparation_plan.md`
14. `docs/story_mission_inventory_camera_plan.md`
15. `docs/spacecraft_design_system.md`

## 3) Görev Atamaları (Rol Bazlı)

- **Core engineer**: Adım 1, 3
- **Simulation engineer**: Adım 4 (robot/motion)
- **Gameplay systems engineer**: Adım 4 (story/inventory/camera)
- **QA/infra**: Adım 5
- **Tech design**: Adım 6

## 4) Hızlı Başlangıç (Sprint-0)

- Gün 1: Adım 1 + Adım 2
- Gün 2: Adım 3
- Gün 3: Adım 4
- Gün 4: Adım 5
- Gün 5: Adım 6 + demo

## 5) Neden Bu Sıra?

- Önce sözleşme (contract) olmadan modüller arası tutarlılık bozulur.
- Veri olmadan pipeline doğru test edilemez.
- Testler en son ama entegrasyondan hemen sonra konur; regressions erken yakalanır.
- Dokümantasyon kapanışı, uygulanan gerçek yapıya göre güncellenir.

Detaylı görev içeriği (fonksiyon/nesne/ortam/kamera/zaman/eylem):
`docs/detailed_task_breakdown.md` ve `scripts/data/task_playbooks.json`.
Başlangıç stratejisi (ilk hafta): `docs/where_to_start_first_7_days.md`.
