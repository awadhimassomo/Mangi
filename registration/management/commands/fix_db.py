from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from registration.models import Business

class Command(BaseCommand):
    help = 'Create superuser bypassing foreign key constraints'

    def handle(self, *args, **kwargs):
        username = input("Phone number: ")
        password = input("Password: ")

        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys=OFF")

            try:
                # Create superuser
                User = get_user_model()
                User.objects.create_superuser(phoneNumber=username, password=password)
                self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
            finally:
                cursor.execute("PRAGMA foreign_keys=ON")


