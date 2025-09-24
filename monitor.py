#!/usr/bin/env python3
"""
Monitor de Sistema - Telegram Daily Briefing
Dashboard para acompanhar performance e status do sistema
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

class SystemMonitor:
    """Monitor completo do sistema de briefing"""

    def __init__(self):
        self.project_root = Path(__file__).parent

    def get_system_status(self):
        """Obtém status completo do sistema"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'performance': {},
            'sources': {},
            'alerts': []
        }

        # Status dos componentes
        status['components'] = self._check_components()

        # Performance
        status['performance'] = self._check_performance()

        # Fontes ativas
        status['sources'] = self._check_sources()

        # Alertas
        status['alerts'] = self._check_alerts()

        return status

    def _check_components(self):
        """Verifica status dos componentes principais"""
        components = {}

        # Arquivos essenciais
        essential_files = [
            'src/main.py',
            'config/sources.json',
            'config/settings.json',
            '.github/workflows/daily-briefing.yml'
        ]

        components['files'] = {}
        for file_path in essential_files:
            exists = (self.project_root / file_path).exists()
            components['files'][file_path] = '✅' if exists else '❌'

        # Dependências
        try:
            result = subprocess.run([sys.executable, '-c', 'import requests, feedparser, telegram'],
                                  capture_output=True, text=True, timeout=10)
            components['dependencies'] = '✅ OK' if result.returncode == 0 else '❌ Missing'
        except:
            components['dependencies'] = '❌ Error'

        # Virtual environment
        venv_exists = (self.project_root / 'venv').exists()
        components['venv'] = '✅ Active' if venv_exists else '❌ Missing'

        return components

    def _check_performance(self):
        """Verifica métricas de performance"""
        performance = {}

        # Estado de processamento
        try:
            with open(self.project_root / 'news_state.json', 'r') as f:
                state = json.load(f)
                performance['processed_urls'] = len(state.get('processed_urls', []))
                performance['last_updated'] = state.get('last_updated', 'Never')
        except:
            performance['processed_urls'] = 0
            performance['last_updated'] = 'Error'

        # Logs recentes
        log_file = self.project_root / 'briefing.log'
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # Últimas 10 linhas
                    performance['recent_logs'] = len(lines)
                    # Verificar se há erros recentes
                    errors = [line for line in lines if 'ERROR' in line or '❌' in line]
                    performance['recent_errors'] = len(errors)
            except:
                performance['recent_logs'] = 'Error reading'
                performance['recent_errors'] = 'Unknown'

        return performance

    def _check_sources(self):
        """Verifica status das fontes de notícias"""
        sources = {}

        try:
            with open(self.project_root / 'config/sources.json', 'r') as f:
                config = json.load(f)

            # RSS feeds
            rss_feeds = config['sources']['rss_feeds']
            sources['rss_feeds'] = {
                'total': len(rss_feeds),
                'active': len([f for f in rss_feeds.values() if f.startswith('http')])
            }

            # Web scraping
            web_sites = config['sources']['web_scraping']['sites']
            sources['web_scraping'] = {
                'total': len(web_sites),
                'enabled': len([s for s in web_sites if s.get('enabled', False)])
            }

        except Exception as e:
            sources['error'] = str(e)

        return sources

    def _check_alerts(self):
        """Verifica alertas e problemas do sistema"""
        alerts = []

        # Verificar se estado está sendo atualizado
        try:
            with open(self.project_root / 'news_state.json', 'r') as f:
                state = json.load(f)
                last_update = state.get('last_updated')
                if last_update:
                    last_update_dt = datetime.fromisoformat(last_update)
                    hours_since_update = (datetime.now() - last_update_dt).total_seconds() / 3600

                    if hours_since_update > 25:  # Mais de 25 horas sem atualização
                        alerts.append(f"⚠️ Sistema não executou há {hours_since_update:.1f} horas")
        except:
            alerts.append("❌ Erro ao ler arquivo de estado")

        # Verificar tamanho do estado (muitas URLs acumuladas)
        try:
            with open(self.project_root / 'news_state.json', 'r') as f:
                state = json.load(f)
                url_count = len(state.get('processed_urls', []))
                if url_count > 1000:  # Muitas URLs armazenadas
                    alerts.append(f"⚠️ Arquivo de estado grande: {url_count} URLs processadas")
        except:
            pass

        return alerts

    def display_dashboard(self):
        """Exibe dashboard completo do sistema"""
        status = self.get_system_status()

        print("📊 TELEGRAM DAILY BRIEFING - DASHBOARD")
        print("=" * 60)
        print(f"📅 Última verificação: {status['timestamp'][:19]}")
        print()

        # Componentes
        print("🔧 COMPONENTES:")
        for component, sub_components in status['components'].items():
            print(f"  {component.upper()}:")
            if isinstance(sub_components, dict):
                for sub_comp, status_val in sub_components.items():
                    print(f"    {sub_comp}: {status_val}")
            else:
                print(f"    Status: {sub_components}")
        print()

        # Performance
        print("⚡ PERFORMANCE:")
        perf = status['performance']
        print(f"  URLs processadas: {perf.get('processed_urls', 'N/A')}")
        print(f"  Última execução: {perf.get('last_updated', 'N/A')[:19] if perf.get('last_updated') != 'Never' else 'Nunca'}")
        print(f"  Logs recentes: {perf.get('recent_logs', 'N/A')}")
        print(f"  Erros recentes: {perf.get('recent_errors', 'N/A')}")
        print()

        # Fontes
        print("📡 FONTES ATIVAS:")
        sources = status['sources']
        if 'error' not in sources:
            print(f"  RSS Feeds: {sources.get('rss_feeds', {}).get('active', 0)}/{sources.get('rss_feeds', {}).get('total', 0)} ativos")
            print(f"  Web Scraping: {sources.get('web_scraping', {}).get('enabled', 0)}/{sources.get('web_scraping', {}).get('total', 0)} habilitados")
        else:
            print(f"  ❌ Erro: {sources['error']}")
        print()

        # Alertas
        alerts = status['alerts']
        if alerts:
            print("🚨 ALERTAS:")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print("✅ NENHUM ALERTA ATIVO")
        print()

        # Status geral
        print("🎯 STATUS GERAL:")
        has_errors = any('❌' in str(comp) for comp in status['components'].values())
        has_alerts = len(alerts) > 0

        if has_errors:
            print("  🔴 SISTEMA COM PROBLEMAS - Verificar componentes acima")
        elif has_alerts:
            print("  🟡 SISTEMA COM ALERTAS - Revisar avisos acima")
        else:
            print("  🟢 SISTEMA OPERANDO NORMALMENTE")
        print()

        # Próximas execuções
        print("⏰ PRÓXIMAS EXECUÇÕES:")
        now = datetime.now()
        executions = [
            ("08:00 BRT", now.replace(hour=8, minute=0, second=0, microsecond=0)),
            ("12:00 BRT", now.replace(hour=12, minute=0, second=0, microsecond=0)),
            ("18:00 BRT", now.replace(hour=18, minute=0, second=0, microsecond=0))
        ]

        for label, exec_time in executions:
            if exec_time > now:
                hours_until = (exec_time - now).total_seconds() / 3600
                print(f"  {label}: {exec_time.strftime('%H:%M')} ({hours_until:.1f}h)")
            else:
                next_exec = exec_time + timedelta(days=1)
                hours_until = (next_exec - now).total_seconds() / 3600
                print(f"  {label}: Amanhã {exec_time.strftime('%H:%M')} ({hours_until:.1f}h)")

    def export_report(self, filename=None):
        """Exporta relatório completo em JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'system_report_{timestamp}.json'

        status = self.get_system_status()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

        print(f"📄 Relatório exportado: {filename}")
        return filename

if __name__ == "__main__":
    monitor = SystemMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == '--export':
        monitor.export_report()
    else:
        monitor.display_dashboard()
