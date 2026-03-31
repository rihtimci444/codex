# Olası Problemler İçin Tedbir Listesi

## A) Teknik Riskler

1. **Cue çakışması (ses/ışık)**
   - Tedbir: `validate_cue_conflicts` zorunlu geçiş
2. **Frame drop (yoğun efekt anları)**
   - Tedbir: LOD + efekt kalite seviyeleri + p95 frame alarmı
3. **Deterministik olmayan simülasyon**
   - Tedbir: tick tabanlı scheduler, seed logging
4. **Veri schema bozulması**
   - Tedbir: startup schema validation + fail-fast
5. **Aşırı bellek kullanımı**
   - Tedbir: timeline cue pooling ve limitler

## B) Oynanış Riskleri

1. **Aşırı zorluk artışı**
   - Tedbir: difficulty curve guardrails (erken/orta/geç oyun)
2. **Görev tekrar hissi**
   - Tedbir: mission template varyasyon havuzu
3. **Robot path deadlock**
   - Tedbir: fallback route + congestion escape rules

## C) Üretim Riskleri (3D/Blender)

1. **Poly budget aşımı**
   - Tedbir: asset gate (tri budget check)
2. **LOD eksikliği**
   - Tedbir: LOD zinciri olmadan merge engeli
3. **Texture memory şişmesi**
   - Tedbir: atlasleme + çözünürlük sınırları

## D) Operasyonel Riskler

1. **Dokümantasyon-kod ayrışması**
   - Tedbir: sprint sonunda docs sync checklist
2. **Takım bağımlılık tıkanması**
   - Tedbir: task_scheduler ile günlük yeniden plan
3. **Regresyonlar**
   - Tedbir: her merge’de test + fixture snapshot

## E) Kontrol Frekansı

- Günlük: frame p95, görev hataları, cue conflict sayısı
- Haftalık: zorluk eğrisi, görev tamamlama oranı, ekonomik denge
- Sprint sonu: teknik borç + kalite kapısı raporu
