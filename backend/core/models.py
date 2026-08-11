from django.db import models


class SiteSettings(models.Model):
    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    phone = models.CharField(
        'Номер телефона',
        max_length=50,
        default='+7 924-375-05-73',
        help_text='Отображается в шапке и подвале сайта'
    )
    telegram_url = models.CharField(
        'Ссылка на Telegram',
        max_length=255,
        default='https://t.me/',
        help_text='Полная ссылка, например: https://t.me/username'
    )
    crm_section_image = models.ImageField(
        'Картинка в блоке «Мы разрабатываем CRM/ERP»',
        upload_to='site/', null=True, blank=True,
        help_text='Декоративное изображение справа в карточке'
    )

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Настройки сайта'
