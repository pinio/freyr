# Generated by Django 2.2.12 on 2020-04-27 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0005_project_repositories"),
    ]

    operations = [
        migrations.AddField(
            model_name="repository",
            name="min_date",
            field=models.DateTimeField(null=True),
        ),
    ]
