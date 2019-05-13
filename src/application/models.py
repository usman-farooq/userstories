
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, quota=None, is_superuser=False):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, quota=quota, is_superuser=is_superuser)
        user.set_password(password)
        user.save()
        return user
 
    def create_superuser(self, email, password, quota=None):
        return self.create_user(email, password, quota, True)

class User(AbstractBaseUser):
    email = models.EmailField(null=False, unique=True, max_length=255)
    is_superuser = models.BooleanField(null=False, default=False)
    quota = models.PositiveIntegerField(null=True, default=None)
    
    USERNAME_FIELD = 'email'
    
    objects = UserManager()

class Resource(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, verbose_name='ID'),
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
