# Generated by Django 2.2.5 on 2019-11-22 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0011_auto_20191122_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationsitem',
            name='is_behind_app_auth',
            field=models.BooleanField(default=False),
        ),
    ]