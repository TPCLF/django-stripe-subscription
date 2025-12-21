import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = 'mdyerga@gmail.com'
new_password = 'rickmoranis2@gmail.com'

try:
    u = User.objects.get(email=email)
    u.set_password(new_password)
    u.save()
    print('updated', u.email, 'check_password:', u.check_password(new_password))
except User.DoesNotExist:
    print('no user with email', email)
