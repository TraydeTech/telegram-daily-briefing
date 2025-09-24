#!/usr/bin/env python3
"""
Test script for Telegram integration
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from telegram_sender import TelegramSender

def test_telegram_sending():
    """Test sending a real message to Telegram"""

    print("📨 Testing Telegram Message Sending")
    print("=" * 40)

    # Get credentials
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False

    # Test message
    test_message = """🤖 *Teste do Sistema Telegram Daily Briefing*

✅ Sistema funcionando corretamente!
📅 Data: $(date)
🕐 Hora: $(time)

Este é um teste automatizado do sistema de briefing diário de IA.
Se você recebeu esta mensagem, o sistema está funcionando perfeitamente!

Próximas execuções:
• 08:00 BRT
• 12:00 BRT  
• 18:00 BRT
"""

    print("📝 Test message prepared")
    print(f"📏 Message length: {len(test_message)} characters")

    # Create sender and test connection
    sender = TelegramSender(token, chat_id)
    print("🔍 Testing connection...")

    if not sender.test_connection():
        print("❌ Connection test failed")
        return False

    print("✅ Connection successful")

    # Send test message
    print("📤 Sending test message...")
    success = sender.send_messages([test_message])

    if success:
        print("✅ Test message sent successfully!")
        print("📱 Check your Telegram for the test message")
        return True
    else:
        print("❌ Failed to send test message")
        return False

if __name__ == "__main__":
    success = test_telegram_sending()
    sys.exit(0 if success else 1)
