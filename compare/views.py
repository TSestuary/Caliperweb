# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.shortcuts import render
from collections import OrderedDict
from task.models import TaskTable

CONFIG_STR = 'Configuration'
TOTAL_STR = 'Total_Scores'
POINT_STR = 'Point_Scores'
PERF_STR = 'Performance'
FUNC_STR = 'Functional'
RESULTS_STR = 'results'

# Create your views here.
def compare(request):
    tasktable = TaskTable.objects.all().order_by("id")
    task_num = TaskTable.objects.all().count()
    filesname = []
    for i in range(task_num):
        filesname.append(tasktable[i].json_path)
    dic_total = {}
    dic_sum = get_sum_dics(filesname)
    dic_total['dic_sum'] = json.dumps(dic_sum)
    for key in dic_sum.keys():
        if dic_sum[key]:
            key = _deal_keyword(key)
            dic_total[key] = True   
    return render(request, 'compare.html',dic_total)

def test_aspect(request,aspect):
    # tasktable = TaskTable.objects.filter().order_by("id")
    # task_num = TaskTable.objects.filter().count()
    tasktable = TaskTable.objects.all().order_by("id")
    task_num = TaskTable.objects.all().count()
    filesname = []
    for i in range(task_num):
        filesname.append(tasktable[i].json_path)
    dic_total = {}
    test_point=[]
    dic_aspect = get_detail_data(filesname, PERF_STR, aspect)   
    dic_total['dic_aspect'] = json.dumps(dic_aspect)
    for key in dic_aspect.keys():
        # key_name = _deal_keyword(key)
        # dic_total[key_name] = True
        test_point.append(key)
    test_point=sorted(test_point)
    dic_total['aspect']=aspect 
    return render(request, 'test_aspect.html', {'dic_total':dic_total,'test_point':test_point})

def get_sum_dics(files):
    dic = {}
    dic['config'] = {}
    dic['test_tools'] = {}
    dic['summary'] = {}

    conf_tmp = OrderedDict()
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp, object_pairs_hook=OrderedDict)
        fp.close()
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        conf_tmp[target] = data[CONFIG_STR]
    dic['config'] = conf_tmp
    dic['perf_summary'] = get_eachItem_sum(files, PERF_STR)
    dic['func_summary'] = get_eachItem_sum(files, FUNC_STR)
    return dic

def get_each_sum_item(files, testItem, category):
    dic = OrderedDict()
    for filename in files:
        tmp_dic = OrderedDict()
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        dic[target] = OrderedDict()
        with open(filename) as fp:
            data = json.load(fp, object_pairs_hook=OrderedDict)
        fp.close()
        try:
            perf_dic = data[RESULTS_STR][testItem][category]
            for key in perf_dic.keys():
                if (key != TOTAL_STR):
                    tmp_dic[key] = perf_dic[key][TOTAL_STR]
        except Exception:
            tmp_dic = {}
        dic[target] = tmp_dic
    return dic

def get_eachItem_sum(files, testItem):

    summary_tmp = OrderedDict()
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        sum_tmp = {}
        if testItem in data[RESULTS_STR].keys():
            sum_dic = data[RESULTS_STR][testItem]
        else:
            return {}
        for key in sum_dic.keys():
            sum_tmp[key] = sum_dic[key][TOTAL_STR]
        summary_tmp[target] = sum_tmp
    return summary_tmp

def get_detail_data(files, testItem, category):
    dic = {}
    dic['sum'] = get_each_sum_item(files, testItem, category)
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp, object_pairs_hook=OrderedDict)
        fp.close()
        try:
            perf_dic = data[RESULTS_STR][testItem][category]
            for key in perf_dic.keys():
                if (key != TOTAL_STR):
                    dic[key] = {}
            break
        except Exception:
            dic = {}
    for key in dic.keys():
        if (key == TOTAL_STR or key == 'sum'):
            continue
        tmp_dic = OrderedDict()
        for filename in files:
            with open(filename) as fp:
                data = json.load(fp, object_pairs_hook=OrderedDict)
            fp.close()
            # get the target hostname from the filename
            target = '_'.join(filename.split('/')[-1].split('_')[:-2])
            try:
                test_points = data[RESULTS_STR][testItem][category][key]
                tmp_dic[target] = test_points[POINT_STR]
            except Exception:
                test_points = {}
                tmp_dic[target] = 0
        dic[key] = tmp_dic
    return dic

def _deal_keyword(string):
    new_str = '_'.join(string.split('/'))
    new_str = '_'.join(new_str.split(' '))
    new_str = '_'.join(new_str.split('-'))
    return new_str