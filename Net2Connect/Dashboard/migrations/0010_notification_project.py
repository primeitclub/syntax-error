# Generated by Django 5.2.3 on 2025-06-14 22:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0009_remove_notification_user_notification_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='Dashboard.project'),
        ),
    ]
