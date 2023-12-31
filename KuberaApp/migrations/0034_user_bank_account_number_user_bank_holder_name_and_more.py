# Generated by Django 4.1.3 on 2023-08-20 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0033_alter_customerbalancehistory_wallet_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='bank_holder_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='bank_ifsc_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
