from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street
import os
import csv
from django.contrib.auth.decorators import login_required
from .forms import AddPersonForm, ProfileForm, PersonSearchForm, AddRelationshipForm, \
					AddRelationshipToExistingPersonForm, EditExistingRelationshipsForm, \
					AddAddressForm, AddressSearchForm, AddRegistrationForm, \
					EditRegistrationForm, LoginForm, EventSearchForm, EventForm, PersonNameSearchForm, \
					AnswerQuestionsForm, UpdateAddressForm, AddressToRelationshipsForm
from .utilities import get_page_list, make_banner
from .utilities import Dashboard_Panel_Row, Dashboard_Panel, Dashboard_Column, Dashboard
from django.contrib import messages
from django.urls import reverse, resolve
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Count

@login_required
def index(request):
	# get the template
	index_template = loader.get_template('people/index.html')
	# get the lists of people who have ever been parent champions
	parent_champions = get_parent_champions()
	# get the parent champion role type
	parent_champion_role_type = get_role_type_by_name('Parent Champion')
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
	# create the parent champions dashboard panel
	parent_champions_dashboard_panel = Dashboard_Panel(
														title = 'PARENT CHAMPIONS',
														column_names = ['counts'],
														label_width = 8,
														column_width = 3,
														right_margin = 1)
	# add the current parent champions row to the panel
	parent_champions_dashboard_panel.rows.append(
													Dashboard_Panel_Row(
																		label = 'Trained parent champions',
																		values = [len(parent_champions['trained'])],
																		url = 'champions',
																		parameter = 'trained'
																		)
													)
	# and add the all time parent champions row to the panel
	parent_champions_dashboard_panel.rows.append(
													Dashboard_Panel_Row(
																		label = 'Active parent champions',
																		values = [len(parent_champions['active'])],
																		url = 'champions',
																		parameter = 'active'
																		)
													)
	# append the parent champions panel to the column
	roles_dashboard_column.panels.append(parent_champions_dashboard_panel)
	# add the age status dashboard panel
	roles_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'ADULTS AND CHILDREN',
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
														title = 'EXCEPTIONS',
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
	# append the parent champions panel to the column
	roles_dashboard_column.panels.append(exceptions_dashboard_panel)
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
															title_url = 'events_this_month',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_types_with_counts(
																					date_from=first_day_of_this_month
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_type_this_month',
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
															title_url = 'events_last_month',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_types_with_counts(
																					date_from=first_day_of_last_month,
																					date_to=last_day_of_last_month
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_type_last_month',
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
															title_url = 'events_this_year',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_types_with_counts(
																					date_from=first_day_of_this_year
																								),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_type_this_year',
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
															title_url = 'events_all_time',
															column_names = ['Registered','Participated'],
															show_column_names = True,
															rows = get_event_types_with_counts(),
															row_name = 'name',
															row_values = ['registered_count','participated_count'],
															row_url = 'event_type',
															row_parameter_name = 'pk',
															totals = True,
															label_width = 5,
															column_width = 3,
															right_margin = 1,
															)
											)
	# append the roles column to the dashboard
	dashboard.columns.append(events_dashboard_column)
	# create the geo column for the dashboard
	geo_dashboard_column = Dashboard_Column(width=4)
	# add the areas panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'AREAS',
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
	# add the wards panel
	geo_dashboard_column.panels.append(
											Dashboard_Panel(
															title = 'WARDS',
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
	# append the geo column to the dashboard
	dashboard.columns.append(geo_dashboard_column)
	# set the context
	context = build_context({
								'dashboard' : dashboard
								})
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

@login_required
def dataload(request):
	# get the template
	index_template = loader.get_template('people/dataload.html')
	# create a list of messages
	messages = []
	# get the directory
	directory = os.path.dirname(__file__)
	# load simple reference data
	messages = messages + load_reference_data(directory)
	# load relationship types
	messages = messages + load_relationship_types(directory)
	# load event categories
	messages = messages + load_event_categories(directory)
	# load event types
	messages = messages + load_event_types(directory)
	# load role types
	messages = messages + load_role_types(directory)
	# load areas
	messages = messages + load_areas(directory)
	# load wards
	messages = messages + load_wards(directory)
	# load post codes and get the results as messages
	messages = messages + load_post_code(directory)
	# load streets and get the results as messages
	messages = messages + load_streets(directory)
	# add the messages to the context
	context = {
				'load_messages' : messages,
				'site_name': os.getenv('BETTERSTART_NAME', None)
				}
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

# DATA LOAD FUNCTIONS
# A set of functions which read csv files and use them to load data

def load_event_categories(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	event_categories_file_name = os.path.join(directory, 'data/event_categories.csv')
	# open the event_categories file
	event_categories_file = open(event_categories_file_name,'r')
	# read it as a csv file
	event_categories = csv.DictReader(event_categories_file)
	# go through the csv file and process it
	for event_category_record in event_categories:
		# get the event category name
		name = event_category_record['name']
		# create a label for use in messages
		event_category_label = 'Event Category: ' + name
		# check whether the event_category already exists
		try:
			event_category = Event_Category.objects.get(name=name)
			# set the message to show that it exists
			messages.append(event_category_label + ' not created: event_category already exists.')
		except (Event_Category.DoesNotExist):
			# the event_category does not exist, so create it
			event_category = Event_Category(
											name=name,
											description=event_category_record['description']
											)
			# save the event_category
			event_category.save()
			# set the message
			messages.append(event_category_label + ' created.')
	# return the messages
	return messages

def load_event_types(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	event_types_file_name = os.path.join(directory, 'data/event_types.csv')
	# open the areas file
	event_types_file = open(event_types_file_name,'r')
	# read it as a csv file
	event_type_rows = csv.DictReader(event_types_file)
	# go through the csv file and process it
	for event_type_row in event_type_rows:
		# get the category name
		event_category_name = event_type_row['event_category']
		# get the event_type name
		event_type_name = event_type_row['name']
		# create a label for use in messages
		event_type_label = 'Event type: ' + event_type_name + ' (Category: ' + event_category_name + ')'
		# check whether the area exists
		try:
			event_category = Event_Category.objects.get(name=event_category_name)
			# now try to find the event_type
			try:
				event_type = Event_Type.objects.get(name=event_type_name)
				# set the message to show that it exists
				messages.append(event_type_label + ' not created: event type already exists.')
			except (Event_Type.DoesNotExist):
				# create the event_type
				event_type = Event_Type(
										name = event_type_name,
										description = event_type_row['description'],
										event_category = event_category
							)
				# save the event_type
				event_type.save()
				# and set the message
				messages.append(event_type_label + ' created.')
		except (Event_Category.DoesNotExist):
			# the area does not exist, so set an error message
			messages.append(event_type_label + ' not created: event category does not exist.')
	# return the messages
	return messages

def load_areas(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	areas_file_name = os.path.join(directory, 'data/areas.csv')
	# open the areas file
	areas_file = open(areas_file_name,'r')
	# read it as a csv file
	areas = csv.DictReader(areas_file)
	# go through the csv file and process it
	for area in areas:
		# get the area name
		area_name = area['area']
		# create a label for use in messages
		area_label = 'Area: ' + area_name
		# check whether the area already exists
		try:
			area = Area.objects.get(area_name=area_name)
			# set the message to show that it exists
			messages.append(area_label + ' not created: area already exists.')
		except (Area.DoesNotExist):
			# the area does not exist, so create it
			area = Area(area_name=area_name)
			# save the area
			area.save()
			# set the message
			messages.append(area_label + ' created.')
	# return the messages
	return messages

def load_wards(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	wards_file_name = os.path.join(directory, 'data/wards.csv')
	# open the areas file
	wards_file = open(wards_file_name,'r')
	# read it as a csv file
	ward_rows = csv.DictReader(wards_file)
	# go through the csv file and process it
	for ward_row in ward_rows:
		# get the area name
		area_name = ward_row['area']
		# get the ward name
		ward_name = ward_row['ward']
		# create a label for use in messages
		ward_label = 'Ward: ' + ward_name + ' (Area: ' + area_name + ')'
		# check whether the area exists
		try:
			area = Area.objects.get(area_name=area_name)
			# now try to find the ward
			try:
				ward = Ward.objects.get(ward_name=ward_name)
				# set the message to show that it exists
				messages.append(ward_label + ' not created: ward already exists.')
			except (Ward.DoesNotExist):
				# create the ward
				ward = Ward(
							ward_name = ward_name,
							area = area
							)
				# save the ward
				ward.save()
				# and set the message
				messages.append(ward_label + ' created.')
		except (Area.DoesNotExist):
			# the area does not exist, so set an error message
			messages.append(ward_label + ' not created: area does not exist.')
	# return the messages
	return messages

def load_post_code(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	postcodes_file_name = os.path.join(directory, 'data/postcodes.csv')
	# open the post code file
	postcodes_file = open(postcodes_file_name,'r')
	# read it as a csv file
	postcode_rows = csv.DictReader(postcodes_file)
	# go through the csv file and process it
	for postcode_row in postcode_rows:
		# get the post code
		post_code_name = postcode_row['postcode']
		# and the ward
		ward_name = postcode_row['ward']
		# create a label for use in messages
		post_code_label = 'Post code: ' + post_code_name + ' (Ward: ' + ward_name + ')'
		# check whether the ward exists
		try:
			ward = Ward.objects.get(ward_name=ward_name)
			# now try to find the post code
			try:
				post_code = Post_Code.objects.get(post_code=post_code_name)
				# set the message to show that it exists
				messages.append(post_code_label + ' not created: postcode already exists.')
			except (Post_Code.DoesNotExist):
				# create the ward
				post_code = Post_Code(
										post_code = post_code_name,
										ward = ward
									)
				# save the ward
				post_code.save()
				# and set the message
				messages.append(post_code_label + ' created.')
		except (Ward.DoesNotExist):
			# the area does not exist, so set an error messaage
			messages.append(post_code_label + ' not created: ward does not exist.')
	# return the messages
	return messages

def load_streets(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	streets_file_name = os.path.join(directory, 'data/streets_and_post_codes.csv')
	# open the streets file
	streets_file = open(streets_file_name,'r')
	# read it as a csv file
	streets_rows = csv.DictReader(streets_file)
	# go through the csv file and process it
	for street_row in streets_rows:
		# get the street
		street_name = street_row['name']
		# and the post code
		post_code_name = street_row['post_code']
		# create a label for use in messages
		street_label = 'Street: ' + street_name + ' (Post Code: ' + post_code_name + ')'
		# check whether the post_code exists
		try:
			post_code = Post_Code.objects.get(post_code=post_code_name)
			# now try to find the street
			try:
				street = Street.objects.get(name=street_name,post_code=post_code)
				# set the message to show that it exists
				messages.append(street_label + ' not created: street already exists.')
			except (Street.DoesNotExist):
				# create the street
				street = Street(
										name = street_name,
										post_code = post_code
									)
				# save the street
				street.save()
				# and set the message
				messages.append(street_label + ' created.')
		except (Post_Code.DoesNotExist):
			# the area does not exist, so set an error messaage
			messages.append(street_label + ' not created: street does not exist.')
	# return the messages
	return messages

def load_reference_data(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	data_file_name = os.path.join(directory, 'data/reference_data.csv')
	# open the areas file
	data_file = open(data_file_name,'r')
	# read it as a csv file
	records = csv.DictReader(data_file)
	# go through the csv file and process it
	for record in records:
		# get the data type
		data_type = record['data_type']
		# get the value
		value = record['value']
		# try to create the record, starting with capture type
		if data_type == 'capture_type':
			messages.append(load_capture_type(value))
		# now ethnicity
		elif data_type == 'ethnicity':
			messages.append(load_ethnicity(value))
		# then relationship type
		elif data_type == 'relationship_type':
			messages.append(load_relationship_type(value))
		# then children centres
		elif data_type == 'children_centre':
			messages.append(load_children_centre(value))
		# and abss type
		elif data_type == 'ABSS_type':
			messages.append(load_ABSS_type(value))
		# and age status
		elif data_type == 'age_status':
			messages.append(load_age_status(value))	
		# and deal with any unknown type
		else:
			# set an error message
			messages = messages + ['Data type: ' + data_type + ' is not recognised.']
	# return the messages
	return messages

def load_role_types(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	role_types_file_name = os.path.join(directory, 'data/role_types.csv')
	# open the role types file
	role_types_file = open(role_types_file_name,'r')
	# read it as a csv file
	role_types = csv.DictReader(role_types_file)
	# go through the csv file and process it
	for role_type_record in role_types:
		# get the name
		role_type_name = role_type_record['role_type_name']
		# create a label for use in messages
		role_type_label = 'Role Type: ' + role_type_name
		# check whether the role type already exists
		try:
			role_type = Role_Type.objects.get(role_type_name=role_type_name)
			# set the message to show that it exists
			messages.append(role_type_label + ' not created: Role Type already exists.')
		# we didn't find a record
		except (Role_Type.DoesNotExist):
			# the role_type does not exist, so create it
			role_type = Role_Type(
									role_type_name = role_type_name,
									use_for_events = (role_type_record['use_for_events'] == 'True'),
									use_for_people = (role_type_record['use_for_people'] == 'True')
									)
			# save the role type
			role_type.save()
			# set the message
			messages.append(role_type_label + ' created.')
	# return the messages
	return messages

def load_capture_type(value):
	# create a label for use in messages
	capture_type_label = 'Capture type: ' + value
	# check whether the capture type already exists
	try:
		capture_type = Capture_Type.objects.get(capture_type_name=value)
		# set the message to show that it exists
		message = capture_type_label + ' not created: capture type already exists.'
	except (Capture_Type.DoesNotExist):
		# the capture type does not exist, so create it
		capture_type = Capture_Type.objects.create(capture_type_name=value)
		# set the message
		message = capture_type_label + ' created.'
	# return the messages
	return message

def load_ethnicity(value):
	# create a label for use in messages
	ethnicity_label = 'Ethnicity: ' + value
	# check whether the capture type already exists
	try:
		ethnicity = Ethnicity.objects.get(description=value)
		# set the message to show that it exists
		message = ethnicity_label + ' not created: ethnicity already exists.'
	except (Ethnicity.DoesNotExist):
		# the capture type does not exist, so create it
		ethnicity = Ethnicity.objects.create(description=value)
		# set the message
		message = ethnicity_label + ' created.'
	# return the messages
	return message

def load_children_centre(value):
	# create a label for use in messages
	children_centre_label = 'Children centre: ' + value
	# check whether the capture type already exists
	try:
		children_centre = Children_Centre.objects.get(children_centre_name=value)
		# set the message to show that it exists
		message = children_centre_label + ' not created: children centre already exists.'
	except (Children_Centre.DoesNotExist):
		# the capture type does not exist, so create it
		children_centre = Children_Centre.create(children_centre_name=value)
		# set the message
		message = children_centre_label + ' created.'
	# return the messages
	return message

def load_ABSS_type(value):
	# create a label for use in messages
	ABSS_type_label = 'ABSS type: ' + value
	# check whether the record already exists
	try:
		ABSS_type = ABSS_Type.objects.get(name=value)
		# set the message to show that it exists
		message = ABSS_type_label + ' not created: ABSS type already exists.'
	except (ABSS_Type.DoesNotExist):
		# the type does not exist, so create it
		ABSS_type = ABSS_Type.objects.create(name=value)
		# set the message
		message = ABSS_type_label + ' created.'
	# return the messages
	return message

def load_age_status(value):
	# create a label for use in messages
	age_status_label = 'Age status: ' + value
	# check whether the record already exists
	try:
		age_status = Age_Status.objects.get(status=value)
		# set the message to show that it exists
		message = age_status_label + ' not created: Age status already exists.'
	except (Age_Status.DoesNotExist):
		# the type does not exist, so create it
		age_status = Age_Status.objects.create(status=value)
		# set the message
		message = age_status_label + ' created.'
	# return the messages
	return message

def load_relationship_types(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	relationship_types_file_name = os.path.join(directory, 'data/relationship_types.csv')
	# open the relationship types file
	relationship_types_file = open(relationship_types_file_name,'r')
	# read it as a csv file
	relationship_type_records = csv.DictReader(relationship_types_file)
	# go through the csv file and process it
	for relationship_type_record in relationship_type_records:
		# get the values
		relationship_type = relationship_type_record['relationship_type']
		relationship_counterpart = relationship_type_record['relationship_counterpart']
		# create a label for use in messages
		relationship_type_label = 'Relationship type: ' + relationship_type
		# check whether the relationship type already exists
		try:
			this_relationship_type = Relationship_Type.objects.get(relationship_type=relationship_type)
			# set the message to show that it exists
			message = relationship_type_label + ' not created: relationship type already exists.'
		# handle the exception (which is what we expect)
		except (Relationship_Type.DoesNotExist):
			# the relationship type does not exist, so create it
			this_relationship_type = Relationship_Type(
														relationship_type=relationship_type,
														relationship_counterpart=relationship_counterpart
														)
			# save the relationship type
			this_relationship_type.save()
			# set the message
			message = relationship_type_label + ' created.'
		# append the message
		messages.append(message)
	# return the messages
	return messages

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

def people_search(
					first_name='',
					last_name='',
					role_type='0',
					ABSS_type='0',
					age_status='0',
					champions='0'):
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
		# check whether this was an all parent champions enquiry
		if role_type == 'Has ever been a Parent Champion':
			# do the filter
			people = people.filter(role_history__role_type__role_type_name='Parent Champion').distinct()
		# otherwise just check for a normal role type
		else:
			# apply the filter
			people = people.filter(default_role_id=int(role_type))
	# if we have an ABSS type, filter by the ABSS type
	if ABSS_type != '0':
		# do the filter
		people = people.filter(ABSS_type_id=int(ABSS_type))
	# if we have an age status, filter by the age status
	if age_status != '0':
		# do the filter
		people = people.filter(age_status_id=int(age_status))
	# if we have a champion setting, filter by the champion flags
	if champions != '0':
		# check what type of query we got
		if champions == 'trained':
			# get the trained champions
			people = people.filter(trained_champion=True)
		# otherwise we got a different request
		elif champions == 'active':
			# get the active champions
			people = people.filter(active_champion=True)
	# if we have an age status, filter by the age status
	if age_status != '0':
		# do the filter
		people = people.filter(age_status_id=int(age_status))
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

def get_parent_champions():
	# return a dict of two lists: trained parent champions and active parent champions
	# declare the dict
	parent_champions = {}
	# get the trained parent champions
	parent_champions['trained'] = Person.objects.filter(trained_champion=True)
	# get actie parent champions
	parent_champions['active'] = Person.objects.filter(active_champion=True)
	# return the dict
	return parent_champions

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

def get_events_by_name_dates_and_type(name,event_type,date_from,date_to):
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
	role_types = Role_Type.objects.all()
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
	questions = Question.objects.all()
	# get the options for each question
	for question in questions:
		# get the answers and stash it in the object
		question.options = question.option_set.all()
		# set a default answer
		question.answer = 0
		# now try to get an answer
		answer = get_answer(
							person=person,
							question=question
							)
		# check whether we got an answer
		if answer:
			# set the answer
			question.answer = answer.option.pk
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
					ethnicity=1,
					ABSS_type=1,
					age_status=1,
					trained_champion=False,
					active_champion=False):
	# check whether we have a role type
	if default_role:
		# get the role
		default_role = get_role_type(default_role)
	# otherwise set unknown
	else:
		# get the UNKNOWN role type
		default_role = get_role_type_by_name('UNKNOWN')
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
					age_status = get_age_status(age_status),
					trained_champion=trained_champion,
					active_champion=active_champion
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

def create_relationship(person_from, person_to, relationship_type_from):
	# create a symmetrical relationship between two people
	# create a flag
	success = False
	# check whether the relationship already exists
	try:
		# do the database call
		relationship = Relationship.objects.get(relationship_from=person_from,
												relationship_to=person_to)
	# handle the exception
	except Relationship.DoesNotExist:
		# start by getting the other half of the relationship
		relationship_type_to = get_relationship_type_by_type(relationship_type_from.relationship_counterpart)
		# now create the from part of the relationship
		relationship_from = Relationship(
										relationship_from = person_from,
										relationship_to = person_to,
										relationship_type = relationship_type_from)
		# now save it
		relationship_from.save()
		# now create the to part of the relationship
		relationship_to = Relationship(
										relationship_from = person_to,
										relationship_to = person_from,
										relationship_type = relationship_type_to)
		# now save it
		relationship_to.save()
		# set the flag
		success = True
	# that's it!
	return success

def create_event(name, description, date, start_time, end_time, event_type, location):
	# create an event
	event = Event(
					name = name,
					description = description,
					location = location,
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

def edit_relationship(request, person_from, person_to, relationship_type_id):
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
			# set the messages
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
			# set a message
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
		if create_relationship(
							 person_from = person_from,
							 person_to = person_to,
							 relationship_type_from = relationship_type_from
							):
			# set the success message
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
			# set the message
			messages.error(request, 'Relationship could not be created.')
	# return the result
	return success

def build_event(request, name, description, date, start_time, end_time, event_type_id, location):
	# get the event type
	event_type = get_event_type(event_type_id)
	# if we got an event type, create the event
	if event_type:
		# create the event
		event = create_event(
								name = name,
								description = description,
								location = location,
								date = date,
								start_time = start_time,
								end_time = end_time,
								event_type = event_type
							)
		# set a message
		messages.success(request, 'New event (' + str(event) + ') created.')
	# otherwise set a message
	else:
		# set the failed creation message
		messages.error(request, 'Event (' + name + ') could not be created: event type does not exist.')
	# return the event
	return event

def build_registration(request, event, person_id, registered, participated, role_type_id):
	# attempt to create a new registration, checking first that the registration does not exit
	# first get the person
	person = get_person(person_id)
	# if that didn't work, set an error and return
	if not person:
		# set the message
		messages.error(request,'Registration for person ' + str(person_id) + ' failed: person does not exist.')
		# and return
		return False
	# now attempt to get the role type
	role_type = get_role_type(role_type_id)
	# if that didn't work, set an error and return
	if not role_type:
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
			# set the success message
			messages.success(request,'Registration (' + str(registration) + ') updated.')
	# return the residence
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

def update_person(
					request,
					person,
					first_name,
					middle_names,
					last_name,
					email_address,
					date_of_birth,
					gender,
					english_is_second_language,
					pregnant,
					due_date,
					default_role_id,
					ethnicity_id,
					ABSS_type_id,
					age_status_id,
					trained_champion,
					active_champion
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
	person.date_of_birth = date_of_birth
	person.gender = gender
	person.english_is_second_language = english_is_second_language
	person.pregnant = pregnant
	person.due_date = due_date
	person.trained_champion = trained_champion
	person.active_champion = active_champion
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
	champions = 0
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
			champions = personsearchform.cleaned_data['champions']
			# conduct a search
			people = people_search(
													first_name=first_name,
													last_name=last_name,
													role_type=role_type,
													ABSS_type=ABSS_type,
													age_status=age_status,
													champions=champions
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
				'champions' : champions,
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
					'champions' : '0'
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
	copy_POST['champions'] = form_values['champions']
	copy_POST['page'] = '1'
	# now copy it back
	request.POST = copy_POST
	# and set the method
	request.method = 'POST'
	# now call the people view
	return people(request)

@login_required
def parent_exceptions(request, page=1):
	# get the path, and figure out what we have been called as
	path = request.get_full_path()
	# set variables based on the type of call
	if 'parents_with_no_children' in path:
		# set the variables, starting with the relevant list of parents
		parents, parents_with_no_children_under_four = get_parents_without_children()
		# set the url
		parent_exceptions_template = loader.get_template('people/parents_without_children.html')
	# otherwise check for parents with no children under four
	elif 'parents_without_children_under_four' in path:
		# set the variables, starting with the relevant list of parents
		parents_with_no_children, parents = get_parents_without_children()
		# set the url
		parent_exceptions_template = loader.get_template('people/parents_without_children_under_four.html')
	# otherwise check for parents with overdue children
	elif 'parents_with_overdue_children' in path:
		# set the variables, starting with the relevant list of parents
		parents = get_parents_with_overdue_children()
		# set the url
		parent_exceptions_template = loader.get_template('people/parents_with_overdue_children.html')
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
				'page_list' : page_list,
				})
	# return the HttpResponse
	return HttpResponse(parent_exceptions_template.render(context=context, request=request))

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
			# see whether this is a confirmation action
			# get the action from the request
			action = request.POST.get('action','')
			# see if there is an action
			if action == 'CONFIRM':
				# create the person
				person = create_person(
										first_name = first_name,
										last_name = last_name,
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
									last_name = last_name
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
	# set the context from the person based on person id
	context = build_context({
				'person' : person,
				'relationships_to' : relationships_to,
				'registrations' : Event_Registration.objects.filter(person=person),
				'answers' : person.answers.all(),
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
								date_of_birth = profileform.cleaned_data['date_of_birth'],
								gender = profileform.cleaned_data['gender'],
								english_is_second_language = profileform.cleaned_data['english_is_second_language'],
								pregnant = profileform.cleaned_data['pregnant'],
								due_date = profileform.cleaned_data['due_date'],
								default_role_id = profileform.cleaned_data['role_type'],
								ethnicity_id = profileform.cleaned_data['ethnicity'],
								ABSS_type_id = profileform.cleaned_data['ABSS_type'],
								age_status_id = profileform.cleaned_data['age_status'],
								trained_champion = profileform.cleaned_data['trained_champion'],
								active_champion = profileform.cleaned_data['active_champion']
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
						'date_of_birth' : person.date_of_birth,
						'role_type' : person.default_role.pk,
						'ethnicity' : person.ethnicity.pk,
						'gender' : person.gender,
						'english_is_second_language' : person.english_is_second_language,
						'pregnant' : person.pregnant,
						'due_date' : person.due_date,
						'ABSS_type' : person.ABSS_type.pk,
						'age_status' : person.age_status.pk,
						'trained_champion' : person.trained_champion,
						'active_champion' : person.active_champion
						}
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
															request.POST,
															relationship_types=relationship_types,
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
											date_of_birth = addrelationshipform.cleaned_data['date_of_birth'],
											default_role = addrelationshipform.cleaned_data['role_type'],
											gender = addrelationshipform.cleaned_data['gender'],
											ABSS_type = addrelationshipform.cleaned_data['ABSS_type'],
											age_status = addrelationshipform.cleaned_data['age_status']
											)
				# set a message to say that we have create a new person
				messages.success(request, str(person_to) + ' created.')
				# now create the relationship
				edit_relationship(request,person, person_to, addrelationshipform.cleaned_data['relationship_type'])
				# clear the add relationship form so that it doesn't display
				addrelationshipform = ''
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
																		relationships=relationships_to,
																		relationship_types=get_relationship_types()
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
		addeventform = EventForm(request.POST, event_types=event_types)
		# check whether the form is valid
		if addeventform.is_valid():
			# create the event
			event = build_event(
								request,
								name = addeventform.cleaned_data['name'],
								description = addeventform.cleaned_data['description'],
								location = addeventform.cleaned_data['location'],
								date = addeventform.cleaned_data['date'],
								start_time = addeventform.cleaned_data['start_time'],
								end_time = addeventform.cleaned_data['end_time'],
								event_type_id = addeventform.cleaned_data['event_type']
								)
			# if we were successful, redirect to the registration page
			if event:
				# create a fresh form
				return redirect('/event_registration/' + str(event.pk))
	# otherwise create a fresh form
	else:
		# create the fresh form
		addeventform = EventForm(event_types=event_types)
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
def event_type(request, event_type='0'):
	# get the calling url
	path = request.get_full_path()
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
	event_type = 0,
	date_from = 0,
	date_to = 0
	# set a blank search_error
	search_error = ''
	# and a zero number of results
	number_of_events = 0
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		eventsearchform = EventSearchForm(request.POST, event_types=get_event_types())
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			if eventsearchform.is_valid():
				# get the values
				name = eventsearchform.cleaned_data['name']
				date_from = eventsearchform.cleaned_data['date_from']
				date_to = eventsearchform.cleaned_data['date_to']
				event_type = eventsearchform.cleaned_data['event_type']
				# conduct a search
				events = get_events_by_name_dates_and_type(
															name=name,
															date_from=date_from,
															date_to=date_to,
															event_type=int(event_type)
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
		eventsearchform = EventSearchForm(event_types=get_event_types())
	# get the template
	events_template = loader.get_template('people/events.html')
	# set the context
	context = build_context({
				'events' : events,
				'eventsearchform' : eventsearchform,
				'name' : name,
				'event_type' : event_type,
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
									event_types=get_event_types()
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
			# save the record
			event.save()
			# set a success message
			messages.success(request, str(event) + ' updated.')
			# send the user back to the main person page
			return redirect('/event/' + str(event.pk))
	else:
		# there is an event, so build a dictionary of initial values we want to set
		event_dict = {
						'name' : event.name,
						'description' : event.description,
						'location' : event.location,
						'date' : event.date,
						'start_time' : event.start_time,
						'end_time' : event.end_time,
						'event_type' : event.event_type.pk
						}
		# create the form
		editeventform = EventForm(
									event_dict,
									event_types=get_event_types()
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
			# get the option id from the value of the field
			option_id = int(answerquestionsform.data[field])
			# build the answer
			build_answer(request,person,question_id,option_id)
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



