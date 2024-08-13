# Generated by Django 5.0.1 on 2024-03-03 19:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0005_remove_store_governorate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='governorate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cities', to='addresses.governorate'),
        ),
    ]