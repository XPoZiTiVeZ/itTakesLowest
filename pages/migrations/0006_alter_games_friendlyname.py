# Generated by Django 4.2.6 on 2023-11-01 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_rename_ответ_answers_answer_alter_answers_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='friendlyname',
            field=models.CharField(max_length=16, verbose_name='Название игры'),
        ),
    ]
