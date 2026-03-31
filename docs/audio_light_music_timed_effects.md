# Ses + Işık + Müzik Zaman Ayarlı Efekt Yapısı

Amaç: Hikaye gücünü artırmak için görev fazına göre senkronlu ses/ışık/müzik akışı kurmak.

## 1) Yapı

Kod kontratları: `scripts/audio_timeline_contracts.py`

- `build_story_timeline_cues(...)`
- `apply_timeline_cues(...)`
- `validate_cue_conflicts(...)`

Veri kaynağı: `scripts/data/audio_light_timeline.json`

## 2) Faz Bazlı Kullanım

- `bootstrap`: düşük yoğunluk, keşif ve kurulum hissi
- `farming_expansion`: ritmik ambient + grow light pulse
- `shipyard_launch`: yüksek tansiyon + alarm + motor spinup

## 3) Senkronizasyon Kuralları

1. Aynı hedefte çakışan lighting cue’ları conflict kontrolünden geçmeli.
2. SFX pikleri müzik yoğunluğu ile otomatik ducking kullanmalı.
3. Hikaye kritik anlarında kamera cinematic moda geçince cue seti yükseltilmeli.

## 4) Teknik Notlar

- Tick tabanlı scheduler kullanılmalı (frame bağımsız).
- Cue intensity değeri volume/light strength multiplier olarak ele alınmalı.
- Tüm cue’lar replay determinism için seed/tick ile çalışmalı.

## 5) İlk Görevler

1. Faz-cue parse katmanı
2. Active cue evaluator (`apply_timeline_cues`)
3. Cue conflict validator
4. Story phase geçişinde cue swap mekanizması
5. Telemetry: cue drop rate, overlap error rate, p95 cue-apply latency
