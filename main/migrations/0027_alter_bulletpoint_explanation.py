# Generated by Django 4.2 on 2023-10-29 02:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0026_bulletpoint_quoted"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bulletpoint",
            name="explanation",
            field=models.TextField(blank=True, null=True),
        ),
    ]
