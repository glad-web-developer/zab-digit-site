from django.db import models


class Client(models.Model):
    class Meta:
        verbose_name = 'Логотип клиента (блок «Нам доверяют»)'
        verbose_name_plural = 'Логотипы клиентов (блок «Нам доверяют»)'
        ordering = ['order_index']

    name = models.CharField('Название компании', max_length=255)
    avatar = models.ImageField(
        'Логотип',
        upload_to='client/',
        help_text='Рекомендуется PNG с прозрачным фоном'
    )
    order_index = models.IntegerField('Порядок в карусели (меньше = левее)', default=0)

    def __str__(self):
        return self.name
