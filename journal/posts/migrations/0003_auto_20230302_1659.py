# Generated by Django 2.2.16 on 2023-03-02 13:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0002_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='posts/',
                verbose_name='Картинка',
            ),
        ),
    ]