# Veri Hazırlama Notları

## Dataset Split Strategy

Bu bölüm, eğitim/doğrulama/test ayrımında veri sızıntısını azaltmak ve gerçekçi değerlendirme yapmak için uygulanacak split stratejisini tanımlar.

### 1) Split birimi: `session_id`
- Split işlemi mesaj satırı seviyesinde **değil**, `session_id` seviyesinde yapılmalıdır.
- Aynı `session_id` altında bulunan tüm mesajlar tek bir gruptur ve yalnızca tek bir split'e atanır.

### 2) Grup bütünlüğü: aynı kişi/aynı sohbet korunumu
- Aynı kullanıcıya (ör. `user_id`) ve aynı sohbete (`session_id`) ait örnekler farklı split'lere dağıtılmamalıdır.
- Uygulamada split anahtarı en azından `session_id` olmalı; gerekiyorsa `user_id + session_id` birleşik anahtarı ile grup bütünlüğü garanti edilmelidir.
- Doğrulama adımı olarak, split sonrası aynı anahtarın birden fazla split içinde geçip geçmediği kontrol edilir.

### 3) Zaman bazlı split opsiyonu
- Rastgele grup split'ine ek olarak zaman bazlı split seçeneği sunulmalıdır.
- Önerilen yaklaşım:
  - Eski dönem verileri: `train`
  - Orta dönem verileri: `val`
  - En güncel dönem verileri: `test`
- Zaman bazlı split için `timestamp` (veya eşdeğer olay zamanı alanı) zorunludur.
- Opsiyonel yapılandırma parametreleri:
  - `split_mode`: `group_random` | `time_based`
  - `time_cutoff_train`
  - `time_cutoff_val`

### 4) Split sonrası benzerlik kontrolü
- Split tamamlandıktan sonra splitler arası yakın kopya/çok benzer örnek taraması yapılmalıdır.
- Amaç: train ile val/test arasında neredeyse aynı içeriklerin bulunmasını tespit etmek.
- Önerilen kontrol yöntemleri (en az biri):
  - Metin hash + near-duplicate (MinHash/LSH)
  - Embedding tabanlı kosinüs benzerliği eşiği
  - Karakter/kelime n-gram Jaccard benzerliği
- Tespit edilen örnekler için aksiyon politikası tanımlanmalıdır (örn. testten çıkar, train'den çıkar, manuel inceleme kuyruğuna al).

### 5) Split dağılım raporu (tablo formatı)
Split sonrasında aşağıdaki standart tablo üretilmelidir:

| Split | Session Count | Message Count | User Count | Time Range | Duplicate Alerts | Ratio (%) |
|------:|--------------:|--------------:|-----------:|------------|-----------------:|----------:|
| train |               |               |            |            |                  |           |
| val   |               |               |            |            |                  |           |
| test  |               |               |            |            |                  |           |
| total |               |               |            |            |                  | 100.00    |

> Not: `Ratio (%)` mesaj sayısı veya session sayısı bazında raporlanabilir; hangi metrik kullanıldıysa başlıkta açıkça belirtilmelidir.
