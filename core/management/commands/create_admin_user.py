from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from proce import settings

class Command(BaseCommand):
    help = 'Create an admin user'

    def handle(self, *args, **options):
        try:
            User.objects.get(username='admin')
        except ObjectDoesNotExist:
            User.objects.create_superuser(
                username='admin', email=settings.ADMIN_EMAIL, password=settings.ADMIN_PASSWORD
            )