from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR.child('db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '****',
        'USER': '****',
        'PASSWORD': '****',
        'HOST': '0.0.0.0',
        'PORT': '5432',
    }

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = '/static/' #BASE_DIR.child('static')

STATIC_URL = '/static/'

STATICFILES_DIRS = [BASE_DIR.child('static')]

MEDIA_ROOT = BASE_DIR.child('media')

MEDIA_URL = '/media/'


# email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIT_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rafalopezrl749@gmail.com'
EMAIL_HOST_PASSWORD = 'R@f@el1995'


# ADMINS = (('Admin', 'rafalopezrl749@gmail.com'),)


# LOGGING = {
# 'version': 1,
# 'disable_existing_loggers': False,
# 'handlers': {
# 'mail_admins': {
# 'level': 'ERROR',
# 'class': 'django.utils.log.AdminEmailHandler'
# }
# },
# 'loggers': {
# 'django.request': {
# 'handlers': ['mail_admins'],
# 'level': 'ERROR',
# 'propagate': True,
# },
# }
# }
