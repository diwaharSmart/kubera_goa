# Generated by Django 4.1.3 on 2023-08-09 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0021_remove_ticketprice_board_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='winning_board',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
