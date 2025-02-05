# Generated by Django 4.2 on 2023-09-10 04:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0006_remove_toastmessage_message_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="toastmessage",
            name="document",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.nceauserdocument",
            ),
        ),
        migrations.AlterField(
            model_name="toastmessage",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="toast",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
