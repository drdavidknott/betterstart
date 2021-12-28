from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
	url(r'^login$', views.log_user_in, name='login'),
	url(r'^logout$', views.log_user_out, name='logout'),
    url(r'^uploaddata$', views.uploaddata, name='uploaddata'),
    url(r'^downloaddata$', views.downloaddata, name='downloaddata'),
    url(r'^listpeople$', views.people, name='listpeople'),
    url(r'^addperson$', views.addperson, name='addperson'),
    url(r'^events$', views.events, name='events'),
    url(r'^addevent$', views.addevent, name='addevent'),
    url(r'^addvenue$', views.add_venue, name='addvenue'),
    url(r'^venues$', views.venues, name='venues'),
    url(r'^person/(?P<person_id>[0-9]+)$', views.person, name='person'),
    url(r'^invitation/(?P<code>[\w]+)$', views.invitation, name='invitation'),
    url(r'^review_invitation/(?P<invitation_id>[0-9]+)$', views.review_invitation, name='review_invitation'),
    url(r'^print_invitation_form/(?P<invitation_id>[0-9]+)$', views.print_invitation_form, name='print_invitation_form'),
    url(r'^validate_invitation/(?P<invitation_id>[0-9]+)$', views.validate_invitation, name='validate_invitation'),
    url(r'^display_signature/(?P<invitation_step_id>[0-9]+)$', views.display_signature, name='display_signature'),
    url(r'^role_type/(?P<id>[0-9]+)$', views.people_query, name='role_type'),
    url(r'^membership_type/(?P<id>[0-9]+)$', views.people_query, name='membership_type'),
    url(r'^age_status/(?P<id>[0-9]+)$', views.people_query, name='age_status'),
    url(r'^ward/(?P<id>[0-9]+)$', views.people_query, name='ward'),
    url(r'^trained_role/(?P<id>[\w]+)$', views.people_query, name='trained_role'),
    url(r'^event/(?P<event_id>[0-9]+)$', views.event, name='event'),
    url(r'^event/(?P<event_id>[0-9]+)/(?P<page>[0-9]+)$', views.event, name='event'),
    url(r'^event_type/(?P<event_group>[0-9]+)$', views.event_group, name='event_type'),
    url(r'^event_venue/(?P<event_group>[0-9]+)$', views.event_group, name='event_venue'),
    url(r'^event_category/(?P<event_group>[0-9]+)$', views.event_group, name='event_category'),
    url(r'^event_ward/(?P<event_group>[0-9]+)$', views.event_group, name='event_ward'),
    url(r'^event_type_this_month/(?P<event_group>[0-9]+)$', views.event_group, name='event_type_this_month'),
    url(r'^event_category_this_month/(?P<event_group>[0-9]+)$', views.event_group, name='event_category_this_month'),
    url(r'^events_this_month$', views.event_group, name='events_this_month'),
    url(r'^event_type_last_month/(?P<event_group>[0-9]+)$', views.event_group, name='event_type_last_month'),
    url(r'^event_category_last_month/(?P<event_group>[0-9]+)$', views.event_group, name='event_category_last_month'),
    url(r'^events_last_month$', views.event_group, name='events_last_month'),
    url(r'^event_type_this_year/(?P<event_group>[0-9]+)$', views.event_group, name='event_type_this_year'),
    url(r'^event_category_this_year/(?P<event_group>[0-9]+)$', views.event_group, name='event_category_this_year'),
    url(r'^events_this_year$', views.event_group, name='events_this_year'),
    url(r'^events_all_time$', views.event_group, name='events_all_time'),
    url(r'^profile/(?P<person_id>[0-9]+)$', views.profile, name='profile'),
	url(r'^edit_event/(?P<event_id>[0-9]+)$', views.edit_event, name='edit_event'),
    url(r'^venue/(?P<venue_id>[0-9]+)$', views.venue, name='venue'),
    url(r'^edit_venue/(?P<venue_id>[0-9]+)$', views.edit_venue, name='edit_venue'),
    url(r'^add_relationship/(?P<person_id>[0-9]+)$', views.add_relationship, name='add_relationship'),
    url(r'^address/(?P<person_id>[0-9]+)$', views.address, name='address'),
    url(r'^address_to_relationships/(?P<person_id>[0-9]+)$',
    		views.address_to_relationships,
    		name='address_to_relationships'),
    url(r'^event_registration/(?P<event_id>[0-9]+)$', views.event_registration, name='event_registration'),
    url(r'^parents_with_no_children/(?P<page>[0-9]+)$',
    	views.exceptions, name='parents_with_no_children'),
    url(r'^parents_without_children_under_four/(?P<page>[0-9]+)$', 
    	views.exceptions, name='parents_without_children_under_four'),
    url(r'^parents_with_overdue_children/(?P<page>[0-9]+)$', 
    	views.exceptions, name='parents_with_overdue_children'),
    url(r'^children_over_four/(?P<page>[0-9]+)$', 
    	views.exceptions, name='children_over_four'),
    url(r'^answer_questions/(?P<person_id>[0-9]+)$', views.answer_questions, name='answer_questions'),
    url(r'^age_exceptions/(?P<age_status_id>[0-9]+)$', views.age_exceptions, name='age_exceptions'),
    url(r'^activities/(?P<person_id>[0-9]+)$', views.activities, name='activities'),
    url(r'^dashboard/(?P<name>[\w]+)$', views.dashboard, name='dashboard'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    url(r'^download_dashboard/(?P<name>[\w]+)$', views.download_dashboard, name='download_dashboard'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^manage_membership$', views.manage_membership, name='manage_membership'),
    url(r'^manage_project_events$', views.manage_project_events, name='manage_project_events'),
    url(r'^manage_unassigned_activities$', views.manage_unassigned_activities, name='manage_unassigned_activities'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^display_qrcode$', views.display_qrcode, name='display_qrcode'),
    url(r'^display_qrcode_image$', views.display_qrcode_image, name='display_qrcode_image'),
    url(r'^login_data$', views.login_data, name='login_data'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^forgot_password$', views.forgot_password, name='forgot_password'),
    url(r'^reset_password/(?P<reset_code>[\w]+)$', views.reset_password, name='reset_password'),
    url(r'^chart/(?P<name>[\w]+)$', views.chart, name='chart'),
    url(r'^charts$', views.chart, name='charts'),
    url(r'^document_links$', views.Document_Link_List.as_view(), name='document_links'),
    url(r'^select_project$', views.select_project, name='select_project'),
    url(r'^add_case_notes/(?P<person_id>[0-9]+)$', views.add_case_notes, name='add_case_notes'),
    url(r'^edit_case_notes/(?P<case_notes_id>[0-9]+)$', views.edit_case_notes, name='edit_case_notes'),
    url(r'^view_case_notes/(?P<person_id>[0-9]+)$', views.view_case_notes, name='view_case_notes'),
    url(r'^survey_series_list$', views.survey_series_list, name='survey_series_list'),
    url(r'^survey_series$', views.survey_series, name='survey_series'),
    url(r'^survey_series/(?P<survey_series_id>[0-9]+)$', views.survey_series, name='survey_series'),
    url(r'^survey/(?P<survey_series_id>[0-9]+)$', views.survey, name='survey'),
    url(r'^survey/(?P<survey_series_id>[0-9]+)/(?P<survey_id>[0-9]+)$', views.survey, name='survey'),
    url(r'^survey_section/(?P<survey_id>[0-9]+)$', views.survey_section, name='survey_section'),
    url(r'^survey_section/(?P<survey_id>[0-9]+)/(?P<survey_section_id>[0-9]+)$', views.survey_section, name='survey_section'),
    url(r'^survey_question/(?P<survey_section_id>[0-9]+)$', views.survey_question, name='survey_question'),
    url(r'^survey_question/(?P<survey_section_id>[0-9]+)/(?P<survey_question_id>[0-9]+)$', views.survey_question, name='survey_question'),
]