# Generated by Django 4.1.3 on 2023-08-14 05:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0032_alter_customerbalancehistory_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerbalancehistory',
            name='wallet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='KuberaApp.customerbalance'),
        ),
        migrations.AlterUniqueTogether(
            name='customerbalancehistory',
            unique_together={('transaction_id', 'upi_address')},
        ),
        migrations.RemoveField(
            model_name='customerbalancehistory',
            name='unique_id',
        ),
    ]
