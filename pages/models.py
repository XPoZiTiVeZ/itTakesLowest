from django.db import models
from login.models import CustomUser

class Games(models.Model):
    id = models.CharField(primary_key = True, verbose_name='Id игры', max_length=6)
    creator = models.ForeignKey(CustomUser, to_field='username', on_delete=models.CASCADE)
    friendlyname = models.CharField(verbose_name='Название игры', max_length=24)
    start = models.DateTimeField(verbose_name='Начало')
    end = models.DateTimeField(verbose_name='Конец')
    ended = models.BooleanField(verbose_name='Статус игры', default=False)
    
class Answers(models.Model):
    gameid = models.ForeignKey(Games, to_field='id',  on_delete=models.CASCADE)
    answer = models.PositiveIntegerField(verbose_name='Ответ', name='answer')
    user = models.ForeignKey(CustomUser, to_field='username', on_delete=models.CASCADE)
