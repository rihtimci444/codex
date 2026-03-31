# Böyle Bir Kod Yapısında Nereden Başlardım? (İlk 7 Gün Planı)

Kısa cevap: **önce sözleşme ve veri**, sonra **çalışan ince bir uçtan uca akış**, en son **optimizasyon**.

## Gün 1 — Harita çıkarma ve risk azaltma

1. `scripts/pre_coding_contracts.py`, `scripts/story_mission_contracts.py`, `scripts/robot_motion_contracts.py`, `scripts/camera_system_contracts.py` dosyalarını okuyup tek bir API sözlüğü çıkar.
2. `scripts/data/*.json` dosyalarında schema uyumu ve eksik alan kontrolü yap.
3. `scripts/tests/test_vectorized_assignment.py` çalıştır, mevcut güvenlik ağını doğrula.

Hedef: "ne var / ne eksik" listesini netleştirmek.

## Gün 2 — Uçtan uca minimum akış (happy path)

1. Tek bir story phase + tek görev + tek block önerisi + tek kamera modu için minimum demo akışı kur.
2. Bu akışta `vectorized_assignment` sadece 1 node üzerinde çalışsın.
3. JSON çıktılarını sabitle (golden output yaklaşımı).

Hedef: çalışan bir referans akış.

## Gün 3 — Veri doğrulama katmanı

1. `story_arcs.json`, `building_materials.json`, `task_playbooks.json` için schema validator ekle.
2. Hatalı veri durumlarına fail-fast davranışı koy.

Hedef: veri bozulduğunda sistem sessizce kırılmasın.

## Gün 4 — Görev orkestrasyonu

1. `implementation_tasks.json` + `task_scheduler.py` ile sprint planını otomatik üret.
2. Role-based atama çıktısı üret (core/simulation/gameplay/qa).

Hedef: ekip iş akışı koddan üretilebilsin.

## Gün 5 — Robot + kamera entegrasyonu

1. Robot hareket kontratlarını tek örnek senaryoda bağla (drive/repair veya farming taşıma).
2. Kamera mod geçişlerini (third-person/top-down/cinematic) olay bazlı bağla.

Hedef: oynanış hissi veren ilk dikey dilim.

## Gün 6 — Telemetry ve profiling

1. p50/p95 latency, fallback rate, recommendation confidence metriklerini üret.
2. `run_ab_tests` ile küçük matris çalıştır (`vector_dim`, `top_k`).

Hedef: kararları ölçülebilir hale getirmek.

## Gün 7 — Sertleştirme

1. Testleri genişlet: edge cases + regression fixtures.
2. Dokümantasyonları güncelle: sadece çalışan gerçek akışlar kalsın.
3. Sprint-2 backlog çıkar.

Hedef: sürdürülebilir geliştirme zemini.

---

## Teknik Öncelik Sırası (Pratik)

1. **Contracts**
2. **Static data validation**
3. **Minimal end-to-end flow**
4. **Task orchestration**
5. **Robot/camera vertical slice**
6. **Telemetry + AB tuning**
7. **Hardening/tests/docs**

Bu sıra, en kısa sürede "çalışan ürün" + "ölçülebilir kalite" sağlar.
