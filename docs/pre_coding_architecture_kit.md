# Pre-Coding Architecture Kit (For Implementation Team)

Bu doküman, kod yazımına başlamadan önce ekipte standartlaştırılacak önerileri bırakır.

## 1) Önerilen Mimariler

### A) Domain + Event-Driven (Önerilen)

- Domain servisleri: `economy`, `logistics`, `construction`, `vehicle`, `shipyard`, `farming`
- Servisler arası iletişim: event bus (`domain_event`)
- Avantaj: gevşek bağlılık, simülasyon akışında izlenebilirlik

### B) Hexagonal (Ports/Adapters)

- Core domain saf Python
- Dış sistemler adapter: storage, telemetry, UI/API
- Avantaj: test edilebilirlik ve taşıma kolaylığı

### C) ECS-like Runtime (oyun döngüsü yoğun ise)

- Entity + Component + System
- Özellikle driving/farming/ship physics için uygun
- Avantaj: performans ve büyük ölçekli state güncellemelerinde sadelik

## 2) Katmanlar (zorunlu)

1. `domain/`: saf iş kuralları
2. `application/`: use-case orchestration
3. `infrastructure/`: dosya, telemetry, queue, db
4. `interfaces/`: CLI, API, tool endpoints

## 3) Kütüphane Önerileri

- Modelleme/validasyon: `pydantic` (veya dataclass + manuel validation)
- Sayısal işlemler/batch: `numpy`
- Grafik/bağımlılık: `networkx`
- Konfigürasyon: `pydantic-settings` veya `dynaconf`
- Log/telemetry: `structlog`, `opentelemetry-api`
- Test: `pytest`, `hypothesis`, `pytest-benchmark`

## 4) Fonksiyon Kontratları (başlangıç)

- `run_vectorized_assignment_pipeline(config) -> PipelineOutputs`
- `precompute_writer_embeddings(writers, vector_dim, ttl) -> dict[str, list[float]]`
- `precompute_block_embeddings(blocks, vector_dim, ttl) -> dict[str, list[float]]`
- `semantic_candidates_for_nodes(nodes, writers, config) -> dict[path, list[(writer, score)]]`
- `recommend_blocks_for_nodes(nodes, blocks, config) -> dict[path, list[(block, score)]]`
- `build_composition_plan(selected_blocks, dependency_graph) -> BuildPlan`
- `simulate_economy_tick(state, events) -> EconomyState`
- `process_earth_cargo_orders(state, tick) -> list[ShipmentEvent]`

## 5) Kodlama Öncesi Checkpoint

- Mimari seçimi (A/B/C) yazılı onaylandı mı?
- Event sözlüğü ve JSON schema tamamlandı mı?
- Deterministik seed ve replay stratejisi belirlendi mi?
- p50/p95 hedefleri servis bazında yazıldı mı?
- İlk sprint için kabul kriterleri (DoD) net mi?

## 6) Sprint-0 Çıktıları (Kod Öncesi)

1. ADR-001: Mimari kararı
2. ADR-002: Event kontratları
3. ADR-003: Data schema ve versiyonlama
4. Test strategy dokümanı
5. Benchmark planı (`vector_dim` x `top_k`)

Bu dosya ekip onboarding’inde ve ilk teknik kick-off toplantısında referans alınmalıdır.
