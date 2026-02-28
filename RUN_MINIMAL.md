# Minimal Çalıştırma (Shell)

Evet, bu sürüm **shell üzerinden** çalışır.

## 1) Örnek WhatsApp input dosyası hazırla

`sample_whatsapp.txt` gibi bir dosya oluştur:

```text
28/02/2026, 10:00 - Ben: Dün attığım rapora baktın mı?
28/02/2026, 10:02 - Ahmet: Evet baktım, veri temizliği eksik.
28/02/2026, 10:03 - Ben: Neyi ekleyelim?
28/02/2026, 10:04 - Ahmet: Medya satırlarını atıp PII maskelemesi ekleyin.
```

## 2) Eğitim verisi üret

```bash
python prepare_dataset.py \
  --input sample_whatsapp.txt \
  --output training.jsonl \
  --assistant-speaker Ahmet
```

## 3) Kalite raporu üret

```bash
python score_dataset.py \
  --input training.jsonl \
  --report-json report.json \
  --report-csv report.csv
```

## 4) Çıktılar

- `training.jsonl`: Qwen chat-style eğitim örnekleri
- `report.json`: metrikler + `release_gate_status`
- `report.csv`: aynı raporun tablo sürümü

## Not

- `--assistant-speaker` parametresi, modelin hangi konuşmacı gibi cevap vermeyi öğreneceğini belirler.
- İstersen aynı scriptleri gerçek WhatsApp export dosyana doğrudan uygulayabilirsin.
