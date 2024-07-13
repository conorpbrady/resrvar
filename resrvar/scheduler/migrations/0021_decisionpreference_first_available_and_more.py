# Generated by Django 4.2.1 on 2024-07-13 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0020_venue_tock_multiple_res_types_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='decisionpreference',
            name='first_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='schedulingpreference',
            name='frequency',
            field=models.IntegerField(default=60),
        ),
        migrations.AlterField(
            model_name='schedulingpreference',
            name='specific_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
