# Dokümantasyon

## Tokenization & Truncation Policy

### 1) Hedef tokenizer/model ailesi
- Bu dokümanda hedef model ailesi **Qwen2.5** olarak kabul edilir.
- Token hesaplaması, kullanılan Qwen sürümünün kendi tokenizer'ı ile yapılmalıdır (örn. Qwen2.5 tokenizer).

### 2) Token limitleri
- **Maksimum context token:** `131072`
- **Maksimum output token:** `8192`

> Not: Farklı bir Qwen sürümüne geçilirse bu değerler, ilgili sürümün resmi limitleriyle güncellenmelidir.

### 3) Aşım durumunda truncation sırası
Context sınırı aşıldığında aşağıdaki sıra **zorunlu** olarak uygulanır:
1. **En eski geçmiş mesajlardan kesme** (FIFO mantığı).
2. **System mesajını koru** (silme/kısaltma yapılmaz).
3. **Hedef assistant cevabını asla kesme** (çıktı bütçesi önceden rezerve edilir).

Uygulama notu:
- Üretim öncesi, hedef assistant cevabı için `max_output_token` kadar alan ayrılır.
- Geriye kalan bütçeye sığmayan geçmiş mesajlar, en eskiden başlayarak çıkarılır.

### 4) Truncation işaretleme kuralı
Truncation uygulanan her örnek aşağıdaki alanla işaretlenmelidir:
- `truncated=true`

Örnek:
```json
{
  "messages": [...],
  "truncated": true
}
```

### 5) Token istatistikleri (zorunlu raporlama)
Her batch/çalıştırma için ortalama token istatistikleri raporlanması zorunludur:
- Ortalama input token
- Ortalama output token
- Ortalama toplam token
- Truncation oranı (`truncated=true` örnek yüzdesi)

Raporlama periyodu en az günlük olmalı ve model/sürüm bazında ayrı izlenmelidir.
