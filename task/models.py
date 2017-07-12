# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class TaskTable(models.Model):
    version = models.CharField(max_length=50,null=True)
    platform = models.CharField(max_length=50)
    target = models.CharField(max_length=50,null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)
    json_path = models.CharField(max_length=100)