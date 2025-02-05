# Generated by Django 4.2 on 2024-01-30 00:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0041_assignment_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="ends_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assignment",
            name="status",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="nceauserdocument",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="main.assignment",
            ),
        ),
        migrations.AddField(
            model_name="nceauserdocument",
            name="editable",
            field=models.BooleanField(default=True),
        ),
    ]
