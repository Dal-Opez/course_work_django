from django.db import models
from users.models import User

# Create your models here.
class Client(models.Model):
    email = models.EmailField(max_length=100, verbose_name="Адрес почты")
    full_name = models.CharField(max_length=150, verbose_name="Полное имя")
    comment = models.TextField(verbose_name="Комментарии", null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    def __str__(self):
        return f"{self.full_name} {self.email}"

    class Meta:
        unique_together = ('email', 'owner')  # Уникальная пара email+владелец
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["full_name"]


class Message(models.Model):
    title = models.CharField(max_length=150, verbose_name="Тема письма")
    letter_body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Кем добавлено письмо")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "письмо"
        verbose_name_plural = "письма"
        ordering = ["title"]
        permissions = [
            ("view_all_mailings", "Can view all mailings"),
        ]



class Mailing(models.Model):
    CREATED = 'created'
    STARTED = 'started'
    FINISHED = 'finished'
    STATUS_CHOICES = [
        (CREATED, "Создана"),
        (STARTED, "Запущена"),
        (FINISHED, "Завершена"),
    ]

    start_sending = models.DateTimeField(verbose_name='Дата и время первой отправки', null=True, blank=True)
    end_sending = models.DateTimeField(verbose_name="Дата и время окончания отправки", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=CREATED, verbose_name="Статус рассылки")
    is_active = models.BooleanField(default=True, verbose_name="активна", null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="mailings", null=True, blank=True)
    client = models.ManyToManyField(Client, verbose_name="Клиент")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кем добавлена рассылка")

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = "рассылка"
        verbose_name_plural = "рассылки"
        ordering = ["start_sending"]


class MailingAttempt(models.Model):
    SUCCESS = 'Успешно'
    FAIL = 'Не успешно'

    ATTEMPT_STATUS_CHOICES = [
        (SUCCESS, 'Успешно'),
        (FAIL, 'Не успешно'),
    ]

    date_attempt = models.DateTimeField(auto_now_add=True, verbose_name="Дата попытки")
    status = models.CharField(max_length=115, choices=ATTEMPT_STATUS_CHOICES, default=SUCCESS, verbose_name="Статус")
    server_response = models.TextField(verbose_name="Ответ почтового сервера", null=True, blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="mailing")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Чья рассылка")

    def __str__(self):
        return f'{self.date_attempt} - {self.status}'

    def save(self, *args, **kwargs):
        if not self.pk and hasattr(self.mailing, 'owner'):
            self.owner = self.mailing.owner
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "попытка"
        verbose_name_plural = "попытки"
        ordering = ["date_attempt"]

