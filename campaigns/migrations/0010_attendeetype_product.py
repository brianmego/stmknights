# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-08 23:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0009_degreeregistration_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendeetype',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='campaigns.Product'),
        ),
    ]
