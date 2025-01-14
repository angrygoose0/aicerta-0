# Generated by Django 4.2 on 2024-03-15 22:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0056_alter_markedchunks_common_questions"),
    ]

    operations = [
        migrations.CreateModel(
            name="NceaUserImages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="")),
                (
                    "user_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.nceauserquestions",
                    ),
                ),
            ],
            options={
                "ordering": ["user_question"],
            },
        ),
    ]
