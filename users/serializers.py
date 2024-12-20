from rest_framework import serializers
from rest_framework.authentication import authenticate
from django.contrib.auth import get_user_model
from .models import OTP, Profile
from django.utils.crypto import get_random_string


User = get_user_model()
    

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    # def create(self, validated_data):
    #     """Save user and generate OTP."""
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         password=validated_data['password'],
    #         user_type=validated_data['user_type']
    #     )
    #     otp = get_random_string(length=6, allowed_chars='0123456789')
    #     OTP.objects.create(user=user, otp=otp)
    #     return user

    def create(self, validated_data):
        user_type = validated_data['user_type']
        is_staff = user_type == 'admin'
        is_superuser = user_type == 'admin'

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=user_type,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        otp = get_random_string(length=6, allowed_chars='0123456789')
        OTP.objects.create(user=user, otp=otp)
        return user



class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ('user', 'otp')


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email", "")
        password = data.get("password", "")
        user = authenticate(email=email, password=password)
        if user is not None:
            if not user.verified:
                raise serializers.ValidationError("Account is not verified, Please verify your account first. ")
            data["user"] = user
            return data
        raise serializers.ValidationError("Invalid credentials.")
    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_image', 'full_name', 'address', 'phone_number', 'state')


# FOR ADMIN USER
class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user_type = validated_data.get('user_type')
        if user_type == 'admin':
            user = User.objects.create_superuser(**validated_data)
        else:
            user = User.objects.create_user(**validated_data)
        return user

