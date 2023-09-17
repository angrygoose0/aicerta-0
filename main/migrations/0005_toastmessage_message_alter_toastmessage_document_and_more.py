# Generated by Django 4.2 on 2023-09-09 22:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0004_toastmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="toastmessage",
            name="message",
            field=models.TextField(default=None, max_length=100),
            preserve_default=False,
        ),
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
