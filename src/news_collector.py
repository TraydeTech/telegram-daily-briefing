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
        """Web scraping para sites sem RSS e redes sociais"""
        news_items = []

        # Configurado via config/sources.json
        scraping_sites = self.sources.get('web_scraping', {}).get('sites', [])

        for site_config in scraping_sites:
            if not site_config.get('enabled', False):
                continue

            site_name = site_config['name']
            site_url = site_config['url']
            site_type = site_config['type']

            try:
                logger.info(f"🌐 Scraping {site_name} ({site_type})")

                if site_type == 'linkedin':
                    items = self._scrape_linkedin_profile(site_config)
                elif site_type == 'instagram':
                    items = self._scrape_instagram_profile(site_config)
                else:
                    logger.warning(f"Unsupported scraping type: {site_type}")
                    continue

                news_items.extend(items)
                logger.info(f"   ✅ Collected {len(items)} items from {site_name}")

            except Exception as e:
                logger.warning(f"❌ Web scraping failed for {site_name}: {e}")

        # Fallback: TechCrunch AI section (se não tiver RSS bom)
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

    def _scrape_linkedin_profile(self, site_config: dict) -> List[NewsItem]:
        """Web scraping de perfil do LinkedIn (limitado e responsável)"""
        items = []

        try:
            url = site_config['url']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            time.sleep(self.request_delay * 2)  # Extra delay para redes sociais
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # ⚠️ AVISO: Este scraping é limitado e pode violar termos de serviço
                # Apenas para fins educacionais - não recomendado para produção

                # Procurar posts recentes (muito limitado devido a proteções do LinkedIn)
                posts = soup.find_all(['div', 'article'], class_=lambda x: x and 'feed' in x.lower(), limit=2)

                for post in posts:
                    try:
                        # Extrair texto do post
                        text_elem = post.find(['p', 'span'], class_=lambda x: x and ('text' in x.lower() or 'content' in x.lower()))
                        if text_elem:
                            text = text_elem.get_text().strip()[:200]

                            # Criar item (com baixa prioridade por ser scraping limitado)
                            item = NewsItem(
                                title=f"LinkedIn Post - {site_config['name']}",
                                summary=text,
                                url=url,
                                source=f"LinkedIn ({site_config['name']})",
                                published_at=datetime.now()
                            )
                            items.append(item)

                    except Exception as e:
                        logger.debug(f"Error parsing LinkedIn post: {e}")
                        continue

                if not items:
                    # Fallback: apenas indicar que há atividade no perfil
                    item = NewsItem(
                        title=f"LinkedIn Activity - {site_config['name']}",
                        summary=f"Nova atividade detectada no perfil de {site_config['name']}. Visite: {url}",
                        url=url,
                        source=f"LinkedIn ({site_config['name']})",
                        published_at=datetime.now()
                    )
                    items.append(item)

            else:
                logger.warning(f"LinkedIn request failed: {response.status_code}")

        except Exception as e:
            logger.warning(f"LinkedIn scraping error: {e}")

        return items

    def _scrape_instagram_profile(self, site_config: dict) -> List[NewsItem]:
        """Web scraping de perfil do Instagram (limitado e responsável)"""
        items = []

        try:
            url = site_config['url']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            time.sleep(self.request_delay * 2)  # Extra delay para redes sociais
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # ⚠️ AVISO: Instagram tem proteções anti-scraping robustas
                # Este método é muito limitado e pode não funcionar

                # Tentar extrair metatags (mais confiável que scraping direto)
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_title = soup.find('meta', attrs={'property': 'og:title'})

                if meta_desc or meta_title:
                    title = meta_title.get('content', 'Instagram Post') if meta_title else 'Instagram Activity'
                    summary = meta_desc.get('content', 'Nova atividade no Instagram') if meta_desc else 'Atividade detectada'

                    item = NewsItem(
                        title=f"{title} - {site_config['name']}",
                        summary=summary[:200],
                        url=url,
                        source=f"Instagram ({site_config['name']})",
                        published_at=datetime.now()
                    )
                    items.append(item)

            else:
                logger.warning(f"Instagram request failed: {response.status_code}")

        except Exception as e:
            logger.warning(f"Instagram scraping error: {e}")

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
                if relevance > 0.3:  # Threshold ajustado (mais permissivo para conteúdo em PT e Thais)
                    item.relevance_score = relevance
                    filtered.append(item)

        # Ordena por relevância
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)
        return filtered

    def _calculate_relevance(self, text: str) -> float:
        """Calcula score de relevância baseado em keywords (inglês + português)"""
        text_lower = text.lower()
        score = 0.0

        # Keywords de alta prioridade (foco principal + Thais Martan)
        high_priority = [
            'chatgpt', 'cursor', 'lovable', 'openai', 'anthropic', 'claude',
            'thais martan', 'martan', 'thaismartan'  # Alta prioridade para conteúdo da Thais
        ]
        for keyword in high_priority:
            if keyword in text_lower:
                score += 1.5  # Bônus extra para conteúdo prioritário

        # Keywords de média prioridade (IA/ML - inglês)
        medium_priority_en = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'gpt', 'llm', 'large language model', 'robotics'
        ]
        for keyword in medium_priority_en:
            if keyword in text_lower:
                score += 0.5

        # Keywords de média prioridade (IA/ML - português)
        medium_priority_pt = [
            'inteligência artificial', 'aprendizado máquina', 'aprendizado profundo',
            'rede neural', 'ia', 'machine learning', 'deep learning', 'robótica',
            'automação', 'tecnologia', 'inovação', 'startup', 'empreendedorismo'
        ]
        for keyword in medium_priority_pt:
            if keyword in text_lower:
                score += 0.5

        # Keywords de baixa prioridade (tech geral - mais permissivo)
        low_priority = [
            'tech', 'technology', 'software', 'hardware', 'digital',
            'tecnologia', 'software', 'hardware', 'digital', 'inovação'
        ]
        for keyword in low_priority:
            if keyword in text_lower:
                score += 0.2

        # Bônus para títulos com termos de IA (inglês + português)
        title_indicators = [
            'ai', 'intelligence', 'neural', 'learning', 'gpt', 'model',
            'ia', 'inteligência', 'aprendizado', 'tecnologia'
        ]
        title_words = text_lower.split()[:10]  # Primeiras 10 palavras (aprox. título)
        for word in title_indicators:
            if word in title_words:
                score += 0.3

        # Bônus para conteúdo de redes sociais (LinkedIn, Instagram da Thais)
        if any(social in text_lower for social in ['linkedin', 'instagram', 'thais martan']):
            score += 0.8  # Bônus significativo para conteúdo da Thais

        return min(score, 3.0)  # Máximo 3.0 (aumentado devido aos bônus)

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
