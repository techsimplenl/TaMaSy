from django.db import models

from django.contrib.auth.models import AbstractUser, AbstractBaseUser,BaseUserManager

# Create your models here.



 
class User(AbstractUser):
    
    login_attempts = models.IntegerField(blank=False,null=False,default=0)
    blocked = models.BooleanField(blank=False, default=False)
    
    def __str__(self):
        return self.username + "," + self.email
    
class AttempsLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempt_date = models.DateTimeField(blank=False,null=False,default=False,)
    
    class Meta:
        verbose_name = "Access attempt"
        
class EmailPasswordReset(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    time_email_sent = models.DateTimeField(blank=False,null=False,default=False,)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.code 