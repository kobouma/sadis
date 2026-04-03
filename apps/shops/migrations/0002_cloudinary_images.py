# apps/shops/migrations/0002_cloudinary_images.py
from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("shops", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shop",
            name="logo",
            field=cloudinary.models.CloudinaryField(
                "logo", blank=True, null=True,
            ),
        ),
        migrations.AlterField(
            model_name="shop",
            name="banner",
            field=cloudinary.models.CloudinaryField(
                "banner", blank=True, null=True,
            ),
        ),
    ]
