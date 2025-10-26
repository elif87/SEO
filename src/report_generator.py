#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator - Excel Rapor Oluşturucu
=========================================

Bu modül scraping sonuçlarını Excel formatında raporlar.
Pandas DataFrame kullanarak profesyonel Excel dosyaları oluşturur.

KULLANIM:
from report_generator import generate_excel_report

results = [...]  # Scraping sonuçları
generate_excel_report(results, "rapor.xlsx")
"""

import pandas as pd
from datetime import datetime
import os

def generate_excel_report(results, filename="rapor.xlsx"):
    """
    Scraping sonuçlarını Excel raporu olarak kaydeder
    
    Args:
        results (list): Scraping sonuçları listesi
        filename (str): Çıktı Excel dosya adı
    """
    print(f"📊 Excel raporu oluşturuluyor: {filename}")
    
    if not results:
        print("⚠️ Rapor edilecek veri bulunamadı!")
        return
    
    try:
        # DataFrame için veri hazırla
        report_data = []
        
        for item in results:
            # Temel bilgiler
            title = item.get("title", "Başlık Bulunamadı")
            sku = item.get("sku", "SKU Bulunamadı")
            url = item.get("url", "")
            
            # Varyasyonları string olarak birleştir
            variations = item.get("variations", [])
            variations_str = ", ".join(variations) if variations else "Varyasyon Bulunamadı"
            
            # Eksik ölçüleri string olarak birleştir
            missing_sizes = item.get("missing_sizes", [])
            missing_sizes_str = ", ".join(missing_sizes) if missing_sizes else "Tüm Ölçüler Mevcut"
            
            # Mockup görsellerini string olarak birleştir
            mockup_images = item.get("mockup_images", [])
            mockup_count = len(mockup_images)
            mockup_str = f"{mockup_count} adet mockup" if mockup_count > 0 else "Mockup Bulunamadı"
            
            # Görsel sayısı
            image_count = item.get("image_count", 0)
            
            # Satır verisi oluştur
            row_data = {
                "Ürün Adı": title,
                "Ürün Kodu": sku,
                "Ürün URL": url,
                "Mevcut Ölçüler": variations_str,
                "Eksik Ölçüler": missing_sizes_str,
                "Eksik Mokaplar": mockup_str,
                "Görsel Sayısı": image_count,
                "Mockup Sayısı": mockup_count,
                "Toplam Varyasyon": len(variations)
            }
            
            report_data.append(row_data)
        
        # DataFrame oluştur
        df = pd.DataFrame(report_data)
        
        # Excel yazıcı ayarları
        excel_writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # Ana rapor sayfası
        df.to_excel(excel_writer, sheet_name='Ana Rapor', index=False)
        
        # Özet istatistikler sayfası
        summary_data = create_summary_statistics(results)
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(excel_writer, sheet_name='Özet İstatistikler', index=False)
        
        # Eksik ölçüler analizi sayfası
        missing_analysis = create_missing_sizes_analysis(results)
        missing_df = pd.DataFrame(missing_analysis)
        missing_df.to_excel(excel_writer, sheet_name='Eksik Ölçüler Analizi', index=False)
        
        # Mockup analizi sayfası
        mockup_analysis = create_mockup_analysis(results)
        mockup_df = pd.DataFrame(mockup_analysis)
        mockup_df.to_excel(excel_writer, sheet_name='Mockup Analizi', index=False)
        
        # Tüm ölçüler analizi sayfası (yeni - gerçek ölçülerin analizi)
        all_sizes_analysis = create_all_sizes_analysis(results)
        sizes_df = pd.DataFrame(all_sizes_analysis)
        sizes_df.to_excel(excel_writer, sheet_name='Gercek Olculer Analizi', index=False)
        
        # Excel dosyasını kaydet
        excel_writer.close()
        
        print(f"✅ Excel raporu başarıyla oluşturuldu: {filename}")
        print(f"📈 Toplam {len(results)} ürün raporlandı")
        
        # Dosya boyutunu göster
        file_size = os.path.getsize(filename) / 1024  # KB
        print(f"📁 Dosya boyutu: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"❌ Excel raporu oluşturma hatası: {e}")
        raise

def create_summary_statistics(results):
    """Özet istatistikler oluşturur"""
    if not results:
        return []
    
    total_products = len(results)
    total_images = sum(item.get("image_count", 0) for item in results)
    total_mockups = sum(len(item.get("mockup_images", [])) for item in results)
    
    # SKU'lu ürün sayısı
    sku_count = sum(1 for item in results if item.get("sku") and item.get("sku") != "SKU Bulunamadı")
    
    # Varyasyonlu ürün sayısı
    variation_count = sum(1 for item in results if item.get("variations"))
    
    # Eksik ölçülü ürün sayısı
    missing_sizes_count = sum(1 for item in results if item.get("missing_sizes"))
    
    summary_data = [
        {"Metrik": "Toplam Ürün Sayısı", "Değer": total_products},
        {"Metrik": "SKU'lu Ürün Sayısı", "Değer": sku_count},
        {"Metrik": "Varyasyonlu Ürün Sayısı", "Değer": variation_count},
        {"Metrik": "Eksik Ölçülü Ürün Sayısı", "Değer": missing_sizes_count},
        {"Metrik": "Toplam Görsel Sayısı", "Değer": total_images},
        {"Metrik": "Toplam Mockup Sayısı", "Değer": total_mockups},
        {"Metrik": "Ortalama Görsel/Ürün", "Değer": round(total_images / total_products, 2) if total_products > 0 else 0},
        {"Metrik": "Mockup Oranı (%)", "Değer": round((total_mockups / total_images) * 100, 2) if total_images > 0 else 0},
        {"Metrik": "Rapor Oluşturma Tarihi", "Değer": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]
    
    return summary_data

def create_missing_sizes_analysis(results):
    """Eksik ölçüler analizi oluşturur"""
    if not results:
        return []
    
    # Beklenen ölçüler
    expected_sizes = ["30x40", "40x60", "50x70"]
    
    analysis_data = []
    
    for size in expected_sizes:
        missing_count = sum(1 for item in results if size in item.get("missing_sizes", []))
        available_count = len(results) - missing_count
        
        analysis_data.append({
            "Ölçü": size,
            "Mevcut Ürün Sayısı": available_count,
            "Eksik Ürün Sayısı": missing_count,
            "Eksiklik Oranı (%)": round((missing_count / len(results)) * 100, 2) if len(results) > 0 else 0
        })
    
    return analysis_data

def create_mockup_analysis(results):
    """Mockup analizi oluşturur"""
    if not results:
        return []
    
    analysis_data = []
    
    for item in results:
        title = item.get("title", "Başlık Bulunamadı")
        mockup_images = item.get("mockup_images", [])
        total_images = item.get("image_count", 0)
        
        if total_images > 0:
            mockup_ratio = len(mockup_images) / total_images
        else:
            mockup_ratio = 0
        
        analysis_data.append({
            "Ürün Adı": title[:50] + "..." if len(title) > 50 else title,
            "Toplam Görsel": total_images,
            "Mockup Sayısı": len(mockup_images),
            "Mockup Oranı (%)": round(mockup_ratio * 100, 2),
            "Mockup Durumu": "Mockup Var" if mockup_images else "Mockup Yok"
        })
    
    return analysis_data

def create_all_sizes_analysis(results):
    """
    Gerçek ürünlerden toplanan tüm ölçülerin analizini oluşturur
    Hangi ölçünün kaç ürün

de var/eksik olduğunu gösterir
    """
    if not results:
        return []
    
    # Tüm benzersiz ölçüleri topla
    all_sizes = set()
    for item in results:
        variations = item.get("variations", [])
        for var in variations:
            # Ölçü formatı olabilir (örn: "30x40", "40x60 cm", "XL", "S")
            var_clean = str(var).strip()
            if len(var_clean) < 20:  # Çok uzun metinleri filtrele
                all_sizes.add(var_clean)
    
    # Her ölçü için istatistik
    analysis_data = []
    for size in sorted(all_sizes):
        products_with = 0
        products_without = 0
        products_with_list = []
        products_without_list = []
        
        for item in results:
            variations = item.get("variations", [])
            if size in variations or size.lower() in [v.lower() for v in variations]:
                products_with += 1
                products_with_list.append(item.get("title", "Bilinmeyen"))
            else:
                products_without += 1
                products_without_list.append(item.get("title", "Bilinmeyen"))
        
        total = len(results)
        existence_rate = round((products_with / total * 100), 2) if total > 0 else 0
        
        analysis_data.append({
            "Olcu": size,
            "Mevcut Urun Sayisi": products_with,
            "Eksik Urun Sayisi": products_without,
            "Toplam Urun": total,
            "Varlik Orani (%)": existence_rate,
            "Durum": "Mevcut" if products_with > 0 else "Eksik"
        })
    
    return analysis_data

def create_detailed_product_report(results, filename="detayli_rapor.xlsx"):
    """
    Detaylı ürün raporu oluşturur (görsel URL'leri dahil)
    
    Args:
        results (list): Scraping sonuçları
        filename (str): Çıktı dosya adı
    """
    print(f"📊 Detaylı Excel raporu oluşturuluyor: {filename}")
    
    try:
        excel_writer = pd.ExcelWriter(filename, engine='openpyxl')
        
        # Her ürün için ayrı sayfa
        for i, item in enumerate(results):
            sheet_name = f"Ürün_{i+1}"[:31]  # Excel sheet adı limiti
            
            # Ürün bilgileri
            product_data = {
                "Özellik": [
                    "Ürün Adı", "SKU", "URL", "Görsel Sayısı", 
                    "Mockup Sayısı", "Varyasyon Sayısı", "Eksik Ölçüler"
                ],
                "Değer": [
                    item.get("title", ""),
                    item.get("sku", ""),
                    item.get("url", ""),
                    item.get("image_count", 0),
                    len(item.get("mockup_images", [])),
                    len(item.get("variations", [])),
                    ", ".join(item.get("missing_sizes", []))
                ]
            }
            
            df_info = pd.DataFrame(product_data)
            df_info.to_excel(excel_writer, sheet_name=sheet_name, index=False, startrow=0)
            
            # Görseller
            images_data = []
            for j, img_url in enumerate(item.get("images", [])):
                is_mockup = img_url in item.get("mockup_images", [])
                images_data.append({
                    "Görsel No": j + 1,
                    "URL": img_url,
                    "Mockup": "Evet" if is_mockup else "Hayır"
                })
            
            if images_data:
                df_images = pd.DataFrame(images_data)
                df_images.to_excel(excel_writer, sheet_name=sheet_name, index=False, startrow=len(df_info) + 3)
        
        excel_writer.close()
        print(f"✅ Detaylı rapor oluşturuldu: {filename}")
        
    except Exception as e:
        print(f"❌ Detaylı rapor oluşturma hatası: {e}")

# Test fonksiyonu
def test_report_generation():
    """Rapor oluşturma fonksiyonunu test eder"""
    # Örnek test verisi
    test_results = [
        {
            "title": "Test Ürün 1",
            "sku": "TEST001",
            "url": "https://example.com/product1",
            "images": ["img1.jpg", "img2.jpg"],
            "mockup_images": ["img1.jpg"],
            "variations": ["30x40", "40x60"],
            "missing_sizes": ["50x70"],
            "image_count": 2
        },
        {
            "title": "Test Ürün 2",
            "sku": "TEST002",
            "url": "https://example.com/product2",
            "images": ["img3.jpg", "img4.jpg", "img5.jpg"],
            "mockup_images": [],
            "variations": ["30x40", "40x60", "50x70"],
            "missing_sizes": [],
            "image_count": 3
        }
    ]
    
    print("🧪 Rapor oluşturma testi:")
    generate_excel_report(test_results, "test_rapor.xlsx")
    print("✅ Test tamamlandı!")

if __name__ == "__main__":
    # Test çalıştır
    test_report_generation()
