# Generated by Django 4.2 on 2023-11-22 00:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0034_alter_bulletpoint_b_alter_bulletpoint_g_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bulletpoint",
            name="no",
            field=models.IntegerField(default=0),
        ),
    ]