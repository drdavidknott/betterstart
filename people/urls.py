from django.urls import path

from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
	url(r'^login$', views.log_user_in, name='login'),
    url(r'^dataload$', views.dataload, name='dataload'),
    url(r'^listpeople$', views.people, name='listpeople'),
    url(r'^addperson$', views.addperson, name='addperson'),
    url(r'^events$', views.events, name='events'),
    url(r'^addevent$', views.addevent, name='addevent'),
    url(r'^person/(?P<person_id>[0-9]+)$', views.person, name='person'),
    url(r'^event/(?P<event_id>[0-9]+)$', views.event, name='event'),
    url(r'^profile/(?P<person_id>[0-9]+)$', views.profile, name='profile'),
    url(r'^add_relationship/(?P<person_id>[0-9]+)$', views.add_relationship, name='add_relationship'),
    url(r'^add_address/(?P<person_id>[0-9]+)$', views.add_address, name='add_address'),
    url(r'^event_registration/(?P<event_id>[0-9]+)$', views.event_registration, name='event_registration'),
]