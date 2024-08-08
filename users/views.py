from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, OTPSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ProfileSerializer, AdminCreateUserSerializer
from .models import OTP, User, PasswordResetToken, Profile
from subscriptions.models import SubscriptionPlan, UserSubscription
import random
import string
from django.conf import settings



User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        otp = get_random_string(length=6, allowed_chars='0123456789')
        OTP.objects.create(user=user, otp=otp)
        send_mail(
            'Verify your email',
            f'Your OTP is {otp}',
            'from@example.com',
            [user.email],
        )
        # Assign default free subscription plan to new clients
        if user.user_type == 'client':
            free_plan = SubscriptionPlan.objects.get(name='free')
            UserSubscription.objects.create(user=user, plan=free_plan, is_active=True, subscription_status='active')



class VerifyEmailView(APIView):
    def post(self, request):
        otp = request.data.get('otp')
        try:
            otp_obj = OTP.objects.get(otp=otp)
            otp_obj.user.is_active = True
            otp_obj.user.save()
            otp_obj.delete()
            return Response({'status': 'verified'}, status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.data['email'], password=serializer.data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                subscription = UserSubscription.objects.filter(user=user).first()
                subscription_type = subscription.plan.name if subscription else None
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type,
                    'username': user.username,
                    'email': user.email,
                    'subscription_type': subscription_type,
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'status': 'logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permissions

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        users = User.objects.filter(email=email)
        
        if users.exists():
            for user in users:
                # Generate token
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
                # Save token to user profile or a separate model (e.g., PasswordResetToken)
                # Send email with token
                send_mail(
                    'Password Reset Request',
                    f'Use this token to reset your password: {token}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                # Save the token to the database, associated with the user
                PasswordResetToken.objects.create(user=user, token=token)
            return Response({"message": "Password reset token sent."}, status=status.HTTP_200_OK)
        return Response({"message": "No user found with this email."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permissions

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is expired (optional, based on your implementation)
        if reset_token.is_expired():
            return Response({"detail": "Token is expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Optionally, delete the token after successful reset
        reset_token.delete()
        
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    


# FOR ADMIN USER

class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsAdminUser]


class AdminDeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

