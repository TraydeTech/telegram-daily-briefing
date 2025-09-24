#!/usr/bin/env python3
"""
Script de Manutenção - Telegram Daily Briefing
Executa limpeza, otimização e verificações de saúde do sistema
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Importa módulos locais
sys.path.insert(0, str(Path(__file__).parent))

def cleanup_temp_files():
    """Limpa arquivos temporários"""
    print("🧹 Limpando arquivos temporários...")

    temp_files = [
        '*.pyc',
        '__pycache__',
        '*.tmp',
        '*.bak',
        'test_*.json',
        'debug_*.json'
    ]

    cleaned = 0
    for pattern in temp_files:
        if '*' in pattern:
            # Remove arquivos com padrão
            for file_path in Path('.').rglob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        print(f"  🗑️ Removed: {file_path}")
                        cleaned += 1
                except Exception as e:
                    print(f"  ❌ Error removing {file_path}: {e}")
        else:
            # Remove diretório específico
            for dir_path in Path('.').rglob(pattern):
                try:
                    if dir_path.is_dir():
                        shutil.rmtree(dir_path)
                        print(f"  🗑️ Removed dir: {dir_path}")
                        cleaned += 1
                except Exception as e:
                    print(f"  ❌ Error removing {dir_path}: {e}")

    print(f"✅ Limpeza concluída: {cleaned} arquivos/diretórios removidos")
    return cleaned

def optimize_state_file():
    """Otimiza arquivo de estado removendo entradas antigas"""
    print("🔧 Otimizando arquivo de estado...")

    state_file = Path('news_state.json')
    if not state_file.exists():
        print("  ⚠️ Arquivo de estado não encontrado")
        return False

    try:
        import json
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)

        original_count = len(state.get('processed_urls', []))
        original_size = state_file.stat().st_size

        # Remove URLs antigas (mais de 30 dias)
        cutoff_date = datetime.now() - timedelta(days=30)
        filtered_urls = []

        for url in state.get('processed_urls', []):
            # Como não temos data por URL, mantemos apenas as mais recentes
            # Implementação simplificada: mantém apenas 50% das URLs mais recentes
            pass

        # Por enquanto, apenas compacta removendo duplicatas
        unique_urls = list(set(state.get('processed_urls', [])))

        if len(unique_urls) < original_count:
            state['processed_urls'] = unique_urls
            state['last_optimized'] = datetime.now().isoformat()
            state['optimization_info'] = f"Removed {original_count - len(unique_urls)} duplicate URLs"

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            new_size = state_file.stat().st_size
            savings = original_size - new_size

            print(f"✅ Otimização concluída:")
            print(f"   URLs originais: {original_count}")
            print(f"   URLs após limpeza: {len(unique_urls)}")
            print(f"   Economia de espaço: {savings} bytes")
            return True
        else:
            print("  ℹ️ Arquivo de estado já otimizado")
            return True

    except Exception as e:
        print(f"  ❌ Erro na otimização: {e}")
        return False

def check_system_integrity():
    """Verifica integridade do sistema"""
    print("🔍 Verificando integridade do sistema...")

    issues = []

    # Verifica arquivos essenciais
    essential_files = [
        'src/main.py',
        'config/sources.json',
        'config/settings.json',
        'requirements.txt'
    ]

    for file_path in essential_files:
        if not Path(file_path).exists():
            issues.append(f"Arquivo essencial não encontrado: {file_path}")

    # Verifica se pode importar módulos principais
    try:
        sys.path.insert(0, 'src')
        import news_collector
        import telegram_sender
        import content_processor
        import message_formatter
        print("  ✅ Módulos principais importáveis")
    except ImportError as e:
        issues.append(f"Erro de importação: {e}")

    # Verifica configurações JSON
    try:
        import json
        with open('config/sources.json', 'r') as f:
            json.load(f)
        with open('config/settings.json', 'r') as f:
            json.load(f)
        print("  ✅ Arquivos de configuração válidos")
    except Exception as e:
        issues.append(f"Erro na configuração: {e}")

    if issues:
        print("❌ Problemas de integridade encontrados:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Sistema íntegro")
        return True

def backup_important_files():
    """Faz backup de arquivos importantes"""
    print("💾 Criando backup de arquivos importantes...")

    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}'
    backup_path = backup_dir / backup_name
    backup_path.mkdir()

    important_files = [
        'news_state.json',
        'briefing.log',
        'config/',
        'src/'
    ]

    backed_up = 0
    for file_path in important_files:
        src_path = Path(file_path)
        if src_path.exists():
            dst_path = backup_path / src_path.name
            try:
                if src_path.is_file():
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                backed_up += 1
                print(f"  📁 Backed up: {file_path}")
            except Exception as e:
                print(f"  ❌ Error backing up {file_path}: {e}")

    # Compacta o backup
    try:
        shutil.make_archive(str(backup_path), 'zip', str(backup_path))
        shutil.rmtree(backup_path)  # Remove diretório após compactar
        print(f"✅ Backup criado: {backup_name}.zip")
    except Exception as e:
        print(f"❌ Erro ao compactar backup: {e}")

    # Limpa backups antigos (mantém apenas os 5 mais recentes)
    try:
        backup_files = list(backup_dir.glob('backup_*.zip'))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if len(backup_files) > 5:
            for old_backup in backup_files[5:]:
                old_backup.unlink()
                print(f"🗑️ Removed old backup: {old_backup.name}")
    except Exception as e:
        print(f"❌ Error cleaning old backups: {e}")

    return backed_up

def run_full_maintenance():
    """Executa manutenção completa do sistema"""
    print("🔧 INICIANDO MANUTENÇÃO COMPLETA")
    print("=" * 50)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

    maintenance_results = {}

    # 1. Verificação de integridade
    print("1️⃣ Verificação de Integridade")
    maintenance_results['integrity'] = check_system_integrity()
    print()

    # 2. Limpeza de arquivos temporários
    print("2️⃣ Limpeza de Arquivos Temporários")
    maintenance_results['cleanup'] = cleanup_temp_files()
    print()

    # 3. Otimização do arquivo de estado
    print("3️⃣ Otimização do Estado")
    maintenance_results['optimization'] = optimize_state_file()
    print()

    # 4. Backup de arquivos importantes
    print("4️⃣ Backup do Sistema")
    maintenance_results['backup'] = backup_important_files()
    print()

    # 5. Verificação final
    print("5️⃣ Verificação Final")
    final_integrity = check_system_integrity()
    maintenance_results['final_integrity'] = final_integrity
    print()

    # Resumo
    print("📊 RESUMO DA MANUTENÇÃO")
    print("=" * 30)

    success_count = 0
    total_tasks = len(maintenance_results)

    for task, result in maintenance_results.items():
        status = "✅" if result else "❌"
        print(f"{status} {task}: {result}")
        if result:
            success_count += 1

    print()
    print(f"🎯 Taxa de Sucesso: {success_count}/{total_tasks} tarefas concluídas")

    if success_count == total_tasks:
        print("🏆 Manutenção concluída com SUCESSO!")
        return True
    else:
        print("⚠️ Manutenção concluída com alguns problemas")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == '--cleanup':
            cleanup_temp_files()
        elif command == '--optimize':
            optimize_state_file()
        elif command == '--backup':
            backup_important_files()
        elif command == '--check':
            check_system_integrity()
        else:
            print("Comando não reconhecido. Use --cleanup, --optimize, --backup, --check ou execute sem argumentos para manutenção completa")
    else:
        # Manutenção completa
        success = run_full_maintenance()
        sys.exit(0 if success else 1)
