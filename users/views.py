from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, OTPSerializer, ResendOTPSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ProfileSerializer, AdminCreateUserSerializer
from .models import OTP, User, PasswordResetToken, Profile
from subscriptions.models import SubscriptionPlan, UserSubscription
import random
import string
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta
from django.utils import timezone
from .utils import generate_random_otp
from django.utils.timezone import now as timezone_now



User = get_user_model()


# Define OTP expiration duration in one place for consistency
OTP_EXPIRATION_MINUTES = 10


def otp_expired(session):
    """Check if OTP in session has expired."""
    otp_expiry = session.get('otp_expiry')
    return otp_expiry and timezone.now() > otp_expiry


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully. OTP sent to email.",
                examples={"application/json": {"message": "User registered successfully. OTP sent to email."}}
            ),
            400: openapi.Response(
                description="Invalid registration details.",
                examples={"application/json": {"error": "Invalid registration details"}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            # Send OTP email
            otp_instance = OTP.objects.get(user=user)
            send_mail(
                'Verify your email',
                f'Your OTP is {otp_instance.otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            return Response({"message": "User registered successfully. OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP code sent via email'),
            },
            required=['otp'],
        ),
        responses={
            200: openapi.Response(
                description="Account verified successfully.",
                examples={"application/json": {"message": "Account verified successfully."}}
            ),
            400: openapi.Response(
                description="Invalid OTP or session expired.",
                examples={"application/json": {"error": "Invalid OTP or session expired."}}
            ),
            404: openapi.Response(
                description="OTP not found.",
                examples={"application/json": {"error": "No OTP found."}}
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')

        if not otp:
            return Response({"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the OTP instance linked to a user
            otp_instance = OTP.objects.get(otp=otp)

            # Check if the OTP is expired
            if otp_instance.is_expired():
                return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            user = otp_instance.user  # Get the associated user

            # Mark user as verified
            user.verified = True
            user.save()

            if user.user_type == 'client':
                try:
                    free_plan = SubscriptionPlan.objects.get(name='free')
                    UserSubscription.objects.create(
                        user=user, plan=free_plan, is_active=False, subscription_status='inactive'
                    )
                except SubscriptionPlan.DoesNotExist:
                    return Response({"error": "Default subscription plan not found."},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete OTP entry after successful verification
            otp_instance.delete()
            return Response({"message": "Account verified successfully."}, status=status.HTTP_200_OK)

        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP or no such OTP found."}, status=status.HTTP_404_NOT_FOUND)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Resend OTP to the user's email for account verification.",
        request_body=ResendOTPSerializer,
        responses={
            200: openapi.Response(
                description="OTP resent successfully.",
                examples={"application/json": {"message": "OTP resent successfully."}}
            ),
            400: openapi.Response(
                description="Invalid email or other error.",
                examples={"application/json": {"error": "Invalid email address."}}
            ),
            404: openapi.Response(
                description="User not found.",
                examples={"application/json": {"error": "User with this email does not exist."}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        # Parse the email from the request data
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']

        # Try to get the user by the provided email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a new OTP
        otp = generate_random_otp()  # Make sure this function generates a valid OTP
        otp_instance, created = OTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp, 'created_at': timezone.now()}  # Ensure the OTP is updated with the timestamp
        )

        # Send the OTP via email
        try:
            send_mail(
                'Your OTP Code',
                f'Use this OTP to verify your email: {otp}',
                'noreply@example.com',  # Change to your email
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send OTP. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return success response
        return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)
    

class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Successful login",
                examples={
                    "application/json": {
                        "refresh": "refresh_token_string",
                        "access": "access_token_string",
                        "user_type": "client",
                        "username": "johndoe",
                        "email": "johndoe@example.com",
                        "subscription_type": "basic"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid credentials or unverified account",
                examples={"application/json": {"error": "Invalid credentials."}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        # First validate the incoming data using the LoginSerializer
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
            
            # Check if the user exists and if the credentials are correct
            if user:
                if not user.verified:
                    return Response({"error": "Account not verified. Please verify your email."}, status=status.HTTP_400_BAD_REQUEST)

                # Create JWT tokens
                refresh = RefreshToken.for_user(user)
                subscription = UserSubscription.objects.filter(user=user).first()
                subscription_type = subscription.plan.name if subscription else None

                # Return the successful login response with the user data
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type,
                    'username': user.username,
                    'email': user.email,
                    'subscription_type': subscription_type,
                }, status=status.HTTP_200_OK)
            
            # Invalid credentials error
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        # If the serializer is invalid, handle the validation errors here
        return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Log out a user by blacklisting the JWT refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist')}
        ),
        responses={
            200: "Logged out successfully.",
            400: "Invalid token or request."
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({"error": "Token blacklisting is not enabled. Configure `django-rest-framework-simplejwt` correctly."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Invalid token or request. {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permissions

    @swagger_auto_schema(
        operation_description="Reset a user's password using the token.",
        request_body=ResetPasswordSerializer,
        responses={
            200: "Password reset successful.",
            400: "Invalid token or password."
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid or non-existent token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_token.expiry_date < timezone_now():
            return Response({"error": "Token has expired. Request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.delete()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    

class ForgotPasswordView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permissions

    @swagger_auto_schema(
        operation_description="Send a password reset token to the user's email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email')}
        ),
        responses={
            200: "Password reset token sent.",
            400: "No user found with this email."
        }
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        expiry_date = timezone_now() + timedelta(hours=1)  # Token valid for 1 hour

        PasswordResetToken.objects.create(user=user, token=token, expiry_date=expiry_date)

        send_mail(
            'Password Reset Request',
            f'Use this token to reset your password: {token}. The token expires in 1 hour.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset token sent."}, status=status.HTTP_200_OK)



class ProfileCreateView(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a profile for the authenticated user.",
        responses={201: "Profile created successfully."}
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update the profile of the authenticated user.",
        responses={200: "Profile updated successfully."}
    )
    def get_object(self):
        return self.request.user.profile


# FOR ADMIN USER

class AdminCreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create a new user as an admin.",
        responses={201: "User created successfully."}
    )
    def perform_create(self, serializer):
        serializer.save()


class AdminDeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Delete a user by ID as an admin.",
        responses={
            204: "User deleted successfully.",
            404: "User not found."
        }
    )
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

