# apps/users/migrations/0003_cloudinary_avatar.py
from django.db import migrations
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_profile_options_alter_user_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="avatar",
            field=cloudinary.models.CloudinaryField(
                "avatar", blank=True, null=True,
            ),
        ),
    ]
