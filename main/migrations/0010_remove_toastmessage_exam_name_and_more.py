# Generated by Django 4.2 on 2023-09-13 22:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0009_toastmessage_document"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="toastmessage",
            name="exam_name",
        ),
        migrations.RemoveField(
            model_name="toastmessage",
            name="user_document_name",
        ),
    ]
