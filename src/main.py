#!/usr/bin/env python3
"""
Telegram Daily Briefing - Main Pipeline
Sistema automatizado de notícias diárias sobre IA
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('briefing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import local modules
from news_collector import NewsCollector, NewsItem
from telegram_sender import TelegramSender
from content_processor import ContentProcessor
from message_formatter import MessageFormatter

def load_config() -> dict:
    """Load configuration from JSON files"""
    config_dir = Path(__file__).parent.parent / 'config'

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
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded")

        # Initialize components
        collector = NewsCollector(config)
        processor = ContentProcessor()
        formatter = MessageFormatter(config.get('formatting', {}))

        # Initialize Telegram sender
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not telegram_token or not telegram_chat_id:
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
        else:
            logger.info("ℹ️ No news to send today")

        logger.info("✅ Pipeline completed successfully")

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise

    finally:
        duration = datetime.now() - start_time
        logger.info(f"⏱️ Execution time: {duration}")

if __name__ == "__main__":
    main()
