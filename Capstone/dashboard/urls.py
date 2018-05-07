from django.conf.urls import *
import dashboard.views

urlpatterns = [
    url(r'^$', dashboard.views.home, name="home"),
    url(r'^charts/(?P<machine_id>\d+)$', dashboard.views.charts, name="charts"),
    url(r'^getData/(?P<strstartTime>.+)/(?P<strendTime>.+)/(?P<machineId>\d+)$', dashboard.views.get_data, name="getData"),
]
