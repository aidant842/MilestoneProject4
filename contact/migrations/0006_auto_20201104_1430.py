# Generated by Django 3.1.1 on 2020-11-04 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0005_messages_date_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='name',
            field=models.CharField(max_length=126),
        ),
    ]
