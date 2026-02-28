# Minimal Çalıştırma

En kolay yol (tek komut):

```bash
python run_pipeline.py --input whatsapp.txt --assistant-speaker Ahmet
```

Bu komut otomatik olarak:
1. `prepare_dataset.py` çalıştırır
2. `score_dataset.py` çalıştırır
3. Çıktıları `outputs/` klasörüne yazar

- `outputs/training.jsonl`
- `outputs/report.json`
- `outputs/report.csv`

Detaylı anlatım için `README.md` dosyasına bak.
