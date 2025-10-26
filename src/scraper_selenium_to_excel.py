#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trendyol Satıcı Sayfası Scraper - Excel Raporu
==============================================

KULLANIM:
1. python -m venv .venv
2. .venv\Scripts\activate.bat
3. pip install -r requirements.txt
4. tools\ klasörüne chromedriver.exe dosyasını koyun
5. python src\scraper_selenium_to_excel.py

UYARI: Demo amaçlı, düşük frekanslı istekler ile kullanın. 
Büyük ölçek veya ticari kullanım için Trendyol izinlerini kontrol edin.

Bu script Trendyol satıcı sayfasından ürün bilgilerini toplar ve Excel raporu oluşturur.
"""

import os
import sys
import json
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Windows terminal encoding düzeltme
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Yardımcı modülleri import et (src klasörü ekleniyor)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.image_analyzer import is_mockup_by_filename
from src.report_generator import generate_excel_report

# =============================================================================
# KONFIGÜRASYON AYARLARI
# =============================================================================

# ChromeDriver yolu (kullanıcı tools/ klasörüne chromedriver.exe koyacak)
CHROMEDRIVER_PATH = os.path.join("tools", "chromedriver.exe")

# Demo için tarayıcıyı göster (False = görünür, True = gizli)
HEADLESS = False

# Maksimum ürün sayısı (demo için hızlı test)
MAX_PRODUCTS = 10

# Beklenen ölçüler (eksik ölçü analizi için)
# Bu ölçüler satıcının her üründe olması beklenen ölçülerdir
# Otomatik olarak tüm ölçüler tarandığı için, 
# burada hangi ölçülerin eksik olduğunu raporlarda göreceksiniz
EXPECTED_SIZES = ["30x40", "40x60", "50x70", "20x30", "60x90"]

# Mockup tespiti için anahtar kelimeler
MOCKUP_KEYWORDS = ["mockup", "mokap", "frame", "psd", "mock"]

# Rastgele bekleme süreleri (saniye)
WAIT_MIN = 1.0
WAIT_MAX = 2.5

# Maksimum retry sayısı
MAX_RETRIES = 3

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def human_wait():
    """İnsan benzeri rastgele bekleme"""
    wait_time = random.uniform(WAIT_MIN, WAIT_MAX)
    print(f"⏳ {wait_time:.1f} saniye bekleniyor...")
    time.sleep(wait_time)

def init_driver():
    """
    ChromeDriver ile tarayıcı başlatma
    User-agent ve timeout ayarları ile
    """
    print("🚀 ChromeDriver başlatılıyor...")
    
    # Chrome seçenekleri
    chrome_options = Options()
    
    if HEADLESS:
        chrome_options.add_argument("--headless")
    
    # User-agent ekle (bot tespitini zorlaştırır)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Diğer ayarlar
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # ChromeDriver servisi
    service = Service(CHROMEDRIVER_PATH)
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # JavaScript ile navigator.webdriver özelliğini gizle
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Timeout ayarları
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        print("✅ ChromeDriver başarıyla başlatıldı")
        return driver
        
    except Exception as e:
        print(f"❌ ChromeDriver başlatma hatası: {e}")
        print("💡 tools/ klasöründe chromedriver.exe dosyasının olduğundan emin olun")
        raise

def collect_product_links_from_seller(driver, seller_url, max_pages=30, max_products=MAX_PRODUCTS):
    """
    Satıcı sayfasından ürün linklerini toplar
    Sayfalama ile çalışır ve maksimum ürün sayısına kadar toplar
    """
    print(f"🔍 Satıcı sayfasından ürün linkleri toplanıyor: {seller_url}")
    
    product_links = []
    page = 1
    
    while page <= max_pages and len(product_links) < max_products:
        try:
            # Sayfa URL'si oluştur
            if page == 1:
                page_url = seller_url
            else:
                page_url = f"{seller_url}?sayfa={page}"
            
            print(f"📄 Sayfa {page} işleniyor: {page_url}")
            
            # Sayfayı yükle
            driver.get(page_url)
            human_wait()
            
            # Ürün linklerini bul (birden fazla CSS seçici dene)
            selectors = [
                "a.p-card-chld",  # Ana ürün kartları
                "a[href*='/p/']",  # Ürün linkleri
                ".p-card a",  # Alternatif seçici
                "[data-testid='product-card'] a"  # Test ID ile
            ]
            
            links_found = []
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and "/p/" in href and href not in links_found:
                            links_found.append(href)
                    
                    if links_found:
                        print(f"✅ {len(links_found)} ürün linki bulundu (seçici: {selector})")
                        break
                        
                except Exception as e:
                    print(f"⚠️ Seçici '{selector}' başarısız: {e}")
                    continue
            
            if not links_found:
                print(f"⚠️ Sayfa {page}'de ürün linki bulunamadı")
                break
            
            # Yeni linkleri ekle
            for link in links_found:
                if link not in product_links and len(product_links) < max_products:
                    product_links.append(link)
            
            print(f"📊 Toplam {len(product_links)} ürün linki toplandı")
            
            # Sonraki sayfa kontrolü
            page += 1
            
            # Eğer maksimum ürün sayısına ulaştıysak dur
            if len(product_links) >= max_products:
                print(f"🎯 Maksimum ürün sayısına ({max_products}) ulaşıldı")
                break
                
        except Exception as e:
            print(f"❌ Sayfa {page} işleme hatası: {e}")
            break
    
    print(f"✅ Toplam {len(product_links)} ürün linki toplandı")
    return product_links

def parse_product_page(driver, product_url):
    """
    Tek bir ürün sayfasından bilgileri toplar
    Başlık, SKU, görseller, varyasyonlar ve mockup tespiti yapar
    """
    print(f"📦 Ürün sayfası işleniyor: {product_url}")
    
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # Sayfayı yükle
            driver.get(product_url)
            human_wait()
            
            # Sayfa yüklenene kadar bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Ürün bilgilerini topla
            product_data = {
                "url": product_url,
                "title": "",
                "sku": "",
                "images": [],
                "variations": [],
                "mockup_images": [],
                "missing_sizes": [],
                "image_count": 0
            }
            
            # Ürün başlığı
            try:
                title_selectors = [
                    "h1.pr-new-br",
                    "h1[data-testid='product-name']",
                    ".pr-new-br",
                    "h1"
                ]
                
                for selector in title_selectors:
                    try:
                        title_element = driver.find_element(By.CSS_SELECTOR, selector)
                        product_data["title"] = title_element.text.strip()
                        if product_data["title"]:
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Başlık bulunamadı: {e}")
            
            # SKU (Ürün Kodu)
            try:
                sku_selectors = [
                    "[data-testid='product-sku']",
                    ".product-sku",
                    ".sku",
                    "[class*='sku']"
                ]
                
                for selector in sku_selectors:
                    try:
                        sku_element = driver.find_element(By.CSS_SELECTOR, selector)
                        product_data["sku"] = sku_element.text.strip()
                        if product_data["sku"]:
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ SKU bulunamadı: {e}")
            
            # Görselleri topla
            try:
                image_selectors = [
                    "img[src*='trendyol']",
                    "img[data-src*='trendyol']",
                    "img[data-lazy*='trendyol']",
                    ".product-image img",
                    "[data-testid='product-image'] img"
                ]
                
                all_images = []
                for selector in image_selectors:
                    try:
                        images = driver.find_elements(By.CSS_SELECTOR, selector)
                        for img in images:
                            # Farklı src özelliklerini kontrol et
                            src_attrs = ["src", "data-src", "data-lazy", "data-original"]
                            for attr in src_attrs:
                                img_url = img.get_attribute(attr)
                                if img_url and img_url not in all_images:
                                    all_images.append(img_url)
                                    break
                    except:
                        continue
                
                product_data["images"] = all_images
                product_data["image_count"] = len(all_images)
                
            except Exception as e:
                print(f"⚠️ Görsel toplama hatası: {e}")
            
            # Mockup görsellerini tespit et
            try:
                mockup_images = []
                for img_url in product_data["images"]:
                    if is_mockup_by_filename(img_url):
                        mockup_images.append(img_url)
                
                product_data["mockup_images"] = mockup_images
                
            except Exception as e:
                print(f"⚠️ Mockup tespit hatası: {e}")
            
            # Varyasyonları topla (ölçüler)
            try:
                variation_selectors = [
                    "ul li",
                    ".variation-item",
                    "[data-testid='variation']",
                    ".size-option",
                    ".option-item"
                ]
                
                variations = []
                for selector in variation_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text.strip()
                            if text and len(text) < 20:  # Çok uzun metinleri filtrele
                                variations.append(text)
                    except:
                        continue
                
                # Tekrarları kaldır ve temizle
                product_data["variations"] = list(set(variations))
                
            except Exception as e:
                print(f"⚠️ Varyasyon toplama hatası: {e}")
            
            # Eksik ölçüleri hesapla
            product_data["missing_sizes"] = evaluate_missing_sizes(product_data, EXPECTED_SIZES)
            
            print(f"✅ Ürün işlendi: {product_data['title'][:50]}...")
            return product_data
            
        except TimeoutException:
            retry_count += 1
            print(f"⏰ Sayfa yükleme timeout (deneme {retry_count}/{MAX_RETRIES})")
            if retry_count < MAX_RETRIES:
                human_wait()
                continue
            else:
                print(f"❌ Ürün sayfası yüklenemedi: {product_url}")
                return None
                
        except Exception as e:
            retry_count += 1
            print(f"❌ Ürün sayfası işleme hatası (deneme {retry_count}/{MAX_RETRIES}): {e}")
            if retry_count < MAX_RETRIES:
                human_wait()
                continue
            else:
                return None

def evaluate_missing_sizes(item, expected_sizes):
    """
    Varyasyonlarda beklenen ölçülerin olup olmadığını kontrol eder
    Eksik ölçüleri döndürür
    """
    missing_sizes = []
    variations_text = " ".join(item.get("variations", [])).lower()
    
    for size in expected_sizes:
        if size.lower() not in variations_text:
            missing_sizes.append(size)
    
    return missing_sizes

def analyze_all_sizes_in_products(results):
    """
    Tüm ürünlerden benzersiz ölçüleri toplar ve analiz eder
    Hangi ölçülerin hangi ürünlerde eksik olduğunu gösterir
    """
    all_sizes = set()
    
    # Tüm ürünlerden ölçüleri topla
    for item in results:
        variations = item.get("variations", [])
        for var in variations:
            # Eğer ölçü formatıysa (örn: "30x40", "40x60")
            if 'x' in var.lower() or 'cm' in var.lower() or var.isdigit():
                all_sizes.add(var)
    
    # Eksik ölçü analizi
    size_analysis = {}
    for size in all_sizes:
        size_analysis[size] = {
            'total_products': 0,
            'products_with_this_size': 0,
            'products_without_this_size': [],
            'existence_rate': 0.0
        }
    
    # Her ürün için hangi ölçülerin olduğunu kontrol et
    for item in results:
        variations = item.get("variations", [])
        variations_lower = [v.lower() for v in variations]
        
        for size in all_sizes:
            size_analysis[size]['total_products'] += 1
            
            if any(size.lower() in var for var in variations_lower):
                size_analysis[size]['products_with_this_size'] += 1
            else:
                size_analysis[size]['products_without_this_size'].append({
                    'title': item.get('title', 'Bilinmeyen'),
                    'url': item.get('url', '')
                })
    
    # Varlık oranını hesapla
    for size, data in size_analysis.items():
        if data['total_products'] > 0:
            data['existence_rate'] = (data['products_with_this_size'] / data['total_products']) * 100
    
    return size_analysis

def save_results_to_json(results, filename="scraped_products.json"):
    """Sonuçları JSON dosyasına kaydeder"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 Sonuçlar JSON dosyasına kaydedildi: {filename}")
    except Exception as e:
        print(f"❌ JSON kaydetme hatası: {e}")

def main():
    """Ana fonksiyon - tüm akışı çalıştırır"""
    print("=" * 60)
    print("*** TRENDYOL SATICI SCRAPER - EXCEL RAPORU ***")
    print("=" * 60)
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) > 1:
        seller_url = sys.argv[1].strip()
        print(f"Komut satirindan URL alindi: {seller_url}")
    else:
        # Kullanıcıdan satıcı URL'si al
        seller_url = input("Trendyol satici URL'sini girin (orn: https://www.trendyol.com/magaza/xxxx): ").strip()
    
    if not seller_url:
        print("[HATA] URL girilmedi!")
        return
    
    if "trendyol.com/magaza/" not in seller_url:
        print("[UYARI] URL Trendyol satici sayfasi gibi gorunmuyor!")
        confirm = input("Devam etmek istiyor musunuz? (e/h): ").lower()
        if confirm != 'e':
            return
    
    # ChromeDriver'ı başlat
    driver = None
    try:
        driver = init_driver()
        
        # Ürün linklerini topla
        product_links = collect_product_links_from_seller(driver, seller_url)
        
        if not product_links:
            print("❌ Hiç ürün linki bulunamadı!")
            return
        
        print(f"\n🔍 {len(product_links)} ürün sayfası işlenecek...")
        
        # Her ürün sayfasını işle
        results = []
        for i, product_url in enumerate(product_links, 1):
            print(f"\n📦 [{i}/{len(product_links)}] Ürün işleniyor...")
            
            product_data = parse_product_page(driver, product_url)
            if product_data:
                results.append(product_data)
            
            # İlerleme göster
            if i % 10 == 0:
                print(f"📊 İlerleme: {i}/{len(product_links)} ürün işlendi")
        
        print(f"\n✅ Toplam {len(results)} ürün başarıyla işlendi!")
        
        # Sonuçları kaydet
        save_results_to_json(results)
        
        # Excel raporu oluştur
        print("📊 Excel raporu oluşturuluyor...")
        generate_excel_report(results, "rapor.xlsx")
        
        print("\n🎉 İşlem tamamlandı!")
        print("📁 Çıktı dosyaları:")
        print("   - scraped_products.json")
        print("   - rapor.xlsx")
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu")
        
    except Exception as e:
        print(f"\n❌ Genel hata: {e}")
        
    finally:
        if driver:
            print("🔚 Tarayıcı kapatılıyor...")
            driver.quit()

if __name__ == "__main__":
    main()
