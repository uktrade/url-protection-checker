# Generated by Django 3.1.4 on 2021-03-15 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0017_auto_20210315_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spaces',
            name='space_guid',
            field=models.CharField(max_length=90, unique=True),
        ),
    ]
