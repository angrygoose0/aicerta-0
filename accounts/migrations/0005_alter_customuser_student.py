# Generated by Django 4.2 on 2024-02-06 00:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_customuser_student"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="student",
            field=models.BooleanField(default=True),
        ),
    ]
