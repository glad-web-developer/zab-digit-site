from django.db import models


class ContactRequest(models.Model):
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=50)
    message = models.TextField('Сообщение', blank=True)
    source = models.CharField('Источник (страница)', max_length=255, default='Главная')
    created_at = models.DateTimeField('Дата подачи', auto_now_add=True)
    is_processed = models.BooleanField('Обработана', default=False)

    def __str__(self):
        return f'{self.name} — {self.phone} ({self.created_at:%d.%m.%Y %H:%M})'
