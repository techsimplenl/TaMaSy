from .settings import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# SECRET_KEY = os.environ.get('SECRET_KEY') #here
SECRET_KEY ='django-insecure-6jk147!82%+v08z4*vi)rua78b!w5b112z1_i7ikm%mr+*tc%c' #here

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # or 'INFO' for less detailed information
    },
}


#EMail 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # e.g., 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mutarayvan123@gmail.com'
EMAIL_HOST_PASSWORD = 'roqdtxabueakgggk'
#Locally

# settings.py

MY_HOST_LINK = 'http://127.0.0.1:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'adminDB', #here 
        'USER':'admin', #here
        'PASSWORD': 'test1234@', #here
        'HOST': 'localhost', #here 
        'PORT': 5432,
    }
}