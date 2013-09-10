# flake8: noqa
from settings_shared import *

STATSD_HOST = '127.0.0.1'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lettuce.db',
        'OPTIONS': {
            'timeout': 30,
        }
    }
}


LETTUCE_SERVER_PORT = 8002
BROWSER = 'Headless' # ["Chrome", "Firefox", "Headless"]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LETTUCE_APPS = (
    'mediathread.main',
    'mediathread.projects',
    'mediathread.assetmgr',
    'mediathread.djangosherd'
)

#ACCOUNT_AUTHENTICATION_METHOD = "username_email"
#ACCOUNT_EMAIL_VERIFICATION = "optional"


LETTUCE_DJANGO_APP = ['lettuce.django']
INSTALLED_APPS = INSTALLED_APPS + LETTUCE_DJANGO_APP

CUSTOMERIO_SITE_ID = ''
CUSTOMERIO_API_KEY = ''
ACCOUNT_LOGOUT_ON_GET = True
SOUTH_TESTS_MIGRATE = False

# Full run
# time(./manage.py harvest --settings=mediathread.settings_test \
# --debug-mode --verbosity=2 --traceback)

# Run a particular file + scenario
# ./manage.py harvest \
# mediathread/main/features/manage_selection_visibility.feature \
# -d --settings=mediathread.settings_test -s 1

class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'courseaffils.middleware.CourseManagerMiddleware',
    'mediathread.main.middleware.AuthRequirementMiddleware',
    'mediathread.course.middleware.CallToActionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mediathread.settings_test.ExceptionLoggingMiddleware'
)
