# WhatsApp -> Qwen Dataset (Minimal)

Kanka en kısa haliyle: bu proje **terminalden** çalışıyor.

## 1) Gerekenler
- Python 3.9+
- WhatsApp dışa aktarma `.txt` dosyası

Kontrol:
```bash
python --version
```

---

## 2) Windows'ta nasıl çalıştıracağım?

### Adım adım
1. Klasörü aç (senin ekrandaki gibi `Deneme-main`).
2. O klasör içinde terminal aç:
   - Adres çubuğuna `cmd` yazıp Enter (veya PowerShell aç).
3. Şu komutu çalıştır:

```bash
python run_pipeline.py --input whatsapp.txt --assistant-speaker Ahmet
```

> `whatsapp.txt` yerine kendi dosya adını yaz.
> `Ahmet` yerine modelin "assistant" gibi öğrenmesini istediğin kişiyi yaz.

Çıktılar `outputs/` klasörüne gelir:
- `outputs/training.jsonl`
- `outputs/report.json`
- `outputs/report.csv`

---

## 3) Tek tek çalıştırmak istersen

### 3.1 Eğitim verisi üret
```bash
python prepare_dataset.py --input whatsapp.txt --output training.jsonl --assistant-speaker Ahmet
```

### 3.2 Kalite skorunu çıkar
```bash
python score_dataset.py --input training.jsonl --report-json report.json --report-csv report.csv
```

---

## 4) Sık hata / çözüm

### `python is not recognized`
- Python kurulu değil veya PATH'e ekli değil.
- Python'u tekrar kurarken **Add Python to PATH** işaretle.

### `No such file or directory: whatsapp.txt`
- Dosya adı yanlış ya da terminal yanlış klasörde.
- `dir` (Windows) veya `ls` (mac/Linux) ile dosya var mı kontrol et.

### `written_examples=0`
- Dosya formatı WhatsApp export formatıyla eşleşmiyor olabilir.
- `--assistant-speaker` adı dosyadaki konuşmacı adıyla birebir aynı olmalı.

---

## 5) Örnek input formatı

```text
28/02/2026, 10:00 - Ben: Dün attığım rapora baktın mı?
28/02/2026, 10:02 - Ahmet: Evet baktım, veri temizliği eksik.
28/02/2026, 10:03 - Ben: Neyi ekleyelim?
28/02/2026, 10:04 - Ahmet: Medya satırlarını atıp PII maskelemesi ekleyin.
```
