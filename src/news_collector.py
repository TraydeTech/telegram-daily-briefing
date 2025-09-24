"""
News Collector Module
Coleta notícias de IA de múltiplas fontes: APIs, RSS feeds, web scraping
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Estrutura de dados para uma notícia"""
    title: str
    summary: str
    url: str
    source: str
    published_at: datetime
    relevance_score: float = 0.0

class NewsCollector:
    """Coletor principal de notícias de IA"""

    def __init__(self, config: Dict):
        self.sources = config.get('sources', {})
        self.keywords = [
            'ChatGPT', 'Cursor', 'Lovable', 'AI', 'artificial intelligence',
            'machine learning', 'deep learning', 'neural network'
        ]
        self.max_age_hours = config.get('news', {}).get('max_age_hours', 24)
        self.request_delay = config.get('processing', {}).get('request_delay', 1.0)

    def collect_all(self) -> List[NewsItem]:
        """Coleta notícias de todas as fontes configuradas"""
        all_news = []

        logger.info("🔍 Starting news collection from all sources")

        # Coleta de APIs
        try:
            api_news = self._collect_from_apis()
            all_news.extend(api_news)
            logger.info(f"📡 Collected {len(api_news)} items from APIs")
        except Exception as e:
            logger.error(f"❌ API collection failed: {e}")

        # Coleta de RSS feeds
        try:
            rss_news = self._collect_from_rss()
            all_news.extend(rss_news)
            logger.info(f"📰 Collected {len(rss_news)} items from RSS feeds")
        except Exception as e:
            logger.error(f"❌ RSS collection failed: {e}")

        # Coleta via web scraping
        try:
            web_news = self._collect_from_web()
            all_news.extend(web_news)
            logger.info(f"🌐 Collected {len(web_news)} items from web scraping")
        except Exception as e:
            logger.error(f"❌ Web scraping failed: {e}")

        # Filtragem por data e relevância
        filtered_news = self._filter_by_date_and_relevance(all_news)
        logger.info(f"🎯 Filtered to {len(filtered_news)} relevant items")

        return filtered_news

    def _collect_from_apis(self) -> List[NewsItem]:
        """Coleta de APIs (OpenAI, Anthropic)"""
        news_items = []

        # OpenAI API (modelos disponíveis)
        try:
            openai_data = self._fetch_openai_models()
            if openai_data:
                item = NewsItem(
                    title="OpenAI Models Update",
                    summary=f"Available models: {', '.join(openai_data[:5])}...",
                    url="https://platform.openai.com/docs/models",
                    source="OpenAI API",
                    published_at=datetime.now()
                )
                news_items.append(item)
        except Exception as e:
            logger.warning(f"OpenAI API collection failed: {e}")

        # Anthropic API (placeholder - requires API key)
        try:
            # TODO: Implementar quando API key estiver disponível
            pass
        except Exception as e:
            logger.warning(f"Anthropic API collection failed: {e}")

        return news_items

    def _collect_from_rss(self) -> List[NewsItem]:
        """Coleta de feeds RSS com melhor rate limiting"""
        news_items = []
        rss_feeds = self.sources.get('rss_feeds', {})

        total_feeds = len(rss_feeds)
        for i, (source_name, feed_url) in enumerate(rss_feeds.items(), 1):
            try:
                logger.info(f"📡 [{i}/{total_feeds}] Fetching RSS from {source_name}")

                # Rate limiting inteligente - delay maior entre feeds
                if i > 1:
                    time.sleep(self.request_delay * 2)  # Delay extra entre feeds diferentes

                # Parse RSS feed
                feed = feedparser.parse(feed_url)

                if feed.entries:
                    items_from_feed = 0
                    for entry in feed.entries[:3]:  # Reduzido para 3 por feed para evitar sobrecarga
                        published = self._parse_rss_date(entry)
                        if published:
                            item = NewsItem(
                                title=entry.title,
                                summary=getattr(entry, 'summary', entry.title)[:300],
                                url=entry.link,
                                source=source_name,
                                published_at=published
                            )
                            news_items.append(item)
                            items_from_feed += 1

                    logger.info(f"   ✅ Collected {items_from_feed} items from {source_name}")
                else:
                    logger.warning(f"   ⚠️ No entries found in {source_name}")

            except Exception as e:
                logger.error(f"❌ RSS collection failed for {source_name}: {e}")

        return news_items

    def _collect_from_web(self) -> List[NewsItem]:
        """Web scraping básico para sites sem RSS"""
        news_items = []

        # Exemplo: TechCrunch AI section (se não tiver RSS bom)
        try:
            techcrunch_items = self._scrape_techcrunch_ai()
            news_items.extend(techcrunch_items)
        except Exception as e:
            logger.warning(f"TechCrunch scraping failed: {e}")

        return news_items

    def _scrape_techcrunch_ai(self) -> List[NewsItem]:
        """Web scraping da seção AI do TechCrunch"""
        items = []

        try:
            url = "https://techcrunch.com/category/artificial-intelligence/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            time.sleep(self.request_delay)
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Encontra artigos na página
                articles = soup.find_all('article', limit=5)

                for article in articles:
                    try:
                        # Extrai título
                        title_elem = article.find('h2') or article.find('h3')
                        if not title_elem:
                            continue

                        title = title_elem.get_text().strip()

                        # Extrai link
                        link_elem = article.find('a', href=True)
                        if not link_elem:
                            continue

                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = f"https://techcrunch.com{url}"

                        # Extrai resumo (se disponível)
                        summary = ""
                        summary_elem = article.find('p')
                        if summary_elem:
                            summary = summary_elem.get_text().strip()[:200]

                        # Cria item
                        item = NewsItem(
                            title=title,
                            summary=summary or title,
                            url=url,
                            source="TechCrunch (scraped)",
                            published_at=datetime.now()  # Aproximação
                        )

                        items.append(item)

                    except Exception as e:
                        logger.debug(f"Error parsing article: {e}")
                        continue

        except Exception as e:
            logger.error(f"TechCrunch scraping error: {e}")

        return items

    def _filter_by_date_and_relevance(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Filtra notícias por data (24h) e relevância"""
        cutoff_date = datetime.now() - timedelta(hours=self.max_age_hours)
        filtered = []

        for item in news_items:
            # Filtro de data - mais permissivo com datas inválidas/futuras
            item_date = item.published_at
            is_recent = True

            # Se data é muito futura (> 1h do presente), considerar como erro e aceitar
            if item_date > datetime.now() + timedelta(hours=1):
                logger.debug(f"Future date detected for '{item.title}', accepting anyway")
                is_recent = True
            # Se data é muito antiga (> 7 dias), rejeitar
            elif item_date < datetime.now() - timedelta(days=7):
                is_recent = False
            # Caso normal: verificar cutoff
            else:
                is_recent = item_date >= cutoff_date

            if is_recent:
                # Cálculo de relevância baseado em keywords
                relevance = self._calculate_relevance(item.title + " " + item.summary)
                if relevance > 0.2:  # Threshold um pouco mais permissivo (era 0.3, agora 0.2)
                    item.relevance_score = relevance
                    filtered.append(item)

        # Ordena por relevância
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)
        return filtered

    def _calculate_relevance(self, text: str) -> float:
        """Calcula score de relevância baseado em keywords"""
        text_lower = text.lower()
        score = 0.0

        # Keywords de alta prioridade (foco principal)
        high_priority = ['chatgpt', 'cursor', 'lovable', 'openai', 'anthropic', 'claude']
        for keyword in high_priority:
            if keyword in text_lower:
                score += 1.0

        # Keywords de média prioridade (IA/ML)
        medium_priority = ['ai', 'artificial intelligence', 'machine learning', 'deep learning',
                          'neural network', 'gpt', 'llm', 'large language model']
        for keyword in medium_priority:
            if keyword in text_lower:
                score += 0.5

        # Keywords de baixa prioridade (tech geral - mais permissivo)
        low_priority = ['tech', 'technology', 'startup', 'software', 'automation', 'robotics']
        for keyword in low_priority:
            if keyword in text_lower:
                score += 0.2

        # Bônus para títulos com termos de IA
        title_indicators = ['ai', 'intelligence', 'neural', 'learning', 'gpt', 'model']
        title_words = text_lower.split()[:10]  # Primeiras 10 palavras (aprox. título)
        for word in title_indicators:
            if word in title_words:
                score += 0.3

        return min(score, 2.0)  # Máximo 2.0

    def _parse_rss_date(self, entry) -> Optional[datetime]:
        """Parse RSS date formats"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_tuple = getattr(entry, field)
                    return datetime(*time_tuple[:6])
                except:
                    continue

        # Fallback para data atual se não conseguir parsear
        return datetime.now()

    def _fetch_openai_models(self) -> List[str]:
        """Fetch available models from OpenAI API"""
        # TODO: Implementar quando API key estiver disponível
        # Por enquanto retorna modelos conhecidos
        return [
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
            "dall-e-3", "whisper-1", "text-embedding-ada-002"
        ]
