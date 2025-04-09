import os
import django
from django.core.management import call_command

def run_django_server():
    # 設定 Django 的 settings 模組路徑
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_service.web_service.settings')
    # 初始化 Django
    django.setup()

    # 如有需要，可以在這裡先 call_command("migrate")、"collectstatic" 等
    # call_command("migrate")

    # 直接呼叫 runserver
    call_command("runserver", "127.0.0.1:8000")

if __name__ == "__main__":
    run_django_server()