# Generated by Django 4.2 on 2023-11-12 01:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0031_remove_nceauserquestions_achievement_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bulletpoint",
            name="b",
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name="bulletpoint",
            name="g",
            field=models.CharField(default=0, max_length=5),
        ),
        migrations.AddField(
            model_name="bulletpoint",
            name="r",
            field=models.CharField(default=0, max_length=5),
        ),
    ]
