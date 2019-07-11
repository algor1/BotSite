"""useracc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url, include
from django.views.static import serve

from django.conf import settings
from django.contrib import admin
from django.shortcuts import HttpResponse
from . import views
from accounts.views import bot_collection,bot_detail,bot_calendar_js
from yandexmoney_notice.views import http_notification


def protected_serve(request, username, path, file_root=None):
    user = request.user.username
    path = '/' + username + path
    if user == username or request.user.is_superuser:
        return serve(request, path, file_root)
    else:
        return HttpResponse("Sorry you don't have permission to access this file")


urlpatterns = [
    url(r'^$', views.index, name='start'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^{}(?P<username>(?!(signout|signup|signin|mugshots|bots)/)[\@\.\w-]+)(?P<path>.*)$'.format(settings.MEDIA_URL[1:]),
        protected_serve, {'file_root': settings.MEDIA_ROOT}),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^telegrambot/', include('telegrambot.urls', namespace="telegrambot")),
    url(r'^yandex-money-notice$', http_notification),
    url(r'^bot_collection$', bot_collection, name='bot_collection' ),
    url(r'^bot_collection/(?P<pk>\d+)/$', bot_detail, name='bot_detail' ),
    url(r'^bot_collection/(?P<pk>\d+)/bot_calendar.js', bot_calendar_js, name='bot_calendar_js' )
]
#
