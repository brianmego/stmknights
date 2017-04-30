# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-30 20:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0024_campaign_lookup_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='when',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='where',
            field=models.TextField(blank=True, null=True),
        ),
    ]
