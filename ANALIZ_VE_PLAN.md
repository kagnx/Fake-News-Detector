# YALAN HABER TESPİT SİSTEMİ — DERİNLEMESİNE ANALİZ VE PRO PLAN

---

## 1. MEVCUT DURUM ANALİZİ

### 1.1 Proje Yapısı

Mevcut proje şu bileşenlerden oluşmaktadır:

| Bileşen | Teknoloji | Durum |
|---------|-----------|-------|
| ML Backend | Python, FastAPI, scikit-learn | Çalışıyor ama yetersiz |
| API Gateway | Express 5, TypeScript | Çalışıyor |
| Frontend | React, Vite, Tailwind | Çalışıyor, İngilizce |
| Veritabanı | PostgreSQL + Drizzle ORM | Çalışıyor |
| Veri Seti | Elle yazılmış 223 örnek | **KRİTİK EKSİK** |

### 1.2 Mevcut ML Modelinin Sorunları

Mevcut model `artifacts/python-ml/main.py` dosyasında tanımlıdır. Sorunlar:

#### a) Veri Seti Facia Düzeyinde
- **Toplam örnek sayısı: 223** (126 Fake + 97 Real)
- Tüm örnekler **İngilizce** — Türkçe veri hiç yok
- Örnekler elle yazılmış, gerçek dünya verisi değil
- Gerçek bir yalan haber tespit sistemi için minimum **10.000-50.000** örnek gerekir
- Veri dengesiz: Fake oranı %56, Real %44 — bu bile dengesiz

#### b) Model Mimarisi Zayıf
- **TF-IDF + PassiveAggressiveClassifier** kullanılmış
- Bu 2015 yılında popüler olan basit bir yaklaşımdır
- Metin özelliklerini sadece kelime frekansı olarak görüyor
- Anlam, bağlam, duygu, yapı gibi özellikleri tamamen görmezden geliyor
- N-gram range (1,2) sadece unigram ve bigram — çok sığ

#### c) Doğruluk Oranı Tahmini
Mevcut veri seti ve model ile beklenen doğruluk: **%75-85 arası**
(Bu bile çok iyimser bir tahmin — gerçek dünya verisiyle düşer)

#### d) Türkçe Desteği Yok
- Tüm training verisi İngilizce
- TF-IDF vektörleyicisi İngilizce için optimize edilmiş
- Türkçe metin işlenemiyor

#### e) Özellik Mühendisliği Sıfır
- Sadece kelime frekansı kullanılıyor
- Duygu analizi yok
- Yapısal özellikler (noktalama, büyük harf kullanımı, ünlem işareti yoğunluğu) yok
- Kaynak güvenilirliği analizi yok
- Mantıksal tutarsızlık tespiti yok

---

## 2. %99 DOĞRULUK İÇİN GEREKLİ MİMARİ

### 2.1 Neden %99 Mümkün (ve Zor)?

%99 doğruluk, yalan haber tespitinde çok yüksek bir hedeftir. Gerçek dünya verilerinde:
- İnsan performansı: %70-80
- İyi ML modelleri: %85-95
- En iyi sistemler: %92-98
- %99+: Sadece belirli domainlerde mümkün

**Ancak**,以下 durumlarda %99'a yaklaşılabilir:
1. Çok geniş ve yüksek kaliteli Türkçe veri seti
2. Çoklu model entegrasyonu (ensemble)
3. Derin özellik mühendisliği
4. Transformer tabanlı dil modelleri (BERTurk, TurkishBERT)
5. Sürekli öğrenme ve güncelleme

### 2.2 Önerilen Mimarî: Çok Katmanlı Ensemble Sistemi

```
┌─────────────────────────────────────────────────────────────┐
│                    GİRDİ: Türkçe Metin                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              1. ÖN İŞLEME KATMANI                           │
│  • Tokenizasyon (Turkish Tokenizer)                         │
│  • Stop-word çıkarma                                        │
│  • Lemmatization / Stemming                                 │
│  • URL, @mention, #hashtag çıkarma                          │
│  • Büyük harf normalizasyonu                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              2. ÖZELLİK ÇIKARMA KATMANI                     │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Metin        │ │ Duygu &      │ │ Yapısal &        │    │
│  │ Özellikleri  │ │ Anlamsal     │ │ Stilistik        │    │
│  │              │ │ Özellikler   │ │ Özellikler       │    │
│  │ • TF-IDF     │ │ • Duygu      │ │ • Ünlem işareti  │    │
│  │ • Word2Vec   │ │   yoğunluğu  │ │ • Büyük harf %   │    │
│  │ • TF         │ │ • Duygusal   │ │ • Noktalama      │    │
│  │   intensifier│ │   polarite   │ │   yoğunluğu      │    │
│  │ • N-gram     │ │ • Subjectiv- │ │ • Cümle uzunluğu │    │
│  │   istatistik │ │   ity skoru  │ │ • Kelime zengin- │    │
│  │              │ │              │ │   liği (TTR)     │    │
│  └──────────────┘ └──────────────┘ └──────────────────┘    │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │
│  │ Yalan        │ │ Kaynak &     │ │ Bağlamsal        │    │
│  │ İşaretleri   │ │ Güvenilirlik │ │ Özellikler       │    │
│  │              │ │              │ │                  │    │
│  │ • Şok edici  │ │ • Bilimsel   │ │ • Konu dağılımı  │    │
│  │   kelimeler  │ │   referans   │ │ • Entity tanılama │    │
│  │ • Aciliyet   │ │ • Kaynak     │ │ • Tema tutarsız- │    │
│  │   ifadeleri  │ │   belirsiz-  │ │   lığı           │    │
│  │ • Konspiras- │ │   lüğü       │ │                  │    │
│  │   yon dili   │ │              │ │                  │    │
│  └──────────────┘ └──────────────┘ └──────────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              3. MODEL KATMANI (ENSEMBLE)                     │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Model A:        │  │ Model B:        │                  │
│  │ TurkishBERT     │  │ XGBoost         │                  │
│  │ (Transformer)   │  │ (Gradient       │                  │
│  │                 │  │  Boosting)      │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                            │
│  ┌────────┴────────┐  ┌───────┴─────────┐                  │
│  │ Model C:        │  │ Model D:        │                  │
│  │ LightGBM        │  │ SVM + RBF       │                  │
│  │                 │  │ Kernel           │                  │
│  └────────┬────────┘  └───────┬─────────┘                  │
│           │                   │                             │
│           ▼                   ▼                             │
│  ┌─────────────────────────────────────┐                   │
│  │       META-CLASSIFIER (Stacking)    │                   │
│  │   Logistic Regression / Ridge       │                   │
│  └──────────────────┬──────────────────┘                   │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              4. ÇIKTI                                       │
│  • label: "FAKE" | "REAL"                                   │
│  • confidence: 0.00 - 1.00                                  │
│  • fakeScore / realScore                                    │
│  • keyFeatures (etkileyen belirteçler)                      │
│  • explanation (açıklama metni)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. VERİ SETİ STRATEJİSİ

### 3.1 Gerekli Veri Miktarı

| Kaynak | Hedef Miktar | Açıklama |
|--------|-------------|----------|
| Türkçe yalan haber | 5.000-10.000 | Gerçek dünya verisi |
| Türkçe gerçek haber | 5.000-10.000 | Güvenilir kaynaklardan |
| Sosyal medya yalanı | 2.000-5.000 | Twitter/Facebook yalanları |
| Konspirasyon teorileri | 1.000-3.000 | Türkçe kaynaklar |
| **TOPLAM** | **13.000-28.000** | **Minimum hedef** |

### 3.2 Veri Kaynakları

1. **Kaggle Datasets**
   - "Fake News Detection" Türkçe versiyonları
   - "Turkish News Dataset"
   - FEVER (Fact Extraction and VERification) Türkçe subset

2. **Gerçek Dünya Kaynakları**
   - Teyit.org (Türkçe doğrulama platformu)
   - Doğruluk Payı
   - SAVA (Sağlık Alanında Yanıltıcı Bilgiyle Mücadele)
   - AFP Fact Check Türkçe

3. **Sentetik Veri Üretimi**
   - Mevcut gerçek haberlerin yalan versiyonlarını LLM ile üretme
   - Back-translation ile veri çeşitliliği artırma
   - Template-based augmentation

### 3.3 Veri Toplama Planı

```python
# Adım 1: Mevcut verileri İngilizce'den Türkçe'ye çevir + genişlet
# Adım 2: Kaggle'dan Türkçe haber verileri indir
# Adım 3: Teyit.org'dan doğrulanmış yalan haberleri topla
# Adım 4: Güvenilir kaynaklardan gerçek haberleri çek
# Adım 5: Veri temizleme ve dengeleme
# Adım 6: Train/Validation/Test bölünmesi (70/15/15)
```

---

## 4. ÖZELLİK MÜHENDİSLİĞİ DETAYI

### 4.1 Metin Özellikleri

```python
class TextFeatures:
    """Temel metin istatistikleri"""
    
    # Kelime bazlı
    - word_count: int               # Toplam kelime sayısı
    - avg_word_length: float        # Ortalama kelime uzunluğu
    - unique_word_ratio: float      # Benzersiz kelime oranı (TTR)
    - vocabulary_richness: float    # Kelime zenginliği
    
    # Cümle bazlı
    - sentence_count: int           # Cümle sayısı
    - avg_sentence_length: float    # Ortalama cümle uzunluğu
    - max_sentence_length: int      # En uzun cümle
    
    # N-gram istatistikleri
    - unigram_freq: dict            # Tek kelime frekansları
    - bigram_freq: dict             # İki kelime frekansları
    - trigram_freq: dict            # Üç kelime frekansları
    
    # TF-IDF vektörleri
    - tfidf_vector: sparse_matrix   # Anahtar kelime vektörleri
```

### 4.2 Duygu & Anlamsal Özellikler

```python
class SentimentFeatures:
    """Duygu ve anlamsal analiz"""
    
    # Duygu analizi
    - sentiment_polarity: float     # -1 (olumsuz) ile +1 (olumlu) arası
    - sentiment_subjectivity: float # 0 (nesnel) ile 1 (öznel) arası
    - emotion_anger: float          # Öfke yoğunluğu
    - emotion_fear: float           # Korku yoğunluğu
    - emotion_joy: float            # Sevinç yoğunluğu
    - emotion_surprise: float       # Şaşkınlık yoğunluğu
    
    # Anlamsal özellikler
    - semantic_coherence: float     # Anlamsal tutarlılık skoru
    - topic_consistency: float      # Konu tutarlılığı
    - entity_density: float         # Varlık yoğunluğu (isim, yer, kurum)
```

### 4.3 Yapısal & Stilistik Özellikler

```python
class StructuralFeatures:
    """Yapısal ve stilistik analiz"""
    
    # Noktalama
    - exclamation_count: int        # Ünlem işareti sayısı
    - question_count: int           # Soru işareti sayısı
    - ellipsis_count: int           # Noktalı virgül sayısı (... )
    - caps_ratio: float             # Büyük harf oranı
    - special_char_ratio: float     # Özel karakter oranı
    
    # Stil
    - hyperbole_score: float        # Abartı düzeyi
    - urgency_score: float          # Aciliyet ifadeleri
    - authority_score: float        # Otorite referansı
    - source_credibility: float     # Kaynak güvenilirliği
    
    # Dilbilgisel
    - passive_voice_ratio: float    # Edilgen çatı oranı
    - named_entity_count: int       # İsimlendirilmiş varlık sayısı
```

### 4.4 Yalan İşaretleri (Fake Indicators)

```python
class FakeIndicators:
    """Yalan haber belirteçleri"""
    
    # Şok edici dil
    - shock_words: int              # "ŞOK", "DEHŞET", "İNANILMAZ" gibi kelimeler
    - urgency_words: int            # "ACİL", "HEMEN PAYLAŞ" gibi ifadeler
    - conspiracy_terms: int         # "KOMPLO", "GİZLİ PLAN" gibi terimler
    
    # Belirsizlik
    - vague_sources: int            # "Bazı kaynaklara göre", "iddia ediliyor"
    - anonymous_count: int          # "Anonim kaynak", "içeriden biri"
    - no_evidence: int              # Kanıt sunulmamışlık belirteçleri
    
    # Duygusal manipülasyon
    - emotional_appeal: float       # Duygusal调用 yoğunluğu
    - fear_mongering: float         # Korku yayma düzeyi
    - outrage_bait: float           # Öfke tuzağı belirteçleri
    
    # Mantıksal tutarsızlık
    - contradiction_score: float    # İç çelişki skoru
    - implausibility_score: float   # İnanılmazlık skoru
    - exaggeration_ratio: float     # Abartı oranı
```

---

## 5. MODEL EĞİTİM STRATEJİSİ

### 5.1 Adım Adım Eğitim Planı

```
Adım 1: Veri Toplama ve Hazırlık
├── Veri kaynaklarını belirle
├── Verileri indir ve temizle
├── Label'ları doğrula
└── Train/Val/Test böl

Adım 2: Basit Modeller (Baseline)
├── TF-IDF + Naive Bayes
├── TF-IDF + Logistic Regression
├── TF-IDF + SVM
└── Sonuçları kaydet (hedef: %85+)

Adım 3: Gelişmiş Modeller
├── XGBoost + Manuel özellikler
├── LightGBM + Manuel özellikler
├── Random Forest + TF-IDF
└── Sonuçları kaydet (hedef: %90+)

Adım 4: Derin Öğrenme
├── TurkishBERT fine-tuning
├── CNN + LSTM hybrid
├── Transformer ensemble
└── Sonuçları kaydet (hedef: %95+)

Adım 5: Ensemble (Yığın)
├── Stacking (Meta-classifier)
├── Voting (Hard/Soft)
├── Blending
└── Hedef: %97-99

Adım 6: Optimizasyon
├── Hiperparametre arama (Optuna)
├── Cross-validation
├── Threshold ayarlama
└── Son hedef: %99
```

### 5.2 Model Karşılaştırması

| Model | Beklenen Accuracy | Hız | Karmaşıklık | Öneri |
|-------|------------------|-----|-------------|-------|
| TF-IDF + NB | %80-85 | Çok Hızlı | Düşük | Baseline |
| TF-IDF + LR | %82-87 | Hızlı | Düşük | Baseline |
| TF-IDF + SVM | %84-88 | Hızlı | Orta | İyi |
| XGBoost | %87-92 | Orta | Orta | Çok İyi |
| LightGBM | %87-93 | Hızlı | Orta | Çok İyi |
| TurkishBERT | %92-96 | Yavaş | Yüksek | En İyi |
| **Ensemble** | **%96-99** | **Orta** | **Yüksek** | **Hedef** |

### 5.3 TurkishBERT Fine-Tuning Planı

```python
# Model: dbmdz/bert-base-turkish-uncased veya bert-base-turkish-cased
# Framework: Transformers + PyTorch

# Eğitim parametreleri:
model_name = "dbmdz/bert-base-turkish-uncased"
max_length = 512
batch_size = 16
learning_rate = 2e-5
epochs = 5
warmup_steps = 500
weight_decay = 0.01

# Fine-tuning stratejisi:
# 1. İlk 3 epoch: Sadece classifier katmanı
# 2. Son 2 epoch: Tüm model (discriminative fine-tuning)
# 3. Gradient accumulation ile更大 batch boyutu
```

---

## 6. UYGULAMA DEĞİŞİKLİKLERİ

### 6.1 Yeni Dosya Yapısı

```
artifacts/python-ml/
├── main.py                    # FastAPI sunucusu (güncellenmiş)
├── requirements.txt           # Bağımlılıklar (güncellenmiş)
├── model/
│   ├── __init__.py
│   ├── trainer.py             # Model eğitimi
│   ├── predictor.py           # Tahmin fonksiyonu
│   ├── features.py            # Özellik çıkarma
│   ├── preprocessor.py        # Türkçe önişleme
│   └── ensemble.py            # Ensemble mantığı
├── data/
│   ├── raw/                   # Ham veriler
│   ├── processed/             # İşlenmiş veriler
│   └── augmented/             # Augmente edilmiş veriler
├── models/
│   ├── saved/                 # Kaydedilmiş modeller
│   └── configs/               # Model konfigürasyonları
├── scripts/
│   ├── collect_data.py        # Veri toplama
│   ├── train_all.py           # Tüm modelleri eğit
│   ├── evaluate.py            # Değerlendirme
│   └── augment.py             # Veri augmentasyonu
└── tests/
    ├── test_features.py
    ├── test_preprocessor.py
    └── test_predictor.py
```

### 6.2 Güncellenmiş main.py

```python
# Yeni API endpoint'leri:
# POST /predict          - Tahmin (mevcut, güncellenmiş)
# GET  /stats            - İstatistikler (mevcut, güncellenmiş)  
# GET  /health           - Sağlık kontrolü (mevcut)
# POST /predict/detailed - Detaylı analiz (yeni)
# POST /retrain          - Yeniden eğit (yeni)
# GET  /model/info       - Model bilgisi (yeni)
```

### 6.3 Frontend Güncellemeleri

1. **Türkçe Arayüz**: Tüm metinler Türkçeye çevirilecek
2. **Detaylı Sonuç Ekranı**: Her özellik için ayrı gösterim
3. **Açıklama Modülü**: "Neden yalan olarak işaretlendi?" bölümü
4. **İstatistik Dashboard**: Gerçek zamanlı准确率 göstergesi
5. **Örnekler**: Türkçe yalan ve gerçek haber örnekleri

---

## 7. PERFORMANS METRİKLERİ

### 7.1 Hedef Metrikler

| Metrik | Hedef | Minimum |
|--------|-------|---------|
| **Accuracy** | **%99** | **%95** |
| Precision (FAKE) | %99 | %95 |
| Recall (FAKE) | %98 | %93 |
| F1-Score (FAKE) | %99 | %94 |
| F1-Score (REAL) | %99 | %94 |
| AUC-ROC | %99.5 | %97 |
| Inference Time | <100ms | <500ms |

### 7.2 Değerlendirme Protokolü

```python
# 5-fold cross-validation
# Stratified splits (sınıf dengesini koruma)
# Confidence threshold: 0.5 (optimize edilecek)
# Metrics: accuracy, precision, recall, F1, AUC, confusion matrix
```

---

## 8. UYGULAMA SIRASI

### Aşama 1: Altyapı (1-2 gün)
- [ ] Python bağımlılıklarını güncelle (transformers, torch, xgboost, lightgbm)
- [ ] TürkçeTokenizer modülünü oluştur
- [ ] Özellik çıkarma modülünü oluştur
- [ ] Veri yükleme ve ön işleme pipeline'ını kur

### Aşama 2: Veri Toplama (2-3 gün)
- [ ] Kaggle'dan Türkçe veri setlerini indir
- [ ] Teyit.org'dan verileri topla
- [ ] Sentetik veri üret
- [ ] Verileri temizle ve birleştir
- [ ] Train/Val/Test böl

### Aşama 3: Basit Modeller (1-2 gün)
- [ ] TF-IDF + NB/LR/SVM modellerini eğit
- [ ] Baseline accuracy'yi kaydet
- [ ] Hiperparametre optimizasyonu

### Aşama 4: Gelişmiş Modeller (2-3 gün)
- [ ] XGBoost modelini eğit
- [ ] LightGBM modelini eğit
- [ ] Manuel özellik mühendisliği
- [ ] Ensemble stratejisi kur

### Aşama 5: Derin Öğrenme (3-5 gün)
- [ ] TurkishBERT fine-tune et
- [ ] CNN+LSTM hybrid modeli eğit
- [ ] Model karşılaştırması yap

### Aşama 6: Ensemble ve Optimizasyon (2-3 gün)
- [ ] Stacking meta-classifier eğit
- [ ] Soft voting entegrasyonu
- [ ] Threshold optimizasyonu
- [ ] Final test ve raporlama

### Aşama 7: API ve Frontend (2-3 gün)
- [ ] API'yi güncelle
- [ ] Frontend'i Türkçeleştir
- [ ] Detaylı sonuç ekranını ekle
- [ ] Test et ve dağıt

---

## 9. RİSKLER VE ÇÖZÜMLER

| Risk | Olasılık | Etki | Çözüm |
|------|---------|------|-------|
| Yeterli Türkçe veri bulunamaması | Orta | Yüksek | Sentetik veri üretimi + back-translation |
| Model overfitting | Yüksek | Orta | Cross-validation + dropout + early stopping |
| Düşük accuracy | Orta | Yüksek | Ensemble + hyperparameter tuning |
- Veri kalitesi düşük | Orta | Yüksek | Manuel doğrulama + veri temizleme pipeline'ı |
| inference yavaşlığı | Düşük | Orta | Model quantization + ONNX export |

---

## 10. SONUÇ

Mevcut sistem **çok yetersiz** ve **%99 doğruluk için tamamen yeniden yazılması gerekiyor**. 

Özellikle:
1. **Veri seti**: 223 örnek → minimum 15.000+ örnek
2. **Model**: Basit TF-IDF → Ensemble + Transformer
3. **Dil**: İngilizce → Türkçe
4. **Özellikler**: Sadece kelime frekansı → 50+ özellik
5. **API**: Gelişmiş analiz endpoint'leri

Bu plan uygulandığında **%97-99** doğruluk oranına ulaşmak mümkündür.

---

*Bu doküman MiMoCode tarafından otomatik olarak oluşturulmuştur.*
*Tarih: 2026-07-25*
