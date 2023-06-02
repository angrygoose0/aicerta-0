# Generated by Django 4.2 on 2023-05-27 22:58

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Emails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("from_email", models.TextField()),
                ("subject", models.TextField()),
                ("message", models.TextField()),
            ],
        ),
    ]