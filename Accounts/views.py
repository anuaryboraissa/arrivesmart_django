from django.shortcuts import render
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UploadedImageSerializer,TicketSerializer,PassengerSerializer,UserSerializer,PostSerializer,BusOwnerSerializer,BusManagerSerializer,BusSerializer,RouteSerializer,UserTicketNotificationSerializer,UserNotificationSerializer
from .models import User,BusManager,BusOwner,Passenger,Bus,Route,Ticket,Post,UploadedImage,UserTicketNotification,UserNotification
from .permissions import *
import os,base64,uuid
from django.conf import settings
import Accounts.FCMManager as fcm
# Create your views here.
from django.core.files.base import ContentFile
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth import get_user_model


class ObtainTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class SomeSecuredView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request):
        user = request.user
        data=request.data
        if user.role=="bus_owner":
            if data['type']=='owner':
                del data['type']
                user_data=User.objects.get(username=data['username'])
                user_data.__dict__.update(**data)
                user_data.save()
                owner_object=BusOwner.objects.get(user__username=user_data.user__username)
                owner_object.__dict__.update(user=user_data,**data)
                owner_object.save()
                
            else:
                del data['type']
                user_data=User.objects.get(username=data['username'])
                user_data.__dict__.update(**data)
                user_data.save()
                manager_object=BusManager.objects.get(user__username=user_data.user__username)
                manager_object.user=user_data
                manager_object.save()
                
        else:
                user_data=User.objects.get(username=data['username'])
                user_data.__dict__.update(**data)
                user_data.save()
                manager_object=BusManager.objects.get(user__username=user_data.user__username)
                manager_object.user=user_data
                manager_object.save()
                
        
    def delete(self,request):
        user = request.user
        data=request.data
        if user.role=="bus_owner":
           manager=BusManager.objects.get(user__username=data['username'])
           manager.objects.delete()
           pass
        else:
            pass
        pass
    def get(self, request):
        user = request.user
        if user.is_authenticated and user.role=="bus_owner":
            my_managers = request.GET.get('my_managers')
            if my_managers is not None and my_managers:
                managers=BusManager.objects.filter(works_for__user__email=user.username)
                serializer=BusManagerSerializer(managers,many=True)
                return Response({"message":"my managers","data":serializer.data,"status":status.HTTP_200_OK})
        elif user.is_authenticated and user.role=="bus_manager":
                    routes = request.GET.get('routes')
                    tickets = request.GET.get('tickets')
                    if routes is not None and routes:
                        routes=Route.objects.filter(manager__user__username=user.username)
                        serializer=RouteSerializer(routes,many=True)
                        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
                        
                    elif tickets is not None and tickets:
                        user_tickets=Ticket.objects.filter(bus__manager__user__username=user.username)
                        serializer=TicketSerializer(user_tickets,many=True)
                        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
                    else:
                        pass
                    return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        else:
           pass
           
        user_serializer=UserSerializer(user)
        return Response({'message': f'You are authenticated! {user.username} {user.date_joined}',"user":user_serializer.data})



class UserManagementAPIView(APIView):
    def post(self, request):
        data=request.data

        user_map={
            "phone":data['phone'],
            "first_name":data['first_name'],
            "last_name":data['last_name'],
            "email":data['email'],
            "username":data['email'],
            "password":data['password'],
            "role":data['role']
        }
        user_serializer=UserSerializer(data=user_map)
        if user_serializer.is_valid():
            auth_user = get_user_model()
            user=auth_user.objects.create_user(**user_map)
            createPermissions()
            if data['role'] == 'bus_owner':
                BusOwner.objects.create(user=user,tin_number=data['tin_number'])
            elif data['role'] == 'bus_manager':
                owner_user=User.objects.get(username=data['works_for'])
                owner=BusOwner.objects.get(user=owner_user)
                BusManager.objects.create(user=user,works_for=owner)
            access_token=create_user_and_generate_token(user)
            serializer_data=user_serializer.data
            serializer_data['access_token']=access_token
            return Response({"message":"success","data":serializer_data,"status":status.HTTP_200_OK})
        return Response({"message":"fail","data":user_serializer.errors,"status":status.HTTP_400_BAD_REQUEST})


class PassengerManagementView(APIView):
    def post(self,request):
        data=request.data
        serializer=PassengerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        return Response({"message":"fail","data":serializer.errors,"status":status.HTTP_400_BAD_REQUEST})
    def get(self,request):
        username = request.GET.get('username')
        all = request.GET.get('all')
        routes = request.GET.get('routes')
        if username is not None:
            passenger=Passenger.objects.filter(phone=username)
            if passenger.exists():
                
               serializer=PassengerSerializer(passenger[0])
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        elif routes is not None and routes:
            all_routes=Route.objects.all()
            serializer=RouteSerializer(all_routes,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        elif all is not None and all:
            all_passengers=Passenger.objects.all()
            serializer=PassengerSerializer(all_passengers,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
              
        
    def put(self,request):
        data=request.data
        passenger=Passenger.objects.get(phone=data['phone'])
        passenger.__dict__.update(**data)
        passenger.save()
        serializer=PassengerSerializer(passenger)
        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
    def delete(self,request):
        self.authentication_classes=[IsAuthenticated]
        user=request.user
        if user.is_authenticated and user.role=="bus_manager":
            data=request.data
            passenger=Passenger.objects.get(passenger_id=data['passenger_id'])
            i=passenger.delete()
            return Response({"message":f"success ","data":1,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})

class TicketManagementView(APIView):
    def post(self,request):
        data=request.data
        try:
            route=Route.objects.get(route_id=data["route"])
            bus=Bus.objects.get(plate_number=data["bus"])
            passenger=Passenger.objects.get(passenger_id=data["user"])
            # # passenger_id
            del data["bus"]
            del data["route"]
            del data["user"]
            ticket=Ticket.objects.create(user=passenger,bus=bus,route=route,**data)
            serializer=TicketSerializer(ticket)
            # Ticket.objects.create(route=route,bus=bus,user=passenger,**data)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        except Exception as e:
            
            return Response({"message":f"fail {e}","data":f"{e}","status":status.HTTP_400_BAD_REQUEST})
    
    def get(self,request):
        id = request.GET.get('id')
        passenger = request.GET.get('passenger')
        if id is not None:
            ticket=Ticket.objects.get(ticket_id=id)
            serializer=TicketSerializer(ticket)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        elif passenger is not None:
            tickets=Ticket.objects.filter(user__passenger_id=passenger)
            serializer=TicketSerializer(tickets,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        else:
            all_tickets=Ticket.objects.all()
            serializer=TicketSerializer(all_tickets,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
            
    def put(self,request):
        data=request.data
        ticket=Ticket.objects.get(ticket_id=data['ticket_id'])
        if "route" in data and "bus" in data:
            route=Route.objects.get(route_id=data["route"])
            bus=Bus.objects.get(plate_number=data["plate_number"])
            del data["plate_number"]
            del data["route"]
            ticket.objects.update(bus=bus,route=route,**data)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        elif "route" in data:
            route=Route.objects.get(route_id=data["route"])
            del data["route"]
            ticket.objects.update(route=route,**data)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        elif "bus" in data:
            bus=Bus.objects.get(plate_number=data["plate_number"])
            del data["plate_number"]
            ticket.objects.update(bus=bus,**data)
        else:
            ticket.__dict__.update(**data)
        ticket.save()
        serializer=TicketSerializer(ticket)
        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
    
    
    def delete(self,request):
        self.permission_classes=[IsAuthenticated]
        data=request.data
        user = request.user
        if user.is_authenticated and user.role=="bus_manager":
            ticket=Ticket.objects.get(ticket_id=data['ticket_id'])
            ticket.delete()
            return Response({"message":"success","data":1,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})

    
class BusManagementView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        data=request.data
        if user.is_authenticated and user.role=="bus_manager":
               manager=BusManager.objects.get(user__username=user.username)
               bus=Bus.objects.create(manager=manager,**data)
               serializer=BusSerializer(bus)
               return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        else:
           return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST}) 
        
    def put(self,request):
        user = request.user
        data=request.data
        if user.is_authenticated and user.role=="bus_manager":
          
            bus=Bus.objects.get(plate_number=data['plate_number'])
            
            bus.__dict__.update(**data)
            bus.save()
            serializer=BusSerializer(bus)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})
    def delete(self,request):
        user = request.user
        data=request.data
        if user.is_authenticated and user.role=="bus_manager":
            bus=Bus.objects.get(plate_number=data['plate_number'])
            bus.delete()
            return Response({"message":"success","data":1,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})
    def get(self,request):
        user = request.user
        if user.is_authenticated and user.role=="bus_manager":
            buses=Bus.objects.filter(manager__user__username=user.username)
            serializer=BusSerializer(buses,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})
class RouteManagementView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        data=request.data
        if user.is_authenticated and user.role=="bus_manager":
             try:
                 manager=BusManager.objects.get(user__username=user.username)
                 route=Route.objects.create(manager=manager,**data)
                 serializer=RouteSerializer(route)
                 return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
             except Exception as e:
                 pass
                 return Response({"message":f"fail {e}","data":{},"status":status.HTTP_400_BAD_REQUEST})
        else:
           return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST}) 
    def put(self,request):
        user = request.user
        if user.is_authenticated and user.role=="bus_manager":
             try:
                data=request.data
                route=Route.objects.get(route_id=data['route_id'])
                if "buses" in data:
                    bus_ids=data['buses']
                    del data['buses']
                    for id in bus_ids:
                        bus=Bus.objects.get(plate_number=id)
                        route.buses.add(bus)
                route.__dict__.update(**data)
                route.save()
                serializer=RouteSerializer(route)
                return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
             except Exception as e:
                 pass
                 return Response({"message":f"fail {e}","data":{},"status":status.HTTP_400_BAD_REQUEST})
        else:
           return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST}) 

    def delete(self,request):
        data=request.data
        route=Route.objects.get(route_id=data['route_id'])
        route.delete()
        return Response({"message":"success","data":1,"status":status.HTTP_200_OK})
    def get(self,request):
        user = request.user
        if user.is_authenticated and user.role=="bus_manager":
            routes=Route.objects.filter(manager__user__username=user.username)
            serializer=RouteSerializer(routes,many=True)
            return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
        return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST})
class PostManagementView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        data=request.data
        if user.is_authenticated and user.role=="bus_manager":
             manager=BusManager.objects.get(user__username=user.username)
             data["manager"]=BusManagerSerializer(manager).data
             serializer=PostSerializer(data=data)
             if serializer.is_valid():
               serializer.save()
               return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
             return Response({"message":"fail","data":serializer.errors,"status":status.HTTP_400_BAD_REQUEST})
        else:
           return Response({"message":"Not authorized","data":{},"status":status.HTTP_400_BAD_REQUEST}) 
    def put(self,request):
        data=request.data
        post=Post.objects.get(post_id=data['post_id'])
        post.__dict__.update(**data)
        post.save()
        serializer=PostSerializer(post)
        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
    def delete(self,request):
        data=request.data
        post=Post.objects.get(post_id=data['post_id'])
        post.delete()
        return Response({"message":"success","data":1,"status":status.HTTP_200_OK})
    def get(self,request):
        user = request.user
        posts=Post.objects.filter(manager__user__username=user.username)
        serializer=PostSerializer(posts,many=True)
        return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})

class NotificationApi(APIView):
    def post(self,request):
        data=request.data
        try:
            serializer = UserNotificationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Notification added success","data":serializer.data,"status":status.HTTP_200_OK})
            return Response({"message":serializer.errors,"data":None,"status":status.HTTP_400_BAD_REQUEST})
        except Exception as e:
             return Response({"message":serializer.errors,"data":None,"status":status.HTTP_400_BAD_REQUEST})
    def get(self,request):
        dev_id = request.query_params.get('dev_id')
        if dev_id is not None:
            try:
                notification_obtained = UserNotification.objects.filter(dev_id=dev_id)
                if notification_obtained.exists():
                   serializer = UserNotificationSerializer(notification_obtained[0])
                   return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
                return Response({"message":"No Notification Found with that token","data":None,"status":status.HTTP_200_OK})
            except Exception as e:
                 return Response({"message":f"something went wrong {e}","data":None,"status":status.HTTP_400_BAD_REQUEST})
        else:
            try:
                notifications=UserNotification.objects.all() 
                serializer=UserNotificationSerializer(notifications,many=True)
                return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
            except Exception as e:
                 return Response({"message":"something went wrong","data":None,"status":status.HTTP_400_BAD_REQUEST})
    def put(self,request):
        data=request.data
        if data['dev_id'] is not None:
            try:
                notify = UserNotification.objects.get(dev_id=data['dev_id'])
                notify.__dict__.update(**data)
                notify.save()
                serializer = UserNotificationSerializer(notify)
                return Response({"message":"success","data":serializer.data,"status":status.HTTP_200_OK})
            except Exception as e:
                 return Response({"message":"something went wrong","data":None,"status":status.HTTP_400_BAD_REQUEST})
        else:
                return Response({"message":"Email is required","data":None,"status":False})
    def delete(self,request,email=None):
        data=request.data
        if data['dev_id'] is not None:
            try:
                notify = UserNotification.objects.get(dev_id=data['dev_id'])
                notify.delete()
                return Response({"message":"success","data":1,"status":status.HTTP_200_OK})
            except Exception as e:
                    return Response({"message":"something went wrong","data":None,"status":status.HTTP_400_BAD_REQUEST})
        else:
                return Response({"message":"something went wrong, must provide id","data":None,"status":status.HTTP_400_BAD_REQUEST}) 
class UserTicketNotificationApi(APIView):
    def post(self,request):
        data=request.data
        try:
            notification=UserNotification.objects.get(dev_id=data['dev_id'])
            ticket=Ticket.objects.get(ticket_id=data['ticket_id'])
            del data['dev_id']
            del data['ticket_id']
            UserTicketNotification.objects.create(notification=notification,ticket=ticket,**data)
            user_ticket=UserTicketNotification.objects.get(doc_id=data['doc_id'])
            serializer=UserTicketNotificationSerializer(user_ticket)
            return Response({"message":"Favorite set success","data":serializer.data,"status":True})
        except Exception as e:
             return Response({"message":f"something went wrong {e}","data":None,"status":False})

    def get(self,request):
            doc_id = request.query_params.get('doc_id')
            if doc_id is not None:
                try:
                    college_favorites = UserTicketNotification.objects.filter(doc_id=doc_id)
                    serializer=UserTicketNotificationSerializer(college_favorites,many=True)
                    return Response({"message":"college favorites","data":serializer.data,"status":True})
                except Exception as e:
                    return Response({"message":f"something went wrong {e}","data":None,"status":False})
            else:
              try:
                notification_tickets = UserTicketNotification.objects.all()
                serializer=UserTicketNotificationSerializer(notification_tickets,many=True)
                return Response({"message":"All favorites","data":serializer.data,"status":True})
              except Exception as e:
                 return Response({"message":f"something went wrong {e}","data":None,"status":False})


    def put(self,request):
            data=request.data
            try:
                notification_ticket=UserTicketNotification.objects.get(doc_id=data['doc_id'])
                notification_ticket.__dict__.update(**data)
                notification_ticket.save()
                favorite_serializer=UserTicketNotificationSerializer(notification_ticket)
                return Response({"message":"Favorite updated","data":favorite_serializer.data,"status":True})
            except Exception as e:
                 return Response({"message":f"something went wrong {e}","data":None,"status":False})
    def delete(self,request,pk=None):
            data=request.data
            try:
                favorite = UserTicketNotification.objects.get(doc_id=data['doc_id'])
                favorite.delete()
                return Response({"message":"success","data":1,"status":True})
            except Exception as e:
                    return Response({"message":f"something went wrong {e}","data":None,"status":False}) 
                
class UploadImageApiView(APIView):
    def post(self,request):
        input=request.data
        response=None
        try:
            serializer=UploadedImageSerializer(data=input)
            if serializer.is_valid():             
                file_ext=input['image_name'].split(".")[-1]
                uuid_string=uuid.uuid4()
                new_file_name=f"{uuid_string}.{file_ext}"
                upload_dir=os.path.join(settings.MEDIA_ROOT,"uploads")
                os.makedirs(upload_dir,exist_ok=True)
                decoded_data = base64.b64decode(input['image_base64'])
                file_to_upload=ContentFile(decoded_data)
                new_file_path=os.path.join(upload_dir,new_file_name)
                with open(new_file_path, 'wb') as destination:
                    for chunk in file_to_upload.chunks():
                        destination.write(chunk)
                uploadImage=UploadedImage(image_name=new_file_name,image_size=input['image_size'],image_base64=f"base of {new_file_name}",image_path=f"media/uploads/{new_file_name}")
                uploadImage.save()
                response = {"message":"success","data":f"media/uploads/{new_file_name}","status":True}
            else:
                response = {"message":"something went wrong","data":"","status":False}
            return Response(response)
        except Exception as e:
            response = {"message":f"{e}","data":"","status":False}
            return Response(response)
             
def create_user_and_generate_token(user):
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return access_token
def delete_file(file_path):
    # Construct the full path to the file
    full_file_path = os.path.join('media', 'uploads', file_path)

    # Check if the file exists
    if os.path.exists(full_file_path):
        # Delete the file
        os.remove(full_file_path)
        return True
    else:
        return False