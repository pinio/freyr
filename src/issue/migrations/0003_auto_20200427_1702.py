# Generated by Django 2.2.12 on 2020-04-27 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("issue", "0002_issue_invalid"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="kanban_total_blocked_time",
            field=models.PositiveIntegerField(blank=True, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="issue",
            name="kanban_total_hold_time",
            field=models.PositiveIntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
