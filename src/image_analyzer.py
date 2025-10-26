#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Analyzer - Mockup Tespit Modülü
=====================================

Bu modül görsel URL'lerinde veya alt-text'lerinde mockup anahtar kelimelerini arar.
İleride CLIP gibi AI modelleri eklemeye uygun yapıda tasarlanmıştır.

KULLANIM:
from image_analyzer import is_mockup_by_filename

result = is_mockup_by_filename("https://example.com/mockup-frame.jpg")
print(result)  # True veya False
"""

import re
from urllib.parse import urlparse

# Mockup tespiti için anahtar kelimeler
MOCKUP_KEYWORDS = [
    "mockup", "mokap", "frame", "psd", "mock", 
    "template", "placeholder", "sample", "preview",
    "çerçeve", "şablon", "örnek", "önizleme"
]

def is_mockup_by_filename(url_or_alt):
    """
    URL veya alt-text içinde mockup anahtar kelimelerini arar
    
    Args:
        url_or_alt (str): Görsel URL'si veya alt-text
        
    Returns:
        bool: Mockup anahtar kelimesi bulunursa True, aksi halde False
    """
    if not url_or_alt or not isinstance(url_or_alt, str):
        return False
    
    # Metni küçük harfe çevir ve temizle
    text = url_or_alt.lower().strip()
    
    # URL'den dosya adını çıkar
    try:
        parsed_url = urlparse(text)
        filename = parsed_url.path.split('/')[-1]
        text = f"{text} {filename}"
    except:
        pass
    
    # Her anahtar kelimeyi kontrol et
    for keyword in MOCKUP_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    # Regex ile daha gelişmiş pattern'ler
    mockup_patterns = [
        r'mock[-_]?up',
        r'frame[-_]?\d*',
        r'psd[-_]?\d*',
        r'template[-_]?\d*',
        r'placeholder[-_]?\d*',
        r'çerçeve[-_]?\d*',
        r'şablon[-_]?\d*'
    ]
    
    for pattern in mockup_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def analyze_image_batch(image_urls):
    """
    Birden fazla görsel URL'sini toplu olarak analiz eder
    
    Args:
        image_urls (list): Görsel URL'leri listesi
        
    Returns:
        dict: {
            'mockup_images': [...],
            'regular_images': [...],
            'mockup_count': int,
            'total_count': int
        }
    """
    mockup_images = []
    regular_images = []
    
    for url in image_urls:
        if is_mockup_by_filename(url):
            mockup_images.append(url)
        else:
            regular_images.append(url)
    
    return {
        'mockup_images': mockup_images,
        'regular_images': regular_images,
        'mockup_count': len(mockup_images),
        'total_count': len(image_urls)
    }

def get_mockup_confidence_score(url_or_alt):
    """
    Mockup olma olasılığını 0-1 arasında skorlar
    (İleride AI modelleri için hazırlık)
    
    Args:
        url_or_alt (str): Görsel URL'si veya alt-text
        
    Returns:
        float: 0.0 (kesinlikle mockup değil) - 1.0 (kesinlikle mockup)
    """
    if not url_or_alt:
        return 0.0
    
    text = url_or_alt.lower()
    score = 0.0
    
    # Anahtar kelime skorları
    keyword_scores = {
        'mockup': 0.9,
        'mokap': 0.9,
        'frame': 0.8,
        'psd': 0.7,
        'template': 0.6,
        'placeholder': 0.5,
        'çerçeve': 0.8,
        'şablon': 0.6
    }
    
    for keyword, weight in keyword_scores.items():
        if keyword in text:
            score = max(score, weight)
    
    # Pattern skorları
    if re.search(r'mock[-_]?up', text):
        score = max(score, 0.9)
    
    if re.search(r'frame[-_]?\d*', text):
        score = max(score, 0.8)
    
    return min(score, 1.0)

# Test fonksiyonu
def test_mockup_detection():
    """Mockup tespit fonksiyonunu test eder"""
    test_cases = [
        ("https://example.com/mockup-frame.jpg", True),
        ("https://example.com/product-photo.jpg", False),
        ("PSD Template File", True),
        ("Çerçeve Örneği", True),
        ("normal-image.png", False),
        ("mock_up_sample.psd", True),
        ("", False),
        (None, False)
    ]
    
    print("🧪 Mockup tespit testleri:")
    for test_input, expected in test_cases:
        result = is_mockup_by_filename(test_input)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{test_input}' -> {result} (beklenen: {expected})")

if __name__ == "__main__":
    # Test çalıştır
    test_mockup_detection()
    
    # Örnek kullanım
    print("\n📝 Örnek kullanım:")
    sample_urls = [
        "https://trendyol.com/images/mockup-frame-30x40.jpg",
        "https://trendyol.com/images/product-photo.jpg",
        "https://trendyol.com/images/psd-template.psd"
    ]
    
    for url in sample_urls:
        is_mockup = is_mockup_by_filename(url)
        confidence = get_mockup_confidence_score(url)
        print(f"URL: {url}")
        print(f"Mockup: {is_mockup}, Güven: {confidence:.2f}")
        print()
