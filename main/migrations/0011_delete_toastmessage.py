# Generated by Django 4.2 on 2023-09-16 00:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_remove_toastmessage_exam_name_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ToastMessage",
        ),
    ]
