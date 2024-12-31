from rest_framework import serializers
from authentication.models import MyUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at']
        read_only_fields = ['date_joined', 'created_at', 'updated_at'] 

class MyUserLoginSerializers(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username and not password:
            raise serializers.ValidationError('Please enter both username and password')
        if not username:
            raise serializers.ValidationError('Please enter username')
        if not password:
            raise serializers.ValidationError('Please enter password')
        
        user = get_user_model()
        
        try:
            user = user.objects.get(username=username)
        except user.DoesNotExist:
            raise serializers.ValidationError({"user": "User with this Email does not exist."})
        
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid password."})
        refresh = RefreshToken.for_user(user)
        # Include only serializable data
        return {
            'username': user.username,
            'email': user.email,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class MyUserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password!= password2:
            raise serializers.ValidationError({"password": "Password and Confirm Password are not match"})
        return attrs
    
    def create(self, validated_data):
        user = MyUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
