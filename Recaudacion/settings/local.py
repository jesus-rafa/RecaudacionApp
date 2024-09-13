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
        'PORT': '5432',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = BASE_DIR.child('static')

STATIC_URL = '/static/'

#STATICFILES_DIRS = [BASE_DIR.child('static')]

MEDIA_ROOT = BASE_DIR.child('media')

MEDIA_URL = '/media/'
#ckeditor upload path
CKEDITOR_UPLOAD_PATH="uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        # document-items: 'Source','-', 'NewPage', 'Preview', 'Print', '-', ,  'Templates'
        # clipboard:  'PasteText',
        # {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
        #{'name': 'forms','items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton','HiddenField']},
        # basicstyles : ,  'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'
        # paragraph: 'CreateDiv', 'Language'
        #links: , 'Anchor'
        #insert: , 'Iframe' , 'PageBreak'
        #tool items: , 'ShowBlocks'
        #{'name': 'about', 'items': ['CodeSnippet']},
        #{'name': 'about', 'items': ['About']},
        'toolbar_Custom': [
            #{'name': 'document', 'items': ['Save']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste',  '-', 'Undo', 'Redo']}, 
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote',  '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl'
                       ]},  
            '/',       
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline']},           
             
            {'name': 'links', 'items': ['Link', 'Unlink']},

             {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
           
            '/',

            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            
            {'name': 'tools', 'items': ['Maximize']},
           
            {'name': 'insert',
             'items': ['Image','Youtube', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar']},
            
           
           
           
            
            
              # put this to force next toolbar on new line '/',
            #{'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
            #    'Preview',
            #    'Maximize',

            #]},
        ],
        'toolbar': 'Custom',  # put selected toolbar config here
        'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        'height': 250,
        'width': '160%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'toolbarCanCollapse': True,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',# the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'codesnippet',
            
        ]),
    }
}


# email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIT_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '*****'
EMAIL_HOST_PASSWORD = '*****'


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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
