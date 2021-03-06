"""
Django settings for betterstart project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# Get the secret key from the environment variable; default is only here to support local development
SECRET_KEY = os.getenv('BETTERSTART_SK','=lnd59!%m+51yz(h&-ud07cs8a(1kzw&_utqjoxi+50+=45f44')

# Get the debug flag from the relevant environment variable
if os.getenv('BETTERSTART_DEBUG',None) == 'True':
	DEBUG = True
# otherwise turn off debug
else:
	DEBUG = False

ALLOWED_HOSTS = [
	'betterstart-236907.appspot.com',
	'127.0.0.1',
	'oysta.org',
	'www.oysta.org',
	'betterstart.oysta.org',
	'betterstart-uat.appspot.com',
]

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'people.apps.PeopleConfig',
	'crispy_forms',
	'django_otp',
	'django_otp.plugins.otp_totp',
	'django_otp.plugins.otp_hotp',
	'django_otp.plugins.otp_static',
	'zxcvbn_password',
	'jsignature',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django_otp.middleware.OTPMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'betterstart.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'betterstart.wsgi.application'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

OTP_TOTP_ISSUER = os.getenv('BETTERSTART_OTP_ISSUER','Betterstart OTP Default')

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if os.getenv('BETTERSTART_DB', None) == 'local':
	DATABASES = {
			'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
		}
	}
elif os.getenv('GAE_APPLICATION', None):
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'HOST': os.getenv('BETTERSTART_DB_HOST', None),
			'USER': os.getenv('BETTERSTART_DB_USER', None),
			'PASSWORD': os.getenv('BETTERSTART_PW', None),
			'NAME': os.getenv('BETTERSTART_DB_NAME', None),
		}
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'HOST': '127.0.0.1',
			'PORT': os.getenv('BETTERSTART_DB_PORT', None),
			'NAME': os.getenv('BETTERSTART_DB_NAME', None),
			'USER': os.getenv('BETTERSTART_DB_USER', None),
			'PASSWORD': os.getenv('BETTERSTART_PW', None),
		}
	}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
	{
		'NAME': 'zxcvbn_password.ZXCVBNValidator',
		'OPTIONS': {
			'min_score': 3,
			'user_attributes': ('username', 'email', 'first_name', 'last_name')
		}
	},
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

# Authentication

LOGIN_URL = '/people/login'

# Sendgrid email settings
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
