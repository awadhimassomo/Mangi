from django.db import models

# Create your models here.
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from inventory.models import Product

class QRCode(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='qr_code')
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Prepare product data
        product_data = (
            f"Product ID: {self.Product.id}\n"
            f"Name: {self.Product.ProductName}\n"
            f"Price: ${self.Product.Price:.2f}"
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        # Save QR code as an image file
        temp_name = f"{self.Product.id}-qr.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_image.save(temp_name, File(buffer), save=False)
        buffer.close()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for {self.Product.ProductName}"


class DynamicQRCode(models.Model):
    data = models.TextField("Data to encode", help_text="This field can contain any text, URL, etc.")
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        temp_name = f"qr-{self.pk}.png" if self.pk else "qr-new.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        self.qr_image.save(temp_name, File(buffer), save=False)
        buffer.close()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for data: {self.data[:50]}"  # Display first 50 characters of data

