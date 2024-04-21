from rest_framework import serializers
from .models import BusOwner,BusManager,User,Passenger,Bus,Route,Ticket,Post,UploadedImage
import base64
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class UserSerializer(serializers.ModelSerializer):
     password = serializers.CharField(write_only=True)
     class Meta:
        model = User
        fields = "__all__"

class BusOwnerSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model=BusOwner
        fields="__all__"
class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Passenger
        fields="__all__"

class BusManagerSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    works_for=BusOwnerSerializer()
    class Meta:
        model=BusManager
        fields="__all__"
class BusSerializer(serializers.ModelSerializer):
    manager=BusManagerSerializer()
    class Meta:
        model=Bus
        fields="__all__"

class RouteSerializer(serializers.ModelSerializer):
    buses=BusSerializer(many=True)
    manager=BusManagerSerializer()
    class Meta:
        model=Route
        fields="__all__"
        
class TicketSerializer(serializers.ModelSerializer):
    bus=BusSerializer()
    route=RouteSerializer()
    user=PassengerSerializer()
    class Meta:
        model=Ticket
        fields="__all__"

class PostSerializer(serializers.ModelSerializer):
    manager=BusManagerSerializer()
    class Meta:
        model=Post
        fields="__all__"  

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        
        token['user'] = user.username

        return token
    def validate(self, attrs):
        data = super().validate(attrs)
        user=User.objects.get(email=self.user.username)
        if user.role=="bus_owner":
            manager=BusOwner.objects.get(user__username=user.username)
            serializer=BusOwnerSerializer(manager)
            data['user'] = serializer.data
        else:
            manager=BusManager.objects.get(user__username=user.username)
            serializer=BusManagerSerializer(manager)
            data['user'] = serializer.data
        return data
    

class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=UploadedImage
        fields="__all__"
    def validate(self,data):
        image_name=data.get("image_name")
        
        image_size=data.get("image_size")
        base_64=data.get("image_base64")
        print(f"image Name {image_name}, size: {image_size} base:{base_64}")
        if not image_name.endswith((".jpg",".png",".jpeg")):
            raise serializers.ValidationError("Not valid image")
        if int(image_size) > 5*1024*1024:
           raise serializers.ValidationError("Image size not valid") 
        if not is_base64(base_64):
            raise serializers.ValidationError("Invalid base 64 String")
        return data


def is_base64(s):
    try:
        # Attempt to decode the string as base64
        decoded_data = base64.b64decode(s)
        
        # Check if the decoded data can be correctly encoded back to the original string
        encoded_data = base64.b64encode(decoded_data).decode('utf-8')
        
        # Check if the encoded data matches the original string
        print(f"tester {s == encoded_data}")
        return s == encoded_data
    except Exception as e:
        # An exception will be raised if the string is not valid base64
        return False