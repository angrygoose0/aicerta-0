# Generated by Django 4.2 on 2024-02-26 21:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0050_alter_nceaquestion_question"),
        ("accounts", "0005_alter_customuser_student"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="example_marks",
            field=models.ManyToManyField(
                blank=True, related_name="examplemark", to="main.bulletpoint"
            ),
        ),
    ]
