# registration/management/commands/find_duplicates.py

from django.core.management.base import BaseCommand
from registration.models import Customer

class Command(BaseCommand):
    help = 'Find duplicate phone numbers in Customer table'

    def handle(self, *args, **kwargs):
        from django.db.models import Count

        duplicates = (Customer.objects
                      .values('phoneNumber')
                      .annotate(count=Count('id'))
                      .order_by()
                      .filter(count__gt=1))

        for duplicate in duplicates:
            self.stdout.write(f"Phone number {duplicate['phoneNumber']} has {duplicate['count']} duplicates.")
