# from django.conf.urls import url
# from django.contrib import admin
#
# from .views import (
# 	post_list,
# 	post_create,
# 	post_detail,
# 	post_update,
# 	post_delete,
# 	)
#
# urlpatterns = [
# 	url(r'^$', post_list, name='list'),
#     url(r'^create/$', post_create),
#     url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'),
#     url(r'^(?P<slug>[\w-]+)/edit/$', post_update, name='update'),
#     url(r'^(?P<slug>[\w-]+)/delete/$', post_delete),
#     #url(r'^posts/$', "<appname>.views.<function_name>"),
# ]

from .views import (
    home,
    evaluater,
    ajax,
    objects_and_values,
tutorials
)
from django.conf.urls import url
from django.contrib import admin
urlpatterns = [
	url(r'^$', home, name='home'),
    url(r'^evaluater/$', evaluater, name='evaluater'),
    url(r'^evaluater/ajax/$', ajax, name='ajax'),

    url(r'^objects_and_values/$', objects_and_values, name='objects_and_values'),
        url(r'^tutorials/$', tutorials, name='tutorials'),



]