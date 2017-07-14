# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import shutil
import ConfigParser
from django.shortcuts import render
from django.http import HttpResponse
import ast
import time
import subprocess
from dwebsocket.decorators import accept_websocket
from django.conf import settings
import paramiko
from paramiko.ssh_exception import AuthenticationException
# Create your views here.
# ORIGINAL_PATH="D:\\origin_caliper\\caliper-master\\test_cases_cfg\\common_backup"
# PATH="D:\\origin_caliper\\caliper-master\\test_cases_cfg\\common"
ORIGINAL_TOTAL_PATH="D:\\origin_caliper\\caliper-master\\test_cases_cfg_backup"
# TOTAL_PATH="D:\\origin_caliper\\caliper-master\\test_cases_cfg"
PRE_PATH="D:\\origin_caliper\\caliper-master"
# USER_PATH = os.path.join(PRE_PATH,request.user.username);
# USER_PATH_TMP = os.path.join(USER_PATH,"tmp");
ORIGINAL_TOTAL_PATH=settings.ORIGINAL_TOTAL_PATH
PRE_PATH=settings.PRE_PATH

ssh = paramiko.SSHClient()

def by_tool(request):
    global USER_PATH,USER_PATH_TMP
    USER_PATH = os.path.join(PRE_PATH,request.user.username);
    USER_PATH_TMP = os.path.join(USER_PATH,"tmp");
    if not os.path.isdir(USER_PATH):
        os.mkdir(USER_PATH)
    else:
        if os.path.isdir(USER_PATH_TMP):
            shutil.rmtree(USER_PATH_TMP)
    shutil.copytree(ORIGINAL_TOTAL_PATH, USER_PATH_TMP)
    dirs=os.listdir(USER_PATH_TMP)
    
    total_test_tools={}
    for dir in dirs:
        dirpath = os.path.join(USER_PATH_TMP,dir)
        if os.path.isdir(dirpath):
            child_dirs=os.listdir(dirpath)
            test_tools={}
            for child_dir in child_dirs:

                filepath = dirpath+"\\"+child_dir
                child_files = os.listdir(filepath)
                for child_file in child_files:
                    if child_file.endswith('cfg'):
                        filename=filepath+"\\"+child_file
                        with open(filename,'r') as fr:
                            conf = ConfigParser.ConfigParser()
                            conf.readfp(fr)
                            sections = conf.sections()
                            test_tools[child_dir]=sections
            total_test_tools[dir]=test_tools
    return render(request, 'by_tool.html',{'total_test_tools':json.dumps(total_test_tools)})

def by_category(request):
    return render(request, 'by_category.html')

def by_import(request):
    return render(request, 'by_import.html')

'''
def run(request):
    USER_PATH_SAVE = os.path.join(USER_PATH,time.strftime('%Y_%m_%d_%H%M%S',time.localtime(time.time())));
    
    # 列出USER_PATH_TMP下所有文件夹名字，存入数组test_dirs
    dirs=os.listdir(USER_PATH_TMP)
    test_dirs=[]
    for dir in dirs:
        dirpath = os.path.join(USER_PATH_TMP,dir)
        if os.path.isdir(dirpath):
            test_dirs.append(dir)
    # 获取前台选择的testcase，存入字典selected_tools
    selected_tools_str = request.POST['selected_tools']
    selected_tools=ast.literal_eval(selected_tools_str)
    # 取差集，未选择的文件夹存入数组unselected_dirs
    unselected_dirs=[unselect for unselect in test_dirs if unselect not in selected_tools.keys()]
    # 清空未选择文件夹对应的_cases_def.cfg配置文件
    if unselected_dirs:
        for unselected_dir in unselected_dirs:
            filename = os.path.join(USER_PATH_TMP,unselected_dir+"_cases_def.cfg")
            with open(filename,'r+') as f:
                f.truncate()
    # 修改_cases_def.cfg配置文件中的子项,已selected的保留，未selected的删除
    # 修改_run.cfg配置文件中的子项,已selected的保留，未selected的删除
    for key in selected_tools.keys():
        filename = os.path.join(USER_PATH_TMP,key+"_cases_def.cfg")
        with open(filename,'r') as fr:
            conf = ConfigParser.ConfigParser()
            conf.readfp(fr)
            sections = conf.sections()
            tmp=[val for val in sections if val in selected_tools[key].keys()]
            removes=[val for val in sections if val not in tmp]
            if removes:
                for remove in removes:
                    conf.remove_section(remove)
        with open(filename, 'w') as fw:
            conf.write(fw)
        for k,v in selected_tools[key].items():
            filename = os.path.join(USER_PATH_TMP,key,k,k+"_run.cfg")
            with open(filename,'r') as fr:
                conf = ConfigParser.ConfigParser()
                conf.readfp(fr)
                sections = conf.sections()
                tmp=[val for val in sections if val in v]
                removes=[val for val in sections if val not in tmp]
                if(removes):
                    for remove in removes:
                        conf.remove_section(remove)
            with open(filename, 'w') as fw:
                conf.write(fw)
    shutil.copytree(USER_PATH_TMP, USER_PATH_SAVE)
    comment=request.POST['comment']
    
    return render(request,'run.html',{"selected_tools":selected_tools})
'''

@accept_websocket
def echo(request):
    host = request.GET.get('host')
    user = request.GET.get('user')
    password = request.GET.get('password')
    command = request.GET.get('command')
    if not request.is_websocket():#判断是不是websocket连接
        return render(request,'run.html')
    else:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host,username=user, password=password)
            stdin, stdout, stderr = ssh.exec_command(command,get_pty=True)
            # popen = subprocess.Popen(command,stdout = subprocess.PIPE,bufsize=1,shell=True)
            for msg in iter(stdout.readline, ''):
                message=msg.decode('gb2312').encode('utf-8')
                print message
                request.websocket.send(message)
            ssh.close()
        except AuthenticationException:
            print 1
            msg="SSH Authentication Failed! Please check."
            message=msg.decode('gb2312').encode('utf-8')
            request.websocket.send(message)
            
    
def run(request):
    ssh.close()
    return render(request,'run.html')

def ajax_stop(request):
    ssh.close()
    return HttpResponse('stop')

def ajax_testtool(request):
    testdir=request.POST['testdir']
    testtool=request.POST['testtool']
    child_files = os.listdir(os.path.join(USER_PATH_TMP,testdir,testtool))
    for filename in child_files:
        if filename.endswith('cfg'):
            file=open(os.path.join(USER_PATH_TMP,testdir,testtool,filename))
            filecontent= file.read()
            file.close()
    return HttpResponse(filecontent)
'''
def ajax_testcase(request):
    testtool=request.POST['testtool']
    testcase=request.POST['testcase']
    child_files = os.listdir(PATH+"\\"+testtool)
    for file in child_files:
        if file.endswith('cfg'):
            filename= PATH+"\\"+testtool+'\\'+file
            with open(filename,'r') as fr:
                conf = ConfigParser.ConfigParser()
                conf.readfp(fr)
                kvs=conf.items(testcase)
    return HttpResponse(kvs)
'''
def ajax_savecfg(request):
    cfg_content= request.POST['cfg_content'];
    testdir= request.POST['testdir'];
    cfg_name= request.POST['cfg_name'];
    cfg_dir=cfg_name.replace("_run.cfg","")
    cfg_path =os.path.join(USER_PATH_TMP,testdir,cfg_dir,cfg_name)
    f=file(cfg_path,"w+")
    f.writelines(cfg_content)
    return HttpResponse(cfg_path)

    
    

