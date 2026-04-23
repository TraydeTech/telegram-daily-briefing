#!/usr/bin/env python3
"""
Telegram Daily Briefing - Main Pipeline
Sistema automatizado de notícias diárias sobre IA
"""

import os
import re
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).parent.parent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(_ROOT / 'briefing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
from news_collector import NewsCollector, NewsItem
from telegram_sender import TelegramSender
from content_processor import ContentProcessor
from message_formatter import MessageFormatter

# Import alert system
try:
    from alerts import send_alert, get_alert_system
    ALERTS_ENABLED = True
except ImportError:
    ALERTS_ENABLED = False
    def send_alert(*args, **kwargs):
        pass

# Import log rotation
try:
    from log_rotate import check_and_rotate_logs
    LOG_ROTATION_ENABLED = True
except ImportError:
    LOG_ROTATION_ENABLED = False
    def check_and_rotate_logs():
        return False

def load_config() -> dict:
    """Load configuration from JSON files"""
    config_dir = _ROOT / 'config'

    # Load settings
    with open(config_dir / 'settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)

    # Load sources
    with open(config_dir / 'sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)

    # Merge configurations
    config = {**settings, **sources}
    return config

def main():
    """Main pipeline execution"""
    start_time = datetime.now()
    logger.info("🚀 Starting Telegram Daily Briefing")

    try:
        # Verificação e rotação de logs (se habilitado)
        if LOG_ROTATION_ENABLED:
            try:
                rotated = check_and_rotate_logs()
                if rotated:
                    logger.info("📏 Log file was rotated during startup")
            except Exception as e:
                logger.warning(f"Log rotation check failed: {e}")

        # Verificação de saúde do sistema (se alertas habilitados)
        if ALERTS_ENABLED:
            try:
                alert_system = get_alert_system()
                health_issues = alert_system.check_system_health()
                if health_issues:
                    logger.warning(f"⚠️ Health check found {len(health_issues)} issues")
                    for issue in health_issues:
                        logger.warning(f"   {issue}")
            except Exception as e:
                logger.warning(f"Health check failed: {e}")

        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded")

        # Initialize components
        collector = NewsCollector(config)
        processor = ContentProcessor(str(_ROOT / 'news_state.json'))
        formatter = MessageFormatter(config.get('formatting', {}))

        # Initialize Telegram sender (extra sanitization for CI secrets)
        raw_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        raw_chat = os.getenv('TELEGRAM_CHAT_ID', '')

        # Remove all whitespace and keep only allowed chars
        telegram_token = ''.join(ch for ch in raw_token if ch.isalnum() or ch in [':', '-', '_'])
        telegram_chat_id = ''.join(ch for ch in raw_chat if ch.isdigit() or ch == '-')

        # Basic diagnostics (length/format only; no secrets)
        token_ok = re.match(r'^\d{5,}:[A-Za-z0-9_-]{30,}$', telegram_token) is not None
        chat_ok = re.match(r'^-?\d{5,}$', telegram_chat_id) is not None
        logger.info(f"🔐 Token len={len(telegram_token)} ok={token_ok} | Chat len={len(telegram_chat_id)} ok={chat_ok}")

        if not telegram_token or not telegram_chat_id or not token_ok or not chat_ok:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables are required")

        sender = TelegramSender(telegram_token, telegram_chat_id)
        logger.info("✅ Components initialized")

        # Test Telegram connection (optional)
        if os.getenv('DEBUG', 'false').lower() == 'true':
            logger.info("🔍 Testing Telegram connection...")
            if not sender.test_connection():
                logger.warning("⚠️ Telegram connection test failed, but continuing...")

        # Execute pipeline
        logger.info("🔍 Phase 1: Collecting news...")
        raw_news = collector.collect_all()

        logger.info("🎯 Phase 2: Processing content...")
        processed_news = processor.process(raw_news)

        logger.info("📝 Phase 3: Formatting messages...")
        messages = formatter.format_messages(processed_news)

        if messages:
            logger.info(f"📤 Phase 4: Sending {len(messages)} message(s)...")
            success = sender.send_messages(messages)

            if success:
                logger.info("✅ All messages sent successfully!")
            else:
                logger.error("❌ Some messages failed to send")
                # Fail the job so Actions shows the error clearly
                raise RuntimeError("Telegram send failed")
        else:
            logger.info("ℹ️ No news to send today")
            # Optionally send a heartbeat message if configured
            send_empty = os.getenv('SEND_EMPTY_BRIEFING', 'false').lower() == 'true'
            if send_empty:
                heartbeat = (
                    "✅ Briefing executado, sem novas notícias relevantes nas últimas 24h.\n"
                    f"🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
                )
                logger.info("📤 Sending heartbeat message (no news)...")
                if not sender.send_messages([heartbeat]):
                    raise RuntimeError("Heartbeat send failed")

        logger.info("✅ Pipeline completed successfully")

    except Exception as e:
        error_message = f"Pipeline failed: {str(e)}"
        logger.error(f"❌ {error_message}")

        # Envia alerta de falha
        send_alert('execution_failure', error_message, 'error')

        raise

    finally:
        duration = datetime.now() - start_time
        logger.info(f"⏱️ Execution time: {duration}")

if __name__ == "__main__":
    main()
