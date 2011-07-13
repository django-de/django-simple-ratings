from django.conf.urls.defaults import *


urlpatterns = patterns('ratings.views',
    url(r'^rate/(?P<ct>\d+)/(?P<pk>[^\/]+)/(?P<score>\-?[\d\.]+)/$', 'rate_object', name='ratings_rate_object'),
    url(r'^unrate/(?P<ct>\d+)/(?P<pk>[^\/]+)/$', 'rate_object', {'add': False}, name='ratings_unrate_object'),
)
