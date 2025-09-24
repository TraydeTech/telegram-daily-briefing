#!/usr/bin/env python3
"""
Script de Deploy Completo - Telegram Daily Briefing
Configura e testa todo o sistema para produção
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class DeployManager:
    """Gerenciador de deploy do sistema"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.required_files = [
            'src/main.py',
            'config/sources.json',
            'config/settings.json',
            '.github/workflows/daily-briefing.yml',
            'requirements.txt'
        ]

    def check_prerequisites(self):
        """Verifica pré-requisitos do sistema"""
        print("🔍 Verificando pré-requisitos...")

        issues = []

        # Verificar arquivos necessários
        for file_path in self.required_files:
            if not (self.project_root / file_path).exists():
                issues.append(f"Arquivo não encontrado: {file_path}")

        # Verificar se é um repositório git
        if not (self.project_root / '.git').exists():
            issues.append("Não é um repositório Git")

        # Verificar Python
        try:
            result = subprocess.run([sys.executable, '--version'],
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ Python: {result.stdout.strip()}")
        except:
            issues.append("Python não encontrado")

        # Verificar pip
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'],
                                  capture_output=True, text=True, check=True)
            print("  ✅ Pip encontrado")
        except:
            issues.append("Pip não encontrado")

        if issues:
            print("❌ Problemas encontrados:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        print("✅ Todos os pré-requisitos atendidos")
        return True

    def setup_environment(self):
        """Configura ambiente virtual e dependências"""
        print("\n🏗️ Configurando ambiente...")

        # Criar virtual environment se não existir
        venv_path = self.project_root / 'venv'
        if not venv_path.exists():
            print("  📦 Criando virtual environment...")
            try:
                subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
                print("  ✅ Virtual environment criado")
            except subprocess.CalledProcessError:
                print("  ❌ Erro ao criar virtual environment")
                return False
        else:
            print("  ✅ Virtual environment já existe")

        # Instalar dependências
        print("  📚 Instalando dependências...")
        pip_path = venv_path / 'bin' / 'pip'
        try:
            subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], check=True)
            print("  ✅ Dependências instaladas")
        except subprocess.CalledProcessError:
            print("  ❌ Erro ao instalar dependências")
            return False

        return True

    def test_system(self):
        """Testa o sistema completo"""
        print("\n🧪 Testando sistema...")

        venv_python = self.project_root / 'venv' / 'bin' / 'python'

        # Testar imports
        print("  🔍 Testando imports...")
        test_code = """
import sys
sys.path.insert(0, 'src')
try:
    from news_collector import NewsCollector
    from telegram_sender import TelegramSender
    from content_processor import ContentProcessor
    from message_formatter import MessageFormatter
    print('✅ Imports OK')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"""
        try:
            result = subprocess.run([str(venv_python), '-c', test_code],
                                  cwd=self.project_root, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Imports funcionando")
            else:
                print(f"  ❌ Erro nos imports: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ Erro ao testar imports: {e}")
            return False

        # Testar pipeline (sem enviar mensagens)
        print("  🔄 Testando pipeline...")
        test_pipeline_code = """
import os
import sys
sys.path.insert(0, 'src')

# Configurar variáveis de teste (sem tokens reais)
os.environ['DEBUG'] = 'true'
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'

from news_collector import NewsCollector
from content_processor import ContentProcessor
from message_formatter import MessageFormatter

try:
    # Carregar config
    import json
    from pathlib import Path
    config_dir = Path('config')
    with open(config_dir / 'settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    with open(config_dir / 'sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)
    config = {**settings, **sources}

    # Testar componentes
    collector = NewsCollector(config)
    news = collector.collect_all()
    print(f'📡 Coletadas {len(news)} notícias')

    processor = ContentProcessor('test_deploy_state.json')
    processed = processor.process(news)
    print(f'🎯 Processadas {len(processed)} notícias')

    formatter = MessageFormatter(config.get('formatting', {}))
    messages = formatter.format_messages(processed)
    print(f'📝 Formatadas {len(messages)} mensagens')

    print('✅ Pipeline testado com sucesso')

except Exception as e:
    print(f'❌ Erro no pipeline: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        try:
            result = subprocess.run([str(venv_python), '-c', test_pipeline_code],
                                  cwd=self.project_root, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ Pipeline funcionando")
                return True
            else:
                print(f"  ❌ Erro no pipeline: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ Erro ao testar pipeline: {e}")
            return False

    def configure_github(self):
        """Configura GitHub Actions e secrets"""
        print("\n🔐 Configurando GitHub...")

        try:
            # Executar script de configuração de secrets
            result = subprocess.run([sys.executable, 'setup_github_secrets.py'],
                                  cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                print("  ✅ GitHub configurado")
                return True
            else:
                print(f"  ❌ Erro na configuração GitHub: {result.stderr}")
                return False

        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return False

    def final_verification(self):
        """Verificação final do deploy"""
        print("\n🎯 Verificação final...")

        checks = [
            ("Arquivos de configuração", self._check_config_files()),
            ("Estrutura do projeto", self._check_project_structure()),
            ("Dependências", self._check_dependencies()),
            ("GitHub Actions", self._check_github_actions())
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def _check_config_files(self):
        """Verifica arquivos de configuração"""
        try:
            with open(self.project_root / 'config' / 'settings.json', 'r') as f:
                json.load(f)
            with open(self.project_root / 'config' / 'sources.json', 'r') as f:
                json.load(f)
            return True
        except:
            return False

    def _check_project_structure(self):
        """Verifica estrutura do projeto"""
        required_dirs = ['src', 'config', '.github/workflows']
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                return False
        return True

    def _check_dependencies(self):
        """Verifica se dependências estão instaladas"""
        try:
            venv_python = self.project_root / 'venv' / 'bin' / 'python'
            result = subprocess.run([str(venv_python), '-c', 'import requests, feedparser'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def _check_github_actions(self):
        """Verifica se GitHub Actions está configurado"""
        workflow_file = self.project_root / '.github' / 'workflows' / 'daily-briefing.yml'
        return workflow_file.exists()

    def run_deploy(self):
        """Executa deploy completo"""
        print("🚀 Iniciando Deploy - Telegram Daily Briefing")
        print("=" * 60)

        steps = [
            ("Verificar pré-requisitos", self.check_prerequisites),
            ("Configurar ambiente", self.setup_environment),
            ("Testar sistema", self.test_system),
            ("Configurar GitHub", self.configure_github),
            ("Verificação final", self.final_verification)
        ]

        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Deploy falhou em: {step_name}")
                return False

        print("\n" + "=" * 60)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("=" * 60)

        print("\n📋 RESUMO:")
        print("✅ Sistema configurado e testado")
        print("✅ Virtual environment criado")
        print("✅ Dependências instaladas")
        print("✅ Pipeline funcionando")
        print("✅ GitHub Actions configurado")

        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Faça commit e push das mudanças:")
        print("   git add .")
        print("   git commit -m 'Deploy: Sistema de briefing diário implementado'")
        print("   git push origin main")
        print()
        print("2. Verifique o primeiro workflow em:")
        print("   https://github.com/[seu-user]/[repo]/actions")
        print()
        print("3. Monitore as execuções automáticas:")
        print("   • 08:00 BRT (11:00 UTC)")
        print("   • 12:00 BRT (15:00 UTC)")
        print("   • 18:00 BRT (21:00 UTC)")

        return True

if __name__ == "__main__":
    deployer = DeployManager()
    success = deployer.run_deploy()
    sys.exit(0 if success else 1)
