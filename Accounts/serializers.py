from rest_framework import serializers
from .models import Admin,BusOwner,BusManager,User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
class UserSerializer(serializers.ModelSerializer):
    #  password = serializers.CharField(write_only=True)
     class Meta:
        model = User
        fields = "__all__"
class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model=Admin
        fields="__all__"

class BusOwnerSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model=BusOwner
        fields="__all__"

class BusManagerSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    works_for=BusOwnerSerializer()
    class Meta:
        model=BusManager
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
        data['user'] = UserSerializer(user).data
        return data