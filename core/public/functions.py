import os

from django.conf import settings
from django.utils import timezone

import public.models as model

def GlobalContext(request):
    
    """
    Generates a global context with basic user information for use by all views of the project.
    "public/core/settings.py"
    TEMPLATES = [{'OPTIONS': {'context_processors': ['public.functions.GlobalContext',],},},]
    """
    
    try:
        settings = model.Settings.objects.first()
    except Exception as e:
        with open(os.path.join(settings.BASE_DIR, 'logs/django.log'), 'a') as f:
            settings = []
            eDate = timezone.now().strftime("%Y-%m-%d %H:%M")
            f.write("Undefined Settings--> Date: {} Error: {}\n".format(eDate, str(e)))

    return {
        'settings':settings,
        }