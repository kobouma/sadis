# apps/products/migrations/0002_cloudinary_images.py
from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimage",
            name="file",
            field=cloudinary.models.CloudinaryField(
                "image",
                blank=True,
                null=True,
            ),
        ),
    ]
