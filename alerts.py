#!/usr/bin/env python3
"""
Sistema de Alertas - Telegram Daily Briefing
Notificações automáticas para falhas e problemas do sistema
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path

class AlertSystem:
    """Sistema de alertas e notificações"""

    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.alerts_file = Path('alerts_history.json')
        self._load_alerts_history()

    def _load_alerts_history(self):
        """Carrega histórico de alertas"""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    self.alerts_history = json.load(f)
            else:
                self.alerts_history = []
        except Exception as e:
            logging.error(f"Erro ao carregar histórico de alertas: {e}")
            self.alerts_history = []

    def _save_alerts_history(self):
        """Salva histórico de alertas"""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts_history[-100:], f, indent=2, ensure_ascii=False)  # Últimos 100 alertas
        except Exception as e:
            logging.error(f"Erro ao salvar histórico de alertas: {e}")

    def send_alert(self, alert_type: str, message: str, severity: str = 'warning'):
        """Envia alerta via Telegram"""

        # Cria entrada no histórico
        alert_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity,
            'sent': False
        }

        # Verifica se já foi enviado recentemente (evita spam)
        if self._should_send_alert(alert_entry):
            success = self._send_telegram_alert(alert_type, message, severity)
            alert_entry['sent'] = success

            if success:
                logging.info(f"✅ Alerta enviado: {alert_type} - {message}")
            else:
                logging.error(f"❌ Falha ao enviar alerta: {alert_type}")

        # Adiciona ao histórico
        self.alerts_history.append(alert_entry)
        self._save_alerts_history()

    def _should_send_alert(self, alert_entry: dict) -> bool:
        """Verifica se o alerta deve ser enviado (evita duplicatas)"""

        # Verifica alertas similares nas últimas 2 horas
        cutoff_time = datetime.now() - timedelta(hours=2)

        for alert in self.alerts_history:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if (alert_time > cutoff_time and
                alert['type'] == alert_entry['type'] and
                alert['severity'] == alert_entry['severity'] and
                alert.get('sent', False)):
                return False  # Já foi enviado recentemente

        return True

    def _send_telegram_alert(self, alert_type: str, message: str, severity: str) -> bool:
        """Envia alerta via Telegram"""

        if not self.telegram_token or not self.telegram_chat_id:
            logging.error("Telegram credentials não configuradas para alertas")
            return False

        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }

        emoji = emoji_map.get(severity, '⚠️')

        alert_message = f"""{emoji} **ALERTA DO SISTEMA**

**Tipo:** {alert_type.upper()}
**Severidade:** {severity.upper()}
**Horário:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

**Mensagem:**
{message}

**Sistema:** Telegram Daily Briefing
"""

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': alert_message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get('ok', False)
            else:
                logging.error(f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logging.error(f"Erro ao enviar alerta Telegram: {e}")
            return False

    def check_system_health(self):
        """Verifica saúde geral do sistema e envia alertas se necessário"""

        issues = []

        # Verifica se arquivo de estado existe e foi atualizado recentemente
        state_file = Path('news_state.json')
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    last_update = state.get('last_updated')
                    if last_update:
                        last_update_dt = datetime.fromisoformat(last_update)
                        hours_since_update = (datetime.now() - last_update_dt).total_seconds() / 3600

                        if hours_since_update > 6:  # Mais de 6 horas sem execução
                            issues.append(f"Sistema não executou há {hours_since_update:.1f} horas")
            except Exception as e:
                issues.append(f"Erro ao ler arquivo de estado: {e}")
        else:
            issues.append("Arquivo de estado não encontrado")

        # Verifica tamanho do log
        log_file = Path('briefing.log')
        if log_file.exists():
            size_mb = log_file.stat().st_size / (1024 * 1024)
            if size_mb > 50:  # Log muito grande
                issues.append(f"Arquivo de log muito grande: {size_mb:.1f} MB")

        # Verifica conectividade de rede (teste básico)
        try:
            requests.get('https://httpbin.org/status/200', timeout=10)
        except:
            issues.append("Problemas de conectividade de rede detectados")

        # Envia alertas para problemas encontrados
        for issue in issues:
            self.send_alert('system_health', issue, 'warning')

        if not issues:
            # Alerta positivo se sistema saudável (uma vez por dia)
            self.send_alert('system_health', 'Sistema operando normalmente', 'info')

        return issues

    def alert_execution_failure(self, error_message: str):
        """Alerta de falha na execução"""
        self.send_alert('execution_failure', error_message, 'error')

    def alert_performance_issue(self, issue: str):
        """Alerta de problema de performance"""
        self.send_alert('performance', issue, 'warning')

    def alert_source_failure(self, source_name: str, error: str):
        """Alerta de falha em fonte de notícias"""
        message = f"Fonte '{source_name}' falhou: {error}"
        self.send_alert('source_failure', message, 'warning')

    def get_alerts_summary(self) -> dict:
        """Retorna resumo dos alertas recentes"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        alerts_24h = [a for a in self.alerts_history
                     if datetime.fromisoformat(a['timestamp']) > last_24h]
        alerts_7d = [a for a in self.alerts_history
                    if datetime.fromisoformat(a['timestamp']) > last_7d]

        return {
            'total_alerts': len(self.alerts_history),
            'alerts_24h': len(alerts_24h),
            'alerts_7d': len(alerts_7d),
            'sent_24h': len([a for a in alerts_24h if a.get('sent', False)]),
            'by_severity': {
                'info': len([a for a in self.alerts_history if a['severity'] == 'info']),
                'warning': len([a for a in self.alerts_history if a['severity'] == 'warning']),
                'error': len([a for a in self.alerts_history if a['severity'] == 'error']),
                'critical': len([a for a in self.alerts_history if a['severity'] == 'critical'])
            }
        }

# Função global para facilitar uso
_alert_system = None

def get_alert_system():
    """Retorna instância singleton do sistema de alertas"""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system

def send_alert(alert_type: str, message: str, severity: str = 'warning'):
    """Função global para enviar alertas"""
    get_alert_system().send_alert(alert_type, message, severity)

if __name__ == "__main__":
    # Teste do sistema de alertas
    alert_system = AlertSystem()

    print("🧪 Testando sistema de alertas...")

    # Simula alguns alertas
    alert_system.send_alert('test', 'Este é um alerta de teste', 'info')
    alert_system.send_alert('system_health', 'Sistema operando normalmente', 'info')

    # Verifica saúde do sistema
    issues = alert_system.check_system_health()
    print(f"Problemas detectados: {len(issues)}")

    # Mostra resumo
    summary = alert_system.get_alerts_summary()
    print(f"Resumo de alertas: {summary}")

    print("✅ Teste concluído")
