# Generated by Django 2.2.16 on 2022-09-09 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220909_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Здесь можно добавить картинку', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]