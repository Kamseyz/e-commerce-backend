from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.contrib.auth import get_user_model


User = get_user_model()

#Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100, allow_blank=False, validators=[validate_email])
    password = serializers.CharField(validators=[validate_password])
    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]
        extra_kwargs = {'email': {'write_only': True}, 'password': {'write_only': True}}
    
    #check if email already exist
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    #save new user
    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        User.objects.create_user(email=email, password=password)
        return validated_data
    
    


#Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, validators=[validate_email])
        
    #check if email already exist in the database
    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email Doesn't exist in the database")
        return value