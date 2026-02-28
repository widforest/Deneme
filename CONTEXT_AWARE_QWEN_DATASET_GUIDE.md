# CONTEXT_AWARE_QWEN_DATASET_GUIDE

## Kabul Kriterleri

Bu bölüm, dataset kalitesini ölçülebilir metriklerle değerlendirir ve yayın kararını (release gate) standartlaştırır.

### 1) Sayısallaştırılmış kalite metrikleri

- **Duplicate oranı (%)**
  - Tanım: Aynı örneğin (veya normalize edilmiş içerik eşleşmesinin) birden fazla kez bulunma oranı.
  - Formül: `(duplicate_kayıt_sayısı / toplam_kayıt_sayısı) * 100`

- **Boş/çok kısa mesaj oranı (%)**
  - Tanım: Boş, sadece whitespace içeren veya minimum içerik uzunluğunun altında kalan mesajların oranı.
  - Formül: `(boş_veya_çok_kısa_mesaj_sayısı / toplam_mesaj_sayısı) * 100`

- **Tek-turn örnek oranı (%)**
  - Tanım: Çok turlu beklenen yapıda yalnızca tek turdan oluşan örneklerin oranı.
  - Formül: `(tek_turn_örnek_sayısı / toplam_örnek_sayısı) * 100`

- **PII kaçak oranı (%)**
  - Tanım: Kişisel veri (PII) içeren örneklerin oranı.
  - Formül: `(pii_içeren_örnek_sayısı / toplam_örnek_sayısı) * 100`

### 2) Eşik değerleri

- **Duplicate oranı:** `< 5%`
- **Boş/çok kısa mesaj oranı:** `< 2%`
- **Tek-turn örnek oranı:** `< 15%`
- **PII kaçak oranı:** `< 0.1%`

### 3) Release gate

Dataset sürüm durumu aşağıdaki kurala göre atanır:

- Tüm eşikler sağlanırsa: **`ready_for_sft`**
- Herhangi bir eşik sağlanmazsa: **`needs_rework`**

Önerilen karar mantığı (pseudocode):

```text
if duplicate_rate < 5
  and short_or_empty_rate < 2
  and single_turn_rate < 15
  and pii_leak_rate < 0.1:
    status = "ready_for_sft"
else:
    status = "needs_rework"
```

### 4) Eşikleri doğrulamak için rapor alanları (JSON/CSV)

Aşağıdaki alanlar hem JSON hem CSV çıktısında üretilmelidir:

- `dataset_version` (string)
- `run_id` (string)
- `generated_at` (ISO-8601 datetime)
- `total_records` (integer)
- `total_messages` (integer)
- `duplicate_records` (integer)
- `duplicate_rate` (float, %)
- `short_or_empty_messages` (integer)
- `short_or_empty_rate` (float, %)
- `single_turn_samples` (integer)
- `single_turn_rate` (float, %)
- `pii_leak_samples` (integer)
- `pii_leak_rate` (float, %)
- `threshold_duplicate_rate` (float, 5.0)
- `threshold_short_or_empty_rate` (float, 2.0)
- `threshold_single_turn_rate` (float, 15.0)
- `threshold_pii_leak_rate` (float, 0.1)
- `passes_duplicate_threshold` (boolean)
- `passes_short_or_empty_threshold` (boolean)
- `passes_single_turn_threshold` (boolean)
- `passes_pii_threshold` (boolean)
- `release_gate_status` (enum: `ready_for_sft` | `needs_rework`)

Örnek JSON satırı:

```json
{
  "dataset_version": "v1.3.0",
  "run_id": "qa_2026-02-28_001",
  "generated_at": "2026-02-28T12:00:00Z",
  "total_records": 120000,
  "total_messages": 420000,
  "duplicate_records": 3600,
  "duplicate_rate": 3.0,
  "short_or_empty_messages": 4200,
  "short_or_empty_rate": 1.0,
  "single_turn_samples": 9600,
  "single_turn_rate": 8.0,
  "pii_leak_samples": 60,
  "pii_leak_rate": 0.05,
  "threshold_duplicate_rate": 5.0,
  "threshold_short_or_empty_rate": 2.0,
  "threshold_single_turn_rate": 15.0,
  "threshold_pii_leak_rate": 0.1,
  "passes_duplicate_threshold": true,
  "passes_short_or_empty_threshold": true,
  "passes_single_turn_threshold": true,
  "passes_pii_threshold": true,
  "release_gate_status": "ready_for_sft"
}
```
