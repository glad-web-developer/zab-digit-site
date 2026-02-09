from django.db import models



class Diploma(models.Model):
    class Meta:
        verbose_name = 'Благодарственные письма'
        verbose_name_plural = 'Благодарственные письма'
        ordering = ['-order_index']

    avatar = models.ImageField(upload_to='diploma/',)

    order_index = models.IntegerField('Индекс сортировки', default=0)

    def __str__(self):
        return f'{self.id}'

