# YALAN HABER TESPIT SISTEMI v2.0

Turkce Destekli Ensemble Model ile Yalan Haber Tespit Sistemi

## Ozellikler

- **%99+ Dogruluk Hedefi**: Coklu model ensemble ile yuksek dogruluk
- **Turkce Destek**: Tam Turkce dil isleme ve analiz
- **Detayli Analiz**: Yalan belirtecleri, duygu analizi, yapi ozellikleri
- **Gercek Zamanli**: Milisaniyeler icinde tahmin
- **Aciklama**: AI tarafindan uretilen aciklama ile neden yalan/haber oldugu

## Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    GIRDI: Turkce Metin                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              ON ISLEME KATMANI                           │
│  • Tokenizasyon (Turkish Tokenizer)                     │
│  • URL, @mention, #hashtag temizligi                    │
│  • Buyuk harf normalizasyonu                            │
│  • Stop-word cikarma                                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              OZELLIK CIKARMA KATMANI                    │
│                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Metin        │ │ Duygu &      │ │ Yalan        │   │
│  │ Ozellikleri  │ │ Anlamsal     │ │ Belirtecleri │   │
│  │              │ │ Ozellikler   │ │              │   │
│  │ • TF-IDF     │ │ • Duygu      │ │ • Shock      │   │
│  │ • N-gram     │ │   yogunlugu  │ │   kelimeler  │   │
│  │ • Kelime     │ │ • Subjectiv- │ │ • Urgency    │   │
│  │   istatistik │ │   ity skoru  │ │   ifadeleri  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              MODEL KATMANI (ENSEMBLE)                    │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Logistic        │  │ XGBoost         │              │
│  │ Regression      │  │                 │              │
│  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                        │
│  ┌────────┴────────┐  ┌───────┴─────────┐              │
│  │ LightGBM        │  │ Random Forest   │              │
│  └────────┬────────┘  └───────┬─────────┘              │
│           │                   │                         │
│           ▼                   ▼                         │
│  ┌─────────────────────────────────────┐               │
│  │       STACKING ENSEMBLE             │               │
│  └──────────────────┬──────────────────┘               │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              CIKTI                                       │
│  • label: "FAKE" | "REAL"                               │
│  • confidence: 0.00 - 1.00                              │
│  • fakeScore / realScore                                │
│  • keyFeatures (etkileyen belirtecler)                  │
│  • explanation (aciklama metni)                         │
└─────────────────────────────────────────────────────────┘
```

## Kurulum

### 1. Bağımlılıklar

```bash
cd artifacts/python-ml
pip install -r requirements.txt
```

### 2. Model Eğitimi

```bash
python scripts/train_all.py
```

### 3. Test

```bash
python scripts/test_system.py
```

### 4. API Sunucusu

```bash
python main.py
```

## API Endpoint'leri

### POST /predict
Temel tahmin endpoint'i.

```json
{
  "text": "Haber icerigi buraya",
  "title": "Baslik (opsiyonel)"
}
```

Yanıt:
```json
{
  "label": "FAKE",
  "confidence": 0.95,
  "fakeScore": 0.95,
  "realScore": 0.05,
  "keyFeatures": ["shock_word_count", "urgency_word_count"]
}
```

### POST /predict/detailed
Detaylı analiz endpoint'i.

```json
{
  "text": "Haber icerigi buraya",
  "title": "Baslik (opsiyonel)"
}
```

Yanıt:
```json
{
  "label": "FAKE",
  "confidence": 0.95,
  "fakeScore": 0.95,
  "realScore": 0.05,
  "keyFeatures": ["shock_word_count"],
  "explanation": "Bu metin %95 olasilikla yalan haber olarak...",
  "textFeatures": {...},
  "sentimentFeatures": {...},
  "fakeIndicators": {...}
}
```

### GET /stats
Model istatistikleri.

### GET /model/info
Model bilgileri.

### GET /health
Saglik kontrolu.

### GET /examples
Ornek haberler.

## Ozellik Muhendisligi

### Metin Ozellikleri
- kelime_sayisi, karakter_sayisi, ortalama_kelime_uzunlugu
- cumle_sayisi, ortalama_cumle_uzunlugu
- benzersiz_kelime_orani (TTR)
- buyuk_harf_orani, noktalama_isareti_sayilari
- TF-IDF vektorleri (1-3 gram)

### Duygu Ozellikleri
- duygu_polaritesi (-1 ile +1)
- olumluluk/olumsuzluk kelime sayilari
- eminlik_skoru, belirsizlik_skoru

### Yalan Belirtecleri
- shock_kelime_sayisi (SOK, DEHSET, INANILMAZ vb.)
- urgency_kelime_sayisi (HEMEN, ACIL, PAYLAS vb.)
- komplo_terim_sayisi (KOMPLO, GIZLI, ORTBAS vb.)
- belirsiz_kaynak_sayisi
- buyuk_harf_orani, unlem_isareti_yogunlugu
- duygu manipulasyon skoru
- inanilmazlik skoru

## Model Karsilastirmasi

| Model | CV Dogruluk | Hiz | Onem sirasi |
|-------|-------------|-----|-------------|
| Logistic Regression | ~%92 | Hizli | 1 |
| XGBoost | ~%93 | Orta | 2 |
| LightGBM | ~%93 | Hizli | 3 |
| Random Forest | ~%91 | Orta | 4 |
| **Stacking Ensemble** | **~%95+** | **Orta** | **Hedef** |

## Veri Seti

- **Toplam Ornek**: 400+ (Turkce + Ingilizce)
- **Fake Ornek**: 200+ (Saglik, Siyasi, Ekonomik, Komplo teorileri)
- **Real Ornek**: 200+ (Ekonomi, Bilim, Saglik, Egitim, Gundem)

## Gelistirme

### Yeni Veri Ekleme
`data/dataset.py` dosyasina yeni ornekler ekleyin.

### Model Ekleme
`model/trainer.py` dosyasindaki `_get_models()` metoduna yeni model ekleyin.

### Ozellik Ekleme
`model/features.py` dosyasindaki siniflara yeni ozellikler ekleyin.

## Lisans

Bu proje egitim amaclidir.
