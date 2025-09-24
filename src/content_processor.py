"""
Content Processor Module
Processa e filtra conteúdo coletado, gerencia estado de notícias enviadas
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Set
from pathlib import Path

from news_collector import NewsItem

logger = logging.getLogger(__name__)

class ContentProcessor:
    """Processador de conteúdo que filtra duplicatas e gerencia estado"""

    def __init__(self, state_file: str = 'news_state.json'):
        self.state_file = Path(state_file)
        self.processed_urls: Set[str] = set()
        self._load_processed_urls()

    def process(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Processa lista de notícias: remove duplicatas, filtra já enviadas, prioriza"""
        logger.info(f"🎯 Processing {len(news_items)} news items")

        # Remove duplicatas por URL
        unique_items = self._remove_duplicates(news_items)
        logger.info(f"🗑️ Removed duplicates: {len(unique_items)} unique items")

        # Remove itens já processados anteriormente
        new_items = self._filter_already_processed(unique_items)
        logger.info(f"🔄 Filtered already processed: {len(new_items)} new items")

        # Prioriza por relevância (keywords)
        prioritized = self._prioritize_by_keywords(new_items)
        logger.info(f"⭐ Prioritized by relevance")

        # Limita quantidade por execução (máximo 10)
        final_items = prioritized[:10]
        logger.info(f"📏 Limited to {len(final_items)} items")

        # Atualiza estado dos itens processados
        self._update_processed_state(final_items)

        return final_items

    def _remove_duplicates(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicatas baseadas em URL"""
        seen_urls = set()
        unique_items = []

        for item in news_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)

        return unique_items

    def _filter_already_processed(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Filtra itens que já foram processados anteriormente"""
        new_items = []

        for item in news_items:
            if item.url not in self.processed_urls:
                new_items.append(item)

        return new_items

    def _prioritize_by_keywords(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Prioriza notícias baseado em keywords de relevância"""
        # Já calculado no NewsCollector, apenas reordena
        return sorted(news_items, key=lambda x: x.relevance_score, reverse=True)

    def _update_processed_state(self, processed_items: List[NewsItem]):
        """Atualiza estado dos itens processados"""
        for item in processed_items:
            self.processed_urls.add(item.url)

        # Salva estado em arquivo
        self._save_processed_urls()

    def _load_processed_urls(self):
        """Carrega URLs processadas do arquivo de estado"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_urls = set(data.get('processed_urls', []))
                    logger.info(f"📁 Loaded {len(self.processed_urls)} processed URLs")
            else:
                logger.info("📁 No previous state file found, starting fresh")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load state file: {e}")
            self.processed_urls = set()

    def _save_processed_urls(self):
        """Salva URLs processadas no arquivo de estado"""
        try:
            data = {
                'processed_urls': list(self.processed_urls),
                'last_updated': datetime.now().isoformat()
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved {len(self.processed_urls)} processed URLs")
        except Exception as e:
            logger.error(f"❌ Failed to save state file: {e}")

    def get_stats(self) -> Dict:
        """Retorna estatísticas do processador"""
        return {
            'total_processed_urls': len(self.processed_urls),
            'state_file': str(self.state_file),
            'state_file_exists': self.state_file.exists()
        }
