# Create a new migration file manually in the migrations folder
from django.db import migrations, models

def populate_default_warehouse(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    Warehouse = apps.get_model('inventory', 'Warehouse')
    default_warehouse = Warehouse.objects.first()  # Use a sensible default or create one

    for product in Product.objects.all():
        product.warehouse = default_warehouse
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_<timestamp>'),
    ]

    operations = [
        migrations.RunPython(populate_default_warehouse),
    ]

