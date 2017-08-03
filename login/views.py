# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.http import StreamingHttpResponse
from django.conf import settings
from run.models import DistributeTable

# Create your views here.
DOWNLOAD_PATH=settings.DOWNLOAD_PATH
DOWNLOAD_NAME=settings.DOWNLOAD_NAME

def main(request):
    return render(request, 'main.html')
# just for test
def userIntoCaliperDB(request):
    # create admin user
    user = User()
    user.username = 'zhangxj'
    user.set_password('zhangxj@123')
    user.save()
    admin_group = Group.objects.get(name="admin user")
    user.groups=[admin_group]
    # create com user
    user = User()
    user.username = 'chenzhihui'
    user.set_password('123456')
    user.save()
    com_group = Group.objects.get(name="com user")
    user.groups=[com_group]

    user = User()
    user.username = 'hsp'
    user.set_password('hsp')
    user.save()
    com_group = Group.objects.get(name="com user")
    user.groups=[com_group]
    return HttpResponse("success")

def login(request):
    auth.logout(request)
    return render(request, 'login.html')

def login_verify(request):
    username=request.POST['userName']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            loginuser=User.objects.get(username=username)
            distribute = DistributeTable.objects.filter(hostuser=username)
            if distribute:
                distribute = DistributeTable.objects.get(hostuser=username)
                distribute.passwd=password
                distribute.save()
            else:
                DistributeTable.objects.create(hostuser=username,passwd=password,user_id=loginuser.id)
            return HttpResponse('success')
        else:
            return HttpResponse('fail')
    else:
        return HttpResponse('fail')

def file_Download(request):
    download_file=os.path.join(DOWNLOAD_PATH,DOWNLOAD_NAME)
    response = StreamingHttpResponse(file_iterator(download_file))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(DOWNLOAD_NAME)
    return response

def file_iterator(filename, chunk_size=512):
    with open(filename,"rb") as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break