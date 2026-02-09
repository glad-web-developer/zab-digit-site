from ckeditor.fields import RichTextField
from django.db import models





class Project(models.Model):
    class Meta:
        verbose_name = 'Проекты'
        verbose_name_plural = 'Проект'
        ordering = ['-order_index']

    name = models.CharField('Имя проекта', max_length=255, null=True, blank=True)
    slug = models.SlugField(verbose_name='Url', unique=True, max_length=255,
                            null=True, blank=True)
    description = RichTextField('Описание', null=True, blank=True)

    show_in_main = models.BooleanField('Показывать на главной странице', default=False)
    order_index = models.IntegerField('Индекс сортировки', default=0)

    def __str__(self):
        return self.name

