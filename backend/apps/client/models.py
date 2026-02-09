from django.db import models



class Client(models.Model):
    class Meta:
        verbose_name = 'Клиенты'
        verbose_name_plural = 'Клиент'
        ordering = ['-order_index']

    name = models.CharField('Наименование', max_length=255)
    avatar = models.ImageField(upload_to='client/',)


    order_index = models.IntegerField('Индекс сортировки', default=0)

    def __str__(self):
        return f'{self.name}'

