# Generated by Django 4.1.3 on 2023-08-08 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0006_order_agent_order_customer_order_draw'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='A',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='AB',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='ABC',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='AC',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='B',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='BC',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='C',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
