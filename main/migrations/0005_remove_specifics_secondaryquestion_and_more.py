# Generated by Django 4.2 on 2023-05-19 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_rename_a1_nceaquestion_n1"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="specifics",
            name="secondaryquestion",
        ),
        migrations.AddField(
            model_name="specifics",
            name="nceaQUESTION",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main.nceaquestion",
            ),
        ),
    ]