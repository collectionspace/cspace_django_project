# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import positions.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('content', models.TextField()),
                ('order', positions.fields.PositionField(default=-1)),
                ('contentType', models.CharField(default=b'HTML', max_length=4, choices=[(b'HTML', b'HTML'), (b'TEXT', b'Plain Text')])),
                ('live', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
