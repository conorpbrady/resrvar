# Generated by Django 4.2.1 on 2024-07-13 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0021_decisionpreference_first_available_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulingpreference',
            name='frequency',
            field=models.IntegerField(null=True),
        ),
    ]
