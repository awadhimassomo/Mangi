# registration/management/commands/remove_duplicates.py

from django.core.management.base import BaseCommand
from registration.models import Customer

class Command(BaseCommand):
    help = 'Remove duplicate phone numbers in Customer table'

    def handle(self, *args, **kwargs):
        from django.db.models import Count

        duplicates = (Customer.objects
                      .values('phoneNumber')
                      .annotate(count=Count('id'))
                      .order_by()
                      .filter(count__gt=1))

        for duplicate in duplicates:
            customers = Customer.objects.filter(phoneNumber=duplicate['phoneNumber'])
            # Keep the first entry and delete the rest
            for customer in customers[1:]:
                customer.delete()

        self.stdout.write("Duplicates removed.")
