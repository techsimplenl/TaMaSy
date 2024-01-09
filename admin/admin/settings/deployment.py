from .settings import *

DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS')]

SECRET_KEY = os.environ.get('SECRET_KEY') #here

# Docker

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'), #here 
        'USER': os.environ.get('DB_USER'), #here
        'PASSWORD': os.environ.get('DB_PASS'), #here
        'HOST': os.environ.get('DB_HOST'), #here 
        'PORT': os.environ.get('DB_PORT'),
    }
}

#EMail 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # e.g., 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
#Locally

# settings.py

MY_HOST_LINK = 'http://127.0.0.1:8000'


