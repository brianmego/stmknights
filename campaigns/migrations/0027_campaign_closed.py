# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-30 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0026_campaign_header'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]
