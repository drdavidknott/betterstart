from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note
import os
import csv
import copy
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AddPersonForm, ProfileForm, PersonSearchForm, AddRelationshipForm, \
					AddRelationshipToExistingPersonForm, EditExistingRelationshipsForm, \
					AddAddressForm, AddressSearchForm, AddRegistrationForm, \
					EditRegistrationForm, LoginForm, EventSearchForm, EventForm, PersonNameSearchForm, \
					AnswerQuestionsForm, UpdateAddressForm, AddressToRelationshipsForm, UploadDataForm, \
					DownloadDataForm
from .utilities import get_page_list, make_banner
from .utilities import Dashboard_Panel_Row, Dashboard_Panel, Dashboard_Column, Dashboard
from django.contrib import messages
from django.urls import reverse, resolve
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count
from io import TextIOWrapper
from .file_handlers import Event_Categories_File_Handler, Event_Types_File_Handler, \
							Wards_File_Handler, Post_Codes_File_Handler, Streets_File_Handler, \
							Role_Types_File_Handler, File_Handler, Relationship_Types_File_Handler, \
							People_File_Handler, Relationships_File_Handler

@login_required
def index(request):
	# get the template
	index_template = loader.get_template('people/index.html')
	# get the exceptions
	parents_with_no_children, parents_with_no_children_under_four = get_parents_without_children()
	# get parents with overdue children
	parents_with_overdue_children = get_parents_with_overdue_children()
	# create a dashboard
	dashboard = Dashboard(margin=0)
	# create the roles column for the dashboard
	roles_dashboard_column = Dashboard_Column(width=4)
	# add the role types dashboard panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'ROLES',
															title_icon = 'glyphicon-user',
															column_names = ['counts'],
															rows = get_role_types_with_people_counts(),
															row_name = 'role_type_name',
															row_values = ['count'],
															row_url = 'role_type',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the trained roles dashboard panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'TRAINED ROLES',
															title_icon = 'glyphicon-user',
															column_names = ['counts'],
															rows = get_trained_role_types_with_people_counts(),
															row_name = 'trained_role_name',
															row_values = ['count'],
															row_url = 'trained_role',
															row_parameter_name = 'trained_role_key',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the age status dashboard panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'ADULTS AND CHILDREN',
															title_icon = 'glyphicon-user',
															column_names = ['counts'],
															rows = get_age_statuses_with_counts(),
															row_name = 'status',
															row_values = ['count'],
															row_url = 'age_status',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the ABSS dashboard panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'ABSS',
															title_icon = 'glyphicon-user',
															column_names = ['counts'],
															rows = get_ABSS_types_with_counts(),
															row_name = 'name',
															row_values = ['count'],
															row_url = 'ABSS_type',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# create the exceptions dashboard panel
	exceptions_dashboard_panel = Dashboard_Panel(
														title = 'EXCEPTIONS: PARENTS',
														title_icon = 'glyphicon-warning-sign',
														column_names = ['counts'],
														label_width = 8,
														column_width = 3,
														right_margin = 1)
	# add the parents with no children row to the panel
	exceptions_dashboard_panel.rows.append(
											Dashboard_Panel_Row(
																label = 'Parents with no children',
																values = [len(parents_with_no_children)],
																url = 'parents_with_no_children',
																parameter = 1
																)
											)
	# add the parents with no children under four row to the panel
	exceptions_dashboard_panel.rows.append(
											Dashboard_Panel_Row(
																label = 'Parents with no children under four',
																values = [len(parents_with_no_children_under_four)],
																url = 'parents_without_children_under_four',
																parameter = 1
																)
											)
	# add the overdue parents row to the panel
	exceptions_dashboard_panel.rows.append(
											Dashboard_Panel_Row(
																label = 'Parents with overdue children',
																values = [len(parents_with_overdue_children)],
																url = 'parents_with_overdue_children',
																parameter = 1
																)
											)
	# append the parent exceptions panel to the column
	roles_dashboard_column.panels.append(exceptions_dashboard_panel)
	# add the children age exceptions panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EXCEPTIONS: AGE STATUS',
															title_icon = 'glyphicon-warning-sign',
															title_url = '',
															column_names = ['counts'],
															rows = get_age_status_exceptions(),
															row_name = 'status',
															row_values = ['count'],
															row_url = 'age_exceptions',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# append the roles column to the dashboard
	dashboard.columns.append(roles_dashboard_column)
	# create the events column for the dashboard
	events_dashboard_column = Dashboard_Column(width=4)
	# get the event dashboard dates
	event_dashboard_dates = get_dashboard_dates()
	# set variables for convenience
	first_day_of_this_month = event_dashboard_dates['first_day_of_this_month']
	first_day_of_last_month = event_dashboard_dates['first_day_of_last_month']
	last_day_of_last_month = event_dashboard_dates['last_day_of_last_month']
	first_day_of_this_year = event_dashboard_dates['first_day_of_this_year']
	# add the this month event panel
	events_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS: ' + \
																	first_day_of_this_month.strftime('%B'),
															title_icon = 'glyphicon-calendar',
															title_url = 'events_this_month',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_categories_with_counts(
																					date_from=first_day_of_this_month
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_category_this_month',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 5,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the last month event panel
	events_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS: ' + \
																	first_day_of_last_month.strftime('%B'),
															title_icon = 'glyphicon-calendar',
															title_url = 'events_last_month',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_categories_with_counts(
																					date_from=first_day_of_last_month,
																					date_to=last_day_of_last_month
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_category_last_month',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 5,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the last month event panel
	events_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS: Since ' + \
																	first_day_of_this_year.strftime('%d %B %Y'),
															title_icon = 'glyphicon-calendar',
															title_url = 'events_this_year',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_categories_with_counts(
																					date_from=first_day_of_this_year
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_category_this_year',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 5,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the all time event panel
	events_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS: ALL TIME',
															title_icon = 'glyphicon-calendar',
															title_url = 'events_all_time',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_categories_with_counts(),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_category',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 5,
															column_width = 3,
															right_margin = 1,
															)
											)
	# append the events column to the dashboard
	dashboard.columns.append(events_dashboard_column)
	# create the geo column for the dashboard
	geo_dashboard_column = Dashboard_Column(width=4)
	# add the events in wards panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS IN WARD',
															title_icon = 'glyphicon-globe',
															column_names = ['counts'],
															rows = get_wards_with_event_counts(),
															row_name = 'ward_name',
															row_values = ['count'],
															row_url = 'event_ward',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the events in areas panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'EVENTS IN AREA',
															title_icon = 'glyphicon-globe',
															column_names = ['counts'],
															rows = get_areas_with_event_counts(),
															row_name = 'area_name',
															row_values = ['count'],
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the people in wards panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'PEOPLE IN WARD',
															title_icon = 'glyphicon-globe',
															column_names = ['counts'],
															rows = get_wards_with_people_counts(),
															row_name = 'ward_name',
															row_values = ['count'],
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the people in areas panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'PEOPLE IN AREA',
															title_icon = 'glyphicon-globe',
															column_names = ['counts'],
															rows = get_areas_with_people_counts(),
															row_name = 'area_name',
															row_values = ['count'],
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# append the geo column to the dashboard
	dashboard.columns.append(geo_dashboard_column)
	# set the context
	context = build_context({
								'dashboard' : dashboard
								})
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

# DATA ACCESS FUNCTIONS
# A set of functions which carry out simple and complex data access, filtering and updates.
# These functions are kept as simple as possible.

def get_person(person_id):
	# try to get a person using the person id
	try:
		# do the database call
		person = Person.objects.get(pk=person_id)
	# handle the exception
	except Person.DoesNotExist:
		# set the person to false
		person = False
	# return the result
	return person

def get_relationships_to(person):
	# this function gets all the Person objects via the relationship_to relationship from Perso
	# it returns a list of people with realtionship type added
	# create an empty list
	relationships_to = []
	# get the relationships using the foreign key
	relationships = Relationship.objects.filter(relationship_from=person.pk)
	# now go through the list and get the person
	for relationship in relationships:
		# get the person
		person = Person.objects.get(pk=relationship.relationship_to.pk)
		# add the relationship type to the person object
		person.relationship_type = relationship.relationship_type.relationship_type
		# and the counterpart
		person.relationship_counterpart = relationship.relationship_type.relationship_counterpart
		# and the key
		person.relationship_type_pk = relationship.relationship_type.pk
		# append the person to the list
		relationships_to.append(person)
	# return the relationships
	return relationships_to

def get_trained_status(person,role_type):
	# determine whether a person is trained to perform this role and whether they are active
	# attempt to get the record
	try:
		# do the database call
		trained_role = Trained_Role.objects.get(person=person,role_type=role_type)
	# handle the exception
	except Trained_Role.DoesNotExist:
		# set the trained role to false
		trained_role = False
	# set the value
	if not trained_role:
		# set the default trained status
		trained_status = 'none'
	# otherwise check if the role is active
	elif not trained_role.active:
		# set the text to trained only
		trained_status = 'trained'
	# otherwise the role must be active
	else:
		# set the text to active
		trained_status = 'active'
	# return the result
	return trained_status

def get_people():
	# get a list of people
	people = Person.objects.order_by('last_name', 'first_name')
	# return the list of people
	return people

def get_people_by_name(first_name,last_name):
	# try to get people with the matching name
	people = Person.objects.filter(first_name=first_name,last_name=last_name)
	# return the people
	return people

def check_person_by_name_and_age_status(first_name,last_name,age_status_status):
	# set a blank error
	error = ''
	# check whether the from person exists
	try:
		# attempt to get the record
		person_from = Person.objects.get(
											first_name = first_name,
											last_name = last_name,
											age_status__status = age_status_status
										)
	# deal with the record not existing
	except (Person.DoesNotExist):
		# set the error
		error = ' does not exist.'
	# deal with more than one match
	except (Person.MultipleObjectsReturned):
		# set the error
		error = ' duplicate with name and age status.'
	# return the errors
	return error

def people_search(
					first_name='',
					last_name='',
					role_type='0',
					ABSS_type='0',
					age_status='0',
					trained_role='none'):
	# get all people
	people = Person.objects.all()
	# check whether we have a first name
	if first_name:
		# filter by the name
		people = people.filter(first_name__icontains=first_name)
	# check whether we have a last name
	if last_name:
		# filter by the name
		people = people.filter(last_name__icontains=last_name)
	# if we have a role type, filter by the role type
	if role_type != '0':
		# do the filter
		people = people.filter(default_role_id=int(role_type))
	# if we have an ABSS type, filter by the ABSS type
	if ABSS_type != '0':
		# do the filter
		people = people.filter(ABSS_type_id=int(ABSS_type))
	# if we have an age status, filter by the age status
	if age_status != '0':
		# do the filter
		people = people.filter(age_status_id=int(age_status))
	# if we have an age status, filter by the age status
	if age_status != '0':
		# do the filter
		people = people.filter(age_status_id=int(age_status))
	# if we have a trained role, filter by the trained role
	if trained_role != 'none':
		# get the role type
		role_type = Role_Type.objects.get(pk=int(extract_id(trained_role)))
		# do the filter
		people = people.filter(trained_roles=role_type)
		# and check whether we want active only
		if 'active' in trained_role:
			# got through the people
			for person in people:
				# attempt to get the active record
				if not person.trained_role_set.filter(role_type=role_type,active=True).exists():
					# exclude the person
					people = people.exclude(pk=person.pk)
	# return the list of people
	return people

def get_parents_without_children():
	# create an empty list
	parents_with_no_children = []
	parents_with_no_children_under_four = []
	# get today's date
	today = datetime.date.today()
	# get the date four years ago
	today_four_years_ago = today.replace(year=today.year-4)
	# attempt to get parents with no children
	parents = Person.objects.filter(default_role__role_type_name__contains='Parent')
	# exclude those with pregnancy dates in the future
	parents = parents.exclude(pregnant=True, due_date__gte=datetime.date.today())
	# order the list
	parents = parents.order_by('last_name','first_name')
	# now exclude those where we can find a child relationship
	for parent in parents:
		# attempt to get parent relationships
		parent_relationships = parent.rel_from.filter(relationship_type__relationship_type='parent')
		# if we didn't get a parent relationship, add the parent to the no children list
		if not parent_relationships:
			# append to the no children list
			parents_with_no_children.append(parent)
		# otherwise check how old the children are
		else:
			# set a flag
			child_under_four = False
			# go through the relationships
			for relationship in parent_relationships:
				# check whether the child has a date of birth
				if relationship.relationship_to.date_of_birth != None:
					# and whether the date is less than four years ago
					if relationship.relationship_to.date_of_birth >= today_four_years_ago:
						# set the flag
						child_under_four = True
			# see whether we got a child
			if not child_under_four:
				# add the parent to the list
				parents_with_no_children_under_four.append(parent)
	# return the results
	return parents_with_no_children, parents_with_no_children_under_four

def get_parents_with_overdue_children():
	# return a list of parents with a pregnancy flag and a due date before today
	return Person.objects.filter(
									pregnant=True,
									due_date__lt=datetime.date.today()
									)

def get_children_over_four():
	# get today's date
	today = datetime.date.today()
	# return the results
	return Person.objects.filter(date_of_birth__lt=today.replace(year=today.year-4),
									age_status__status='Child under four')

def get_age_status_exceptions():
	# return a list of all the age statuses, supplemented with counts of people outside the age range
	age_statuses = []
	# get today's date
	today = datetime.date.today()
	# now go through the age statuses
	for age_status in Age_Status.objects.all():
		# get the exceptions
		age_exceptions = age_status.person_set.filter(
								date_of_birth__lt=today.replace(year=today.year-age_status.maximum_age))
		# see whether we got any exceptions
		if age_exceptions.count() > 0:
			# add the count to the object
			age_status.count = age_exceptions.count()
			# add the object to the list
			age_statuses.append(age_status)
	# return the results
	return age_statuses

def get_addresses_by_number_or_street(house_name_or_number,street):
	# try to get addresses with the matching properties
	addresses = Address.objects.filter(
										house_name_or_number__contains=house_name_or_number,
										street__contains=street)
	# return the people
	return addresses

def get_post_code_by_code(code):
	# try to get a post code using the code
	try:
		# do the database call
		post_code = Post_Code.objects.get(post_code=code)
	# handle the exception
	except Post_Code.DoesNotExist:
		# set the post code to false
		post_code = False
	# return the result
	return post_code

def get_streets_by_name_and_post_code(name='',post_code=''):
	# get the streets
	streets = Street.objects.all()
	# if there is a name, filter by name
	if name:
		# apply the filter
		streets = streets.filter(name__icontains=name)
	# if there is a post code, filter by post code
	if post_code:
		# apply the filter
		streets = streets.filter(post_code__post_code__icontains=post_code)
	# return the results
	return streets

def get_street(street_id):
	# try to get street
	try:
		street = Street.objects.get(pk=street_id)
	# handle the exception
	except Street.DoesNotExist:
		# set a false value
		street = False
	# return the street
	return street

def get_ward(ward_id):
	# try to get ward
	try:
		ward = Ward.objects.get(pk=ward_id)
	# handle the exception
	except Ward.DoesNotExist:
		# set a false value
		ward = False
	# return the ward
	return ward

def get_ethnicity(ethnicity_id):
	# try to get ethnicity
	try:
		ethnicity = Ethnicity.objects.get(pk=ethnicity_id)
	# handle the exception
	except Ethnicity.DoesNotExist:
		# set a false value
		ethnicity = False
	# return the ethnicity
	return ethnicity

def get_relationship_type(relationship_type_id):
	# try to get relationship type
	try:
		relationship_type = Relationship_Type.objects.get(pk=relationship_type_id)
	# handle the exception
	except Relationship_Type.DoesNotExist:
		# set a false value
		relationship_type = False
	# return the relationship_type
	return relationship_type

def get_relationship_type_by_type(relationship_type):
	# try to get relationship type using the name of the relationship type
	try:
		relationship_type = Relationship_Type.objects.get(relationship_type=relationship_type)
	# handle the exception
	except Relationship_Type.DoesNotExist:
		# set a false value
		relationship_type = false
	# return the relationship type
	return relationship_type

def get_event(event_id):
	# try to get an event using the event id
	try:
		# do the database call
		event = Event.objects.get(pk=event_id)
	# handle the exception
	except Event.DoesNotExist:
		# set the address to false
		event = False
	# return the result
	return event

def get_events():
	# get a list of events
	events = Event.objects.order_by('-date', '-start_time')
	# return the list of people
	return events

def search_events(name='',event_type=0,event_category=0,ward=0,date_from=None,date_to=None):
	# check whether we have any search terms, otherwise return all events
	# start by getting all the events
	events = Event.objects.all()
	# now filter by name if we have a name
	if name:
		# filter by name
		events = events.filter(name__icontains=name)
	# if we have a from date, filter by that date
	if date_from != None:
		# filter by date
		events = events.filter(date__gte=date_from)
	# if we have a to date, filter by that date
	if date_to != None:
		# filter by date
		events = events.filter(date__lte=date_to)
	# if we have a type, filter by that
	if event_type != 0:
		# filter by type
		events = events.filter(event_type_id=event_type)
	# if we have a category, filter by that
	if event_category != 0:
		# filter by type
		events = events.filter(event_type__event_category_id=event_category)
	# if we have a ward, filter by that
	if ward != 0:
		# filter by type
		events = events.filter(ward_id=ward)
	# return the list of events
	return events

def add_counts_to_events(events):
	# take a list of events, and add the count of participated and volunteered numbers to them
	for event in events:
		# get the registrations
		event.registered_count = event.event_registration_set.filter(registered=True).count()
		# and the participations
		event.participated_count = event.event_registration_set.filter(participated=True).count()
	# return the results
	return events

def get_event_type(event_type_id):
	# try to get event type
	try:
		event_type = Event_Type.objects.get(pk=event_type_id)
	# handle the exception
	except Event_Type.DoesNotExist:
		# set a false value
		event_type = False
	# return the event type
	return event_type

def get_event_types():
	# return a list of all the event type objects
	return Event_Type.objects.all()

def get_event_types_with_counts(date_from=0, date_to=0):
	# return a list of all the event type objects, supplemented with counts
	event_types = get_event_types()
	# now go through the role types
	for event_type in event_types:
		# get the registrations
		event_registrations = Event_Registration.objects.filter(event__event_type=event_type, registered=True)
		# get the participations
		event_participations = Event_Registration.objects.filter(event__event_type=event_type, participated=True)
		# if we have a from date, filter further
		if date_from:
			# filter the registrations
			event_registrations = event_registrations.filter(event__date__gte=date_from)
			# and the participations
			event_participations = event_participations.filter(event__date__gte=date_from)
		# if we have a before date, filter further
		if date_to:
			# filter the registrations
			event_registrations = event_registrations.filter(event__date__lte=date_to)
			# and the participations
			event_participations = event_participations.filter(event__date__lte=date_to)
		# set the counts
		event_type.registered_count = event_registrations.count()
		event_type.participated_count = event_participations.count()
	# return the results
	return event_types

def get_trained_role_types_with_people_counts():
	# create the list
	trained_role_list = []
	# return a list of all the trained role type objects, supplemented with counts
	role_types = Role_Type.objects.filter(trained=True)
	# now go through the role types
	for role_type in role_types:
		# set the count for trained
		role_type.count = role_type.trained_people.count()
		# and the key for trained
		role_type.trained_role_key = 'trained_' + str(role_type.pk)
		# and the name for trained
		role_type.trained_role_name = 'Trained ' + role_type.role_type_name
		# and append a copy of the object to the list
		trained_role_list.append(role_type)
		# create a new object
		active_role_type = copy.deepcopy(role_type)
		# now set the count for active
		active_role_type.count = active_role_type.trained_role_set.filter(active=True).count()
		# and the key for the url
		active_role_type.trained_role_key = 'active_' + str(active_role_type.pk)
		# and the name for active
		active_role_type.trained_role_name = 'Active ' + role_type.role_type_name
		# and append the object to the list
		trained_role_list.append(active_role_type)
	# return the results
	return trained_role_list

def get_event_categories_with_counts(date_from=0, date_to=0):
	# get the event categories
	event_categories = Event_Category.objects.all().order_by('name')
	# go throught the event categories
	for event_category in event_categories:
		# get the registrations
		event_registrations = Event_Registration.objects.filter(
																event__event_type__event_category=event_category,
																registered=True)
		# get the participations
		event_participations = Event_Registration.objects.filter(event__event_type__event_category=event_category,
																participated=True)
		# if we have a from date, filter further
		if date_from:
			# filter the registrations
			event_registrations = event_registrations.filter(event__date__gte=date_from)
			# and the participations
			event_participations = event_participations.filter(event__date__gte=date_from)
		# if we have a before date, filter further
		if date_to:
			# filter the registrations
			event_registrations = event_registrations.filter(event__date__lte=date_to)
			# and the participations
			event_participations = event_participations.filter(event__date__lte=date_to)
		# set the counts
		event_category.registered_count = event_registrations.count()
		event_category.participated_count = event_participations.count()
	# return the results
	return event_categories

def get_event_registrations(event):
	# return a list of registrations for an event
	return event.event_registration_set.all()

def get_registration(person, event):
	# try to get a registration
	try:
		# do the database query
		event_registration = Event_Registration.objects.get(
																person=person,
																event=event
															)
	# handle the exception
	except Event_Registration.DoesNotExist:
		# set a false value
		event_registration = False
	# return the value
	return event_registration

def get_role_types(events_or_people='all'):
	# get a list of the role type objects
	role_types = Role_Type.objects.all().order_by('role_type_name')
	# now filter if necessary
	if events_or_people == 'events':
		# filter on event flag
		role_types.filter(use_for_events=True)
	# otherwise check for people
	elif events_or_people == 'people':
		# filter on people flag
		role_types.filter(use_for_events=True)
	# return the results
	return role_types

def get_role_types_with_people_counts():
	# return a list of all the role type objects, supplemented with counts
	role_types = get_role_types('people')
	# now go through the role types
	for role_type in role_types:
		# get the count
		role_type.count = Person.objects.filter(default_role=role_type).count()
	# return the results
	return role_types

def get_wards_with_people_counts():
	# return a list of all the wards with people counts
	wards = Ward.objects.all()
	# now go through the wards
	for ward in wards:
		# get the count
		ward.count = Person.objects.filter(street__post_code__ward=ward).count()
	# return the results
	return wards

def get_areas_with_people_counts():
	# return a list of all the areas with people counts
	areas = Area.objects.all()
	# now go through the areas
	for area in areas:
		# get the count
		area.count = Person.objects.filter(street__post_code__ward__area=area).count()
	# return the results
	return areas

def get_wards_with_event_counts():
	# return a list of all the wards with event counts
	wards = Ward.objects.all()
	# now go through the wards
	for ward in wards:
		# get the count
		ward.count = Event.objects.filter(ward=ward).count()
	# return the results
	return wards

def get_areas_with_event_counts():
	# return a list of all the areas with people counts
	areas = Area.objects.all()
	# now go through the areas
	for area in areas:
		# get the count
		area.count = Event.objects.filter(ward__area=area).count()
	# return the results
	return areas

def get_role_type(role_type_id):
	# try to get role type
	try:
		role_type = Role_Type.objects.get(pk=role_type_id)
	# handle the exception
	except Role_Type.DoesNotExist:
		# set a false value
		role_type = False
	# return the role type
	return role_type

def get_role_type_by_name(role_type_name):
	# try to get role type
	try:
		role_type = Role_Type.objects.get(role_type_name=role_type_name)
	# handle the exception
	except Role_Type.DoesNotExist:
		# set a false value
		role_type = False
	# return the role type
	return role_type

def get_ethnicities():
	# return a list of all the ethnicity objects
	return Ethnicity.objects.all()

def get_ethnicity_list():
	# return a list containing all of the ethnicity descriptions
	ethnicity_list = []
	# get the ethnicities
	ethnicities = Ethnicity.objects.all()
	# go through them all
	for ethnicity in ethnicities:
		# append to the list
		ethnicity_list.append(ethnicity.description)
	# return the list
	return ethnicity_list

def get_relationship_types():
	# return a list of all the relationship type objects
	return Relationship_Type.objects.all()

def get_relationship(person_from, person_to):
	# try to get a relationship
	try:
		# do the database query
		relationship = Relationship.objects.get(
												relationship_from=person_from.pk,
												relationship_to=person_to.pk
												)
	# handle the exception
	except Relationship.DoesNotExist:
		# set a false value
		relationship = False
	# return the value
	return relationship

def get_relationship_from_and_to(person_from, person_to):
	# get both sides of a relationship
	# start with the from side
	relationship_from = get_relationship(person_from, person_to)
	# and the to side
	relationship_to = get_relationship(person_to, person_from)
	# return the results
	return relationship_from, relationship_to

def get_question(question_id):
	# try to get a question
	try:
		question = Question.objects.get(pk=question_id)
	# handle the exception
	except Question.DoesNotExist:
		# set a false value
		question = False
	# return the role type
	return question

def get_option(option_id):
	# try to get a option
	try:
		option = Option.objects.get(pk=option_id)
	# handle the exception
	except Option.DoesNotExist:
		# set a false value
		option = False
	# return the role type
	return option

def get_questions_and_answers(person):
	# this function gets a list of questions, and adds the answers relevant to the person
	# get the list of questions
	questions = Question.objects.all().order_by('question_text')
	# get the options for each question
	for question in questions:
		# get the answers and stash it in the object
		question.options = question.option_set.all().order_by('option_label')
		# set a default answer
		question.answer = 0
		# and default answer test
		question.answer_text = 'No answer'
		# now try to get an answer
		answer = get_answer(
							person=person,
							question=question
							)
		# check whether we got an answer
		if answer:
			# set the answer
			question.answer = answer.option.pk
			# and the text
			question.answer_text = answer.option.option_label
		# set a default note
		question.note = ''
		# now try to get an answer note
		answer_note = get_answer_note(
										person=person,
										question=question
										)
		# check whether we got an answer note
		if answer_note:
			# set the answer
			question.note = answer_note.notes
	# return the results
	return questions

def get_answer(person,question):
	# try to get an answer
	try:
		# do the database query
		answer = Answer.objects.get(
									person=person,
									question=question
									)
	# handle the exception
	except Answer.DoesNotExist:
		# set a false value
		answer = False
	# return the value
	return answer

def get_answer_note(person,question):
	# try to get an answer note
	try:
		# do the database query
		answer_note = Answer_Note.objects.get(
												person=person,
												question=question
												)
	# handle the exception
	except Answer_Note.DoesNotExist:
		# set a false value
		answer_note = False
	# return the value
	return answer_note

def get_ABSS_types():
	# return a list of all the ABSS type objects
	return ABSS_Type.objects.all()

def get_ABSS_types_with_counts():
	# return a list of all the ABSS type objects, supplemented with counts
	ABSS_types = get_ABSS_types()
	# now go through the ABSS types
	for ABSS_type in ABSS_types:
		# get the count
		ABSS_type.count = Person.objects.filter(ABSS_type=ABSS_type).count()
	# return the results
	return ABSS_types

def get_ABSS_type(ABSS_type_id):
	# try to get ABSS type
	try:
		ABSS_type = ABSS_Type.objects.get(pk=ABSS_type_id)
	# handle the exception
	except ABSS_Type.DoesNotExist:
		# set a false value
		ABSS_type = False
	# return the ABSS type
	return ABSS_type

def get_age_statuses():
	# return a list of all the ABSS type objects
	return Age_Status.objects.all()

def get_age_statuses_with_counts():
	# return a list of all the ABSS type objects, supplemented with counts
	age_statuses = get_age_statuses()
	# now go through the ABSS types
	for age_status in age_statuses:
		# get the count
		age_status.count = Person.objects.filter(age_status=age_status).count()
	# return the results
	return age_statuses

def get_age_status(age_status_id):
	# try to get ABSS type
	try:
		age_status = Age_Status.objects.get(pk=age_status_id)
	# handle the exception
	except Age_Status.DoesNotExist:
		# set a false value
		age_status = False
	# return the ABSS type
	return age_status

def create_person(
					first_name,
					last_name,
					middle_names='',
					default_role=False,
					date_of_birth=None,
					gender='',
					ethnicity=0,
					ABSS_type=0,
					age_status=0,
					):
	# get the age status
	if not age_status:
		# set the default to adult
		age_status = Age_Status.objects.get(status='Adult').pk
	# otherwise get the actual age status
	else:
		# get the age status
		age_status = get_age_status(age_status)
	# check whether we have a role type
	if default_role:
		# get the role
		default_role = get_role_type(default_role)
	# otherwise set unknown
	else:
		# get the role type dependent on the age status
		default_role = age_status.default_role_type
	# get the default values for ethnicity, ABSS Type and age_status
	if not ethnicity:
		ethnicity = Ethnicity.objects.get(description='Prefer not to say').pk
	# and the ABSS type
	if not ABSS_type:
		ABSS_type = ABSS_Type.objects.get(name='ABSS beneficiary').pk
	# create a person
	person = Person(
					first_name = first_name,
					middle_names = middle_names,
					last_name = last_name,
					date_of_birth = date_of_birth,
					gender = gender,
					default_role = default_role,
					ethnicity = get_ethnicity(ethnicity),
					ABSS_type = get_ABSS_type(ABSS_type),
					age_status = age_status,
						)
	# save the record
	person.save()
	# create the role history
	role_history = Role_History(
								person = person,
								role_type = default_role)
	# and save it
	role_history.save()
	# and return the person
	return person

def create_address(house_name_or_number,street,town,post_code):
	# create an address
	address = Address(
					house_name_or_number = house_name_or_number,
					street = street,
					town = town,
					post_code = post_code
						)
	# save the record
	address.save()
	# and return the address
	return address

def create_residence(person, address):
	# create a residence
	residence = Residence(
					person = person,
					address = address
							)
	# save the residence
	residence.save()
	# return the residence
	return residence

def create_event(name, description, date, start_time, end_time, event_type, location, ward):
	# create an event
	event = Event(
					name = name,
					description = description,
					location = location,
					ward = ward,
					date = date,
					start_time = start_time,
					end_time = end_time,
					event_type = event_type
						)
	# save the record
	event.save()
	# and return the event
	return event

def create_registration(event, person, registered, participated, role_type):
	# create a registration
	registration = Event_Registration(
								event = event,
								person = person,
								registered = registered,
								participated = participated,
								role_type = role_type
						)
	# save the record
	registration.save()
	# and return the registration
	return registration

def update_registration(registration, registered, participated, role_type):
	# update the registration
	registration.registered = registered
	registration.participated = participated
	registration.role_type = role_type
	# save the record
	registration.save()
	# and return the record
	return registration

# BUILD FUNCTIONS
# These are slightly more sophisticated creation functions which do additional work such as looking up values and 
# setting messsages.

def edit_relationship(request, person_from, person_to, relationship_type_id, show_messages=True):
	# edit a relationship: this includes deletion of existing relationships and creation of new relationships
	# if we have been passed a relationship type id of zero of False, we just do the deletion
	# set a flag
	success = False
	# check whether we either have a valid relationship type or a zero
	if relationship_type_id:
		# get the relationship type
		relationship_type_from = get_relationship_type(relationship_type_id)
		# if we didn't get one, set an error message and crash out
		if not relationship_type_from:
			# set the messages if messages are required
			if show_messages:
				 # set the message
				messages.error(request, 'Relationship type ' + str(relationship_type_id) + ' does not exist.')
			# crash out
			return success
	# see whether we have an existing relationship
	relationship_from, relationship_to = get_relationship_from_and_to(person_from, person_to)
	# if there is an existing relationship, check whether it is different from the one we have been passed
	if relationship_from:
		# check whether the relationship has changed
		if (relationship_from.relationship_type.pk != relationship_type_id):
			# delete the existing relationships
			relationship_from.delete()
			relationship_to.delete()
			# set a message if messages are required
			if show_messages:
				# set the message
				messages.success(request,'Relationship between ' + str(person_from) + ' and ' 
									+ str(person_to) + ' deleted.')
		# if nothing has changed, we are done, so we can return success
		else:
			# set the flag
			success = True
			# return the value
			return success
	# if we have a valid realtionship type, create the relationship
	if relationship_type_id:
		# try to create the relationship
		if Relationship.create_relationship(
											person_from = person_from,
											person_to = person_to,
											relationship_type_from = relationship_type_from
											):
			# set the success message if messages are required
			if show_messages:
				# set the message
				messages.success(request,
					'Relationship created: ' + str(person_from) + 
					' is the ' + relationship_type_from.relationship_type + ' of ' + str(person_to))
				# and the other success message
				messages.success(request,
					'Relationship created: ' + str(person_to) + 
					' is the ' + relationship_type_from.relationship_counterpart + ' of ' + str(person_from))
			# set the success flag
			success = True
		# otherwise set the failure message
		else:
			# set the message if messages are required
			if show_messages:
				# set the message
				messages.error(request, 'Relationship could not be created.')
	# return the result
	return success

def build_event(request, name, description, date, start_time, end_time, event_type_id, location, ward_id, areas):
	# get the event type
	event_type = get_event_type(event_type_id)
	# check whether we have a ward
	if ward_id != '0':
		# get the ward
		ward = get_ward(ward_id)
	# otherwise set null
	else:
		# set the ward to null
		ward = None
	# if we got an event type, create the event
	if event_type:
		# create the event
		event = create_event(
								name = name,
								description = description,
								location = location,
								ward = ward,
								date = date,
								start_time = start_time,
								end_time = end_time,
								event_type = event_type
							)
		# set a message
		messages.success(request, 'New event (' + str(event) + ') created.')
		# got through the areas
		for area_id in areas.keys():
			# determine whether the event is available to this area
			if (areas[area_id] == True) or (ward and ward.area.pk == area_id):
				# add the area
				event.areas.add(Area.objects.get(id=area_id))
	# otherwise set a message
	else:
		# set the failed creation message
		messages.error(request, 'Event (' + name + ') could not be created: event type does not exist.')
	# return the event
	return event

def build_registration(request, event, person_id, registered, participated, role_type_id, show_messages=True):
	# attempt to create a new registration, checking first that the registration does not exit
	# first get the person
	person = get_person(person_id)
	# if that didn't work, set an error and return
	if not person:
		# check whether messages are needed
		if show_messages:
			# set the message
			messages.error(request,'Registration for person ' + str(person_id) + ' failed: person does not exist.')
		# and return
		return False
	# now attempt to get the role type
	role_type = get_role_type(role_type_id)
	# if that didn't work, set an error and return
	if not role_type:
		# check whether messages are needed
		if show_messages:
			# set the message
			messages.error(request,'Registration for person ' + str(person_id) + ' failed: role type does not exist.')
		# and return
		return False
	# now attempt to get the registration
	registration = get_registration(person,event)
	# check whether we got a registration or not
	if not registration:
		# create the registration
		registration = create_registration(
											event = event,
											person = person,
											registered = registered,
											participated = participated,
											role_type = role_type
											)
		# check whether messages are needed
		if show_messages:
			# set the success message
			messages.success(request,'New registration (' + str(registration) + ') created.')
	# otherwise set a warning message
	else:
		# check whether there is any change
		if registration.registered != registered \
		or registration.participated != participated \
		or registration.role_type != role_type:
			# edit the registration
			registration = update_registration(
												registration = registration,
												registered = registered,
												participated = participated,
												role_type = role_type)
			# check whether messages are needed
			if show_messages:
				# set the success message
				messages.success(request,'Registration (' + str(registration) + ') updated.')
	# return the registration
	return registration

def remove_registration(request, event, person_id):
	# attempt to remove a registration record, checking first that the registration exists
	# first get the person
	person = get_person(person_id)
	# if that didn't work, set an error and return
	if not person:
		# set the message
		messages.error(request,'Deletion of registration for person ' + str(person_id) + ' failed: person does not exist.')
		# and return
		return False
	# now attempt to get the registration
	registration = get_registration(
									person=person,
									event=event
									)
	# check whether we got the registration or not
	if registration:
		# preserve the name
		registration_name = str(registration)
		# delete the registration
		registration.delete()
		# set the success message
		messages.success(request,'Registration (' + registration_name + ') deleted.')
	# otherwise set a warning message
	else:
		# set the warning that the registration does not exist
		messages.error(request,'Registration does not exist.')
	# return with no parameters
	return

def build_answer(request, person, question_id, option_id):
	# attempt to get the question
	question = get_question(question_id)
	# deal with exceptions if we didn't get a question
	if not question:
		# set the error
		messages.error(request,'Could not create answer: question' + str(question_id) + ' does not exist.')
		# and crash out
		return False
	# check that we have a valid option
	if option_id != 0:
		# get the option
		option = get_option(option_id)
		# deal with exceptions if we didn't get an option
		if not option:
			# set the error
			messages.error(request,'Could not create answer: option ' + str(option_id) + ' does not exist.')
			# and crash out
			return False
	# see whether we have an answer
	answer = get_answer(person,question)
	# if we got an answer, check what we have been asked to do to it
	if answer:
		# see whether we have an option id
		if option_id == 0:
			# save the answer text
			answer_text = str(answer)
			# we have been asked to delete the answer
			answer.delete()
			# and set the message
			messages.success(request,answer_text + ' - deleted successfully.')
		# otherwise we have been asked to set an option
		elif answer.option.pk != option_id:
			# we have been asked to update the answer
			answer.option = option
			# save the answer
			answer.save()
			# and set the message
			messages.success(request,str(answer) + ' - updated successfully.')
	# otherwise we have to do a creation if we have an option id
	elif option_id != 0:
		# create the answer
		answer = Answer(
						person = person,
						option = option,
						question = question
						)
		# save the answer
		answer.save()
		# and set the message
		messages.success(request,str(answer) + ' - created successfully.')
	# and we're done
	return answer

def build_answer_note(request, person, question_id, notes):
	# attempt to get the question
	question = get_question(question_id)
	# deal with exceptions if we didn't get a question
	if not question:
		# set the error
		messages.error(request,'Could not create answer note: question' + str(question_id) + ' does not exist.')
		# and crash out
		return False
	# see whether we have an answer note
	answer_note = get_answer_note(person,question)
	# if we got an answer note, check what we have been asked to do to it
	if answer_note:
		# see whether we have any text
		if notes == '':
			# save the answer text
			answer_note_text = str(answer_note)
			# we have been asked to delete the answer
			answer_note.delete()
			# and set the message
			messages.success(request,answer_note_text + ' - deleted successfully.')
		# otherwise we have been asked to record an answer note
		elif answer_note.notes != notes:
			# we have been asked to update the answer note
			answer_note.notes = notes
			# save the answer note
			answer_note.save()
			# and set the message
			messages.success(request,str(answer_note) + ' - updated successfully.')
	# otherwise we have to do a creation if we have an option id
	elif notes != '':
		# create the answer note
		answer_note = Answer_Note(
							person = person,
							question = question,
							notes = notes
						)
		# save the answer note
		answer_note.save()
		# and set the message
		messages.success(request,str(answer_note) + ' - created successfully.')
	# and we're done
	return answer_note

def update_person(
					request,
					person,
					first_name,
					middle_names,
					last_name,
					email_address,
					home_phone,
					mobile_phone,
					emergency_contact_details,
					date_of_birth,
					gender,
					pregnant,
					due_date,
					default_role_id,
					ethnicity_id,
					ABSS_type_id,
					ABSS_start_date,
					ABSS_end_date,
					age_status_id,
					notes
				):
	# set the role change flag to false: we don't know whether the role has changed
	role_change = False
	# attempt to get the ethnicity
	ethnicity = get_ethnicity(ethnicity_id)
	# set the value for the person
	if ethnicity:
		# set the value
		person.ethnicity = ethnicity
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'Ethnicity does not exist.')
	# attempt to get the ABSS type
	ABSS_type = get_ABSS_type(ABSS_type_id)
	# set the value for the person
	if ABSS_type:
		# set the value
		person.ABSS_type = ABSS_type
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'ABSS Type does not exist.')
	# attempt to get the age status
	age_status = get_age_status(age_status_id)
	# set the value for the person
	if age_status:
		# set the value
		person.age_status = age_status
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'Age Status does not exist.')
	# attempt to get the role type
	default_role = get_role_type(default_role_id)
	# set the value for the person
	if default_role:
		# check whether the role has changed
		if person.default_role != default_role:
			# set the role change flag
			role_change = True
		# set the value
		person.default_role = default_role
	# otherwise set a message
	else:
		# set the banner
		messages.error(request, 'Role type does not exist.')
	# update the person record
	person.first_name = first_name
	person.middle_names = middle_names
	person.last_name = last_name
	person.email_address = email_address
	person.home_phone = home_phone
	person.mobile_phone = mobile_phone
	person.date_of_birth = date_of_birth
	person.gender = gender
	person.pregnant = pregnant
	person.due_date = due_date
	person.notes = notes
	person.ABSS_start_date = ABSS_start_date
	person.ABSS_end_date = ABSS_end_date
	person.emergency_contact_details = emergency_contact_details
	# save the record
	person.save()
	# and save a role history if the role has changed
	if role_change:
		# create the object
		role_history = Role_History(
									person = person,
									role_type = default_role
									)
		# and save it
		role_history.save()
	# set a success message
	messages.success(request, str(person) + ' profile updated.')
	# return the person
	return person

def update_address(
					request,
					person,
					house_name_or_number,
					street_id
				):
	# set the success flag
	success = False
	# attempt to get the street
	street = get_street(street_id)
	# set the value for the person
	if street:
		# set the value
		person.street = street
		# set the house name or numer
		person.house_name_or_number = house_name_or_number
		# save the person
		person.save()
		# set the message
		messages.success(request, 'Address updated for ' + str(person))
		# set the success flag
		success = True
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'Street does not exist.')
	# return the flag
	return success

def remove_address(
					request,
					person
				):
	# set the value
	person.street = None
	# set the house name or numer
	person.house_name_or_number = ''
	# save the person
	person.save()
	# set the message
	messages.success(request, 'Address removed for ' + str(person))

def build_trained_role(person,role_type_id,trained_status):
	# create, delete or modify a trained role record, based on its current state and the desired trained status
	# get the role type
	role_type = Role_Type.objects.get(pk=role_type_id)
	# check that the combination of role type and age status is valid
	if not person.age_status.role_types.filter(pk=role_type.pk).exists():
		# set the status to 'none'
		trained_status = 'none'
	# attempt to get the record
	try:
		# do the database call
		trained_role = Trained_Role.objects.get(person=person,role_type=role_type)
	# handle the exception
	except Trained_Role.DoesNotExist:
		# set the trained role to false
		trained_role = False
	# delete an unwanted trained status
	if trained_status == 'none':
		# check whether a status exist
		if trained_role:
			# delete the record
			trained_role.delete()
	# deal with a trained status which is required
	else:
		# set up a trained role if one is required
		if not trained_role:
			# create the role
			trained_role = Trained_Role(person=person,role_type=role_type)
		# set the active status if required
		if trained_status == 'active':
			# set the flag
			trained_role.active = True
		# otherwise set the flag to false
		else:
			# set the flag
			trained_role.active = False
		# save the record
		trained_role.save()
	# go back to where we came from
	return

# UTILITY FUNCTIONS
# A set of functions which perform basic utility tasks such as string handling and list editing

# function to extract an id number from the end of an underscore delimited string
def extract_id(field_name):
	# build a list from the string
	name_elements = field_name.split('_')
	# now return the final element
	return name_elements[-1]

def remove_existing_relationships(person_from, people):
	# this function takes a person and a list of people, and returns a list of only those people who do
	# not have an existing relationship
	# create an empty list
	people_without_existing_relationships = []
	# now got through the list
	for person_to in people:
		# check that we haven't got the person themselves
		if person_to != person_from:
			# try to get a relationship
			try:
				# do the database query
				relationship = Relationship.objects.get(
														relationship_from=person_from.pk,
														relationship_to=person_to.pk
														)
			# handle the exception
			except Relationship.DoesNotExist:
				# add the person to the list
				people_without_existing_relationships.append(person_to)
	# return the list
	return people_without_existing_relationships

def remove_existing_addresses(person, addresses):
	# this function takes a person and a list of addresses, and returns a list of only those addresses where
	# the person does not have an existing residence
	# create an empty list
	addresses_without_existing_residences = []
	# now got through the list
	for address in addresses:
		# attempt to get the residence
		if not get_residence(person,address):
			# add the address to the list
			addresses_without_existing_residences.append(address)
	# return the list
	return addresses_without_existing_residences

def remove_existing_registrations(event, people):
	# this function takes an and a list of people, and returns a list of only those events where
	# the person does not have an existing registration for that event
	# create an empty list
	people_without_existing_registrations = []
	# now got through the list
	for person in people:
		# attempt to get the residence
		if not get_registration(person,event):
			# add the address to the list
			people_without_existing_registrations.append(person)
	# return the list
	return people_without_existing_registrations

def check_checkbox(field_dict, field_name):
	# take a dictionary of fields and a field name, and return true if a checkbox of that field name is marked 'on',
	# otherwise return false
	# set the result
	result = False
	# check the value
	if field_dict.get(field_name, False) == 'on':
		# set the result
		result = True
	# return the result
	return result

def build_context(context_dict):
	# take a context dictionary and add additional items
	# check whether we have a default date
	if not context_dict.get('default_date', False):
		# set the default date to the default
		context_dict['default_date'] = '01/01/2010'
	# set the site details from the environment variables
	context_dict['site_name'] = os.getenv('BETTERSTART_NAME', None)
	context_dict['nav_background'] = os.getenv('BETTERSTART_NAV','betterstart-background-local-test')
	# return the dictionary
	return context_dict

def get_dashboard_dates(date=0):
	# this function returns a dict of dates inclduing the first day of the month, the first day of the previous
	# month, and the first day of this financial year
	# create an empty dictionary
	date_dict = {}
	# check whether we got a date
	if date:
		# set today to the date
		today = date
	# otherwise set the date to today
	else:
		# set the date to today
		today = datetime.date.today()
	# and set the dictionary entry to today
	date_dict['today'] = today
	# first, figure out the first day of this month
	date_dict['first_day_of_this_month'] = today.replace(day=1)
	# now, figure out the last day of the previous month
	date_dict['last_day_of_last_month'] = date_dict['first_day_of_this_month'] - datetime.timedelta(days=1)
	# now, figure out the first day of the last month
	date_dict['first_day_of_last_month'] = date_dict['last_day_of_last_month'].replace(day=1)
	# now figure out the first day of this year (most recent 1st of April)
	date_dict['first_day_of_this_year'] = today.replace(day=1,month=4)
	# now check whether the date is in the future
	if date_dict['first_day_of_this_year'] > today:
		# go back to last year
		date_dict['first_day_of_this_year'] = first_day_of_this_year.replace(year=first_day_of_this_year.year-1)
	# return the dictionary
	return date_dict

def build_event_area_dict(form_dict):
	# go through the cleaned data dict from a form and build a list of areas
	# create the dict
	area_dict = {}
	# got through the areas
	for area in Area.objects.filter(use_for_events=True):
		# get the value
		area_dict[area.pk] = form_dict['area_' + str(area.pk)]
	# return the new dict
	return area_dict

def convert_optional_ddmmyy(date):
	# set the date
	if date != '':
		# parse the value
		date = datetime.datetime.strptime(date,'%d/%m/%Y')
	# otherwise set the value to None
	else:
		# set it to None
		date = None
	# return the value
	return date

def convert_optional_datetime(this_datetime,format='%d/%m/%Y'):
	# set the datetime
	if this_datetime != None:
		# parse the value
		this_datetime = this_datetime.strftime(format)
	# otherwise set the value to blank
	else:
		# set it to blank
		this_datetime = ''
	# return the value
	return this_datetime

def datetime_valid(datetime_value,datetime_format):
	# check the datetime
	try:
		datetime.datetime.strptime(datetime_value, datetime_format)
		# set the result
		result = True
	# deal with the exception
	except ValueError:
		# set the result
		result = False
	# return the result
	return result

def build_records(data_class,fields):
	# create the blank list of records
	records = []
	# now go through the reccords
	for record in data_class.objects.all():
		# create a blank set of csv fields
		field_list = []
		# go through the fields
		for field in fields:
			# get the attritbute
			field_list.append(getattr(record,field))
		# append a record
		records.append(field_list)
	# return the results
	return records

# VIEW FUNCTIONS
# A set of functions which implement the functionality of the site and serve pages.

def log_user_in(request):
	# set a flag to indicate whether this is a successful login
	successful_login = False
	# check whether user is already logged in
	if request.user.is_authenticated:
		# the user is already logged in
		successful_login = True
	else:
		# handle the login request
		# get the template
		login_template = loader.get_template('people/login.html')
		# check whether this is a form submission
		if request.method == 'POST':
			# get the form from the request object
			login_form = LoginForm(request.POST)
			# check whether it has basic validity
			if login_form.is_valid():
				# attempt to authenticate the user
				user = authenticate(
									request,
									username=login_form.cleaned_data['email_address'],
									password=login_form.cleaned_data['password']
									)
				# login the user if successful
				if user is not None:
					# log the user in
					login(request, user)
					# set the login flag
					successful_login = True
				else:
					# set an error for the login failure
					messages.error(request, 'Email address or password not recognised.')
		else:
			# this is a first time submission, so create an empty form
			login_form = LoginForm()
	# see if we logged in succssfully
	if successful_login:
		# set a success message
		messages.success(request, 'Successfully logged in. Welcome back ' + str(request.user.first_name) + '!')
		# redirect to the home page
		return redirect('index')
	# otherwsise, set the context and output a form
	context = build_context({'login_form' : login_form})
	# set the output
	return HttpResponse(login_template.render(context, request))

@login_required
def log_user_out(request):
	# log the user out
	logout(request)
	# set a success message
	messages.success(request, 'Successfully logged out. ')
	# redirect to the home page
	return redirect('index')

@login_required
def people(request):
	# set a blank list
	people = []
	# and a blank page_list
	page_list = []
	# and zero search results
	number_of_people = 0
	# and blank search terms
	first_name = ''
	last_name = ''
	role_type = 0
	ABSS_type = 0
	age_status = 0
	trained_role = 'none'
	# set a blank search_error
	search_error = ''
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		personsearchform = PersonSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			personsearchform.is_valid()
			# get the names
			first_name = personsearchform.cleaned_data['first_name']
			last_name = personsearchform.cleaned_data['last_name']
			role_type = personsearchform.cleaned_data['role_type']
			ABSS_type = personsearchform.cleaned_data['ABSS_type']
			age_status = personsearchform.cleaned_data['age_status']
			trained_role = personsearchform.cleaned_data['trained_role']
			# conduct a search
			people = people_search(
													first_name=first_name,
													last_name=last_name,
													role_type=role_type,
													ABSS_type=ABSS_type,
													age_status=age_status,
													trained_role=trained_role
													)
			# figure out how many people we got
			number_of_people = len(people)
			# get the page number
			page = int(request.POST['page'])
			# figure out how many pages we have
			page_list = get_page_list(people, results_per_page)
			# set the previous page
			previous_page = page - 1
			# sort and truncate the list of people
			people = people.order_by('last_name','first_name')[previous_page*results_per_page:page*results_per_page]
	# otherwise set a bank form
	else:
		# create the blank form
		personsearchform = PersonSearchForm()
	# get the template
	people_template = loader.get_template('people/people.html')
	# set the context
	context = build_context({
				'personsearchform' : personsearchform,
				'people' : people,
				'page_list' : page_list,
				'first_name' : first_name,
				'last_name' : last_name,
				'role_type' : role_type,
				'ABSS_type' : ABSS_type,
				'age_status' : age_status,
				'trained_role' : trained_role,
				'search_error' : search_error,
				'number_of_people' : number_of_people
				})
	# return the HttpResponse
	return HttpResponse(people_template.render(context=context, request=request))

@login_required
def people_query(request, id):
	# this function emulates a post from a search form
	# the criterion to be searched on is dependent on the url name
	# create a dictionary of items
	form_values = {
					'role_type' : '0',
					'ABSS_type' : '0',
					'age_status' : '0',
					'trained_role' : 'none'
					}
	# set the value based on the url
	form_values[resolve(request.path_info).url_name] = id
	# copy the request
	copy_POST = request.POST.copy()
	# set search terms for a people search
	copy_POST['action'] = 'search'
	copy_POST['role_type'] = form_values['role_type']
	copy_POST['first_name'] = ''
	copy_POST['last_name'] = ''
	copy_POST['ABSS_type'] = form_values['ABSS_type']
	copy_POST['age_status'] = form_values['age_status']
	copy_POST['trained_role'] = form_values['trained_role']
	copy_POST['page'] = '1'
	# now copy it back
	request.POST = copy_POST
	# and set the method
	request.method = 'POST'
	# now call the people view
	return people(request)

@login_required
def exceptions(request, page=1):
	# blank the lists
	parents = []
	children = []
	# get the path, and figure out what we have been called as
	path = request.get_full_path()
	# set variables based on the type of call
	if 'parents_with_no_children' in path:
		# set the variables, starting with the relevant list of parents
		parents, parents_with_no_children_under_four = get_parents_without_children()
		# set the url
		exceptions_template = loader.get_template('people/parents_without_children.html')
	# otherwise check for parents with no children under four
	elif 'parents_without_children_under_four' in path:
		# set the variables, starting with the relevant list of parents
		parents_with_no_children, parents = get_parents_without_children()
		# set the url
		exceptions_template = loader.get_template('people/parents_without_children_under_four.html')
	# otherwise check for parents with overdue children
	elif 'parents_with_overdue_children' in path:
		# set the variables, starting with the relevant list of parents
		parents = get_parents_with_overdue_children()
		# set the url
		exceptions_template = loader.get_template('people/parents_with_overdue_children.html')
	# otherwise check for children over four
	elif 'children_over_four' in path:
		# set the variables, starting with the relevant list of parents
		children = get_children_over_four().order_by('date_of_birth')
		# set the url
		exceptions_template = loader.get_template('people/children_over_four.html')
	# and a blank page_list
	page_list = []
	# set the results per page
	results_per_page = 25
	# get the page number
	page = int(page)
	# figure out how many pages we have
	page_list = get_page_list(parents, results_per_page)
	# set the previous page
	previous_page = page - 1
	# sort and truncate the list of people
	parents = parents[previous_page*results_per_page:page*results_per_page]
	# set the context
	context = build_context({
				'parents' : parents,
				'children' : children,
				'page_list' : page_list,
				})
	# return the HttpResponse
	return HttpResponse(exceptions_template.render(context=context, request=request))

@login_required
def age_exceptions(request, age_status_id=0):
	# load the template
	age_exceptions_template = loader.get_template('people/age_exceptions.html')
	# get the age status
	age_status = get_age_status(age_status_id)
	# if the age status doesn't exist, crash to a banner
	if not age_status:
		return make_banner(request, 'Age status does not exist.')
	# get today's date
	today = datetime.date.today()
	# get the exceptions
	age_exceptions = age_status.person_set.filter(
							date_of_birth__lt=today.replace(year=today.year-age_status.maximum_age))
	# set the context from the person based on person id
	context = build_context({
				'age_status' : age_status,
				'people' : age_exceptions,
				})
	# return the response
	return HttpResponse(age_exceptions_template.render(context=context, request=request))

@login_required
def addperson(request):
	# create a blank list of matching people
	matching_people = []
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		addpersonform = AddPersonForm(request.POST)
		# check whether the form is valid
		if addpersonform.is_valid():
			# get the names
			first_name = addpersonform.cleaned_data['first_name']
			last_name = addpersonform.cleaned_data['last_name']
			age_status = addpersonform.cleaned_data['age_status']
			# see whether this is a confirmation action
			# get the action from the request
			action = request.POST.get('action','')
			# see if there is an action
			if action == 'CONFIRM':
				# create the person
				person = create_person(
										first_name = first_name,
										last_name = last_name,
										age_status = age_status
										)
				# set a success message
				messages.success(request,
									'Another ' + str(person) + ' created.'
									)
				# go to the profile of the person
				return redirect('/profile/' + str(person.pk))
		# otherwise see whether the person matches an existing person by name
		matching_people = get_people_by_name(first_name,last_name)
		# if there aren't any matching people, also create the person
		if not matching_people:
			# create the person
			person = create_person(
									first_name = first_name,
									last_name = last_name,
									age_status = age_status
									)
			# set a success message
			messages.success(request,
								'Base data for ' + str(person) + ' created.'
								)
			# go to the profile of the person
			return redirect('/profile/' + str(person.pk))
	# otherwise create a fresh form
	else:
		# create the fresh form
		addpersonform = AddPersonForm()
	# get the template
	addperson_template = loader.get_template('people/addperson.html')
	# set the context
	context = build_context({
				'addpersonform' : addpersonform,
				'matching_people' : matching_people
				})
	# return the HttpResponse
	return HttpResponse(addperson_template.render(context=context, request=request))

@login_required
def person(request, person_id=0):
	# load the template
	person_template = loader.get_template('people/person.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the relationships for the person
	relationships_to = get_relationships_to(person)
	# get the 
	# set the context from the person based on person id
	context = build_context({
				'person' : person,
				'relationships_to' : relationships_to,
				'registrations' : Event_Registration.objects.filter(person=person),
				'questions' : get_questions_and_answers(person),
				'role_history' : person.role_history_set.all()
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def profile(request, person_id=0):
	# set the old role to false: this indicates that the role hasn't changed yet
	old_role = False
	# try to get the person
	person = get_person(person_id)
	# if there isn't a person, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# check whether this is a post
	if request.method == 'POST':
		# create a form
		profileform = ProfileForm(request.POST)
		# check whether the entry is valid
		if profileform.is_valid():
			# update the person
			person = update_person(
								request = request,
								person = person,
								first_name = profileform.cleaned_data['first_name'],
								middle_names = profileform.cleaned_data['middle_names'],
								last_name = profileform.cleaned_data['last_name'],
								email_address = profileform.cleaned_data['email_address'],
								home_phone = profileform.cleaned_data['home_phone'],
								mobile_phone = profileform.cleaned_data['mobile_phone'],
								emergency_contact_details = profileform.cleaned_data['emergency_contact_details'],
								date_of_birth = profileform.cleaned_data['date_of_birth'],
								gender = profileform.cleaned_data['gender'],
								pregnant = profileform.cleaned_data['pregnant'],
								due_date = profileform.cleaned_data['due_date'],
								default_role_id = profileform.cleaned_data['role_type'],
								ethnicity_id = profileform.cleaned_data['ethnicity'],
								ABSS_type_id = profileform.cleaned_data['ABSS_type'],
								ABSS_start_date = profileform.cleaned_data['ABSS_start_date'],
								ABSS_end_date = profileform.cleaned_data['ABSS_end_date'],
								age_status_id = profileform.cleaned_data['age_status'],
								notes = profileform.cleaned_data['notes'],
									)
			# clear out the existing trained roles
			person.trained_role_set.all().delete()
			# process the trained role entries by going through the keys
			for field_name in profileform.cleaned_data.keys():
				# check the field
				if 'trained_role_' in field_name:
					# build the trained role
					build_trained_role(
										person=person,
										role_type_id=int(extract_id(field_name)),
										trained_status=profileform.cleaned_data[field_name]
										)
			# send the user back to the main person page
			return redirect('/person/' + str(person.pk))
	else:
		# there is a person, so build a dictionary of initial values we want to set
		profile_dict = {
						'first_name' : person.first_name,
						'middle_names' : person.middle_names,
						'last_name' : person.last_name,
						'email_address' : person.email_address,
						'home_phone' : person.home_phone,
						'mobile_phone' : person.mobile_phone,
						'emergency_contact_details' : person.emergency_contact_details,
						'date_of_birth' : person.date_of_birth,
						'role_type' : person.default_role.pk,
						'ethnicity' : person.ethnicity.pk,
						'gender' : person.gender,
						'pregnant' : person.pregnant,
						'due_date' : person.due_date,
						'ABSS_type' : person.ABSS_type.pk,
						'ABSS_start_date' : person.ABSS_start_date,
						'ABSS_end_date' : person.ABSS_end_date,
						'age_status' : person.age_status.pk,
						'notes' : person.notes
						}
		# add the trained role values to the profile dictionary
		for trained_role in Role_Type.objects.filter(trained=True):
			# set the profile dictionary value
			profile_dict['trained_role_' + str(trained_role.pk)] = get_trained_status(person,trained_role)
		# create the form
		profileform = ProfileForm(profile_dict)
	# load the template
	profile_template = loader.get_template('people/profile.html')
	# set the context
	context = build_context({
				'profileform' : profileform,
				'person' : person
				})
	# return the response
	return HttpResponse(profile_template.render(context, request))

@login_required
def add_relationship(request,person_id=0):
	# this is one of the most complex views on the site, which allows the user to search for people and to 
	# add relationships to both existing and new people
	# initalise the forms which we might not need
	addrelationshipform = ''
	addrelationshiptoexistingpersonform = ''
	editexistingrelationshipsform = ''
	# load the template
	person_template = loader.get_template('people/add_relationship.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get existing relationships
	relationships_to = get_relationships_to(person)
	# get relationship types
	relationship_types = get_relationship_types()
	# get role types
	role_types = get_role_types()
	# set the search results
	search_results = []
	# set a blank search_error
	search_error = ''
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		personsearchform = PersonNameSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			personsearchform.is_valid()
			# get the names
			first_name = personsearchform.cleaned_data['first_name']
			last_name = personsearchform.cleaned_data['last_name']
			# if neither name is blank, do the search
			if first_name or last_name:
				# conduct a search
				people = people_search(first_name,last_name)
				# remove the people who already have a relationship
				search_results = remove_existing_relationships(person, people)
				# if there are search results, create a form to create relationships from the search results
				if search_results:
					# create the form
					addrelationshiptoexistingpersonform = AddRelationshipToExistingPersonForm(
															people=search_results
															)
					# go through the search results and add a field name to the object
					for result in search_results:
						# add the field
						result.field_name = 'relationship_type_' + str(result.pk)
				# create a form to add the relationship
				addrelationshipform = AddRelationshipForm(
															first_name = personsearchform.cleaned_data['first_name'],
															last_name = personsearchform.cleaned_data['last_name'],
															)
			# otherwise we have a blank form
			else:
				# set the message
				search_error = 'First name or last name must be entered.'
		# check whether we have been asked to edit relationships
		# note that we get this action for editing existing relationships and creating new relationships
		elif request.POST['action'] == 'editrelationships':
			# go through the post
			for field_name, field_value in request.POST.items():
				# check whether this is a relevant field
				if field_name.startswith('relationship_type'):
					# try to find a person using the id at the end of the field name
					person_to = get_person(int(extract_id(field_name)))
					# if we got a person, edit the relationship
					if person_to:
						# edit the relationship
						edit_relationship(request, person, person_to, int(field_value))
		# check whether we have been asked to add a relationship to a new person
		elif request.POST['action'] == 'addrelationshiptonewperson':
			# create the form
			addrelationshipform = AddRelationshipForm(
														request.POST,
														first_name = request.POST['first_name'],
														last_name = request.POST['last_name']
														)
			# check whether the form is valid
			if addrelationshipform.is_valid():
				# we now need to create the person
				person_to = create_person(
											first_name = addrelationshipform.cleaned_data['first_name'],
											middle_names = addrelationshipform.cleaned_data['middle_names'],
											last_name = addrelationshipform.cleaned_data['last_name'],
											age_status = addrelationshipform.cleaned_data['age_status']
											)
				# set a message to say that we have create a new person
				messages.success(request, str(person_to) + ' created.')
				# now create the relationship
				edit_relationship(request,person, person_to, addrelationshipform.cleaned_data['relationship_type'])
				# redirect to the profile form for the new person
				return redirect('/profile/' + str(person_to.pk))
	# otherwise we didn't get a post
	else:
		# create a blank form
		personsearchform = PersonNameSearchForm()
	# update the existing relationships: there may be new ones
	relationships_to = get_relationships_to(person)
	# if there are existing relationships, create an edit form
	if relationships_to:
		# build the form
		editexistingrelationshipsform = EditExistingRelationshipsForm(
																		relationships=relationships_to
																		)
		# and go through the relationships, adding the name of the select field and the hidden field
		for relationship_to in relationships_to:
			# set the values
			relationship_to.select_name = 'relationship_type_' + str(relationship_to.pk)
			relationship_to.hidden_name = 'original_relationship_type_' + str(relationship_to.pk)
	# set the context from the person based on person id
	context = build_context({
				'personsearchform' : personsearchform,
				'addrelationshipform' : addrelationshipform,
				'addrelationshiptoexistingpersonform' : addrelationshiptoexistingpersonform,
				'editexistingrelationshipsform' : editexistingrelationshipsform,
				'search_results' : search_results,
				'search_error' : search_error,
				'person' : person,
				'relationships_to' : relationships_to
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def address(request,person_id=0):
	# this view is used to set the address for a person, by searching on post code or street name
	# load the template
	person_template = loader.get_template('people/address.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# set the search results
	search_results = []
	# and a blank page_list
	page_list = []
	# and zero search results
	search_number = 0
	# and blank search terms
	house_name_or_number = ''
	street = ''
	post_code = ''
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		addresssearchform = AddressSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			if addresssearchform.is_valid():
				# get the house name or number, street name and post code
				house_name_or_number = addresssearchform.cleaned_data['house_name_or_number']
				street = addresssearchform.cleaned_data['street']
				post_code = addresssearchform.cleaned_data['post_code']
				# do the search
				search_results = get_streets_by_name_and_post_code(
																	name=street,
																	post_code=post_code
																	)
				# figure out how many results we got
				search_number = len(search_results)
				# get the page number
				page = int(request.POST['page'])
				# figure out how many pages we have
				page_list = get_page_list(search_results, results_per_page)
				# set the previous page
				previous_page = page - 1
				# sort and truncate the list of results
				search_results = search_results.order_by('name')[previous_page*results_per_page:page*results_per_page]
		# see whether we got an update
		elif request.POST['action'] == 'update':
			# create an update form
			updateaddressform = UpdateAddressForm(request.POST)
			# validate the form
			if updateaddressform.is_valid():
				# attempt to update the address
				if update_address(
									request,
									person=person,
									street_id=int(updateaddressform.cleaned_data['street_id']),
									house_name_or_number=updateaddressform.cleaned_data['house_name_or_number']
									):
					# go to the profile of the person
					return redirect('/person/' + str(person.pk))
		# or a remove
		elif request.POST['action'] == 'remove':
			# remove the address
			remove_address(
							request,
							person=person,
							)
			# go to the profile of the person
			return redirect('/person/' + str(person.pk))
	# otherwise we didn't get a post
	else:
		# create a blank form
		addresssearchform = AddressSearchForm()
	# set the context from the person based on person id
	context = build_context({
				'addresssearchform' : addresssearchform,
				'search_results' : search_results,
				'search_number' : search_number,
				'person' : person,
				'page_list' : page_list,
				'house_name_or_number' : house_name_or_number,
				'street' : street,
				'post_code' : post_code
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def address_to_relationships(request,person_id=0):
	# this view is used to set the address for a person, by searching on post code or street name
	# load the template
	person_template = loader.get_template('people/address_to_relationships.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# set a blank set of application keys
	application_keys = ''
	# and a blank delimiter
	application_key_delimiter = ''
	# and a blank form
	addresstorelationshipsform = ''
	# check whether this is a post
	if request.method == 'POST':
		# check what type of submission we got
		if request.POST['action'] == 'apply_address':
			# get the list of search keys from the hidden field
			application_keys = request.POST['application_keys'].split(',')
			# go through the application
			for application_key in application_keys:
				# get the indicators of whether the address should be applied
				applied = check_checkbox(request.POST, 'apply_' + application_key)
				# if the address is to be applied, we need to update the address
				if applied:
					# apply the address
					update_address(
									request,
									person=Person.objects.get(id=int(application_key)),
									street_id=person.street.pk,
									house_name_or_number=person.house_name_or_number
									)
	# create the lists
	people_at_same_address = []
	people_not_at_same_address = []
	# go through the peple
	for relationship_to in get_relationships_to(person):
		# check the address
		if relationship_to.house_name_or_number == person.house_name_or_number and \
			relationship_to.street == person.street:
			# add the person to the same address list
			people_at_same_address.append(relationship_to)
		# otherwise hit the other list
		else:
			# add the person to the not same address list
			people_not_at_same_address.append(relationship_to)
	# if there are people not at the same address, create the form
	if people_not_at_same_address:
		# clear the application keys
		application_keys = ''
		# create the form
		addresstorelationshipsform = AddressToRelationshipsForm(people = people_not_at_same_address)
		# add field name to each person
		for this_person in people_not_at_same_address:
			# add the field name
			this_person.apply_field_name = 'apply_' + str(this_person.pk)
			# add the key of the  person to the string of keys
			application_keys += application_key_delimiter + str(this_person.pk)
			# and set the delimiter
			application_key_delimiter = ','
	# set the context from the person based on person id
	context = build_context({
				'person' : person,
				'people_at_same_address' : people_at_same_address,
				'people_not_at_same_address' : people_not_at_same_address,
				'application_keys' : application_keys,
				'addresstorelationshipsform' : addresstorelationshipsform
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def addevent(request):
	# get the event types
	event_types = get_event_types()
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		addeventform = EventForm(request.POST)
		# check whether the form is valid
		if addeventform.is_valid():
			# create the event
			event = build_event(
								request,
								name = addeventform.cleaned_data['name'],
								description = addeventform.cleaned_data['description'],
								location = addeventform.cleaned_data['location'],
								ward_id = addeventform.cleaned_data['ward'],
								date = addeventform.cleaned_data['date'],
								start_time = addeventform.cleaned_data['start_time'],
								end_time = addeventform.cleaned_data['end_time'],
								event_type_id = addeventform.cleaned_data['event_type'],
								areas = build_event_area_dict(addeventform.cleaned_data)
								)
			# if we were successful, redirect to the registration page
			if event:
				# create a fresh form
				return redirect('/event_registration/' + str(event.pk))
	# otherwise create a fresh form
	else:
		# create the fresh form
		addeventform = EventForm()
	# get the template
	addevent_template = loader.get_template('people/addevent.html')
	# set the context
	context = build_context({
				'addeventform' : addeventform,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y')
				})
	# return the HttpResponse
	return HttpResponse(addevent_template.render(context=context, request=request))

@login_required
def event(request, event_id=0):
	# load the template
	event_template = loader.get_template('people/event.html')
	# get the event
	event = get_event(event_id)
	# if the event doesn't exist, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# get the registrations for the event
	registrations = get_event_registrations(event)
	# set the context
	context = build_context({
				'event' : event,
				'registrations' : registrations
				})
	# return the response
	return HttpResponse(event_template.render(context=context, request=request))

@login_required
def event_group(request, event_group='0'):
	# set the variables to zero
	event_type = 0
	event_category = 0
	ward = 0
	# get the calling url
	path = request.get_full_path()
	# set the grouping based on the path
	if 'type' in path:
		# we have an event type
		event_type = event_group
	elif 'category' in path:
		# we have an event category
		event_category = event_group
	elif 'ward' in path:
		# we have a ward
		ward = event_group
	# get the dashboard dates
	dashboard_dates = get_dashboard_dates()
	# set blank dates
	date_from = ''
	date_to = ''
	# set the dates, dependent on the url
	if 'this_month' in path:
		# set the date_from to the first of the month
		date_from = dashboard_dates['first_day_of_this_month'].strftime('%d/%m/%Y')
	# otherwise check for last month
	elif 'last_month' in path:
		# set the date from to the first of last month
		date_from = dashboard_dates['first_day_of_last_month'].strftime('%d/%m/%Y')
		# and the date to to the last of last month
		date_to = dashboard_dates['last_day_of_last_month'].strftime('%d/%m/%Y')
	# otherwise check for this year
	elif 'this_year' in path:
		# set the date from to the beginning of the year
		date_from = dashboard_dates['first_day_of_this_year'].strftime('%d/%m/%Y')
	# copy the request
	copy_POST = request.POST.copy()
	# set search terms for an event search
	copy_POST['action'] = 'search'
	copy_POST['event_type'] = event_type
	copy_POST['event_category'] = event_category
	copy_POST['ward'] = ward
	copy_POST['name'] = ''
	copy_POST['date_from'] = date_from
	copy_POST['date_to'] = date_to
	copy_POST['page'] = '1'
	# now copy it back
	request.POST = copy_POST
	# and set the method
	request.method = 'POST'
	# now call the people view
	return events(request)

@login_required
def events(request):
	# set a blank list
	events = []
	# and a blank page_list
	page_list = []
	# and blank search terms
	name = ''
	event_type = 0
	event_category = 0
	date_from = 0
	date_to = 0
	ward = 0
	# set a blank search_error
	search_error = ''
	# and a zero number of results
	number_of_events = 0
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		eventsearchform = EventSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			if eventsearchform.is_valid():
				# get the values
				name = eventsearchform.cleaned_data['name']
				date_from = eventsearchform.cleaned_data['date_from']
				date_to = eventsearchform.cleaned_data['date_to']
				event_type = eventsearchform.cleaned_data['event_type']
				event_category = eventsearchform.cleaned_data['event_category']
				ward = eventsearchform.cleaned_data['ward']
				# conduct a search
				events = search_events(
										name=name,
										date_from=date_from,
										date_to=date_to,
										event_type=int(event_type),
										event_category=int(event_category),
										ward=int(ward)
										)
				# set the number of results
				number_of_events = len(events)
				# get the page number
				page = int(request.POST['page'])
				# figure out how many pages we have
				page_list = get_page_list(events, results_per_page)
				# set the previous page
				previous_page = page - 1
				# sort and truncate the list of events
				events = events.order_by('-date')[previous_page*results_per_page:page*results_per_page]
				# add the counts to the events
				events = add_counts_to_events(events)
			# otherwise we have incorrect dates
			else:
				# set a search error
				search_error = 'Dates must be entered in DD/MM/YYYY format.'
	# otherwise set a bank form
	else:
		# create the blank form
		eventsearchform = EventSearchForm()
	# get the template
	events_template = loader.get_template('people/events.html')
	# set the context
	context = build_context({
				'events' : events,
				'eventsearchform' : eventsearchform,
				'name' : name,
				'event_type' : event_type,
				'event_category' : event_category,
				'ward' : ward,
				'date_from' : date_from,
				'date_to' : date_to,
				'page_list' : page_list,
				'search_error' : search_error,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y'),
				'number_of_events' : number_of_events
				})
	# return the HttpResponse
	return HttpResponse(events_template.render(context=context, request=request))

@login_required
def edit_event(request, event_id=0):
	# try to get the event
	event = get_event(event_id)
	# if there isn't an event, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# check whether this is a post
	if request.method == 'POST':
		# create a form
		editeventform = EventForm(
									request.POST,
									)
		# check whether the entry is valid
		if editeventform.is_valid():
			# update the event object
			event.name = editeventform.cleaned_data['name']
			event.description = editeventform.cleaned_data['description']
			event.location = editeventform.cleaned_data['location']
			event.date = editeventform.cleaned_data['date']
			event.start_time = editeventform.cleaned_data['start_time']
			event.end_time = editeventform.cleaned_data['end_time']
			# attempt to get the event type
			event_type = get_event_type(editeventform.cleaned_data['event_type'])
			# set the value for the event
			if event_type:
				# set the value
				event.event_type = event_type
			# otherwise crash out to a banner
			else:
				# set the banner
				return make_banner(request, 'Event type does not exist.')
			# attempt to get the ward
			ward_id = editeventform.cleaned_data['ward']
			# check whether we have a ward id
			if ward_id != '0':
				# get the ward
				ward = get_ward(ward_id)
				# set the value for the event
				if ward:
					# set the value
					event.ward = ward
				# otherwise crash out to a banner
				else:
					# set the banner
					return make_banner(request, 'Ward does not exist.')
			# otherwise, set null
			else:
				# set the ward to none
				event.ward = None
			# save the record
			event.save()
			# set a success message
			messages.success(request, str(event) + ' updated.')
			# get the dictionary
			area_dict = build_event_area_dict(editeventform.cleaned_data)
			# go through the areas and update the area relationships
			for area_id in area_dict.keys():
				# check whether the box is unchecked but the record exists
				if not area_dict[area_id] and event.areas.filter(pk=area_id).exists():
					# remove the record
					event.areas.remove(Area.objects.get(pk=area_id))
				# if the box is checked or this is the area for the ward, add the record
				if area_dict[area_id] or (event.ward and area_id == event.ward.area.pk):
					# add the record
					event.areas.add(Area.objects.get(pk=area_id))
			# send the user back to the main event page
			return redirect('/event/' + str(event.pk))
	else:
		# check whether we have a ward
		if not event.ward:
			# set the id to the 'unknown' ward
			ward_id = 0
		# otherwise, get the ward id
		else:
			# get the ward id
			ward_id = event.ward.pk
		# there is an event, so build a dictionary of initial values we want to set
		event_dict = {
						'name' : event.name,
						'description' : event.description,
						'location' : event.location,
						'ward' : ward_id,
						'date' : event.date,
						'start_time' : event.start_time,
						'end_time' : event.end_time,
						'event_type' : event.event_type.pk
						}
		# go through the areas and add the values
		for area in Area.objects.all():
			# set the initial value
			available_in_area = False
			# check whether the event is available in the area
			if area in event.areas.all():
				# set the value to True
				available_in_area = True
			# now update the dict
			event_dict['area_' + str(area.pk)] = available_in_area
		# create the form
		editeventform = EventForm(
									event_dict,
									)
	# load the template
	edit_event_template = loader.get_template('people/edit_event.html')
	# set the context
	context = build_context({
				'editeventform' : editeventform,
				'event' : event
				})
	# return the response
	return HttpResponse(edit_event_template.render(context, request))

@login_required
def event_registration(request,event_id=0):
	# this is one of the most complex views on the site, which allows the user to search for people and to 
	# edit the registration and participation in an event
	# initalise the forms which we might not need
	addregistrationform = ''
	editregistrationform = ''
	# load the template
	event_registration_template = loader.get_template('people/event_registration.html')
	# get the event
	event = get_event(event_id)
	# if the event doesn't exist, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# get existing registrations
	registrations = get_event_registrations(event)
	# get the role types
	role_types = get_role_types()
	# set the search results
	search_results = []
	# and a blank string of search result keys
	search_keys = ''
	# and a blank delimiter
	search_key_delimiter = ''
	# set a blank search_error
	search_error = ''
	# set a blank set of registration keys
	registration_keys = ''
	# and a blank delimiter
	registration_key_delimiter = ''
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		personsearchform = PersonNameSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			personsearchform.is_valid()
			# get the names
			first_name = personsearchform.cleaned_data['first_name']
			last_name = personsearchform.cleaned_data['last_name']
			# if neither name is blank, do the search
			if first_name or last_name:
				# conduct a search
				people = people_search(first_name,last_name)
				# remove the people who already have a registration
				search_results = remove_existing_registrations(event, people)
				# if there are search results, create a form to create relationships from the search results
				if search_results:
					# create the form
					addregistrationform = AddRegistrationForm(people=search_results)
				# add field names to each result, so that we know when to display them
				for result in search_results:
					# add the three field names
					result.role_type_field_name = 'role_type_' + str(result.pk)
					result.registered_field_name = 'registered_' + str(result.pk)
					result.participated_field_name = 'participated_' + str(result.pk)
					# add the key of the search result to the string of keys
					search_keys += search_key_delimiter + str(result.pk)
					# and set the delimiter
					search_key_delimiter = ','
			# otherwise we have a blank form
			else:
				# set the message
				search_error = 'First name or last name must be entered.'
		# check whether we have been asked to add registrations
		elif request.POST['action'] == 'addregistration':
			# get the list of search keys from the hidden field
			search_keys = request.POST['search_keys'].split(',')
			# go through the search keys
			for search_key in search_keys:
				# get the indicators of whether the person registered or participated, as well as the role type
				registered = check_checkbox(request.POST, 'registered_' + search_key)
				participated = check_checkbox(request.POST, 'participated_' + search_key)
				role_type_id = request.POST.get('role_type_' + search_key, False)
				# if the person participated or registered, we need to build a registration
				if registered or participated:
					# build the registration
					registration = build_registration(
														request = request,
														event = event,
														person_id = int(search_key),
														registered = registered,
														participated = participated,
														role_type_id = int(role_type_id)
														)
		# check whether we have been asked to edit registations
		elif request.POST['action'] == 'editregistration' :
			# get the list of registration keys from the hidden field
			registration_keys = request.POST['registration_keys'].split(',')
			# go through the keys
			for registration_key in registration_keys:
				# get the indicators and role type
					# get the indicators of whether the person registered or participated, as well as the role type
					registered = check_checkbox(request.POST, 'registered_' + registration_key)
					participated = check_checkbox(request.POST, 'participated_' + registration_key)
					role_type_id = request.POST.get('role_type_' + registration_key, False)
					# if the person participated or registered, we need to build a registration
					if registered or participated:
						# build the registration
						registration = build_registration(
															request = request,
															event = event,
															person_id = int(registration_key),
															registered = registered,
															participated = participated,
															role_type_id = int(role_type_id)
															)
					# otherwise we need to remove the registration
					else:
						# remove the registration
						remove_registration(
											request = request,
											event = event,
											person_id = int(registration_key)
										)
	# otherwise we didn't get a post
	else:
		# create a blank form
		personsearchform = PersonNameSearchForm()
	# update the existing registrations: there may be new ones
	registrations = get_event_registrations(event)
	# if there are registrations, create the form
	if registrations:
		# clear the registration keys
		registration_keys = ''
		# create the form
		editregistrationform = EditRegistrationForm(registrations = registrations)
		# add field names to each registration, so that we know when to display them
		for registration in registrations:
			# add the three field names
			registration.role_type_field_name = 'role_type_' + str(registration.person.pk)
			registration.registered_field_name = 'registered_' + str(registration.person.pk)
			registration.participated_field_name = 'participated_' + str(registration.person.pk)
			# add the key of the registered person to the string of keys
			registration_keys += registration_key_delimiter + str(registration.person.pk)
			# and set the delimiter
			registration_key_delimiter = ','
	# set the context from the person based on person id
	context = build_context({
				'personsearchform' : personsearchform,
				'addregistrationform' : addregistrationform,
				'editregistrationform' : editregistrationform,
				'search_results' : search_results,
				'search_keys' : search_keys,
				'search_error' : search_error,
				'search_number' : len(search_results),
				'event' : event,
				'registrations' : registrations,
				'registration_keys' : registration_keys
				})
	# return the response
	return HttpResponse(event_registration_template.render(context=context, request=request))

@login_required
def answer_questions(request,person_id=0):
	# this view enables people to answer a dynamic set of questions from the database
	# load the template
	answer_questions_template = loader.get_template('people/answer_questions.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the questions, with the answers included as an attribute
	questions = get_questions_and_answers(person)
	# build the form
	if request.method == 'POST':
		# build the form
		answerquestionsform = AnswerQuestionsForm(request.POST,questions=questions)
		# go through the fields
		for field in answerquestionsform.fields:
			# get the question id from the field name
			question_id = int(extract_id(field))
			# ignore spacers
			if 'spacer' not in field:
				# check whether it is a note or not
				if 'notes' not in field:
					# get the option id from the value of the field
					option_id = int(answerquestionsform.data[field])
					# build the answer
					build_answer(request,person,question_id,option_id)
				# process the note
				else:
					build_answer_note(request,person,question_id,answerquestionsform.data[field])
		# send the user back to the main person page
		return redirect('/person/' + str(person.pk))
	# otherwise create an empty form
	else:
		# create the empty form
		answerquestionsform = AnswerQuestionsForm(questions=questions)
	# set the context from the person based on person id
	context = build_context({
				'person' : person,
				'answerquestionsform' : answerquestionsform
				})
	# return the response
	return HttpResponse(answer_questions_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def uploaddata(request):
	# set results to empty
	results = []
	# define the records that need simple file handlers
	simple_file_handlers = {
							'Areas' : {'file_class' : Area, 'field_name' : 'area_name'},
							'Age Statuses' : {'file_class' : Age_Status, 'field_name' : 'status'},
							'Ethnicities' : {'file_class' : Ethnicity, 'field_name' : 'description'},
							'ABSS Types' : {'file_class' : ABSS_Type, 'field_name' : 'name'},
							}
	# define the records that need more complex file handlers
	file_handlers = {
						'Event Categories' : Event_Categories_File_Handler,
						'Event Types' : Event_Types_File_Handler,
						'Wards' : Wards_File_Handler,
						'Post Codes' : Post_Codes_File_Handler,
						'Streets' : Streets_File_Handler,
						'Role Types' : Role_Types_File_Handler,
						'Relationship Types' : Relationship_Types_File_Handler,
						'People' : People_File_Handler,
						'Relationships' : Relationships_File_Handler
					}
	# define the functions for each file type
	load_functions = {
						# 'People' : load_people,
						'Events' : load_events,
						'Relationships' : load_relationships,
						'Registrations' : load_registrations
						}
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		uploaddataform = UploadDataForm(request.POST, request.FILES)
		# check whether the form is valid
		if uploaddataform.is_valid():
			# decode the file
			file = TextIOWrapper(request.FILES['file'], encoding=request.encoding, errors='ignore')
			# get the file type
			file_type = uploaddataform.cleaned_data['file_type']
			# check to see whether we have a simple loader
			if file_type in simple_file_handlers.keys():
				# get the parameters
				file_handler_kwargs = simple_file_handlers[file_type]
				# load using a simple file handler
				file_handler = File_Handler(**file_handler_kwargs)
				# handle the uploaded file
				file_handler.handle_uploaded_file(file)
				# get the results
				results = file_handler.results
			# otherwise deal with an old fashioned load functions
			elif file_type not in file_handlers.keys():
				# read it as a csv file
				records = csv.DictReader(file)
				# get the load function
				load_function = load_functions[file_type]
				# call the load functions
				results = load_function(records)
			else:
				# create a file handler
				file_handler = file_handlers[file_type]()
				# handle the uploaded file
				file_handler.handle_uploaded_file(file)
				# get the results
				results = file_handler.results
	# otherwise create a fresh form
	else:
		# create the fresh form
		uploaddataform = UploadDataForm()
	# get the template
	upload_data_template = loader.get_template('people/upload_data.html')
	# set the context
	context = build_context({
				'uploaddataform' : uploaddataform,
				'results' : results
				})
	# return the HttpResponse
	return HttpResponse(upload_data_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def downloaddata(request):
	# set results to empty
	results = []
	# define the functions for each file type
	download_functions = {
							'People' : people_download,
							'Events' : events_download,
							'Relationships' : relationships_download,
							'Registrations' : registrations_download
							}
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		downloaddataform = DownloadDataForm(request.POST)
		# check whether the form is valid
		if downloaddataform.is_valid():
			# get the file type
			file_type = downloaddataform.cleaned_data['file_type']
			# get the function
			download_function = download_functions[file_type]
			# get the fields and the records from the download function
			fields, records = download_function()
			# create the response
			response = HttpResponse(content_type='text/csv')
			# set the content details
			response['Content-Disposition'] = 'attachment; filename="' + file_type + '.csv"'
			# now create the writer
			writer = csv.writer(response)
			# write the keys
			writer.writerow(fields)
			# and go through the records
			for record in records:
				# write the record
				writer.writerow(record)
			# return the response
			return response
	# otherwise create a fresh form
	else:
		# create the fresh form
		downloaddataform = DownloadDataForm()
	# get the template
	download_data_template = loader.get_template('people/download_data.html')
	# set the context
	context = build_context({
				'downloaddataform' : downloaddataform,
				'results' : results
				})
	# return the HttpResponse
	return HttpResponse(download_data_template.render(context=context, request=request))

# DATA LOAD FUNCTIONS
# A set of functions which read csv files and use them to load data

def file_fields_valid(file_keys,fields):
	# set results to a blank list
	results = []
	# sort them
	file_keys.sort()
	fields.sort()
	# now check that they match
	if file_keys != fields:
		# set the message to a failure message
		results.append('File cannot be loaded as it does not contain the right fields.')
		results.append('Expected ' + str(fields) + ' but got ' + str(file_keys) + '.')
	# return the result
	return results

def check_mandatory_fields(record,label,fields):
	# set the error list
	errors = []
	# go through the fields
	for field in fields:
		# check the field
		if not record[field]:
			# set the error
			errors.append(label + ' not created: mandatory field ' + field + ' not provided.')
	# return the errors
	return errors

def load_relationships(records):
	# check the file format
	results = file_fields_valid(
									records.fieldnames.copy(),
									[
										'from_first_name',
										'from_last_name',
										'from_age_status',
										'to_first_name',
										'to_last_name',
										'to_age_status',
										'relationship_type',
									]
								)
	# check whether we got any results: if we did, something went wrong
	if not results:
		# go through the csv file and process it
		for relationship in records:
			# validate the record
			errors = validate_relationship_record(relationship)
			# check whether we got any errors
			if not errors:
				# get the records, starting with the person from
				person_from = Person.objects.get(
													first_name = relationship['from_first_name'],
													last_name = relationship['from_last_name'],
													age_status__status = relationship['from_age_status']
												)
				# and the person to
				person_to = Person.objects.get(
													first_name = relationship['to_first_name'],
													last_name = relationship['to_last_name'],
													age_status__status = relationship['to_age_status']
												)
				# and the relationship type
				relationship_type = Relationship_Type.objects.get(relationship_type = relationship['relationship_type'])
				# set a label
				relationship_label = str(person_from) + ' is ' + str(relationship_type) + ' of ' + str(person_to)
				# build the relationship using the edit relationship function
				edit_relationship(
									request = '',
									person_from = person_from,
									person_to = person_to,
									relationship_type_id = relationship_type.pk,
									show_messages = False
									)
				# set a message
				results.append(relationship_label + ' created.')
			# otherwise append the errors
			else:
				# add the error list to the results list
				results += errors
	# return the results
	return results

def validate_relationship_record(relationship):
	# check whether a relationship record is valid
	# set the error list
	errors = []
	# set a label
	relationship_label = str(relationship['from_first_name']) + ' ' + str(relationship['from_last_name']) \
							+ ' is ' + str(relationship['relationship_type']) + ' of ' \
							+ str(relationship['to_first_name']) + ' ' + str(relationship['to_last_name'])
	# check for mandatory fields
	errors += check_mandatory_fields(
										record=relationship,
										label=relationship_label,
										fields=[
												'from_first_name',
												'from_last_name',
												'from_age_status',
												'to_first_name',
												'to_last_name',
												'to_age_status',
												'relationship_type'
												]
									)
	# only do the rest of the check if we have the right fields
	if not errors:
		# check whether the from person exists
		error = check_person_by_name_and_age_status(
														first_name = relationship['from_first_name'],
														last_name = relationship['from_last_name'],
														age_status_status = relationship['from_age_status']
													)
		# if there was an error, add it
		if error:
			# append the error message
			errors.append(relationship_label + ' not created: from' + error)
		# check whether the to person exists
		error = check_person_by_name_and_age_status(
														first_name = relationship['to_first_name'],
														last_name = relationship['to_last_name'],
														age_status_status = relationship['to_age_status']
													)
		# if there was an error, add it
		if error:
			# append the error message
			errors.append(relationship_label + ' not created: to' + error)
		# check whether the relationship type exists
		try:
			# get the relationship type
			relationship_type = Relationship_Type.objects.get(relationship_type = relationship['relationship_type'])
		# deal with the exception
		except (Relationship_Type.DoesNotExist):
			# set the error
			errors.append(
							relationship_label + ' not created: relationship type ' + 
							relationship['relationship_type'] + ' does not exist.'
						)
	# return the errors
	return errors

def load_registrations(records):
	# check the file format
	results = file_fields_valid(
									records.fieldnames.copy(),
									[
										'first_name',
										'last_name',
										'age_status',
										'event_name',
										'event_date',
										'registered',
										'participated',
										'role_type'
									]
								)
	# check whether we got any results: if we did, something went wrong
	if not results:
		# go through the csv file and process it
		for registration in records:
			# validate the record
			errors = validate_registration_record(registration)
			# check whether we got any errors
			if not errors:
				# get the records, starting with the person from
				person = Person.objects.get(
											first_name = registration['first_name'],
											last_name = registration['last_name'],
											age_status__status = registration['age_status']
											)
				# and the event
				event = Event.objects.get(
											name = registration['event_name'],
											date = datetime.datetime.strptime(registration['event_date'],'%d/%m/%Y')
											)
				# and the role type
				role_type = Role_Type.objects.get(role_type_name = registration['role_type'])
				# build the registration using the function
				registration = build_registration(
													request = '',
													event = event,
													person_id = person.pk,
													registered = (registration['registered'] == 'True'),
													participated = (registration['participated'] == 'True'),
													role_type_id = role_type.pk,
													show_messages = False
													)
				# set a message
				results.append(str(registration) + ' created.')
			# otherwise append the errors
			else:
				# add the error list to the results list
				results += errors
	# return the results
	return results

def validate_registration_record(registration):
	# check whether a registration record is valid
	# set the error list
	errors = []
	# and some dummy values
	role_type = False
	age_status = False
	# set a label
	registration_label = str(registration['first_name']) + ' ' + str(registration['last_name']) \
							+ ' (' + str(registration['age_status']) + ')' \
							+ ' at ' + str(registration['event_name'])
	# check for mandatory fields
	errors += check_mandatory_fields(
										record=registration,
										label=registration_label,
										fields=[
												'first_name',
												'last_name',
												'age_status',
												'event_name',
												'event_date',
												'role_type',
												]
									)
	# only do the rest of the check if we have the right fields
	if not errors:
		# check whether the from person exists
		error = check_person_by_name_and_age_status(
														first_name = registration['first_name'],
														last_name = registration['last_name'],
														age_status_status = registration['age_status']
													)
		# if there was an error, add it
		if error:
			# append the error message
			errors.append(registration_label + ' not created: person' + error)
		# check whether the role type exists
		try:
			# get the role type
			role_type = Role_Type.objects.get(role_type_name = registration['role_type'])
		# deal with the exception
		except (Role_Type.DoesNotExist):
			# set the error
			errors.append(
							registration_label + ' not created: role type ' + 
							registration['role_type'] + ' does not exist.'
						)
		# check whether the age status exists
		try:
			# get the age status
			age_status = Age_Status.objects.get(status = registration['age_status'])
		# deal with the exception
		except (Age_Status.DoesNotExist):
			# set the error
			errors.append(
							registration_label + ' not created: age status ' + 
							registration['age_status'] + ' does not exist.'
						)
		# check whether the role type is valid for the age status
		if role_type and age_status and role_type not in age_status.role_types.all():
			# set the error
			errors.append(
							registration_label + ' not created: ' + str(role_type) + 
							' is not valid for ' + str(age_status) + '.'
						)
		# get the event date
		event_date = registration['event_date']
		# check whether the date is valid
		if not datetime_valid(event_date,'%d/%m/%Y'):
			# set the error
			errors.append(registration_label + ' not created: event date ' + str(event_date) + ' is not valid.')
		# otherwise do the rest of the checks
		else:
			# set the date
			event_date = convert_optional_ddmmyy(registration['event_date'])
			# try to get the event record
			try:
				# get the event record
				event = Event.objects.get(name = registration['event_name'], date = event_date)
			# deal with missing event
			except (Event.DoesNotExist):
				# set the error
				errors.append(registration_label + ' not created: event does not exist.')
			# deal with more than one match
			except (Event.MultipleObjectsReturned):
				# set the error
				errors.append(registration_label + ' not created: multiple matching events exist.')
		# check that one of registered or participated is set
		if (not registration['registered'] == 'True') and (not registration['participated'] == 'True'):
			# set the error
			errors.append(registration_label + ' not created: neither registered nor participated is True.')
	# return the errors
	return errors

def load_events(records):
	# check the file format
	results = file_fields_valid(
									records.fieldnames.copy(),
									[
										'name',
										'description',
										'event_type',
										'date',
										'start_time',
										'end_time',
										'location',
										'ward',
										'areas',
									]
								)
	# check whether we got any results: if we did, something went wrong
	if not results:
		# go through the csv file and process it
		for event in records:
			# set a label
			event_label = event['name']
			# validate the record
			errors = validate_event_record(event)
			# check whether we got any errors
			if not errors:
				# get the ward
				ward = Ward.objects.get(ward_name = event['ward'])
				# create an event
				new_event = Event.objects.create(
								name = event['name'],
								description = event['description'],
								event_type = Event_Type.objects.get(name = event['event_type']),
								date = convert_optional_ddmmyy(event['date']),
								start_time = datetime.datetime.strptime(event['start_time'],'%H:%M'),
								end_time = datetime.datetime.strptime(event['end_time'],'%H:%M'),
								location = event['location'],
								ward = ward,
									)
				# set the message to show that the creation was successful
				results.append(event_label + ' created.')
				# get the areas
				areas = event['areas'].split(',')
				# now go through the areas
				for area_name in areas:
					# get the area
					area = Area.objects.get(area_name = area_name)
					# create the area
					new_event.areas.add(area)
					# and add a message
					results.append(event_label + ': area ' + area_name + ' created.')
				# add the area which the ward is in, if it hasn't been created already
				if ward.area.area_name not in areas:
					# add the area
					new_event.areas.add(ward.area)
					# and add a message
					results.append(event_label + ': area ' + ward.area.area_name + ' created.')
			# otherwise append the errors
			else:
				# add the error list to the results list
				results += errors
	# return the results
	return results

def validate_event_record(event):
	# check whether an event record is valid
	# set the error list
	errors = []
	# set a label
	event_label = event['name']
	# check for mandatory fields
	errors += check_mandatory_fields(
										record=event,
										label=event_label,
										fields=['name','description','date','start_time','end_time']
									)
	# check the date
	if not datetime_valid(event['date'],'%d/%m/%Y'):
		# set the messages
		errors.append(event_label + ' not created: date is not in DD/MM/YYYY format.')
	# otherwise convert the date
	else:
		# set the date
		date = convert_optional_ddmmyy(event['date'])
		# now attempt to get a matching event
		if Event.objects.filter(
									name = event['name'],
									date = convert_optional_ddmmyy(event['date']),
									).exists():
			# set the message to show that it exists
			errors.append(event_label + ' not created: event already exists.')
	# check the event type
	try:
		# attempt to get the record
		event_type = Event_Type.objects.get(name = event['event_type'])
	# deal with an event type that doesn't exist		
	except (Event_Type.DoesNotExist):
		# set the error
		errors.append(event_label + ' not created: event type ' + event['event_type'] + ' does not exist.')
	# check whether the ward exists
	try:
		# attempt to get the record
		ward = Ward.objects.get(ward_name = event['ward'])
	# deal with a ward that doesn't exist		
	except (Ward.DoesNotExist):
		# set the error
		errors.append(event_label + ' not created: ward ' + event['ward'] + ' does not exist.')
	# check the areas
	if event['areas']:
		# break the areas string down into areas
		areas = event['areas'].split(',')
		# now go through the areas
		for area_name in areas:
			# try to get the area
			try:
				# attempt to get the record
				area = Area.objects.get(area_name = area_name)
			# deal with the exception
			except (Area.DoesNotExist):
				# set the error
				errors.append(event_label + ' not created: area ' + area_name + ' does not exist.')
	# check the start_time
	if not datetime_valid(event['start_time'],'%H:%M'):
		# set the messages
		errors.append(event_label + ' not created: start time is not in HH:MM format.')
	# and the end_time
	if not datetime_valid(event['end_time'],'%H:%M'):
		# set the messages
		errors.append(event_label + ' not created: end time is not in HH:MM format.')
	# return the errors
	return errors

# DOWNLOAD FUNCTIONS
# functions that return records for download as csv files

def people_download():
	# set the fields
	fields = [
				'first_name',
				'last_name',
				'email_address',
				'home_phone',
				'mobile_phone',
				'date_of_birth',
				'gender',
				'pregnant',
				'due_date',
				'default_role',
				'ethnicity',
				'ABSS_type',
				'age_status',
				'house_name_or_number',
				'street',
				'street.post_code',
				'notes',
				'ABSS_start_date',
				'ABSS_end_date',
				'emergency_contact_details'
				]
	# and a blank list of records
	records = []
	# go through the records
	for person in Person.objects.all():
		# set the post_code
		if person.street:
			# set the post_code
			post_code = person.street.post_code
		# otherwise set a blank
		else:
			# set the blank
			post_code = ''
		# set the field list
		field_list = [
						person.first_name,
						person.last_name,
						person.email_address,
						person.home_phone,
						person.mobile_phone,
						convert_optional_datetime(person.date_of_birth),
						person.gender,
						person.pregnant,
						convert_optional_datetime(person.due_date),
						person.default_role,
						person.ethnicity,
						person.ABSS_type,
						person.age_status,
						person.house_name_or_number,
						person.street,
						post_code,
						person.notes,
						convert_optional_datetime(person.ABSS_start_date),
						convert_optional_datetime(person.ABSS_end_date),
						person.emergency_contact_details
						]
		# append the record
		records.append(field_list)
	# return the values
	return fields, records

def events_download():
	# set the fields
	fields = [
				'name',
				'description',
				'event_type',
				'date',
				'start_time',
				'end_time',
				'location',
				'ward',
				'areas',
				]
	# and a blank list of records
	records = []
	# go through the records
	for event in Event.objects.all():
		# set the ward
		if event.ward:
			# set the ward
			ward = event.ward.ward_name
		# otherwise set a blank
		else:
			# set the blank
			ward = ''
		# set the blank list of areas
		areas = ''
		# go through the areas
		for area in event.areas.all():
			# check whether we need a comma
			if len(areas):
				# add a comma
				areas += ','
			# add the area name to the list
			areas += area.area_name
		# set the field list
		field_list = [
						event.name,
						event.description,
						event.event_type.name,
						convert_optional_datetime(event.date),
						convert_optional_datetime(event.start_time,format='%H:%M'),
						convert_optional_datetime(event.end_time,format='%H:%M'),
						event.location,
						ward,
						areas
						]
		# append the record
		records.append(field_list)
	# return the values
	return fields, records

def relationships_download():
	# set the fields
	fields = [
				'from_first_name',
				'from_last_name',
				'from_age_status',
				'to_first_name',
				'to_last_name',
				'to_age_status',
				'relationship_type',
				]
	# and a blank list of records
	records = []
	# go through the records
	for relationship in Relationship.objects.all():
		# set the field list
		field_list = [
						relationship.relationship_from.first_name,
						relationship.relationship_from.last_name,
						relationship.relationship_from.age_status.status,
						relationship.relationship_to.first_name,
						relationship.relationship_to.last_name,
						relationship.relationship_to.age_status.status,
						relationship.relationship_type.relationship_type
						]
		# append the record
		records.append(field_list)
	# return the values
	return fields, records

def registrations_download():
	# set the fields
	fields = [
				'first_name',
				'last_name',
				'age_status',
				'event_name',
				'event_date',
				'registered',
				'participated',
				'role_type'
				]
	# and a blank list of records
	records = []
	# go through the records
	for registration in Event_Registration.objects.all():
		# set the field list
		field_list = [
						registration.person.first_name,
						registration.person.last_name,
						registration.person.age_status.status,
						registration.event.name,
						convert_optional_datetime(registration.event.date),
						registration.registered,
						registration.participated,
						registration.role_type.role_type_name

						]
		# append the record
		records.append(field_list)
	# return the values
	return fields, records
