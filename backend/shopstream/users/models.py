from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone


# Create your models here.


#DELETE THIS BEFORE PUSHING TO PRODUCTION 
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


#USER REGISTRATION
class User(AbstractUser):
        
    username = None
    email = models.EmailField(unique=True, blank= False, null= False, max_length=100)
   
        
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    
    
    def __str__(self):
        return f'The account {self.email}'
    
    
#LOGIN WITH MAGIC LINK

class LoginModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.expired_at
        
    