# Generated by Django 4.2 on 2023-09-30 01:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0013_file"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="nceaexam",
            name="user",
        ),
        migrations.AddField(
            model_name="nceaexam",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="nceaexam",
            name="users",
            field=models.ManyToManyField(
                blank=True, related_name="nceaexams", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
