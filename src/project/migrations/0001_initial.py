# Generated by Django 2.2.12 on 2020-04-23 17:00

import django.db.models.deletion
from django.db import migrations, models

import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Repository",
            fields=[
                (
                    "_id",
                    djongo.models.fields.ObjectIdField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("organization", models.CharField(max_length=64)),
                ("code", models.CharField(max_length=64)),
                ("name", models.CharField(max_length=128)),
            ],
            options={"verbose_name_plural": "Repositories"},
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "_id",
                    djongo.models.fields.ObjectIdField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("number", models.PositiveIntegerField()),
                (
                    "organization",
                    models.CharField(blank=True, max_length=64, null=True),
                ),
                (
                    "repository",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.Repository",
                    ),
                ),
            ],
        ),
    ]
