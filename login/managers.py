from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from difflib import SequenceMatcher

allowedLettersForUsername = 'abcdefghijklmnopqrstuvwxyzABCDEFHIJKLMNOPQRSTUVWXYZ'
allowedDigitsForUsername = '0123456789'

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class CustomManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError('User must have a username')
        
        digits = 0
        for letter in username:
            if letter not in allowedLettersForUsername + allowedDigitsForUsername:
                raise ValueError('UnallowedCharacters')
            if letter in allowedDigitsForUsername:
                digits += 1
        
        if digits > 3:
            raise ValueError('MoreThen3Digits')
        
        if self.model.objects.filter(username=username).exists():
            raise ValueError('UsernameExists')
        
        existing_usernames = self.model.objects.values_list('username', flat=True)

        for existing_username in existing_usernames:
            ratio = similar(username, existing_username)
            if ratio > 0.66:
                raise ValueError("UsernameSimilarity")
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)