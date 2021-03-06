# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from models import TaskTable


# Create your views here.
def home(request):
    if not request.user.is_authenticated():
        return render(request,'main.html')
    else:
        task_tab = TaskTable.objects.all().order_by("-id")
        print(dir(request.user.groups.values))
        return render(request,'home.html',{"task_tab": task_tab})

def upload(request):
    files = get_files()
    for filename in files:
        with open(filename) as fp:
            data1 = json.load(fp)
            TaskTable.objects.create(platform=data1["name"],
                                    user='ytt',
                                    json_path=filename)
    return HttpResponse("success")

def get_files():
    json_dir = settings.DATAFILES_FOLDER
    filesname = []
    for root, dirs, files in os.walk(json_dir):
        for i in range(0, len(files)):
            if files[i].endswith('.json'):
                filesname.append(os.path.join(root, files[i]))
    files_new = []
    for i in range(0, len(filesname)):
        print i, filesname[i]
        fp = open(filesname[i])
        data = json.load(fp)
        data = data['Configuration']
        if data['Machine_arch'] == 'x86_64':
            files_new.append(filesname[i])
    files_new.sort()
    filesname = [i for i in filesname if not i in files_new]
    filesname.sort()
    files_new.sort()
    for i in files_new:
        filesname.append(i)

    return filesname

def result(request,taskid):
    task = TaskTable.objects.get(id=taskid)
    serverpath = task.serverpath
    result_files = showtree(serverpath)
    return render(request,'result.html',{'result_files':json.dumps(result_files)})   

def showtree(rootDir): 
    # result_dirs=[]
    result_files=[]
    list_dirs = os.walk(rootDir) 
    for root, dirs, files in list_dirs: 
        '''
        for d in dirs: 
            dirpath=os.path.join(root, d)
            result_dirs.append(dirpath.split("output\\")[1])    
        '''
        for f in files: 
            filepath=os.path.join(root, f)  
            result_files.append(filepath)
    return result_files

def ajax_showresult(request):
    resultpath=request.POST['resultpath']
    file=open(resultpath)
    filecontent= file.read()
    file.close()
    return HttpResponse(filecontent)
