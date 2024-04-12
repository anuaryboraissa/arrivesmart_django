from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=50)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=15)
    def __str__(self):
       return self.username
    
class Admin(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    def __str__(self):
       return self.user
    
class BusOwner(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    tin_number=models.IntegerField(unique=True)
    def __str__(self):
       return self.tin_number

class BusManager(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    works_for=models.ForeignKey(BusOwner,on_delete=models.CASCADE)
    def __str__(self):
       return self.user

# Create your models here.
