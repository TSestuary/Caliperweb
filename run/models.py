# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class ConfigTable(models.Model):
    comment = models.CharField(max_length=200)
    path = models.CharField(max_length=100)    
