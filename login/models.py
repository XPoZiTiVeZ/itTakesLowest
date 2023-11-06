import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from .managers import CustomManager
from difflib import SequenceMatcher



class CustomUser(AbstractBaseUser):
    ''' 
    Custom user model
    '''
    id = models.UUIDField(primary_key = True, 
                          default = uuid.uuid4,
                          editable = False)
    username = models.CharField(verbose_name='Имя пользователя',
                                 max_length=16,
                                 unique=True)
    firstname = models.CharField(verbose_name='Имя',
                                 max_length=32)
    lastname = models.CharField(verbose_name='Фамилия',
                                max_length=32)
    password = models.CharField(verbose_name='Пароль',
                                max_length=128,
                                help_text='Пароль')
    wins = models.PositiveIntegerField(verbose_name='Победы',
                                       default=0,
                                       help_text='Победы')
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    
    @property
    def is_staff(self):
        return self.is_admin
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    objects = CustomManager()

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'