# apps/orders/migrations/0002_c2c_refactor.py
# Migration manuelle — remplace le modèle panier par commande directe C2C
import uuid
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Supprimer CartItem, Cart, OrderItem ───────────────
        migrations.DeleteModel(name="CartItem"),
        migrations.DeleteModel(name="Cart"),
        migrations.DeleteModel(name="OrderItem"),

        # ── Ajouter les nouveaux champs sur Order ─────────────
        migrations.AddField(
            model_name="order",
            name="product",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="products.product",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="product_name",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="variant_label",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="unit_price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=12,
                validators=[django.core.validators.MinValueValidator(0)]
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="quantity",
            field=models.PositiveIntegerField(
                default=1,
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_type",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="delivery_fee",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="order",
            name="shipped_at",
            field=models.DateTimeField(blank=True, null=True),
        ),

        # ── Mettre à jour les statuts de Order ────────────────
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending",    "En attente de paiement"),
                    ("paid",       "Payé"),
                    ("preparing",  "En préparation"),
                    ("shipped",    "Expédié"),
                    ("delivering", "En livraison"),
                    ("delivered",  "Livré"),
                    ("disputed",   "Litige"),
                    ("refunded",   "Remboursé"),
                    ("cancelled",  "Annulé"),
                ],
                db_index=True, default="pending", max_length=20,
            ),
        ),
    ]