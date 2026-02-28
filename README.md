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
