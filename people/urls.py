from django.urls import path

from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^dataload$', views.dataload, name='dataload'),
    url(r'^listpeople$', views.people, name='listpeople'),
    url(r'^addperson$', views.addperson, name='addperson'),
]