
# Create your views here.

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from .serializers import UserSerializer,RegisterUserSerializer,LoginSerializer,LogoutSerializer,SendEmailSerializer,PasswordResetSerializer
from datetime import datetime
from .models import User,EmailPasswordReset
from django.contrib.auth import login,logout
from rest_framework.authtoken.models import Token
import random
import string
from dateutil.parser import parse
import pytz 
from django.shortcuts import get_object_or_404

def get_queryset():
   return  User.objects.all()

# Function to send the email to the user
def difference_between_current_save_time(time):
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'
    parsed_datetime = parse(time)
    current_datetime = datetime.now(tz=pytz.utc)
    time_out = current_datetime - parsed_datetime
    time_minutes = time_out.total_seconds() / 60
    rounded_minutes = round(time_minutes)
    return rounded_minutes

class UserRegister(generics.CreateAPIView):
    queryset = get_queryset()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            data['msg'] = 'user successfuly registered'
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class LoginView(generics.GenericAPIView):
   
    queryset = get_queryset()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request,format=None):
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        if user is not None:
            if user.is_active and user.blocked != True:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'status': status.HTTP_202_ACCEPTED, 'token': token.key, 'user_id': user.pk,'email':user.email})
            else:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'error': 'This user is not active.'})
        else:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'error': 'Invalid credentials.'})
            
class LogoutView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            # Perform logout logic here
            logout(request)
            request.auth.delete()
            # Add your code to handle logout and token invalidation
            return Response({'status':status.HTTP_200_OK})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
class UserListView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = get_queryset()
    serializer_class = UserSerializer
    
class SendEmailView(generics.GenericAPIView):
    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]
    
    def get_user(self,email):
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            return user
        return None 
        
    def post(self, request, format=None):
        
        user = self.get_user(request.data['email'])
        time = 0
        if user is not None:
            if EmailPasswordReset.objects.filter(user=user).exists(): 
                object = EmailPasswordReset.objects.get(user=user)
                serializer = self.serializer_class(object)
                time = serializer.data['time_email_sent']
            else:
                
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=25))
                data = {
                    'user': user.pk,
                    'code': code,
                }
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    time = serializer.data['time_email_sent']
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
            return Response({'message':f'Email already sent! Check your email to reset the password.The email is valid for 15 minutes'}, status=status.HTTP_200_OK)
        else:
            return Response({'error: User not found!Are you sure you have account'}, status=status.HTTP_404_NOT_FOUND)
              
class CodeStillValidView(generics.GenericAPIView):
    
    serializer_class = SendEmailSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        code = request.data['code']
        object = get_object_or_404(EmailPasswordReset, code=code)
        serializer = self.serializer_class(object)
        time = difference_between_current_save_time(serializer.data['time_email_sent'])
        print(time)
        if time <= 15:
            #the user can reset the password
            return Response({'status':True})
        else:
            object.delete()
            return Response({'status': False})
        
class PasswordResetView(generics.GenericAPIView):
    # queryset = get_queryset()
    permission_classes = (AllowAny,)
    serializer_class = PasswordResetSerializer
    
    def post(self,request,format=None):
        # get the user id with the code given
        code = request.data['code']
        
        user = get_object_or_404(EmailPasswordReset, code=code)
        data = {
            'id': user.user_id,
            'password': request.data['password'],
            'password2': request.data['password2']
        }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response({'msg':'the password is reset! now u can login with the new password'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # print(user)
        
        