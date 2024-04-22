# Generated by Django 5.0.4 on 2024-04-22 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0011_usernotification_userticketnotification'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentNotification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField(null=True)),
                ('sent_status', models.BooleanField(default=False)),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Accounts.post')),
                ('user_ticket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Accounts.userticketnotification')),
            ],
        ),
    ]