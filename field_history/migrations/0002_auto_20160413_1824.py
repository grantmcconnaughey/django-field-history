# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('field_history', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldhistory',
            options={'get_latest_by': 'date_created'},
        ),
        migrations.AlterField(
            model_name='fieldhistory',
            name='field_name',
            field=models.CharField(max_length=500, db_index=True),
            preserve_default=True,
        ),
    ]
