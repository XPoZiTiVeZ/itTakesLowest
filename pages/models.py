from django.db import models
from login.models import CustomUser
import uuid

class Games(models.Model):
    id = models.UUIDField(primary_key = True, 
                          default = uuid.uuid4,
                          editable = False)
    creator = models.ForeignKey(CustomUser, to_field='username', on_delete=models.CASCADE)
    friendname = models.CharField(verbose_name='Название игры', name='friendlyname', max_length=24)
    start = models.DateField(verbose_name='Начало', name='startdate', auto_now_add=True)
    end = models.DateField(verbose_name='Конец', name='enddate')
    
class Answers(models.Model):
    gameid = models.ForeignKey(Games, to_field='id',  on_delete=models.CASCADE)
    answer = models.PositiveIntegerField(verbose_name='Ответ', name='answer')
    user = models.ForeignKey(CustomUser, to_field='username', on_delete=models.CASCADE)
