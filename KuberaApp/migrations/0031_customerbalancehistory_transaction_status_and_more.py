# Generated by Django 4.1.3 on 2023-08-14 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0030_customerbalancehistory_delete_walletbalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerbalancehistory',
            name='transaction_status',
            field=models.CharField(choices=[('pending', 'pending'), ('rejected', 'rejected'), ('approved', 'approved')], default='pending', max_length=25),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'pending'), ('not_verified', 'not_verified'), ('processing', 'processing'), ('accepted', 'accepted'), ('cancelled', 'cancelled'), ('settled', 'settled')], default='processing', max_length=30),
        ),
    ]