# Generated by Django 4.1.3 on 2023-08-08 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0016_collectionamount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentcollection',
            name='collection_status',
            field=models.CharField(blank=True, choices=[('partial', 'Partial'), ('full', 'Full')], default='partial', max_length=10, null=True),
        ),
    ]