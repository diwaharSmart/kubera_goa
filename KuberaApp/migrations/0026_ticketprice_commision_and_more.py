# Generated by Django 4.1.3 on 2023-08-13 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0025_agentwinning_settled'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketprice',
            name='commision',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='ticketprice',
            name='price_after_commision',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='AgentCollectionBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgentCollectionAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_recieved', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('collection_date', models.DateField(default=django.utils.timezone.now)),
                ('agent_collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='KuberaApp.agentcollectionbalance')),
            ],
        ),
    ]