# Generated by Django 4.2.6 on 2023-10-31 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_customuser_is_superuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_authenticated',
        ),
    ]
