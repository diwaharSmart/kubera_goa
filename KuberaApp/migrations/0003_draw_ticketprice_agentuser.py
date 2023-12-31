# Generated by Django 4.1.3 on 2023-08-08 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0002_user_google_pay_number_user_paytm_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Draw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('draw_date', models.DateField()),
                ('draw_time', models.TimeField()),
                ('result_number', models.PositiveIntegerField(default=0)),
                ('released', models.BooleanField(default=False)),
                ('winning_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('loot_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TicketPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_name', models.CharField(max_length=50, unique=True)),
                ('ticket_value', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='AgentUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_mobile_number', models.CharField(max_length=15)),
                ('name', models.CharField(max_length=100)),
                ('upi_id', models.CharField(blank=True, max_length=50, null=True)),
                ('paytm_number', models.CharField(blank=True, max_length=15, null=True)),
                ('phonepe_number', models.CharField(blank=True, max_length=15, null=True)),
                ('google_pay_number', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
    ]
