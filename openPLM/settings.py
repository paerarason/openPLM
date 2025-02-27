#-!- coding:utf-8 -!-
# Django settings for openPLM project.
# settings that you may have to modify are marked with a #XYZ: comment
# File for django settings

import sys
import os.path

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

#XYZ: once your installation is ok, you should change this to False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #XYZ: some error are notified to this address
    ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS




#XYZ: Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/django/openPLM/trunk/openPLM/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATIC_URL = "/static/"

# Make this unique, and don't share it with anybody.
# XYZ: the script change_secret_key.py can do this for you
SECRET_KEY = '0ham7d#fh669-xi@wxf1wcpbhn6tbbegtv_cml()_wcboyw&u&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'openPLM.plmapp.middleware.locale.ProfileLocaleMiddleware',
)
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, "locale"),
)

ugettext = lambda s: s
LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
    ('ja', '日本語'),
    ('ru', 'Русский'),
    ('zh-hans', '中文'),
)

ROOT_URLCONF = 'openPLM.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/var/django/openPLM/trunk/openPLM/templates",
)
USE_TZ = True

MIGRATION_MODULES = {'plmapp': 'plmapp.migrations'}

#: list of installed apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_comments',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'djcelery',
    'haystack',
    'openPLM.plmapp',
    'openPLM.apps.rss',
    'openPLM.apps.pdfgen', # enable pdf generations
    #XYZ: you can add your application after this line
    'openPLM.apps.cad',
    'openPLM.apps.computer',
    'openPLM.apps.cae',
    'openPLM.apps.office',
    # document3D requires pythonOCC, uncomment this line to enable it
     'openPLM.apps.document3D',
     'openPLM.apps.subversion',
)

COMMENTS_APP = "openPLM.plmapp"
# comment these settings to disable the MarkDown syntax
RICHTEXT_FILTER = 'openPLM.plmapp.filters.markdown_filter'
RICHTEXT_WIDGET_CLASS = 'openPLM.plmapp.widgets.MarkdownWidget'


CELERY_CREATE_MISSING_QUEUES = True
CELERY_ROUTES = {
    "openPLM.plmapp.tasks.update_index": {"queue": "index"},
    "openPLM.plmapp.tasks.update_indexes": {"queue": "index"},
    "openPLM.plmapp.tasks.remove_index": {"queue": "index"},
    "openPLM.plmapp.mail.do_send_histories_mail" : {"queue" : "mails"},
    "openPLM.plmapp.mail.do_send_mail" : {"queue" : "mails"},
}
if "openPLM.apps.document3D" in INSTALLED_APPS:
    CELERY_ROUTES.update({
        "openPLM.apps.document3d.models.handle_step_file": {"queue": "step"},
        "openPLM.apps.document3d.models.decomposer_all": {"queue": "step"},
    })

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_CONFIG_MODULE = 'your_celery_config_module'

#XYZ: allowed hosts
#: see :django:setting:`ALLOWED_HOSTS`
ALLOWED_HOSTS = ["*"]
DEBUG = True 
#XYZ: EMAIL settings
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-EMAIL_HOST
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

#: True if mails sending should fail silently. If False, all connection errors
#: to the SMTP server will be logged by celery (`/var/log/celery/*.log`).
EMAIL_FAIL_SILENTLY = True

#: directory that stores documents. Make sure to use a trailing slash.
DOCUMENTS_DIR = "/var/openPLM/docs/"
#: directory that stores thumbnails. Make sure to use a trailing slash.
THUMBNAILS_DIR = os.path.join(MEDIA_ROOT, "thumbnails/")
#: URL where thumbnails are located . Make sure to use a trailing slash.
THUMBNAILS_URL = MEDIA_URL + "thumbnails/"

# Cookie used for session is temporary and is deleted when browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Add user, messages and perms variables in RequestContext
TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.request",
        "django.contrib.messages.context_processors.messages",
        )
import os
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}


MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # ...
]

#XYZ:
#: expeditor's mail used when sending notification emails
EMAIL_OPENPLM = "no-reply@openplm.example.com"

#XYZ:
#: Subject of a sponsor mail.
#: It can be a valid django template string, two variables are available:
#: ``new_user`` and ``sponsor`` (:class:`.User` instances)
#: for example, it could be
#: ``u"Welcome {{new_user.get_full_name}}, {{sponsor.get_full_name}} has sponsored you on OpenPLM"``.
NEW_ACCOUNT_SUBJECT = "New account on OpenPLM"

#: Max file size for documents in bytes, -1 means illimited
MAX_FILE_SIZE = -1

# search stuff
#if "rebuild_index" not in sys.argv:
#HAYSTACK_ENABLE_REGISTRATIONS = False
#HAYSTACK_SITECONF = 'openPLM.plmapp.search_sites'
#HAYSTACK_SEARCH_ENGINE = 'xapian'
#HAYSTACK_XAPIAN_PATH = "/var/openPLM/xapian_index/"
#EXTRACTOR = os.path.abspath(os.path.join(os.path.dirname(__file__), "bin", "extractor.sh"))
import os 
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'openPLM/templates')],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR/"media"
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:9001/solr/default',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
    'autocomplete': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/home/search/whoosh_index',
        'STORAGE': 'file',
        'POST_LIMIT': 128 * 1024 * 1024,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
    'db': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    }
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

# celery stuff
#import djcelery
#djcelery.setup_loader()

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "openplm"

#XYZ: you will have to change this password
# it must be the same as the one set by the command ``rabbitmqctl add_user openplm 'secret'``
BROKER_PASSWORD = "secret"
BROKER_VHOST = "openplm"

BROKER_URL = "amqp://%s:%s@%s:%d/%s" % (BROKER_USER,
        BROKER_PASSWORD, BROKER_HOST, BROKER_PORT, BROKER_VHOST)
del BROKER_USER, BROKER_PASSWORD, BROKER_HOST, BROKER_PORT, BROKER_VHOST

#Gestion native
ENABLE_NATIVE_FILE_MANAGEMENT=True


# change these settings to True to force https connection
#: set to True so that browsers ensure the cookie is only sent under an HTTPS connection
SESSION_COOKIE_SECURE = False
#: Force HTTPS connections
FORCE_HTTPS = False

#: set to True to hide emails
HIDE_EMAILS = False

#: Never delete files. If a user deletes a file, the file is deprecated instead of being deleted.
#: Warning, if set to True, OpenPLM may consume a lot of disk place.
KEEP_ALL_FILES = False

COMPANY = "company"

# change this setting if you use an other user documentation for OpenPLM
DOCUMENTATION_URL = "http://wiki.openplm.org/docs/user/"
