from django.contrib import admin
from .models import Passenger,User,BusManager,BusOwner,Ticket,Bus,UploadedImage,Post,Route,UserNotification,UserTicketNotification,SentNotification
# Register your models here.

admin.site.register(Passenger)
admin.site.register(User)
admin.site.register(BusManager)
admin.site.register(BusOwner)
admin.site.register(Ticket)
admin.site.register(Bus)
admin.site.register(UploadedImage)
admin.site.register(Post)
admin.site.register(Route)
admin.site.register(UserNotification)
admin.site.register(UserTicketNotification)
admin.site.register(SentNotification)
