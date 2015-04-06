try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'^', include('ratings.urls')),
)
