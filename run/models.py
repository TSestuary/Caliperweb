# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class ConfigTable(models.Model):
    path = models.CharField(max_length=100)    
