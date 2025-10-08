from .serializer import LoginSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import LoginModel
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta   
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

User = get_user_model()

#registration view
class RegistrationView(APIView):
    def post(self,request):
        try:
            serializer = RegistrationSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"details":"Account was successfully registered"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"details":f"An internal error {e} occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
        
#login view
class LoginView(APIView):
    def post(self,request):
        try:
            serializer = LoginSerializer(data = request.data)
            if serializer.is_valid():
                user=serializer.user
                
                
                #check if it has expired(POV: CHANGE IT TO 3 MINS BEFORE PRODUCTION)
                expired_at = timezone.now() + timedelta(days=3)
                #send link
                magic_token = LoginModel.objects.create(user=user, expired_at=expired_at)
               
                
                link = f"{settings.FRONTEND_URL}/login/magic?token={magic_token.token}&redirect=/dashboard"
                
                #send mail
                send_mail(
                    subject='Logic Link was sent successfully',
                    message= f'Kindly uses this link to login:{link} ,please remember that this link expires after 3 minutes',
                    from_email= "pain@xyz.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                    )
                return Response({'details':"A login link has been sent to your email"},status=status.HTTP_200_OK)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"details":f"An error {e} occurred"}, status=status.HTTP_400_BAD_REQUEST)
        
    


#consume link once the user get the token
class ConsumeLink(APIView):
    def post(self,request):
        token_value = request.data.get('token')
        try:
            magic_token = LoginModel.objects.get(token=token_value)
        except LoginModel.DoesNotExist:
            return Response({'details':"Login Link could'nt be found"}, status=status.HTTP_400_BAD_REQUEST)
        
        if timezone.now() > magic_token.expired_at:
            return Response({'details':"Login Link has expired"}, status=status.HTTP_410_GONE)
        
        # check if the link has been used
        if magic_token.used:
            return Response({'details':"Link has been used!, try to login again"}, status=status.HTTP_401_UNAUTHORIZED)
        
        #pass a jwt
        user = magic_token.user
        refresh = RefreshToken.for_user(user)
        
        response = Response({'access':str(refresh.access_token)})
        
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            secure=False,   # change the secure to true after development
            httponly=True,     
            samesite='Strict',
            max_age=60*60*24*7,
        )
        return response
        
#Refresh token
class RefreshAccessToken(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response({'details':"No refresh token was found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            return Response({'access':new_access})
        except Exception:
            return Response({'details':"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

#logout User
class Logout(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
                return Response({"details":"Token not found"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"details": f"Invalid or expired token: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)
        
        response = Response({"details":"Logout successfully"}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh")
        return response


