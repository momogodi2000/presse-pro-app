# Generated by Django 5.0.6 on 2024-09-28 11:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_payments_servicebook'),
    ]

    operations = [
        migrations.AddField(
            model_name='pressingprofile',
            name='predefined',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pressingprofile',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='payments',
            name='receipt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.receipt'),
        ),
    ]
