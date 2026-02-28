# Konuşma Dönüştürme Kılavuzu

## Role Mapping Policy

Aşağıdaki kurallar, ham konuşmacı etiketlerinden hedef model rollerine güvenli ve tutarlı bir eşleme yapmak için zorunludur.

1. **"Ben" konuşmacısını sabitleme**
   - `owner_name` veya `owner_phone` ile eşleşen satırlar her zaman **konuşma sahibi** olarak kabul edilir.
   - Bu eşleşme sonrası aynı konuşmacı kimliği tüm kayıt boyunca tek bir role sabitlenir (oturum içinde role kayması yapılmaz).

2. **Hedef modele göre `assistant` tarafını açık tanımlama**
   - **Chat-style hedef modeller** için:
     - Konuşma sahibi (`owner_*` ile eşleşen kişi) -> `user`
     - Karşı taraf (tekil diğer katılımcı) -> `assistant`
   - **Instruction-style / tek yönlü hedef modeller** için:
     - Konuşma sahibi -> `assistant` (ajan/prompt yürüten taraf)
     - Karşı taraf -> `user`
   - Kullanılan model türü pipeline konfigürasyonunda açıkça belirtilmeli; varsayılan role-map buna göre seçilmelidir.

3. **Grup sohbeti dışlama / çok konuşmacı indirgeme**
   - Ham kayıtta ikiden fazla farklı konuşmacı varsa kayıt **grup sohbeti** olarak işaretlenir.
   - Politika:
     - Varsayılan: grup sohbeti kayıtları dışlanır (`exclude_group_chat = true`).
     - İzin verilirse: en yüksek mesaj hacmine sahip iki konuşmacı korunur, diğerleri `drop` edilir (çok konuşmacı indirgeme).

4. **Belirsiz konuşmacı satırları için `drop` etiketi**
   - Konuşmacı bilgisi eksik, çelişkili veya kimlik eşleşmesi yapılamayan satırlar `drop` olarak etiketlenir.
   - `drop` satırları eğitim/çıktı örneğine dahil edilmez; yalnızca kalite raporunda sayısal olarak izlenir.

5. **Örnek role-map tablosu**

| Ham konuşmacı (`raw_speaker`) | Eşleşme/Koşul | Nihai role |
|---|---|---|
| `Ahmet Y.` | `owner_name = Ahmet Y.` | `user` |
| `+90 555 111 22 33` | `owner_phone = +90 555 111 22 33` | `user` |
| `Müşteri Destek` | owner ile eşleşmiyor, tekil karşı taraf | `assistant` |
| `Bilinmiyor` | kimlik çözümlenemedi | `drop` |
| `Katılımcı-3` | grup sohbeti indirgemede ilk iki dışında kaldı | `drop` |
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
