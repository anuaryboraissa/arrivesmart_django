from django.shortcuts import render
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer,AdminSerializer,BusOwnerSerializer,BusManagerSerializer
from .models import User,Admin,BusManager,BusOwner
from .permissions import *
# Create your views here.

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
    def get(self, request):
        user = request.user
        if user.role=="admin":
            all_managers = request.GET.get('all_managers')
            managers_works_to = request.GET.get('owner')
            all_owners = request.GET.get('all_owners')
            if all_managers is not None and all_managers:
                managers=BusManager.objects.all()
                serializer=BusManagerSerializer(managers,many=True)
                return Response({"message":"success","data":serializer.data})
            else:
                owners=BusOwner.objects.all()
                serializer=BusOwnerSerializer(owners,many=True)
                return Response({"message":"success","data":serializer.data})
        elif user.role=="bus_owner":
            owners=BusOwner.objects.all()
            serializer=BusOwnerSerializer(owners,many=True)
            return Response({"message":"success","data":serializer.data})
        elif user.role=="bus_manager":
            owners=BusOwner.objects.all()
            serializer=BusOwnerSerializer(owners,many=True)
            return Response({"message":"success","data":serializer.data})
        else:
           pass
           
        user_serializer=UserSerializer(user)
        return Response({'message': f'You are authenticated! {user.username} {user.date_joined}',"user":user_serializer.data})



class UserRegistrationAPIView(APIView):
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
            if data['role'] == 'admin':
                Admin.objects.create(user=user)
            elif data['role'] == 'bus_owner':
                BusOwner.objects.create(user=user,tin_number=data['tin_number'])
            elif data['role'] == 'bus_manager':
                user=User.objects.get(username=data['works_for'])
                owner=BusOwner.objects.get(user=user)
                BusManager.objects.create(user=user,works_for=owner)
            access_token=create_user_and_generate_token(user)
            serializer_data=user_serializer.data
            serializer_data['access_token']=access_token
            return Response(serializer_data,status=status.HTTP_200_OK)
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)



def create_user_and_generate_token(user):

    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return access_token