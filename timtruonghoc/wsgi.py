"""
WSGI config for timtruonghoc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timtruonghoc.settings')
os.environ['GOOGLE_CLIENT_ID'] = '875195545395-kh54279ju4pea3h5n1b85uj3hohn0aih.apps.googleusercontent.com'

print(f"DEBUG: GOOGLE_CLIENT_ID is set to {os.environ.get('GOOGLE_CLIENT_ID')}")
application = get_wsgi_application()





