"""
Telegram Sender Module
Envia mensagens formatadas via Telegram Bot API
"""

import json
import logging
import time
from typing import List
import requests

logger = logging.getLogger(__name__)

class TelegramSender:
    """Enviador de mensagens via Telegram Bot API"""

    def __init__(self, token: str, chat_id: str, max_retries: int = 3):
        self.token = token
        self.chat_id = chat_id
        self.max_retries = max_retries
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = requests.Session()

    def send_messages(self, messages: List[str]) -> bool:
        """Envia múltiplas mensagens com tratamento de erros"""
        success = True

        for i, message in enumerate(messages, 1):
            logger.info(f"📤 Sending message {i}/{len(messages)}")

            if not self._send_single_message(message):
                success = False
                logger.error(f"❌ Failed to send message {i}")
            else:
                logger.info(f"✅ Message {i} sent successfully")

            # Pequeno delay entre mensagens para evitar rate limiting
            if i < len(messages):
                time.sleep(0.5)

        return success

    def _send_single_message(self, text: str) -> bool:
        """Envia uma única mensagem com retry logic"""
        url = f"{self.base_url}/sendMessage"

        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'HTML',  # Permite formatação básica
            'disable_web_page_preview': False
        }

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempting to send message (attempt {attempt + 1})")

                response = self.session.post(
                    url,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('ok'):
                        return True
                    else:
                        logger.error(f"Telegram API error: {result.get('description')}")
                else:
                    logger.error(f"HTTP error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")

            # Wait before retry
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        return False

    def test_connection(self) -> bool:
        """Testa conexão com Telegram API"""
        try:
            url = f"{self.base_url}/getMe"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info = result.get('result', {})
                    logger.info(f"🤖 Connected to bot: @{bot_info.get('username')}")
                    return True

            logger.error(f"Connection test failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False
