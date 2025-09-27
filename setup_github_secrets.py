#!/usr/bin/env python3
"""
Script para configurar secrets do GitHub Actions
Executar uma vez para configurar o repositório
"""

import os
import subprocess
import sys

def setup_github_secrets():
    """Configura os secrets necessários no GitHub"""

    print("🔐 Configuração de Secrets do GitHub Actions")
    print("=" * 50)

    # Verificar se estamos em um repositório git
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True, text=True, check=True)
        repo_url = result.stdout.strip()
        print(f"📂 Repositório: {repo_url}")
    except subprocess.CalledProcessError:
        print("❌ Erro: Não estamos em um repositório Git válido")
        return False

    # Verificar se gh CLI está instalado
    try:
        result = subprocess.run(['gh', '--version'],
                              capture_output=True, text=True, check=True)
        print("✅ GitHub CLI encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI não encontrado")
        print("💡 Instale o GitHub CLI: https://cli.github.com/")
        print("   brew install gh  # macOS")
        print("   Ou baixe de: https://github.com/cli/cli/releases")
        return False

    # Verificar se usuário está logado no GitHub
    try:
        result = subprocess.run(['gh', 'auth', 'status'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Autenticado no GitHub")
        else:
            print("❌ Não autenticado no GitHub")
            print("💡 Execute: gh auth login")
            return False
    except subprocess.CalledProcessError:
        print("❌ Erro ao verificar autenticação")
        return False

    # Configurar secrets
    # Ler de env ou solicitar ao usuário (nunca versionar tokens reais)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or input('Informe TELEGRAM_BOT_TOKEN: ').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID') or input('Informe TELEGRAM_CHAT_ID: ').strip()

    secrets = {
        'TELEGRAM_BOT_TOKEN': {
            'description': 'Token do bot Telegram (@TraydeNewsbot)',
            'value': bot_token
        },
        'TELEGRAM_CHAT_ID': {
            'description': 'ID do chat para envio das mensagens',
            'value': chat_id
        }
    }

    print("\n🔑 Configurando secrets...")

    for secret_name, secret_info in secrets.items():
        try:
            print(f"  📝 Configurando {secret_name}...")

            # Usar echo para passar o valor para gh secret set
            cmd = f'echo -n "{secret_info["value"]}" | gh secret set {secret_name}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"    ✅ {secret_name} configurado")
            else:
                print(f"    ❌ Erro ao configurar {secret_name}: {result.stderr}")

        except Exception as e:
            print(f"    ❌ Erro: {e}")

    print("\n✅ Configuração concluída!")
    print("\n📋 Próximos passos:")
    print("1. Verifique se os secrets foram criados em: https://github.com/[seu-user]/[repo]/settings/secrets/actions")
    print("2. Execute um teste manual do workflow")
    print("3. Verifique os logs da execução")

    return True

def test_workflow():
    """Testa o workflow manualmente"""

    print("\n🧪 Testando workflow...")

    try:
        # Executar workflow dispatch
        result = subprocess.run(['gh', 'workflow', 'run', 'daily-briefing.yml'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Workflow iniciado com sucesso")
            print("📊 Acompanhe em: https://github.com/[seu-user]/[repo]/actions")
        else:
            print(f"❌ Erro ao iniciar workflow: {result.stderr}")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_workflow()
    else:
        success = setup_github_secrets()
        if success:
            test_choice = input("\n🔍 Deseja testar o workflow agora? (y/N): ").lower().strip()
            if test_choice == 'y':
                test_workflow()
