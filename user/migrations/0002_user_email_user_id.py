# Generated by Django 2.2.27 on 2022-02-21 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_user_id',
            field=models.EmailField(default=1, max_length=254, unique=True, verbose_name='email address'),
            preserve_default=False,
        ),
    ]