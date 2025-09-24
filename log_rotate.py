#!/usr/bin/env python3
"""
Sistema de Rotação de Logs - Telegram Daily Briefing
Gerencia tamanho e rotação automática de arquivos de log
"""

import os
import gzip
import logging
from pathlib import Path
from datetime import datetime, timedelta

class LogRotator:
    """Gerenciador de rotação de logs"""

    def __init__(self, log_file='briefing.log', max_size_mb=10, backup_count=5):
        self.log_file = Path(log_file)
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count

    def should_rotate(self) -> bool:
        """Verifica se o log deve ser rotacionado"""
        if not self.log_file.exists():
            return False

        size_mb = self.log_file.stat().st_size / (1024 * 1024)
        return size_mb >= self.max_size_mb

    def rotate_log(self):
        """Executa rotação do arquivo de log"""
        if not self.log_file.exists():
            return

        try:
            # Fecha handlers de logging se estiverem abertos
            for handler in logging.getLogger().handlers[:]:
                if hasattr(handler, 'baseFilename') and handler.baseFilename == str(self.log_file):
                    handler.close()
                    logging.getLogger().removeHandler(handler)

            # Remove arquivos antigos (mantém apenas backup_count)
            self._cleanup_old_logs()

            # Cria arquivo rotacionado
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            rotated_file = self.log_file.with_suffix(f'.{timestamp}.gz')

            # Comprime o arquivo atual
            with open(self.log_file, 'rb') as f_in:
                with gzip.open(rotated_file, 'wb') as f_out:
                    f_out.writelines(f_in)

            # Trunca o arquivo original
            with open(self.log_file, 'w') as f:
                f.write(f"[{datetime.now().isoformat()}] Log rotated - Previous content compressed to {rotated_file.name}\n")

            print(f"✅ Log rotated: {self.log_file.name} -> {rotated_file.name}")

        except Exception as e:
            print(f"❌ Error rotating log: {e}")

    def _cleanup_old_logs(self):
        """Remove arquivos de log antigos"""
        try:
            log_files = list(self.log_file.parent.glob(f"{self.log_file.stem}*.gz"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Mantém apenas os mais recentes
            if len(log_files) >= self.backup_count:
                files_to_remove = log_files[self.backup_count:]
                for old_file in files_to_remove:
                    old_file.unlink()
                    print(f"🗑️ Removed old log: {old_file.name}")

        except Exception as e:
            print(f"❌ Error cleaning old logs: {e}")

    def get_log_stats(self) -> dict:
        """Retorna estatísticas dos arquivos de log"""
        stats = {
            'main_log': {'exists': False, 'size_mb': 0, 'modified': None},
            'rotated_logs': []
        }

        # Estatísticas do log principal
        if self.log_file.exists():
            stat = self.log_file.stat()
            stats['main_log'] = {
                'exists': True,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }

        # Estatísticas dos logs rotacionados
        try:
            rotated_files = list(self.log_file.parent.glob(f"{self.log_file.stem}*.gz"))
            for rotated_file in rotated_files:
                stat = rotated_file.stat()
                stats['rotated_logs'].append({
                    'filename': rotated_file.name,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            # Ordena por data de modificação (mais recente primeiro)
            stats['rotated_logs'].sort(key=lambda x: x['modified'], reverse=True)

        except Exception as e:
            stats['error'] = str(e)

        return stats

    def force_rotate(self):
        """Força rotação do log (para testes)"""
        print("🔄 Forçando rotação do log...")
        self.rotate_log()

def check_and_rotate_logs():
    """Função utilitária para verificar e rotacionar logs automaticamente"""
    rotator = LogRotator()

    if rotator.should_rotate():
        print("📏 Log file is too large, rotating...")
        rotator.rotate_log()
        return True
    else:
        print("✅ Log file size is OK")
        return False

if __name__ == "__main__":
    import sys

    rotator = LogRotator()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--rotate':
            rotator.force_rotate()
        elif sys.argv[1] == '--stats':
            stats = rotator.get_log_stats()
            print("📊 Log Statistics:")
            print(f"  Main log: {stats['main_log']}")
            print(f"  Rotated logs: {len(stats['rotated_logs'])}")
            for log in stats['rotated_logs'][:3]:  # Mostra os 3 mais recentes
                print(f"    {log['filename']}: {log['size_mb']} MB")
        elif sys.argv[1] == '--check':
            check_and_rotate_logs()
    else:
        # Modo interativo
        print("🔧 Log Rotation Tool")
        print("=" * 30)
        print("Commands:")
        print("  --stats    Show log statistics")
        print("  --check    Check if rotation needed")
        print("  --rotate   Force log rotation")
        print()

        stats = rotator.get_log_stats()
        print("📊 Current Status:")
        main_log = stats['main_log']
        if main_log['exists']:
            print(f"  Main log: {main_log['size_mb']} MB")
            should_rotate = main_log['size_mb'] >= rotator.max_size_mb
            print(f"  Should rotate: {'Yes' if should_rotate else 'No'}")
        else:
            print("  Main log: Does not exist")

        print(f"  Rotated logs: {len(stats['rotated_logs'])}")
        print(f"  Max backups: {rotator.backup_count}")
