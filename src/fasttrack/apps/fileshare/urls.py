"""
URLConf for Django user profile management.

Recommended usage is to use a call to ``include()`` in your project's
root URLConf to include this URLConf for any URL beginning with
'/profiles/'.

"""

from django.conf.urls.defaults import *



urlpatterns = patterns('fileshare.views',
                       url(r'^$',
                           'setting',
                           name='setting'),
                       url(r'^(?P<rule_id>\d+)/$',
                           'edit_setting',
                           name='edit_setting'),
                       )

