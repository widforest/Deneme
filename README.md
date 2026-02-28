# Doküman

## LLM-Assisted Rewrite Guardrails

Bu bölüm, LLM destekli metin yeniden yazım süreçlerinde güvenlik, izlenebilirlik ve kalite güvencesi gereksinimlerini tanımlar.

### 1) İzinli Dönüşümler
Aşağıdaki dönüşümler **izinlidir**:

- İmla, noktalama ve tipografi düzeltmeleri.
- Gereksiz tekrarların temizlenmesi (anlamı koruyarak sadeleştirme).
- Dil bilgisi iyileştirmeleri (zaman/kişi uyumu, cümle akışı).
- Biçimsel standardizasyon (başlık/cümle biçimi, liste formatı).
- Anlamı değiştirmeyen netlik artırımı (belirsizliği azaltan küçük düzenlemeler).

### 2) Yasak Dönüşümler
Aşağıdaki dönüşümler **yasaktır**:

- Kaynak metinde bulunmayan anlam veya bilgi eklemek.
- Olay, tarih, kişi, alıntı veya veri uydurmak.
- Yazarın niyetini, tonunu veya hükmünü değiştirmek.
- Kapsamı genişletmek veya daraltmak (orijinal sınırların dışına çıkmak).
- Kesinlik düzeyini değiştirmek (olasılığı kesin ifade etmek veya tersini yapmak).

### 3) Diff Saklama Zorunluluğu
Her dönüşüm için diff kaydı tutulması zorunludur:

- Her yeniden yazım çıktısı için satır bazlı `before/after` diff saklanır.
- Diff kaydı; içerik kimliği, zaman damgası, model sürümü ve işlem kimliği ile birlikte arşivlenir.
- Diff kayıtları denetim amacıyla geri çağrılabilir ve en az 180 gün saklanır.
- Diff kaydı olmayan dönüşümler geçersiz sayılır ve yayına alınmaz.

### 4) Yüksek Etkili Değişikliklerde İnsan Onayı
Yüksek etkili değişikliklerde `human_review_required` koşulu zorunludur.

`human_review_required = true` tetikleme koşulları:

- Politika, hukuk, finans, güvenlik veya kamuya açık resmi beyan içeren metinlerde anlamı etkileyen düzenlemeler.
- Sayısal değer, tarih, kişi/kurum adı veya yükümlülük ifadesi içeren değişiklikler.
- Orijinal metnin iddia düzeyini, riski veya sorumluluk kapsamını etkileyen düzenlemeler.
- Otomatik kalite kontrollerinden herhangi birini geçemeyen dönüşümler.

Onay akışı:

1. LLM çıktısı ve diff kaydı incelemeye alınır.
2. Yetkili insan gözden geçiren onaylar veya reddeder.
3. Onay sonucu ve gerekçesi audit kaydına eklenir.

### 5) Rastgele Örneklemle Manuel Kalite Denetimi
Süreç kalitesi için periyodik manuel denetim uygulanır:

1. Her üretim döneminde (ör. günlük/haftalık) dönüşümlerin en az %5'i rastgele örneklenir.
2. Örneklem, farklı içerik türleri ve risk sınıflarını temsil edecek şekilde tabakalı rastgele seçilir.
3. Denetçiler şu kontrol listesini uygular:
   - Anlam korunumu
   - Yasak dönüşüm ihlali var/yok
   - Dil kalitesi ve okunabilirlik
   - Diff ve meta-kayıt bütünlüğü
4. Hata oranı eşik değeri aşarsa düzeltici aksiyon açılır ve ilgili model/prompt sürümü askıya alınır.
5. Denetim sonuçları aylık raporlanır; bulgular, politika güncelleme girdisi olarak kullanılır.
