from ckeditor.fields import RichTextField
from django.db import models


class SitePage(models.Model):
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    slug = models.SlugField('URL (slug)', unique=True, max_length=100)
    title = models.CharField('Заголовок', max_length=255)
    content = RichTextField('Содержание')
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    def __str__(self):
        return self.title


class TechStack(models.Model):
    class Meta:
        verbose_name = 'Технология (блок «Fullstack-разработка»)'
        verbose_name_plural = 'Технологии (блок «Fullstack-разработка»)'
        ordering = ['order_index']

    name = models.CharField('Название технологии', max_length=100)
    icon = models.ImageField(
        'Иконка',
        upload_to='tech/',
        null=True, blank=True,
        help_text='Логотип технологии (PNG/SVG, рекомендуется 32×32 px)'
    )
    order_index = models.IntegerField('Порядок отображения (меньше = раньше)', default=0)

    def __str__(self):
        return self.name
