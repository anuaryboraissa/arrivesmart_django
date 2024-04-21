from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=50)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=15,unique=True)
    def __str__(self):
       return self.email
    
class BusOwner(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    tin_number=models.IntegerField(unique=True)
    def __str__(self):
       return f"{self.tin_number}"

class BusManager(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    works_for=models.ForeignKey(BusOwner,on_delete=models.CASCADE)
   
    def __str__(self):
       return self.user.username
   
class Passenger(models.Model):
    phone=models.CharField(max_length=15)
    passenger_id=models.CharField(primary_key=True,max_length=255)
    email=models.EmailField(blank=True,null=True)
    f_name=models.CharField(blank=True,null=True,max_length=100)
    l_name=models.CharField(blank=True,null=True,max_length=100)
    type=models.CharField(blank=True,null=True,max_length=10)
    gender=models.CharField(blank=True,null=True,max_length=6)
    
    def __str__(self):
        return self.phone

class Bus(models.Model):
    name=models.CharField(unique=True,max_length=100)
    plate_number=models.CharField(primary_key=True,max_length=100)
    seats_number=models.IntegerField()
    image=models.CharField(max_length=100,blank=True)
    manager=models.ForeignKey(BusManager,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.plate_number
class Route(models.Model):
    station=models.CharField(max_length=100)
    route_id=models.CharField(primary_key=True,max_length=200)
    starting_point=models.EmailField(blank=True,null=True)
    destination=models.CharField(max_length=100)
    via=models.CharField(max_length=100)
    time=models.CharField(max_length=100)
    buses=models.ManyToManyField(Bus,related_name="routes")
    manager=models.ForeignKey(BusManager,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.starting_point}-{self.destination}"
class Ticket(models.Model):
    user=models.ForeignKey(Passenger,on_delete=models.CASCADE)
    route=models.ForeignKey(Route,on_delete=models.CASCADE)
    bus=models.ForeignKey(Bus,on_delete=models.CASCADE)
    ticket_id=models.CharField(primary_key=True,max_length=255)
    date=models.DateField()
    seatNo=models.IntegerField()
    def __str__(self):
        return self.ticket_id
class Post(models.Model):
    post_id=models.CharField(primary_key=True,max_length=255)
    body=models.CharField(max_length=500)
    title=models.CharField(max_length=255)
    manager=models.ForeignKey(BusManager,on_delete=models.CASCADE)
    date_created=models.CharField(max_length=30)
    image=models.CharField(max_length=255,blank=True)
    
    def __str__(self):
        return self.title
class UploadedImage(models.Model):
    image_size=models.IntegerField()
    image_path=models.CharField(max_length=200,primary_key=True)
    image_name=models.CharField(max_length=50)
    
    def __str__(self):
        return self.image_path
# Create your models here.
