# Müşteri hizmetleri tabanı + Kelime hazinesi

## Yapılanlar

### 1. Kelime hazinesi (profesyonel iş için)

- **TDK + büyük kaynaklar** (`collect_from_tdk_api`):
  - hexapode (~195k), bilalozdemir (~92k), gurelkaynak, ardagurcan, ogun/bora TDK 12, mertemin, ahmetax, stopwords.
  - Uzun timeout (60–90 sn) ile indiriliyor.
- **Mevcut 450k sözlük** toplama başında yüklenip morfoloji temeli olarak kullanılıyor.
- **Müşteri hizmetleri sözlüğü** (`musteri_hizmetleri_sozluk.txt`): 500+ ifade; KELIME_TOPLA içinde otomatik ekleniyor.

### 2. Müşteri hizmetleri tabanı (daha çok önermek)

- **Context analyzer**
  - `customer_service` intent + topic; `topic_keywords` ve `cs_boost_keywords` genişletildi.
  - CS konusunda **+8** (cs_boost) ve **+4** (topic) skor artışı.
- **Relevance filter**
  - `domain_keywords['customer_service']` genişletildi; CS bağlamında prefix/uyum skoru **0.9–1.0**.
- Sipariş, kargo, iade, fatura, destek, şikayet, kampanya, abonelik vb. yazıldığında **müşteri hizmeti odaklı öneriler öne çıkar**.

## Kullanım

1. **KELIME_TOPLA.bat** çalıştır (TDK + büyük kaynaklar + CS sözlüğü + morfoloji).
2. Backend’i yeniden başlat (`PRODUCTION_BASLAT.bat` veya `python main.py`).
3. Müşteri hizmeti senaryolarında test et: "sipariş", "destek", "fatura", "iade" vb.

## Müşteri hizmeti önceliği

- "sipariş takibi", "kargo durumu", "iade talebi", "fatura sorgulama", "nasıl yardımcı olabilirim" gibi ifadeler yazıldığında önerilerde **daha üst sırada** gelir.
