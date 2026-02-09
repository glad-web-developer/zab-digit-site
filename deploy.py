import os
import paramiko
from datetime import datetime

from deploy_settings import BEGET_EXCLUDE, BEGET_LOCAL_DIR, BEGET_SFTP_HOST, BEGET_SFTP_PORT, BEGET_SFTP_USER, \
    BEGET_SFTP_PASSWORD, BEGET_REMOTE_DIR


class Deploy():
    count = 0
    i = 1

    def count_file(self, local_path):
        for item in os.listdir(local_path):
            if item == '__pycache__':
                continue
            local_item = os.path.join(local_path, item)
            if local_item in BEGET_EXCLUDE:
                continue
            if os.path.isdir(local_item):
                self.count_file(local_item)
            else:
                self.count += 1


    def reload_beget(self, sftp):
        with sftp.file(BEGET_REMOTE_DIR+'/tmp/restart.txt', 'w') as remote_file:
            remote_file.write(str(datetime.now()))



    def sync_with_sftp(self):
        print('Начинаю считать файлы')
        start_time = datetime.now()
        self.count_file(BEGET_LOCAL_DIR)

        # Создаем SSH-клиент
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Подключаемся (с паролем)
            ssh.connect(BEGET_SFTP_HOST, port=BEGET_SFTP_PORT,
                        username=BEGET_SFTP_USER, password=BEGET_SFTP_PASSWORD)

            sftp = ssh.open_sftp()

            # Рекурсивная синхронизация
            self.sync_directory(sftp, BEGET_LOCAL_DIR, BEGET_REMOTE_DIR)
            print('Перезагружаю Beget')
            self.reload_beget(sftp)

            print(f"\nСинхронизация завершена успешно в {datetime.now()}. Прошло {datetime.now() - start_time}")

        except Exception as e:
            print(f"{datetime.now()} Ошибка: {str(e)}")
        finally:
            if 'sftp' in locals():
                sftp.close()
            if 'ssh' in locals():
                ssh.close()


    def sync_directory(self, sftp, local_path, remote_path):
        """Рекурсивная синхронизация папки"""
        # Создаем папку на сервере, если её нет
        try:
            sftp.stat(remote_path)
        except IOError:
            sftp.mkdir(remote_path)
            print(f"{datetime.now()} Создана папка: {remote_path}")

        # Получаем список файлов на сервере
        remote_files = set()
        for item in sftp.listdir_attr(remote_path):
            remote_files.add(item.filename)

        # Обрабатываем локальные файлы
        for item in os.listdir(local_path):
            local_item = os.path.join(local_path, item)
            if item == '__pycache__':
                continue
            if local_item in BEGET_EXCLUDE:
                print(f'{datetime.now()} Исключение {local_item}')
                continue

            remote_item = f"{remote_path}/{item}"

            if os.path.isdir(local_item):
                # Рекурсивно обрабатываем подпапки
                self.sync_directory(sftp, local_item, remote_item)
            else:
                # Проверяем, нужно ли обновлять файл
                upload = False
                if item not in remote_files:
                    upload = True
                    print(f"[{self.i}/{self.count}] [{datetime.now()}] Новый файл: {remote_item}")
                else:
                    # Сравниваем время модификации
                    remote_attr = sftp.stat(remote_item)
                    local_mtime = os.path.getmtime(local_item)
                    if local_mtime > remote_attr.st_mtime:
                        upload = True
                        print(f"[{self.i}/{self.count}] [{datetime.now()}] Обновлён файл: {remote_item}")
                    else:
                        print(f"[{self.i}/{self.count}] [{datetime.now()}] Пропущен файл: {remote_item}")

                self.i += 1

                if upload:
                    sftp.put(local_item, remote_item)


if __name__ == '__main__':
    tmp = input("Запустить деплой y/N ?")
    if tmp == 'y' or tmp == 'Y':
        deploy = Deploy()
        deploy.sync_with_sftp()
    else:
        print('Отмена')
