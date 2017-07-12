# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.http import StreamingHttpResponse

# Create your views here.
DOWNLOAD_PATH="C:\\Users\\yangtt\\Desktop"
DOWNLOAD_NAME="4.png"

def main(request):
    return render(request, 'main.html')

def userIntoCaliperDB(request):
    user = User()
    user.username = 'ytt'
    user.set_password('123')
    user.save()
    com_group = Group.objects.get(name="admin user")
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