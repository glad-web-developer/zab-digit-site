from ckeditor.fields import RichTextField
from django.db import models


CATEGORY_CHOICES = [
    ('erp', 'ERP/CRM с нуля'),
    ('app', 'Приложения'),
    ('site', 'Сайты'),
]


class Project(models.Model):
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-order_index']

    name = models.CharField('Имя проекта', max_length=255, null=True, blank=True)
    slug = models.SlugField(verbose_name='URL', unique=True, max_length=255,
                            null=True, blank=True)
    description = RichTextField('Описание', null=True, blank=True)
    thumbnail = models.ImageField('Превью-изображение', upload_to='project/thumbnails/',
                                  null=True, blank=True)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES,
                                null=True, blank=True)
    show_in_main = models.BooleanField('Показывать на главной странице', default=False)
    order_index = models.IntegerField('Индекс сортировки', default=0)

    def __str__(self):
        return self.name or f'Проект #{self.pk}'


class ProjectImage(models.Model):
    class Meta:
        verbose_name = 'Фото галереи'
        verbose_name_plural = 'Галерея проекта'
        ordering = ['order_index']

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Проект'
    )
    image = models.ImageField('Фото', upload_to='project/gallery/')
    caption = models.CharField('Подпись к фото', max_length=255, blank=True)
    order_index = models.IntegerField('Порядок', default=0)

    def __str__(self):
        return f'Фото #{self.pk} — {self.project}'
