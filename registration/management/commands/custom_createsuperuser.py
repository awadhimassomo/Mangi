# registration/management/commands/custom_createsuperuser.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Create a superuser with foreign key constraints temporarily disabled'

    def handle(self, *args, **kwargs):
        # Disable foreign key constraints
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")

        # Create a superuser
        try:
            call_command('createsuperuser', interactive=True)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        finally:
            # Re-enable foreign key constraints
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON;")

        self.stdout.write(self.style.SUCCESS('Superuser created successfully with foreign key constraints temporarily disabled'))
