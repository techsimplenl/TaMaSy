from rest_framework import serializers
from .models import User,AttempsLogin,EmailPasswordReset
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from datetime import datetime,timezone
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

# Function to convert minutes to hours and minutes
def convert_minutes_to_hours_and_minutes(minutes):
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return hours, remaining_minutes

def send_email_view(emailTo,code):
    link = getattr(settings, 'MY_HOST_LINK')
    subject = f'Reset password {emailTo}'
    
    message = 'Reset password'
    
    html_message = '<h1>This is the link to update your password.</h1>'
    html_message += '<p>Click to the link below to reset your password</br><a href="'f'{link}/password_reset/{code}''">'f'{link}/password_reset/{code}''</a></p>'
    emailFrom = 'noreply@techsimple.nl'
    email_to = [emailTo]
    send_mail(
        subject, message, emailFrom, email_to,
        fail_silently=False, html_message=html_message
    )

class RegisterUserSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        if not (
            any(char.isdigit() for char in attrs['password']) and
            any(char.isupper() for char in attrs['password']) and
            any(char.islower() for char in attrs['password']) and
            any(not char.isalnum() for char in attrs['password'])
        ):
            raise serializers.ValidationError("The password must have at least 8 characters, 1 capital letter, 1 uppercase letter, 1 number, and 1 special character.")
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        data = {}
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        data['email'] = user.email
        data['username'] = user.username
        return data

class LoginSerializer(serializers.Serializer):
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def login_user(self,user):
        if not user.is_active:
            raise serializers.ValidationError('This user is not active.')        
        # If authentication succeeds, reset the login attempts
        user.login_attempts = 0
        user.save()
    
    def attempt_function(self,username,max_login_attempts):
        
        user = User.objects.filter(username=username).first()
        login_attempts = getattr(user, 'login_attempts', 0)
        current_time = datetime.now(tz=timezone.utc)
        
        if user.blocked != True:
            
            if login_attempts < max_login_attempts:
                user.login_attempts = login_attempts + 1
                user.save()
                raise serializers.ValidationError(user.login_attempts)
            else:
                data = {
                'attempt_date': current_time,
                'user':user
                }
                user.blocked = True
                user.save()
                attemps = AttempsLogin.objects.create(**data)
                attemps.save()
                raise serializers.ValidationError(f'Maximum login attempts exceeded. Account locked. you can try again in {15} minute(s)')        
        else:
            attemp = AttempsLogin.objects.filter(user=user).first()
            time_stay_to_try_again = current_time - getattr(attemp, 'attempt_date')
            time_minutes = time_stay_to_try_again.total_seconds() / 60
            rounded_minutes = round(time_minutes)
            hours, remaining_minutes = convert_minutes_to_hours_and_minutes(rounded_minutes)
            limutes_time = 15
            if rounded_minutes < limutes_time: 
                raise serializers.ValidationError(f'Maximum login attempts exceeded. Account locked. you can try again in {15 - rounded_minutes} minute(s)')   
            user.blocked = False
            user.login_attempts = 0
            user.save()
            attemp.delete()
            return True
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if not username or not password:
            raise serializers.ValidationError('Must include "username" and "password".')
          
        data = {
            'username':username,
            'password':password
        }
        user  = authenticate(**data)
        if user:    
            self.login_user(user)
        else:
            max_login_attempts = 3
            if User.objects.filter(username=username).exists():
                can_login_ = self.attempt_function(username,max_login_attempts)
                if can_login_ == True:
                    if user :
                        self.login_user(user)
                    else:
                        self.attempt_function(username,max_login_attempts)
                raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs

class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate_token(self, value):
        try:
            data = Token.objects.get(key=value)
            return data
        except Exception as e:
            return serializers.ValidationError(str(e))
        
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email','username','date_joined','last_login','is_active','is_superuser']
        
class SendEmailSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    code = serializers.CharField()
    time_email_sent = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = EmailPasswordReset
        fields = ['user', 'code']
    
    def validate(self, data):
        current_time = datetime.now(tz=timezone.utc)
        query = {
            'user': data['user'],
            'code': data['code'],
            'time_email_sent': current_time
        }
        email_object = EmailPasswordReset.objects.create(**query)
        send_email_view(data['user'].email,email_object.code)
        return email_object

class PasswordResetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    password = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('id','password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        if not (
            any(char.isdigit() for char in attrs['password']) and
            any(char.isupper() for char in attrs['password']) and
            any(char.islower() for char in attrs['password']) and
            any(not char.isalnum() for char in attrs['password'])
        ):
            raise serializers.ValidationError("The password must have at least 8 characters, 1 capital letter, 1 uppercase letter, 1 number, and 1 special character.")
        
        user_object = get_object_or_404(User, pk=attrs['id'])
        user_object.set_password(attrs['password'])
        user_object.save()
        return user_object