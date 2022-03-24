from django.db import models

class CreatedModel(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        help_text='Показывает дату создания записи в базе данных',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
