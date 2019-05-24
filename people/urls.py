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
    url(r'^role_type/(?P<id>[0-9]+)$', views.people_query, name='role_type'),
    url(r'^ABSS_type/(?P<id>[0-9]+)$', views.people_query, name='ABSS_type'),
    url(r'^age_status/(?P<id>[0-9]+)$', views.people_query, name='age_status'),
    url(r'^champions(?P<id>[a-z]+)$', views.people_query, name='champions'),
    url(r'^event/(?P<event_id>[0-9]+)$', views.event, name='event'),
    url(r'^event_type/(?P<event_type>[0-9]+)$', views.event_type, name='event_type'),
    url(r'^event_type_this_month/(?P<event_type>[0-9]+)$', views.event_type, name='event_type_this_month'),
    url(r'^event_type_last_month/(?P<event_type>[0-9]+)$', views.event_type, name='event_type_last_month'),
    url(r'^event_type_this_year/(?P<event_type>[0-9]+)$', views.event_type, name='event_type_this_year'),
    url(r'^profile/(?P<person_id>[0-9]+)$', views.profile, name='profile'),
	url(r'^edit_event/(?P<event_id>[0-9]+)$', views.edit_event, name='edit_event'),
    url(r'^add_relationship/(?P<person_id>[0-9]+)$', views.add_relationship, name='add_relationship'),
    url(r'^add_address/(?P<person_id>[0-9]+)$', views.add_address, name='add_address'),
    url(r'^address/(?P<person_id>[0-9]+)$', views.address, name='address'),
    url(r'^event_registration/(?P<event_id>[0-9]+)$', views.event_registration, name='event_registration'),
    url(r'^parents_with_no_children/(?P<page>[0-9]+)$',
    	views.parent_exceptions, name='parents_with_no_children'),
    url(r'^parents_without_children_under_four/(?P<page>[0-9]+)$', 
    	views.parent_exceptions, name='parents_without_children_under_four'),
    url(r'^parents_with_overdue_children/(?P<page>[0-9]+)$', 
    	views.parent_exceptions, name='parents_with_overdue_children'),
    url(r'^answer_questions/(?P<person_id>[0-9]+)$', views.answer_questions, name='answer_questions')
]