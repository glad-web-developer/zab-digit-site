from django.db import models


class Diploma(models.Model):
    class Meta:
        verbose_name = 'Грамота / письмо (блок «Нам говорят спасибо»)'
        verbose_name_plural = 'Грамоты / письма (блок «Нам говорят спасибо»)'
        ordering = ['order_index']

    name = models.CharField(
        'Название', max_length=255, blank=True,
        help_text='Необязательно — только для удобства в админке, на сайте не показывается'
    )
    avatar = models.ImageField(
        'Изображение (грамота или благодарственное письмо)',
        upload_to='diploma/'
    )
    order_index = models.IntegerField('Порядок в слайдере (меньше = левее)', default=0)

    def __str__(self):
        return self.name or f'Грамота #{self.pk}'


class Award(models.Model):
    class Meta:
        verbose_name = 'Награда (блок «Награды»)'
        verbose_name_plural = 'Награды (блок «Награды»)'
        ordering = ['order_index']

    name = models.CharField(
        'Название', max_length=255, blank=True,
        help_text='Необязательно — для удобства в админке'
    )
    image = models.ImageField(
        'Изображение награды',
        upload_to='awards/'
    )
    order_index = models.IntegerField('Порядок отображения (меньше = первее)', default=0)

    def __str__(self):
        return self.name or f'Награда #{self.pk}'
