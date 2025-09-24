#!/usr/bin/env python3
"""
Debug script para investigar coleta RSS
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from news_collector import NewsCollector

# Configuração de teste
config = {
    'sources': {
        'rss_feeds': {
            'techcrunch': 'https://techcrunch.com/feed/',
            'venturebeat': 'https://feeds.feedburner.com/venturebeat/SZYF'
        }
    },
    'news': {
        'max_age_hours': 48  # Aumentado para 48h para teste
    }
}

print("🔍 Debug RSS Collection")
print("=" * 40)

collector = NewsCollector(config)
all_news = collector.collect_all()

print(f"📊 Total collected: {len(all_news)}")

for i, news in enumerate(all_news, 1):
    print(f"\n{i}. {news.title}")
    print(f"   Source: {news.source}")
    print(f"   Published: {news.published_at}")
    print(f"   Relevance: {news.relevance_score}")
    print(f"   URL: {news.url}")

# Testar coleta RSS diretamente
print("\n🧪 Testing RSS collection directly...")
rss_news = collector._collect_from_rss()
print(f"RSS items collected: {len(rss_news)}")

for i, news in enumerate(rss_news, 1):
    print(f"\n{i}. {news.title}")
    print(f"   Source: {news.source}")
    print(f"   Published: {news.published_at}")
    print(f"   Relevance: {news.relevance_score}")
