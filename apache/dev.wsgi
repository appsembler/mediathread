import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/mediathread/mediathread/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/mediathread/mediathread/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mediathread.settings_dev'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
