# Generated by Django 4.2 on 2023-10-28 22:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0022_criteria_image_alter_nceasecondaryquestion_evidence"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nceasecondaryquestion",
            name="evidence",
            field=models.TextField(blank=True, null=True),
        ),
    ]
