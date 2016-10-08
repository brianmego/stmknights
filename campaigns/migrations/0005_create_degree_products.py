# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-08 14:03
from __future__ import unicode_literals

from django.db import migrations
from .. import models


def forwards(apps, schema_editor):
    campaign = models.Campaign.objects.create(name='Major Degree')
    models.Product.objects.create(
        name='Medallion',
        cost=8,
        campaign=campaign
    )
    models.Product.objects.create(
        name='Candidate',
        cost=40,
        campaign=campaign
    )
    models.Product.objects.create(
        name='Guest',
        cost=8,
        campaign=campaign
    )


def backwards(apps, schema_editor):
    models.Campaign.objects.get(name='Major Degree').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0004_campaign_product'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
