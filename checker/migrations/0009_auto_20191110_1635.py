# Generated by Django 2.2.5 on 2019-11-10 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0008_auto_20191004_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='app_name',
            field=models.CharField(max_length=90),
        ),
        migrations.AlterField(
            model_name='spaces',
            name='space_guid',
            field=models.CharField(max_length=90),
        ),
        migrations.AlterField(
            model_name='spaces',
            name='space_name',
            field=models.CharField(max_length=90),
        ),
    ]
