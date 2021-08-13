from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """ Расширение встроенного UserManager """
    use_in_migrations = True

    def _create_user(self, email, password, telephone, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, telephone=telephone, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, telephone, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, telephone, first_name, last_name, **extra_fields)

    def create_staffuser(self, email, telephone, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staffuser must have is_staff=True.')
        return self._create_user(email, password, telephone, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, telephone, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staffuser must have is_staff=True.')

        return self._create_user(email, password, telephone, first_name, last_name, **extra_fields)


class User(AbstractUser):
    """
        Расширенная модель пользователя
    """
    first_name = models.CharField('Имя пользователя', max_length=32)
    last_name = models.CharField('Фамилия пользователя', max_length=32)
    email = models.EmailField('E-mail', max_length=96, unique=True)
    telephone = models.CharField('Номер телефона', max_length=32, unique=True)
    username = models.CharField('Лоигн', max_length=150, null=True, blank=True)
    date_birthday = models.DateField('Дата рождения', null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['telephone', 'first_name', 'last_name']
    objects = UserManager()

    def __str__(self):
        return f'{self.last_name} {self.first_name} , {self.email}'

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
