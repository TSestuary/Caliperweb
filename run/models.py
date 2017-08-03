# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import auth

# Create your models here.
class ConfigTable(models.Model):
    path = models.CharField(max_length=200)    

class DistributeTable(models.Model):
    host = models.CharField(max_length=50,null=True)
    hostuser = models.CharField(max_length=50,null=True)
    passwd = models.CharField(max_length=50,null=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True)