# 🛍️ Trendyol Satıcı Scraper - Excel Raporu

Bu proje Trendyol satıcı sayfalarından ürün bilgilerini toplayıp Excel formatında rapor oluşturan bir Python otomasyonudur.

## ⚠️ ÖNEMLİ UYARI

**Demo amaçlı, düşük frekanslı istekler ile kullanın. Büyük ölçek veya ticari kullanım için Trendyol izinlerini kontrol edin.**

## 📋 Özellikler

- ✅ Trendyol satıcı sayfasından ürün linklerini toplama
- ✅ Ürün detaylarını otomatik çıkarma (başlık, SKU, görseller, varyasyonlar)
- ✅ Mockup görsel tespiti
- ✅ Eksik ölçü analizi
- ✅ Excel raporu oluşturma (çoklu sayfa)
- ✅ Hata yönetimi ve retry mekanizması
- ✅ İnsan benzeri bekleme süreleri
- ✅ Windows cmd uyumlu

## 🏗️ Proje Yapısı

```
trendyol-otomasyon/
├── tools/
│   └── chromedriver.exe          # ChromeDriver (kullanıcı koyacak)
├── src/
│   ├── scraper_selenium_to_excel.py  # Ana scraper scripti
│   ├── image_analyzer.py             # Mockup tespit modülü
│   └── report_generator.py           # Excel rapor oluşturucu
├── requirements.txt                  # Python bağımlılıkları
├── .gitignore                        # Git ignore kuralları
└── README.md                         # Bu dosya
```

## 🚀 Kurulum ve Kullanım

### 1. Python Sanal Ortamı Oluşturma

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2. Bağımlılıkları Yükleme

```cmd
pip install -r requirements.txt
```

### 3. ChromeDriver Kurulumu

1. `tools/` klasörünü oluşturun
2. ChromeDriver'ı indirin: https://chromedriver.chromium.org/
3. `chromedriver.exe` dosyasını `tools/` klasörüne koyun

### 4. Scripti Çalıştırma

```cmd
python src\scraper_selenium_to_excel.py
```

## 📊 Çıktı Dosyaları

### 1. `scraped_products.json`
Ham scraping verilerini içerir:

```json
[
  {
    "url": "https://www.trendyol.com/urun-url",
    "title": "Ürün Adı",
    "sku": "ÜRÜN-KODU",
    "images": ["url1", "url2"],
    "mockup_images": ["url1"],
    "variations": ["30x40", "40x60"],
    "missing_sizes": ["50x70"],
    "image_count": 2
  }
]
```

### 2. `rapor.xlsx`
Excel raporu (4 sayfa):

#### Ana Rapor Sayfası
| Ürün Adı | Ürün Kodu | Ürün URL | Mevcut Ölçüler | Eksik Ölçüler | Eksik Mokaplar | Görsel Sayısı | Mockup Sayısı | Toplam Varyasyon |
|----------|-----------|----------|---------------|---------------|----------------|---------------|----------------|------------------|
| Örnek Ürün | ABC123 | https://... | 30x40, 40x60 | 50x70 | 1 adet mockup | 5 | 1 | 2 |

#### Özet İstatistikler Sayfası
| Metrik | Değer |
|--------|-------|
| Toplam Ürün Sayısı | 25 |
| SKU'lu Ürün Sayısı | 20 |
| Toplam Görsel Sayısı | 150 |
| Mockup Oranı (%) | 15.5 |

#### Eksik Ölçüler Analizi Sayfası
| Ölçü | Mevcut Ürün Sayısı | Eksik Ürün Sayısı | Eksiklik Oranı (%) |
|------|-------------------|-------------------|-------------------|
| 30x40 | 20 | 5 | 20.0 |
| 40x60 | 18 | 7 | 28.0 |
| 50x70 | 15 | 10 | 40.0 |

#### Mockup Analizi Sayfası
| Ürün Adı | Toplam Görsel | Mockup Sayısı | Mockup Oranı (%) | Mockup Durumu |
|----------|---------------|----------------|------------------|----------------|
| Ürün 1 | 5 | 1 | 20.0 | Mockup Var |
| Ürün 2 | 3 | 0 | 0.0 | Mockup Yok |

## ⚙️ Konfigürasyon

Ana script dosyasında (`src/scraper_selenium_to_excel.py`) aşağıdaki ayarları değiştirebilirsiniz:

```python
# Demo için tarayıcıyı göster (False = görünür, True = gizli)
HEADLESS = False

# Maksimum ürün sayısı (demo için hızlı test)
MAX_PRODUCTS = 50

# Beklenen ölçüler (eksik ölçü analizi için)
EXPECTED_SIZES = ["30x40", "40x60", "50x70"]

# Mockup tespiti için anahtar kelimeler
MOCKUP_KEYWORDS = ["mockup", "mokap", "frame", "psd", "mock"]

# Rastgele bekleme süreleri (saniye)
WAIT_MIN = 1.0
WAIT_MAX = 2.5
```

## 🧪 Test Etme

Küçük bir test için `MAX_PRODUCTS = 5` yapın:

```python
# Test için maksimum ürün sayısını azalt
MAX_PRODUCTS = 5
```

## 🔧 Sorun Giderme

### ChromeDriver Hatası
```
❌ ChromeDriver başlatma hatası
```
**Çözüm:** `tools/` klasöründe `chromedriver.exe` dosyasının olduğundan emin olun.

### Sayfa Yükleme Hatası
```
⏰ Sayfa yükleme timeout
```
**Çözüm:** İnternet bağlantınızı kontrol edin ve `HEADLESS = False` yaparak tarayıcıyı gözlemleyin.

### Ürün Linki Bulunamadı
```
⚠️ Sayfa X'de ürün linki bulunamadı
```
**Çözüm:** Trendyol'un sayfa yapısı değişmiş olabilir. CSS seçicileri güncellenebilir.

## 📝 Geliştirme Notları

### CSS Seçicileri
Script birden fazla CSS seçiciyi dener:
- `a.p-card-chld` (Ana ürün kartları)
- `a[href*='/p/']` (Ürün linkleri)
- `.p-card a` (Alternatif seçici)
- `[data-testid='product-card'] a` (Test ID ile)

### Mockup Tespiti
Anahtar kelime tabanlı tespit:
- URL'de: "mockup", "mokap", "frame", "psd"
- Alt-text'te: "çerçeve", "şablon", "örnek"

### Rate Limiting
- Her istek arasında 1-2.5 saniye rastgele bekleme
- Maksimum 3 retry denemesi
- İnsan benzeri davranış simülasyonu

## 🔮 Gelecek Özellikler

- [ ] CLIP AI ile görsel analizi
- [ ] Veritabanı entegrasyonu
- [ ] Web arayüzü
- [ ] Otomatik ChromeDriver güncelleme
- [ ] Çoklu platform desteği (Linux, macOS)
- [ ] API entegrasyonu

## 📄 Lisans

Bu proje demo amaçlıdır. Ticari kullanım için Trendyol'un izinlerini kontrol edin.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 Destek

Sorunlar için GitHub Issues kullanın.

---

**Not:** Bu tool eğitim amaçlıdır. Gerçek kullanımda Trendyol'un robots.txt ve kullanım şartlarını kontrol edin.
