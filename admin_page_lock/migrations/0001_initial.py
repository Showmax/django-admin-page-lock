# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import admin_page_lock.models.base_model


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DatabasePageLockModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("url", models.URLField()),
                (
                    "url_parameters",
                    models.CharField(max_length=1024, null=True, blank=True),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "user_reference",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("locked", models.BooleanField(default=True)),
                ("locked_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("locked_out", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("locked_at",),
            },
            bases=(admin_page_lock.models.base_model.BasePageLockModel, models.Model),
        ),
    ]
