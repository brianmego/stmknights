# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-09 19:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0010_attendeetype_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendeetype',
            name='product',
        ),
        migrations.AlterField(
            model_name='attendee',
            name='attendee_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaigns.Product'),
        ),
        migrations.DeleteModel(
            name='AttendeeType',
        ),
    ]