"""
WSGI config for sipustaka project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

path = '/home/fudhailalatsary/web-sipustaka/'

if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'sipustaka.settings'
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()