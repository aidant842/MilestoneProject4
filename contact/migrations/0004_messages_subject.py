# Generated by Django 3.1.1 on 2020-11-02 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0003_auto_20201102_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='subject',
            field=models.CharField(default='subject', max_length=64),
        ),
    ]
