from django.urls import path

from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^dataload$', views.dataload, name='dataload'),
    url(r'^listpeople$', views.people, name='listpeople'),
    url(r'^addperson$', views.addperson, name='addperson'),
    url(r'^person/(?P<person_id>[0-9]+)$', views.person, name='person'),
    url(r'^profile/(?P<person_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^add_relationship/(?P<person_id>[0-9]+)$', views.add_relationship, name='add_relationship'),
]