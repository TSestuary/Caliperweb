"""caliper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from login import views as login_views
from task import views as task_views
from compare import views as compare_views
from trend import views as trend_views
from run import views as run_views

urlpatterns = [
    url(r'^$',login_views.main,name='main'),
    url(r'^createuser$',login_views.userIntoCaliperDB,name='createuser'),
    url(r'^login$',login_views.login,name='login'),
    url(r'^login_verify$', login_views.login_verify, name='login_verify'),
    url(r'^downloadfile$', login_views.file_Download, name='downloadfile'),

    url(r'^task$',task_views.home,name='home'),
    url(r'^upload$',task_views.upload,name='upload'),
    url(r'^task/(\w+)/$',task_views.result,name='result'),
    url(r'^ajax_showresult$',task_views.ajax_showresult,name='ajax_showresult'),

    url(r'^compare$',compare_views.compare,name='compare'),
    url(r'^compare/(\w+)/$',compare_views.test_aspect,name='test_aspect'),
    url(r'^trend$',trend_views.trend,name='trend'),
    url(r'^run/host$',run_views.host,name='host'),
    
    url(r'^ajax_passhost$',run_views.ajax_passhost,name='ajax_passhost'),
    
    url(r'^ajax_distribute$',run_views.ajax_distribute,name='ajax_distribute'),
    url(r'^ajax_install$',run_views.ajax_install,name='ajax_install'),
    url(r'^ajax_uploadresult$',run_views.ajax_uploadresult,name='ajax_uploadresult'),
    url(r'^run/by_tool$',run_views.by_tool,name='by_tool'),
    url(r'^run/by_category$',run_views.by_category,name='by_category'),
    url(r'^run/by_import$',run_views.by_import,name='by_import'),
    url(r'^cfg$',run_views.cfg,name='cfg'),
    url(r'^run$',run_views.run,name='run'),
    url(r'^echo/$',run_views.echo,name='echo'),
    url(r'^ajax_db$',run_views.ajax_db,name='ajax_db'),
    url(r'^ajax_stop$',run_views.ajax_stop,name='ajax_stop'),
    url(r'^ajax_testtool$',run_views.ajax_testtool,name='ajax_testtool'),
    url(r'^ajax_testcfg$',run_views.ajax_testcfg,name='ajax_testcfg'),
    url(r'^ajax_savecfg$',run_views.ajax_savecfg,name='ajax_savecfg'),
    url(r'^ajax_run$',run_views.ajax_run,name='ajax_run'),
    url(r'^admin/', admin.site.urls),
    url(r'static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}, name='static'),
]
