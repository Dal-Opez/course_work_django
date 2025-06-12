from django.core.management.base import BaseCommand
from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Запускает все активные рассылки'

    def handle(self, *args, **options):
        # Получаем все активные рассылки
        mailings = Mailing.objects.filter(is_active=True)

        self.stdout.write(f"Найдено {mailings.count()} активных рассылок")

        for mailing in mailings:
            self.stdout.write(f"Отправка рассылки ID {mailing.id}...")
            send_mailing(mailing)
            self.stdout.write(f"Рассылка ID {mailing.id} отправлена")

        self.stdout.write(self.style.SUCCESS("Все рассылки обработаны"))