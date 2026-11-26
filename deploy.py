import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime

from deploy_settings import (
    BEGET_EXCLUDE,
    BEGET_LOCAL_DIR,
    BEGET_REMOTE_DIR,
    BEGET_SFTP_HOST,
    BEGET_SFTP_PASSWORD,
    BEGET_SFTP_PORT,
    BEGET_SFTP_USER,
)

try:
    from deploy_settings import BEGET_SSH_KEY
except ImportError:
    BEGET_SSH_KEY = ''

DEFAULT_RSYNC_EXCLUDES = [
    '__pycache__/',
    '*.pyc',
    '*.pyo',
    '.pytest_cache/',
    '.mypy_cache/',
    'venv/',
    '.git/',
]


def _normalize_exclude(path, local_dir):
    local = local_dir.replace('\\', '/').rstrip('/')
    item = str(path or '').replace('\\', '/')
    for prefix in (f'{local}/', 'backend/'):
        if item.startswith(prefix):
            item = item[len(prefix):]
            break
    return item.strip('/')


def build_excludes(local_dir):
    seen = set()
    result = []
    for pattern in DEFAULT_RSYNC_EXCLUDES + [_normalize_exclude(item, local_dir) for item in BEGET_EXCLUDE]:
        pattern = (pattern or '').strip()
        if not pattern or pattern in seen:
            continue
        seen.add(pattern)
        result.append(pattern)
    return result


def build_ssh_argv():
    argv = [
        'ssh',
        '-p', str(BEGET_SFTP_PORT),
        '-o', 'BatchMode=no',
        '-o', 'StrictHostKeyChecking=accept-new',
    ]
    key_path = (BEGET_SSH_KEY or '').strip()
    if key_path:
        argv.extend(['-i', os.path.expanduser(key_path)])
    return argv


def remote_target():
    return f'{BEGET_SFTP_USER}@{BEGET_SFTP_HOST}:{BEGET_REMOTE_DIR.rstrip("/")}/'


def run_command(cmd, *, env=None, rsync=False):
    print('→', ' '.join(shlex.quote(part) for part in cmd))
    completed = subprocess.run(cmd, env=env)
    if completed.returncode != 0:
        hint = ''
        if rsync and completed.returncode == 23:
            hint = (
                '\nrsync 23: часть файлов не записана (права на хостинге, chmod/utime). '
                'Проверьте строки rsync выше. Часто помогает exclude для db.sqlite3 и public_html/media/.'
            )
        raise RuntimeError(f'Команда завершилась с кодом {completed.returncode}{hint}')


class Deploy:
    def sync_with_rsync(self):
        local_dir = os.path.abspath(BEGET_LOCAL_DIR.rstrip('/'))
        if not os.path.isdir(local_dir):
            raise FileNotFoundError(f'Локальная папка не найдена: {local_dir}')

        if not shutil.which('rsync'):
            raise RuntimeError('Установите rsync (sudo apt install rsync)')

        start_time = datetime.now()
        print(f'Синхронизация {local_dir}/ → {remote_target()}')

        ssh_argv = build_ssh_argv()
        # Без -a: на Beget часто падает chmod/chown/utime → код 23
        rsync_cmd = [
            'rsync',
            '-rlvz',
            '--no-perms',
            '--no-owner',
            '--no-group',
            '--omit-dir-times',
            '--no-specials',
            '--info=stats2,progress2',
        ]
        for pattern in build_excludes(BEGET_LOCAL_DIR):
            rsync_cmd.extend(['--exclude', pattern])

        rsync_cmd.extend([
            '-e', ' '.join(shlex.quote(part) for part in ssh_argv),
            f'{local_dir}/',
            remote_target(),
        ])

        env = os.environ.copy()
        password = (BEGET_SFTP_PASSWORD or '').strip()
        key_path = (BEGET_SSH_KEY or '').strip()
        if password and not key_path:
            if not shutil.which('sshpass'):
                raise RuntimeError(
                    'Задан пароль, но нет sshpass. Установите: sudo apt install sshpass '
                    'или укажите BEGET_SSH_KEY в deploy_settings.py',
                )
            rsync_cmd = ['sshpass', '-p', password, *rsync_cmd]

        run_command(rsync_cmd, env=env, rsync=True)

        print('Перезагружаю Beget (tmp/restart.txt)')
        restart_remote = (
            f'mkdir -p {shlex.quote(BEGET_REMOTE_DIR.rstrip("/") + "/tmp")} && '
            f'printf %s "$(date -Iseconds)" > {shlex.quote(BEGET_REMOTE_DIR.rstrip("/") + "/tmp/restart.txt")}'
        )
        ssh_cmd = list(ssh_argv)
        ssh_cmd.append(f'{BEGET_SFTP_USER}@{BEGET_SFTP_HOST}')
        ssh_cmd.append(restart_remote)
        if password and not key_path:
            ssh_cmd = ['sshpass', '-p', password, *ssh_cmd]
        run_command(ssh_cmd, env=env)

        print(f'\nГотово за {datetime.now() - start_time}')


if __name__ == '__main__':
    answer = input('Запустить деплой y/N ?')
    if answer not in ('y', 'Y'):
        print('Отмена')
        sys.exit(0)
    try:
        Deploy().sync_with_rsync()
    except Exception as exc:
        print(f'{datetime.now()} Ошибка: {exc}')
        sys.exit(1)
