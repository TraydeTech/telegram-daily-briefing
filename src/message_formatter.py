"""
Message Formatter Module
Formata notícias em mensagens compatíveis com Telegram
"""

import logging
from typing import List
from textwrap import shorten

from news_collector import NewsItem

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Formatador de mensagens para Telegram"""

    def __init__(self, formatting_config: dict):
        self.max_length = formatting_config.get('max_message_length', 4000)
        self.summary_max_length = formatting_config.get('summary_max_length', 150)
        self.template = formatting_config.get('format_template',
            "📰 {title}\n📝 {summary}\n🔗 {url}\n\n")

    def format_messages(self, news_items: List[NewsItem]) -> List[str]:
        """Formata lista de notícias em mensagens Telegram"""
        if not news_items:
            return []

        messages = []
        current_message = ""

        logger.info(f"📝 Formatting {len(news_items)} news items into messages")

        for item in news_items:
            formatted_item = self._format_single_item(item)

            # Verifica se cabe na mensagem atual
            if len(current_message + formatted_item) > self.max_length:
                if current_message:
                    messages.append(current_message.strip())
                    logger.debug(f"📦 Created message with {len(current_message)} chars")
                current_message = formatted_item
            else:
                current_message += formatted_item

        # Adiciona última mensagem se existir
        if current_message:
            messages.append(current_message.strip())
            logger.debug(f"📦 Created final message with {len(current_message)} chars")

        logger.info(f"📨 Generated {len(messages)} message(s) for Telegram")
        return messages

    def _format_single_item(self, item: NewsItem) -> str:
        """Formata um único item de notícia"""
        try:
            # Limpa e formata o título
            title = self._clean_text(item.title)

            # Limpa e limita o resumo
            summary = self._clean_text(item.summary)
            summary = shorten(summary, width=self.summary_max_length, placeholder="...")

            # Limpa a URL
            url = item.url.strip()

            # Aplica template
            formatted = self.template.format(
                title=title,
                summary=summary,
                url=url
            )

            return formatted

        except Exception as e:
            logger.error(f"❌ Error formatting item '{item.title}': {e}")
            # Fallback simples
            return f"📰 {item.title}\n🔗 {item.url}\n\n"

    def _clean_text(self, text: str) -> str:
        """Limpa texto para compatibilidade com Telegram"""
        if not text:
            return ""

        # Remove caracteres problemáticos
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        # Remove quebras de linha excessivas
        import re
        text = re.sub(r'\n\s*\n', '\n', text)

        # Limpa espaços extras
        text = ' '.join(text.split())

        return text.strip()

    def get_message_stats(self, messages: List[str]) -> dict:
        """Retorna estatísticas das mensagens"""
        if not messages:
            return {'count': 0, 'total_chars': 0, 'avg_chars': 0}

        total_chars = sum(len(msg) for msg in messages)

        return {
            'count': len(messages),
            'total_chars': total_chars,
            'avg_chars': total_chars // len(messages),
            'max_chars': max(len(msg) for msg in messages),
            'min_chars': min(len(msg) for msg in messages)
        }
