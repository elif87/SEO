#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test scripti - Scraper test
"""
import sys
import os

# Path düzeltmesi
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test URL'si
test_url = "https://www.trendyol.com/magaza/fotografcanta"

print("=" * 60)
print("TEST: Trendyol Scraper")
print("=" * 60)
print(f"Test URL: {test_url}")
print()
print("Test URL ornekleri:")
print("1. https://www.trendyol.com/magaza/fotografcanta")
print("2. https://www.trendyol.com/magaza/karaca")
print("3. https://www.trendyol.com/magaza/xxx")
print()
print("Scripti calistirmak icin:")
print(f"python src\\scraper_selenium_to_excel.py \"{test_url}\"")
print()
print("VEYA interaktif mod:")
print("python src\\scraper_selenium_to_excel.py")
print("=" * 60)
