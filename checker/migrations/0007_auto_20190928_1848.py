# Generated by Django 2.2.5 on 2019-09-28 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0006_auto_20190928_1833'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationsitem',
            old_name='enabled',
            new_name='check_enabled',
        ),
        migrations.RenameField(
            model_name='spaces',
            old_name='enabled',
            new_name='check_enabled',
        ),
    ]
