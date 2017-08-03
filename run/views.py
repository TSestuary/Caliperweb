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
from django.shortcuts import redirect
from models import ConfigTable,DistributeTable
from task.models import TaskTable
from django.contrib.auth.models import User, Group 
from django.contrib.auth.hashers import check_password 
# Create your views here.

ORIGINAL_TOTAL_PATH=settings.ORIGINAL_TOTAL_PATH
PRE_PATH=settings.PRE_PATH

global CLIENTS
CLIENTS={}
# client = paramiko.SSHClient()

def host(request):  
    distribute = DistributeTable.objects.filter(hostuser=request.user.username)
    if distribute:
        distribute = DistributeTable.objects.get(hostuser=request.user.username)
        hostip = distribute.host
    else:
        hostip=''
    return render(request, 'host.html',{'hostip':hostip})

def ajax_passhost(request):
    selectuser=request.user.username
    firstdis = DistributeTable.objects.all().first()
    firstdis_hostip = firstdis.host
    distribute = DistributeTable.objects.filter(hostuser=selectuser)
    if distribute:
        distribute = DistributeTable.objects.get(hostuser=selectuser)
        distribute.host = firstdis_hostip
        distribute.save()
        success_dict={"host":distribute.host,'hostpassword':distribute.passwd,"exist":"yes"}
        return HttpResponse(json.dumps(success_dict),content_type="application/json")
    else:
        success_dict={"exist":"no"}
        return HttpResponse(json.dumps(success_dict),content_type="application/json")
'''
def ajax_showhost(request):
    selectuser=request.POST['selectuser']
    distribute = DistributeTable.objects.filter(hostuser=selectuser)
    if distribute:
        distribute = DistributeTable.objects.get(hostuser=selectuser)
        success_dict={"host":distribute.host,"exist":"yes"}
        return HttpResponse(json.dumps(success_dict),content_type="application/json")
    else:
        success_dict={"exist":"no"}
        return HttpResponse(json.dumps(success_dict),content_type="application/json")
'''

def ajax_distribute(request):
    host=request.POST['host']
    DistributeTable.objects.all().update(host=host)
    return HttpResponse(host)

def auth_host(request):
    host=request.POST['host']
    hostuser=request.POST['hostuser']
    hostpassword=request.POST['hostpassword']
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host,username=hostuser, password=hostpassword) 
        client.close()
        return HttpResponse("pass")
    except AuthenticationException:
        return HttpResponse("fail")

def by_tool(request):
    global USER_PATH,USER_PATH_TMP,USER_PATH_CASE_TMP,USER_PATH_CFG_TMP
    USER_PATH = os.path.join(PRE_PATH,request.user.username);
    USER_PATH_TMP = os.path.join(USER_PATH,"tmp");
    if not os.path.isdir(USER_PATH):
        os.mkdir(USER_PATH)
    else:
        if os.path.isdir(USER_PATH_TMP):
            shutil.rmtree(USER_PATH_TMP)
    shutil.copytree(ORIGINAL_TOTAL_PATH, USER_PATH_TMP)
    USER_PATH_CFG_TMP=os.path.join(USER_PATH_TMP,"config")
    cfg_files = os.listdir(USER_PATH_CFG_TMP)
    cfg={}
    for cfg_file in cfg_files:
        cfg_filename=os.path.join(USER_PATH_CFG_TMP,cfg_file)
        with open(cfg_filename,'r') as fr:
            conf = ConfigParser.ConfigParser()
            conf.readfp(fr)
            sections = conf.sections()
            cfg[cfg_file]=sections

    USER_PATH_CASE_TMP=os.path.join(USER_PATH_TMP,"test_cases_cfg")
    dirs=os.listdir(USER_PATH_CASE_TMP)
    total_test_tools={}
    for dir in dirs:
        dirpath = os.path.join(USER_PATH_CASE_TMP,dir)
        if os.path.isdir(dirpath):
            child_dirs=os.listdir(dirpath)
            test_tools={}
            for child_dir in child_dirs:

                filepath = os.path.join(dirpath,child_dir)
                child_files = os.listdir(filepath)
                for child_file in child_files:
                    if child_file.endswith('cfg'):
                        filename=os.path.join(filepath,child_file)
                        with open(filename,'r') as fr:
                            conf = ConfigParser.ConfigParser()
                            conf.readfp(fr)
                            sections = conf.sections()
                            test_tools[child_dir]=sections
            total_test_tools[dir]=test_tools
    host=request.POST['host']
    hostuser=request.POST['hostuser']
    hostpassword=request.POST['hostpassword']
    return render(request, 'by_tool.html',{'total_test_tools':json.dumps(total_test_tools),'cfg':json.dumps(cfg),'host':host,'hostuser':hostuser,'hostpassword':hostpassword})

def by_category(request):
    cfg_files = os.listdir(USER_PATH_CFG_TMP)
    cfg={}
    for cfg_file in cfg_files:
        cfg_filename=os.path.join(USER_PATH_CFG_TMP,cfg_file)
        with open(cfg_filename,'r') as fr:
            conf = ConfigParser.ConfigParser()
            conf.readfp(fr)
            sections = conf.sections()
            cfg[cfg_file]=sections
    host=request.POST['host']
    hostuser=request.POST['hostuser']
    hostpassword=request.POST['hostpassword']
    
    return render(request, 'by_category.html',{'cfg':json.dumps(cfg),'host':host,'hostuser':hostuser,'hostpassword':hostpassword})

def by_import(request):
    host=request.POST['host']
    hostuser=request.POST['hostuser']
    hostpassword=request.POST['hostpassword']
    return render(request, 'by_import.html',{'host':host,'hostuser':hostuser,'hostpassword':hostpassword})


def ajax_run(request):
    # client.close()
    USER_PATH_SAVE = os.path.join(USER_PATH,time.strftime('%Y_%m_%d_%H%M%S',time.localtime(time.time())));
    
    # 列出USER_PATH_TMP下所有文件夹名字，存入数组test_dirs
    dirs=os.listdir(USER_PATH_CASE_TMP)
    test_dirs=[]
    for dir in dirs:
        dirpath = os.path.join(USER_PATH_CASE_TMP,dir)
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
            filename = os.path.join(USER_PATH_CASE_TMP,unselected_dir+"_cases_def.cfg")
            with open(filename,'r+') as f:
                f.truncate()
    # 修改_cases_def.cfg配置文件中的子项,已selected的保留，未selected的删除
    # 修改_run.cfg配置文件中的子项,已selected的保留，未selected的删除
    for key in selected_tools.keys():
        filename = os.path.join(USER_PATH_CASE_TMP,key+"_cases_def.cfg")
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
            filename = os.path.join(USER_PATH_CASE_TMP,key,k,k+"_run.cfg")
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
    # comment=request.POST['comment']
    host=request.POST['host']
    hostuser=request.POST['hostuser']
    hostpassword=request.POST['hostpassword']
    copy_cfg(host,hostuser,hostpassword,USER_PATH_TMP)

    success_dict={"host":host,"hostuser":hostuser,"hostpassword":hostpassword,"serverpath":USER_PATH_SAVE}
    return HttpResponse(json.dumps(success_dict),content_type="application/json")
    # return HttpResponse(selected_tools)


@accept_websocket
def echo(request):
    host = request.GET.get('host')
    user = request.GET.get('user')
    password = request.GET.get('password')
    command = request.GET.get('command')
    comment = request.GET.get('comment')
    if not request.is_websocket():#判断是不是websocket连接
        return render(request,'run.html')
    else:
        # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        locals()[request.user.username]= paramiko.SSHClient()
        CLIENTS[request.user.username]=locals()[request.user.username]
        try:
            # client.connect(host,username=user, password=password) 
            trans = paramiko.Transport((host, 22))
            trans.connect(username=user, password=password)
            locals()[request.user.username]._transport = trans
            stdin, stdout, stderr = locals()[request.user.username].exec_command(command,get_pty=True)
            # popen = subprocess.Popen(command,stdout = subprocess.PIPE,bufsize=1,shell=True)
            for msg in iter(stdout.readline, ''):
                message=msg.decode('gb2312').encode('utf-8')
                print message
                request.websocket.send(message)
            trans.close()
            locals()[request.user.username].close()
        except AuthenticationException:
            print 1
            msg="SSH Authentication Failed! Please check."
            message=msg.decode('gb2312').encode('utf-8')
            request.websocket.send(message)
            
    
def run(request):
    # client.close()
    # platform=request.POST['platform']
    # ip=request.POST['ip']
    host = request.POST['host']
    hostuser = request.POST['hostuser']
    hostpassword = request.POST['hostpassword']
    serverpath = request.POST['serverpath']
    # filename = "D:\\origin_caliper\\caliper-master\\configuration\\config\\client_config.cfg"
    # with open(filename,'r') as fr:
    #     conf = ConfigParser.ConfigParser()
    #     conf.readfp(fr)
    #     sections = conf.sections()
        
    #     conf.set("TARGET", "ip", ip)
    #     conf.set("TARGET", "user", user)
    # with open(filename, 'w') as fw:
    #     conf.write(fw)
    return render(request,'run.html',{'host':host,'hostuser':hostuser,'hostpassword':hostpassword,'serverpath':serverpath})

def ajax_db(request):
    host = request.POST['host']
    hostuser = request.POST['hostuser']
    comment = request.POST['comment']
    serverpath = request.POST['serverpath']
    # command = request.POST['command']
    user = request.user.username
    cfg = ConfigTable(path=serverpath)
    cfg.save()
    TaskTable.objects.create(host=host,
                                hostuser=hostuser,
                                comment=comment,
                                user=user,
                                path_id=cfg.id
                                )
    return HttpResponse('success')


def cfg(request):
    # filedir = "D:\\origin_caliper\\caliper-master\\configuration\\config"
    filedir = os.path.join(ORIGINAL_TOTAL_PATH,'config')
    cfg_dict={}
    for file in os.listdir(filedir):
        filename=os.path.join(filedir,file)
        name, ext = os.path.splitext(file)
        cfg_list=[]
        with open(filename,'r') as fr:
            conf = ConfigParser.ConfigParser()
            conf.readfp(fr)
            sections = conf.sections()
            for section in sections:
                cfg={}
                options = conf.options(section)
                cfg['section'] = section
                cfg['option'] = options
                cfg_list.append(cfg)
        cfg_dict[name]=cfg_list
    return render(request,'cfg.html',{"cfg_dict":cfg_dict})

def ajax_stop(request):
    if CLIENTS.has_key(request.user.username):
        print request.user.username
        print 'stop'
        CLIENTS[request.user.username].get_transport().close()
        CLIENTS[request.user.username].close()
        del CLIENTS[request.user.username]
    return HttpResponse('stop')

def ajax_testtool(request):
    testdir=request.POST['testdir']
    testtool=request.POST['testtool']
    child_files = os.listdir(os.path.join(USER_PATH_CASE_TMP,testdir,testtool))
    for filename in child_files:
        if filename.endswith('cfg'):
            file=open(os.path.join(USER_PATH_CASE_TMP,testdir,testtool,filename))
            filecontent= file.read()
            file.close()
    return HttpResponse(filecontent)

def ajax_testcfg(request):
    testcfg=request.POST['testcfg']
    file=open(os.path.join(USER_PATH_CFG_TMP,testcfg))
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
    if testdir:
        cfg_path =os.path.join(USER_PATH_CASE_TMP,testdir,cfg_dir,cfg_name)
    else:
        cfg_path =os.path.join(USER_PATH_CFG_TMP,cfg_dir)
    f=file(cfg_path,"w+")
    f.writelines(cfg_content)
    return HttpResponse(cfg_path)

def copy_cfg(host,user,password,cfg_path):
    # path = os.getcwd()
    # cfg_path = os.path.join(path, 'resources%scfg%sconfiguration_backup'%(os.sep, os.sep))
    # host = request.GET.get('host')
    # user = request.GET.get('user')
    # password = request.GET.get('password')
    # host = '192.168.65.249'
    # user = 'ts'
    # password = '123'
    ssh = paramiko.Transport(host,22)
    ssh.connect(username= user, password = password)
    sftp = paramiko.SFTPClient.from_transport(ssh)
    search(user, sftp, cfg_path)
    ssh.close()
    return HttpResponse('copy')

def search(user, sftp, path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            host_path = os.path.join('/home/%s/caliper_output/configuration' % user,
                                     item_path.split('tmp')[-1].replace(os.sep, '', 1)).replace('\\', '/')
            try:
                sftp.mkdir(host_path)
            except:
                pass
            search(user, sftp, item_path)

        elif os.path.isfile(item_path):
            host_path = os.path.join('/home/%s/caliper_output/configuration'%user,
                                     item_path.split('tmp')[-1].replace(os.sep, '',1)).replace('\\', '/')
            try:
                sftp.put(item_path, host_path)
            except:
                sftp.open(host_path, 'a')
                sftp.put(item_path, host_path)
    