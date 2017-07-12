# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import TaskTable

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    list_display = ('platform', 'version','user')
    list_filter = ('platform','user')
    list_editable= ('user',)

admin.site.register(TaskTable,TaskAdmin)