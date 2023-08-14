# Generated by Django 4.1.3 on 2023-08-08 20:11

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0015_order_order_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_recieved', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('collection_date', models.DateField(default=django.utils.timezone.now)),
                ('agent_collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='KuberaApp.agentcollection')),
            ],
        ),
    ]