from django.urls import path,include
 
# from rest_framework import routers
 
from accounts.views import UserListView,UserRegister,LoginView,LogoutView,SendEmailView,CodeStillValidView,PasswordResetView
 
# router = routers.DefaultRouter()
# router.register("users", UserViewSet)
 
urlpatterns = [
    path("", UserListView.as_view(),name='list'),
    path("login",LoginView.as_view(),name='login'),
    path("register",UserRegister.as_view(),name='register'),
    path("logout",LogoutView.as_view(),name='logout'),
    path("send-email",SendEmailView.as_view(),name='send-email'),
    path("code-validation",CodeStillValidView.as_view(),name='code-validation'),
    path("reset-password",PasswordResetView.as_view(),name='reset-password'),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]