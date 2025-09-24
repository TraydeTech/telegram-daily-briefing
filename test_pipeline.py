#!/usr/bin/env python3
"""
Test script for the Telegram Daily Briefing pipeline
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from news_collector import NewsCollector
from content_processor import ContentProcessor
from message_formatter import MessageFormatter
from telegram_sender import TelegramSender

def test_full_pipeline():
    """Test the complete pipeline without sending messages"""

    print("🧪 Testing Full Pipeline")
    print("=" * 50)

    # Load configuration
    config_dir = Path('config')

    # Simple config for testing
    config = {
        'sources': {
            'rss_feeds': {
                'techcrunch': 'https://techcrunch.com/feed/',
                'venturebeat': 'https://feeds.feedburner.com/venturebeat/SZYF'
            }
        },
        'news': {
            'max_age_hours': 24,
            'max_news_per_run': 10
        },
        'formatting': {
            'max_message_length': 4000,
            'summary_max_length': 150,
            'format_template': "📰 {title}\n📝 {summary}\n🔗 {url}\n\n"
        },
        'processing': {
            'state_file': 'test_state.json',
            'request_delay': 1.0
        }
    }

    # Phase 1: News Collection
    print("📡 Phase 1: News Collection")
    collector = NewsCollector(config)
    raw_news = collector.collect_all()
    print(f"   Collected: {len(raw_news)} items")

    # Phase 2: Content Processing
    print("🎯 Phase 2: Content Processing")
    processor = ContentProcessor('test_state.json')
    processed_news = processor.process(raw_news)
    print(f"   Processed: {len(processed_news)} items")

    # Phase 3: Message Formatting
    print("📝 Phase 3: Message Formatting")
    formatter = MessageFormatter(config.get('formatting', {}))
    messages = formatter.format_messages(processed_news)

    if messages:
        print(f"   Generated: {len(messages)} message(s)")
        print(f"   Total chars: {sum(len(m) for m in messages)}")
        print(f"   Sample message preview:")
        print("   " + "-" * 30)
        preview = messages[0][:200] + "..." if len(messages[0]) > 200 else messages[0]
        print(f"   {preview}")
    else:
        print("   No messages generated")

    # Phase 4: Telegram Connection Test (if token available)
    print("📨 Phase 4: Telegram Connection Test")
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if telegram_token and telegram_chat_id:
        sender = TelegramSender(telegram_token, telegram_chat_id)
        connection_ok = sender.test_connection()
        if connection_ok:
            print("   ✅ Telegram connection successful")
            print("   ⚠️  Would send messages in production")
        else:
            print("   ❌ Telegram connection failed")
    else:
        print("   ⚠️  Telegram credentials not found - skipping connection test")
        print("   💡 Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to test")

    print("\n✅ Test completed successfully!")

    # Summary
    print("\n📊 Summary:")
    print(f"   News collected: {len(raw_news)}")
    print(f"   News processed: {len(processed_news)}")
    print(f"   Messages ready: {len(messages)}")

    return True

if __name__ == "__main__":
    test_full_pipeline()
