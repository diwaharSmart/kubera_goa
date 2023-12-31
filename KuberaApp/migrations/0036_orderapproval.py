# Generated by Django 4.1.3 on 2023-08-27 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('KuberaApp', '0035_websiteinfo_upi_qr_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderApproval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_approved', models.BooleanField(default=False)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('upi_address', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_date', models.DateField(default=django.utils.timezone.now)),
                ('transaction_status', models.CharField(choices=[('pending', 'pending'), ('rejected', 'rejected'), ('approved', 'approved')], default='pending', max_length=25)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='KuberaApp.order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
