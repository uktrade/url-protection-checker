# Generated by Django 2.2.5 on 2019-09-28 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0005_auto_20190928_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationsitem',
            name='app_route',
            field=models.URLField(blank=True),
        ),
    ]
