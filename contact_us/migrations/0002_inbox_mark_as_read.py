# Generated by Django 3.1.1 on 2020-12-02 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact_us', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='mark_as_read',
            field=models.BooleanField(default=False),
        ),
    ]
