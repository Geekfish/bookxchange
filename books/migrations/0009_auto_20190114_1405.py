# Generated by Django 2.1.2 on 2019-01-14 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_bookholder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='description',
            field=models.TextField(help_text='Enter         a brief description of the book', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.CharField(help_text='13 Character ISBN number', max_length=13, null=True),
        ),
    ]