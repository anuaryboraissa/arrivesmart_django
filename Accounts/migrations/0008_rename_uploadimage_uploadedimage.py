# Generated by Django 5.0.4 on 2024-04-16 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0007_passenger_uploadimage_bus_post_route_ticket_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UploadImage',
            new_name='UploadedImage',
        ),
    ]
