# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-08 15:41
from __future__ import unicode_literals

from django.db import migrations
from .. import models


def forwards(apps, schema_editor):
    models.AttendeeType.objects.create(
        label='Guest',
    )
    models.AttendeeType.objects.create(
        label='Candidate',
    )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0006_auto_20161008_1538'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
