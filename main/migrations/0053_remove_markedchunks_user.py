# Generated by Django 4.2 on 2024-02-27 03:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0052_alter_criteria_options_remove_markedchunks_alpha_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="markedchunks",
            name="user",
        ),
    ]