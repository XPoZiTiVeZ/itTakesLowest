# Generated by Django 4.2.6 on 2023-10-31 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_rename_конец_games_enddate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='games',
            name='friendlyname',
            field=models.CharField(default='', max_length=32, verbose_name='Название игры'),
            preserve_default=False,
        ),
    ]