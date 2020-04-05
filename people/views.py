from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note, Site, Activity_Type, Activity, Dashboard, \
					Venue_Type, Venue
import os
import csv
import copy
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import AddPersonForm, ProfileForm, PersonSearchForm, AddRelationshipForm, \
					AddRelationshipToExistingPersonForm, EditExistingRelationshipsForm, \
					AddAddressForm, AddressSearchForm, AddRegistrationForm, \
					EditRegistrationForm, LoginForm, EventSearchForm, EventForm, PersonNameSearchForm, \
					AnswerQuestionsForm, UpdateAddressForm, AddressToRelationshipsForm, UploadDataForm, \
					DownloadDataForm, PersonRelationshipSearchForm, ActivityForm, AddPersonAndRegistrationForm, \
					VenueForm, VenueSearchForm
from .utilities import get_page_list, make_banner, extract_id, build_page_list, Page, Chart
from .old_dashboards import Old_Dashboard_Panel_Row, Old_Dashboard_Panel, Old_Dashboard_Column, Old_Dashboard
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
							People_File_Handler, Relationships_File_Handler, Events_File_Handler, \
							Registrations_File_Handler, Questions_File_Handler, Options_File_Handler, \
							Answers_File_Handler, Answer_Notes_File_Handler, Activities_File_Handler, \
							Event_Summary_File_Handler
import matplotlib.pyplot as plt, mpld3

@login_required
def index(request):
	# if we have a dashboard for the site, load that, otherwise use the default dashboard
	site = Site.objects.all().first()
	if site and site.dashboard:
		dashboard = site.dashboard
		index_template = loader.get_template('people/dashboard.html')
	else:
		dashboard = build_default_dashboard()
		index_template = loader.get_template('people/index.html')
	# set the context
	context = build_context({
								'dashboard' : dashboard,
								'show_title' : False
								})
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

# DATA ACCESS FUNCTIONS
# A set of functions which carry out simple and complex data access, filtering and updates.
# These functions are kept as simple as possible.

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

def get_parents_without_children():
	# create an empty list
	parents_with_no_children = []
	parents_with_no_children_under_four = []
	# get today's date
	today = datetime.date.today()
	# get the date four years ago
	today_four_years_ago = today.replace(year=today.year-4)
	# attempt to get parents with no children
	parents = Person.search(default_role__role_type_name__contains='Parent')
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
	return Person.search(
							pregnant=True,
							due_date__lt=datetime.date.today()
							)

def get_children_over_four():
	# get today's date
	today = datetime.date.today()
	# return the results
	return Person.search(date_of_birth__lt=today.replace(year=today.year-4),
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
								date_of_birth__lt=today.replace(year=today.year-age_status.maximum_age),
								ABSS_end_date__isnull=True)
		# see whether we got any exceptions
		if age_exceptions.count() > 0:
			# add the count to the object
			age_status.count = age_exceptions.count()
			# add the object to the list
			age_statuses.append(age_status)
	# return the results
	return age_statuses

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

def add_counts_to_events(events):
	# take a list of events, and add the count of participated and volunteered numbers to them
	for event in events:
		# get the registrations
		event.registered_count = event.event_registration_set.filter(registered=True).count()
		# and the participations
		event.participated_count = event.event_registration_set.filter(participated=True).count()
		# and the apologies
		event.apologies_count = event.event_registration_set.filter(apologies=True).count()
	# return the results
	return events

def get_trained_role_types_with_people_counts():
	# create the list
	trained_role_list = []
	# return a list of all the trained role type objects, supplemented with counts
	role_types = Role_Type.objects.filter(trained=True)
	# now go through the role types
	for role_type in role_types:
		# set the count for trained
		role_type.count = role_type.trained_people.exclude(ABSS_end_date__isnull=False).count()
		# and the key for trained
		role_type.trained_role_key = 'trained_' + str(role_type.pk)
		# and the name for trained
		role_type.trained_role_name = 'Trained ' + role_type.role_type_name
		# and append a copy of the object to the list
		trained_role_list.append(role_type)
		# create a new object
		active_role_type = copy.deepcopy(role_type)
		# now set the count for active
		active_role_type.count = active_role_type.trained_role_set.filter(
										active=True,
										person__ABSS_end_date__isnull=False).count()
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
		role_type.count = Person.search(default_role=role_type).count()
	# return the results
	return role_types

def get_wards_with_people_counts():
	# return a list of all the wards with people counts
	wards = Ward.objects.all()
	# now go through the wards
	for ward in wards:
		# get the count
		ward.count = Person.search(street__post_code__ward=ward).count()
	# return the results
	return wards

def get_areas_with_people_counts():
	# return a list of all the areas with people counts
	areas = Area.objects.all()
	# now go through the areas
	for area in areas:
		# get the count
		area.count = Person.search(street__post_code__ward__area=area).count()
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

def get_questions_and_answers(person):
	# this function gets a list of questions, and adds the answers relevant to the person
	# set the flag to false to show whether we have answers for this person
	answer_flag = False
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
		answer = Answer.try_to_get(
									person=person,
									question=question
									)
		# check whether we got an answer
		if answer:
			# set the answer
			question.answer = answer.option.pk
			# and the text
			question.answer_text = answer.option.option_label
			# and the flag
			answer_flag = True
		# set a default note
		question.note = ''
		# now try to get an answer note
		answer_note = Answer_Note.try_to_get(
											person=person,
											question=question
											)
		# check whether we got an answer note
		if answer_note:
			# set the answer
			question.note = answer_note.notes
			# and the flag
			answer_flag = True
	# return the results
	return questions, answer_flag

def get_ABSS_types_with_counts():
	# define the list
	ABSS_types = ABSS_Type.objects.all()
	# go through the ABSS types
	for ABSS_type in ABSS_types:
		# get the count
		ABSS_type.count = Person.search(ABSS_type=ABSS_type).count()
	# return the results
	return ABSS_types

def get_age_statuses_with_counts():
	# define the list
	age_statuses = Age_Status.objects.all()
	# now go through the ABSS types
	for age_status in age_statuses:
		# get the count
		age_status.count = Person.search(age_status=age_status).count()
	# return the results
	return age_statuses

def create_person(
					first_name,
					last_name,
					middle_names='',
					default_role_id=False,
					date_of_birth=None,
					gender='',
					ethnicity_id=0,
					ABSS_type_id=0,
					age_status_id=0,
					):
	# get the age status, defaulting to Adult if not supplied
	if not age_status_id:
		age_status = Age_Status.objects.get(status='Adult')
	else:
		age_status = Age_Status.try_to_get(pk=age_status_id)
	# get the role, defaulting to the age status default if not supplied
	if default_role_id:
		default_role = Role_Type.try_to_get(pk=default_role_id)
	else:
		default_role = age_status.default_role_type
	# get the ethnicity, defaulting to Prefer not to say if not supplied
	if not ethnicity_id:
		ethnicity = Ethnicity.objects.get(description='Prefer not to say')
	else:
		ethnicity = Ethnicity.try_to_get(pk=ethnicity_id)
	# and the ABSS type
	if not ABSS_type_id:
		ABSS_type = ABSS_Type.objects.get(name='ABSS beneficiary')
	else:
		ABSS_type = ABSS_Type.try_to_get(pk=ABSS_type_id)
	# and get a membership if the ABSS type needs it, otherwise set it to zero
	if ABSS_type.membership_number_required:
		membership_number = Person.get_next_membership_number()
	else:
		membership_number = 0
	# create a person
	person = Person(
					first_name = first_name,
					middle_names = middle_names,
					last_name = last_name,
					date_of_birth = date_of_birth,
					gender = gender,
					default_role = default_role,
					ethnicity = ethnicity,
					ABSS_type = ABSS_type,
					age_status = age_status,
					membership_number = membership_number
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

def create_registration(event, person, registered, apologies, participated, role_type):
	# create a registration
	registration = Event_Registration(
								event = event,
								person = person,
								registered = registered,
								apologies = apologies,
								participated = participated,
								role_type = role_type
						)
	# save the record
	registration.save()
	# and return the registration
	return registration

def update_registration(registration, registered, apologies, participated, role_type):
	# update the registration
	registration.registered = registered
	registration.apologies = apologies
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
		relationship_type_from = Relationship_Type.try_to_get(pk=relationship_type_id)
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

def build_event(
				request,
				name,
				description,
				date,
				start_time,
				end_time,
				event_type_id,
				location,
				venue,
				ward_id,
				areas
				):
	# get the related objects
	event_type = Event_Type.try_to_get(pk=event_type_id)
	ward = Ward.try_to_get(pk=ward_id) if ward_id != '0' else None
	venue = Venue.try_to_get(pk=venue) if venue != '0' else None
	# create the event
	if event_type:
		# create the event
		event = Event(
						name = name,
						description = description,
						location = location,
						venue = venue,
						ward = ward,
						date = date,
						start_time = start_time,
						end_time = end_time,
						event_type = event_type
						)
		event.save()
		# set a message
		messages.success(request, 'New event (' + str(event) + ') created.')
		# got through the areas and add them
		for area_id in areas.keys():
			if (areas[area_id] == True) or (ward and ward.area.pk == area_id):
				event.areas.add(Area.objects.get(id=area_id))
	# otherwise set a message
	else:
		messages.error(request, 'Event (' + name + ') could not be created: event type does not exist.')
	# return the event
	return event

def build_registration(request, event, person_id, registered, apologies, participated, role_type_id, show_messages=True):
	# attempt to create a new registration, checking first that the registration does not exit
	# first get the person
	person = Person.try_to_get(pk=person_id)
	# if that didn't work, set an error and return
	if not person:
		# check whether messages are needed
		if show_messages:
			# set the message
			messages.error(request,'Registration for person ' + str(person_id) + ' failed: person does not exist.')
		# and return
		return False
	# now attempt to get the role type
	role_type = Role_Type.try_to_get(pk=role_type_id)
	# if that didn't work, set an error and return
	if not role_type:
		# check whether messages are needed
		if show_messages:
			# set the message
			messages.error(request,'Registration for person ' + str(person_id) + ' failed: role type does not exist.')
		# and return
		return False
	# now attempt to get the registration
	registration = Event_Registration.try_to_get(person=person,event=event)
	# check whether we got a registration or not
	if not registration:
		# create the registration
		registration = create_registration(
											event = event,
											person = person,
											registered = registered,
											apologies = apologies,
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
		or registration.apologies != apologies \
		or registration.role_type != role_type:
			# edit the registration
			registration = update_registration(
												registration = registration,
												registered = registered,
												participated = participated,
												apologies = apologies,
												role_type = role_type)
			# check whether messages are needed
			if show_messages:
				# set the success message
				messages.success(request,'Registration (' + str(registration) + ') updated.')
	# check whether the role type requires training, and, if it does set the role to active for the person
	if role_type.trained:
		set_trained_role_to_active(
									person=person,
									role_type = role_type
									)
	# return the registration
	return registration

def set_trained_role_to_active(person, role_type):
	# take a person and role type and, if the role type requires training, set it to active
	# check whether the role type requires training: return if it doesn't
	if not role_type.trained:
		return
	# check whether a relationship exists
	trained_role = Trained_Role.try_to_get(
											person=person,
											role_type=role_type
											)
	# if we have a role, check whether it's active, and set it to active if it isn't
	if trained_role:
		if not trained_role.active:
			trained_role.active = True
			trained_role.save()
	# otherwise we don't have a trained role, so create one
	else:
		Trained_Role.objects.create(
									person=person,
									role_type=role_type,
									active=True
									)
	# return the trained role
	return trained_role

def remove_registration(request, event, person_id):
	# attempt to remove a registration record, checking first that the registration exists
	# first get the person
	person = Person.try_to_get(pk=person_id)
	# if that didn't work, set an error and return
	if not person:
		# set the message
		messages.error(request,'Deletion of registration for person ' + str(person_id) + ' failed: person does not exist.')
		# and return
		return False
	# now attempt to get the registration
	registration = Event_Registration.try_to_get(
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
	question = Question.try_to_get(pk=question_id)
	# deal with exceptions if we didn't get a question
	if not question:
		# set the error
		messages.error(request,'Could not create answer: question' + str(question_id) + ' does not exist.')
		# and crash out
		return False
	# check that we have a valid option
	if option_id != 0:
		# get the option
		option = Option.try_to_get(pk=option_id)
		# deal with exceptions if we didn't get an option
		if not option:
			# set the error
			messages.error(request,'Could not create answer: option ' + str(option_id) + ' does not exist.')
			# and crash out
			return False
	# see whether we have an answer
	answer = Answer.try_to_get(person=person,question=question)
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
	question = Question.try_to_get(pk=question_id)
	# deal with exceptions if we didn't get a question
	if not question:
		# set the error
		messages.error(request,'Could not create answer note: question' + str(question_id) + ' does not exist.')
		# and crash out
		return False
	# see whether we have an answer note
	answer_note = Answer_Note.try_to_get(person=person,question=question)
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
					other_names,
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
					notes,
					membership_number
				):
	# set the role change flag to false: we don't know whether the role has changed
	role_change = False
	# attempt to get the ethnicity
	ethnicity = Ethnicity.try_to_get(pk=ethnicity_id)
	# set the value for the person
	if ethnicity:
		# set the value
		person.ethnicity = ethnicity
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'Ethnicity does not exist.')
	# attempt to get the ABSS type
	ABSS_type = ABSS_Type.try_to_get(pk=ABSS_type_id)
	# set the value for the person
	if ABSS_type:
		# set the value
		person.ABSS_type = ABSS_type
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'ABSS Type does not exist.')
	# attempt to get the age status
	age_status = Age_Status.try_to_get(pk=age_status_id)
	# set the value for the person
	if age_status:
		# set the value
		person.age_status = age_status
	# otherwise set a message
	else:
		# set the message
		messages.error(request, 'Age Status does not exist.')
	# attempt to get the role type
	default_role = Role_Type.try_to_get(pk=default_role_id)
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
	person.other_names = other_names
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
	person.membership_number = membership_number
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
	street = Street.try_to_get(pk=street_id)
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

def build_activity(request, person, activity_type_id, date, hours):
	# attempt to get the activity type
	activity_type = Activity_Type.try_to_get(pk=activity_type_id)
	# deal with exceptions if we didn't get a valid activity type
	if not activity_type:
		# set the error
		messages.error(
						request,
						'Could not create activity: activity type' + str(activity_type_id) + ' does not exist.'
						)
		# and crash out
		return False
	# see whether we already have an activity
	activity = Activity.try_to_get(person=person,activity_type=activity_type,date=date)
	# if we got an activity, check whether this is an update or delete
	if activity:
		# check the action
		if hours == 0:
			# get the description
			activity_desc = str(activity)
			# delete the record
			activity.delete()
			# set the message
			messages.success(request,activity_desc + ' - deleted successfully.')
		# otherwise do the update
		else:
			# set the hours
			activity.hours = hours
			# and save the record
			activity.save()
			# and the message
			messages.success(request,str(activity) + ' - updated successfully.')
	# otherwise we have a new activity
	else:
		# check the action
		if hours == 0:
			# set a message to say that we haven't created anything
			messages.success(request,'Activity not created - hours set to zero.')
		# otherwise create the record
		else:
			# create the object
			activity = Activity(
								person = person,
								activity_type = activity_type,
								date = date,
								hours = hours
								)
			# and save it to the database
			activity.save()
			# and set a message
			messages.success(request,str(activity) + ' - created successfully.')
	# and we're done
	return activity

def build_default_dashboard():
	# get the exceptions
	parents_with_no_children, parents_with_no_children_under_four = get_parents_without_children()
	# get parents with overdue children
	parents_with_overdue_children = get_parents_with_overdue_children()
	# create a dashboard
	dashboard = Old_Dashboard(margin=0)
	# create the roles column for the dashboard
	roles_dashboard_column = Old_Dashboard_Column(width=4)
	# add the role types dashboard panel
	roles_dashboard_column.panels.append(
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
	exceptions_dashboard_panel = Old_Dashboard_Panel(
														title = 'EXCEPTIONS: PARENTS',
														title_icon = 'glyphicon-warning-sign',
														column_names = ['counts'],
														label_width = 8,
														column_width = 3,
														right_margin = 1)
	# add the parents with no children row to the panel
	exceptions_dashboard_panel.rows.append(
											Old_Dashboard_Panel_Row(
																label = 'Parents with no children',
																values = [len(parents_with_no_children)],
																url = 'parents_with_no_children',
																parameter = 1
																)
											)
	# add the parents with no children under four row to the panel
	exceptions_dashboard_panel.rows.append(
											Old_Dashboard_Panel_Row(
																label = 'Parents with no children under four',
																values = [len(parents_with_no_children_under_four)],
																url = 'parents_without_children_under_four',
																parameter = 1
																)
											)
	# add the overdue parents row to the panel
	exceptions_dashboard_panel.rows.append(
											Old_Dashboard_Panel_Row(
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
											Old_Dashboard_Panel(
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
	events_dashboard_column = Old_Dashboard_Column(width=4)
	# get the event dashboard dates
	event_dashboard_dates = get_dashboard_dates()
	# set variables for convenience
	first_day_of_this_month = event_dashboard_dates['first_day_of_this_month']
	first_day_of_last_month = event_dashboard_dates['first_day_of_last_month']
	last_day_of_last_month = event_dashboard_dates['last_day_of_last_month']
	first_day_of_this_year = event_dashboard_dates['first_day_of_this_year']
	# add the this month event panel
	events_dashboard_column.panels.append(
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
											Old_Dashboard_Panel(
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
	geo_dashboard_column = Old_Dashboard_Column(width=4)
	# add the events in wards panel
	geo_dashboard_column.panels.append(
											Old_Dashboard_Panel(
															title = 'EVENTS IN WARD',
															title_icon = 'glyphicon-map-marker',
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
											Old_Dashboard_Panel(
															title = 'EVENTS IN AREA',
															title_icon = 'glyphicon-map-marker',
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
											Old_Dashboard_Panel(
															title = 'PEOPLE IN WARD',
															title_icon = 'glyphicon-map-marker',
															column_names = ['counts'],
															rows = get_wards_with_people_counts(),
															row_name = 'ward_name',
															row_url = 'ward',
															row_parameter_name='pk',
															row_values = ['count'],
															totals = True,
															label_width = 8,
															column_width = 3,
															right_margin = 1,
															)
											)
	# add the people in areas panel
	geo_dashboard_column.panels.append(
											Old_Dashboard_Panel(
															title = 'PEOPLE IN AREA',
															title_icon = 'glyphicon-map-marker',
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
	# return the dashboard
	return dashboard

# UTILITY FUNCTIONS
# A set of functions which perform basic utility tasks such as string handling and list editing

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

def remove_existing_registrations(event, people):
	# this function takes an and a list of people, and returns a list of only those events where
	# the person does not have an existing registration for that event
	# create an empty list
	people_without_existing_registrations = []
	# now got through the list
	for person in people:
		# attempt to get the residence
		if not Event_Registration.try_to_get(person=person,event=event):
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
	# set the defaults
	site_name = 'test site'
	navbar_background = ''
	navbar_text = ''
	show_messages = True
	dob_offset = 0
	# attempt to get the site
	site = Site.objects.all().first()
	# if we have a site, set the details
	if site:
		# set the details
		site_name = site.name
		navbar_background = site.navbar_background
		navbar_text = site.navbar_text
		show_messages = site.messages
		dob_offset = site.dob_offset
	# now set the dictionary
	context_dict['site_name'] = site_name
	context_dict['navbar_background'] = navbar_background
	context_dict['navbar_text'] = navbar_text
	context_dict['show_messages'] = show_messages
	# check whether we have a default date
	if not context_dict.get('default_date', False):
		# set the default date to the default
		context_dict['default_date'] = datetime.date.today().strftime('%d/%m/%Y')
	# check whether we have a date of birth
	if not context_dict.get('default_date_of_birth', False):
		# get today's date
		today = datetime.date.today()
		# set the date to 15 years ago
		default_date_of_birth = today.replace(year=today.year-dob_offset)
		# set the string for use in the page
		context_dict['default_date_of_birth'] = default_date_of_birth.strftime('%d/%m/%Y')
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
		date_dict['first_day_of_this_year'] = \
			date_dict['first_day_of_this_year'].replace(year=date_dict['first_day_of_this_year'].year-1)
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

def split_names(names):
	# split a name string into a first name and last name
	if ' ' in names:
		# split the name
		first_name, last_name = names.split(' ',1)
	# otherwise set the names
	else:
		# set the names
		first_name = names
		last_name = ''
	# return the results
	return first_name, last_name

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
	pages = []
	page_list = []
	# and zero search results
	number_of_people = 0
	this_page = 0
	search_attempted = False
	# and blank search terms
	names = ''
	keywords = ''
	role_type = 0
	ABSS_type = 0
	age_status = 0
	trained_role = 'none'
	ward = 0
	include_people = 'in_project'
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
			# set the flag to show that a search was attempted
			search_attempted = True
			# validate the form
			personsearchform.is_valid()
			# get the names
			names = personsearchform.cleaned_data['names']
			keywords = personsearchform.cleaned_data['keywords']
			role_type = personsearchform.cleaned_data['role_type']
			ABSS_type = personsearchform.cleaned_data['ABSS_type']
			age_status = personsearchform.cleaned_data['age_status']
			trained_role = personsearchform.cleaned_data['trained_role']
			ward = personsearchform.cleaned_data['ward']
			include_people = personsearchform.cleaned_data['include_people']
			# conduct a search
			people = Person.search(
									names=names,
									keywords=keywords,
									default_role_id=role_type,
									ABSS_type_id=ABSS_type,
									age_status_id=age_status,
									trained_role=trained_role,
									street__post_code__ward_id=ward,
									include_people=include_people
									).order_by('last_name','first_name')
			# figure out how many people we got
			number_of_people = len(people)
			# get the page number
			this_page = int(request.POST['page'])
			# figure out how many pages we have
			page_list = build_page_list(
										objects=people,
										page_length=results_per_page,
										attribute='last_name',
										length=3
										)
			# set the previous page
			previous_page = this_page - 1
			# sort and truncate the list of people
			people = people[previous_page*results_per_page:this_page*results_per_page]
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
				'this_page' : this_page,
				'names' : names,
				'keywords' : keywords,
				'role_type' : role_type,
				'ABSS_type' : ABSS_type,
				'age_status' : age_status,
				'trained_role' : trained_role,
				'ward' : ward,
				'include_people' : include_people,
				'search_error' : search_error,
				'number_of_people' : number_of_people,
				'search_attempted' : search_attempted
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
					'trained_role' : 'none',
					'ward' : '0'
					}
	# set the value based on the url
	form_values[resolve(request.path_info).url_name] = id
	# copy the request
	copy_POST = request.POST.copy()
	# set search terms for a people search
	copy_POST['action'] = 'search'
	copy_POST['role_type'] = form_values['role_type']
	copy_POST['names'] = ''
	copy_POST['ABSS_type'] = form_values['ABSS_type']
	copy_POST['age_status'] = form_values['age_status']
	copy_POST['trained_role'] = form_values['trained_role']
	copy_POST['ward'] = form_values['ward']
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
	# and a blank page_list
	page_list = []
	# set the results per page
	results_per_page = 25
	# get the page number
	page = int(page)
	# figure out how many pages we have
	page_list = build_page_list(
								objects=parents,
								page_length=results_per_page,
								attribute='last_name',
								length=3
								)
	# set the previous page
	previous_page = page - 1
	# sort and truncate the list of people
	parents = parents[previous_page*results_per_page:page*results_per_page]
	# set the context
	context = build_context({
				'parents' : parents,
				'children' : children,
				'page_list' : page_list,
				'this_page' : page
				})
	# return the HttpResponse
	return HttpResponse(exceptions_template.render(context=context, request=request))

@login_required
def age_exceptions(request, age_status_id=0):
	# load the template
	age_exceptions_template = loader.get_template('people/age_exceptions.html')
	# get the age status
	age_status = Age_Status.try_to_get(pk=age_status_id)
	# if the age status doesn't exist, crash to a banner
	if not age_status:
		return make_banner(request, 'Age status does not exist.')
	# get today's date
	today = datetime.date.today()
	# get the exceptions
	age_exceptions = age_status.person_set.filter(
							date_of_birth__lt=today.replace(year=today.year-age_status.maximum_age),
							ABSS_end_date__isnull=True).order_by('last_name','first_name')
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
										age_status_id = age_status
										)
				# set a success message
				messages.success(request,
									'Another ' + str(person) + ' created.'
									)
				# go to the profile of the person
				return redirect('/profile/' + str(person.pk))
		# otherwise see whether the person matches an existing person by name
		matching_people = Person.objects.filter(first_name=first_name,last_name=last_name)
		# if there aren't any matching people, also create the person
		if not matching_people:
			# create the person
			person = create_person(
									first_name = first_name,
									last_name = last_name,
									age_status_id = age_status
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
	person = Person.try_to_get(pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the relationships for the person
	relationships_to = get_relationships_to(person)
	# get the questions and the answer flag
	questions, answer_flag = get_questions_and_answers(person)
	# set the context from the person based on person id
	context = build_context({
				'person' : person,
				'relationships_to' : relationships_to,
				'registrations' : person.event_registration_set.order_by('-event__date'),
				'activities' : person.activity_set.order_by('-date'),
				'questions' : questions,
				'answer_flag' : answer_flag,
				'role_history' : person.role_history_set.all()
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def profile(request, person_id=0):
	# set the old role to false: this indicates that the role hasn't changed yet
	old_role = False
	# try to get the person
	person = Person.try_to_get(pk=person_id)
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
								other_names = profileform.cleaned_data['other_names'],
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
								membership_number = profileform.cleaned_data['membership_number']
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
						'other_names' : person.other_names,
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
						'notes' : person.notes,
						'membership_number' : person.membership_number
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

	# SUBFUNCTIONS TO PROCESS DIFFERENT ACTION TYPES
	# search function: searches on the basis of criteria suppied, and creates forms to add relationships
	# to the people found, and to create a new person if necessary
	def add_relationship_search(person,request):
		# initialise variables
		search_results = []
		addrelationshipform = ''
		addrelationshiptoexistingpersonform = ''
		# create a search form from the POST
		personsearchform = PersonNameSearchForm(request.POST)
		# validate the form
		if personsearchform.is_valid():
			# get the names
			names = personsearchform.cleaned_data['names']
			# and the flag of which people we include
			include_people = personsearchform.cleaned_data['include_people']
			# conduct a search
			people = Person.search(
									names=names,
									include_people=include_people
									)
			# remove the people who already have a relationship
			search_results = remove_existing_relationships(person, people)
			# if there are search results, and the names are not all numeric create a form to create 
			# relationships from the search results
			if search_results:
				addrelationshiptoexistingpersonform = AddRelationshipToExistingPersonForm(
														people=search_results,
														from_person=person
														)
				# go through the search results and add a field name to the object
				for result in search_results:
					result.field_name = 'relationship_type_' + str(result.pk)
			# get the first name and last name from the names search string
			first_name, last_name = split_names(names)
			# create a form to add the relationship unless we have just a membership number in the names
			if not all(map(str.isdigit,names)):
				addrelationshipform = AddRelationshipForm(
															person = person,
															first_name = first_name,
															last_name = last_name
															)
		# return the results
		return search_results, addrelationshiptoexistingpersonform, addrelationshipform

	# edit relationships function: goes through the form and updates the relationship if it has changed or is new
	def add_relationship_editrelationships(person,request):
		# go through the post
		for field_name, field_value in request.POST.items():
			# check whether this is a relevant field
			if field_name.startswith('relationship_type'):
				# try to find a person using the id at the end of the field name
				person_to = Person.try_to_get(pk=int(extract_id(field_name)))
				# if we got a person, edit the relationship
				if person_to:
					edit_relationship(request, person, person_to, int(field_value))
		# return - no results returned at the moment
		return

	# add relationship to new person function: creates the person if valid, and then indicates that we should
	# redirect to edit the page for that person
	def add_relationship_addrelationshiptonewperson(person,request):
		# initialise the variables
		person_to = False
		# create the form
		addrelationshipform = AddRelationshipForm(
													request.POST,
													person = person,
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
										age_status_id = addrelationshipform.cleaned_data['age_status']
										)
			# set a message to say that we have created a new person
			messages.success(request, str(person_to) + ' created.')
			# now create the relationship
			edit_relationship(request,person, person_to, addrelationshipform.cleaned_data['relationship_type'])
		# return the form and the result
		return addrelationshipform, person_to

	# MAIN VIEW LOGIC
	# initalise the forms which we might not need
	addrelationshipform = ''
	addrelationshiptoexistingpersonform = ''
	editexistingrelationshipsform = ''
	# load the template
	person_template = loader.get_template('people/add_relationship.html')
	# get the person
	person = Person.try_to_get(pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get existing relationships
	relationships_to = get_relationships_to(person)
	# set the search results
	search_results = []
	# set a blank search_error
	search_error = ''
	# create a blank search form
	personsearchform = PersonNameSearchForm()
	# check whether this is a post
	if request.method == 'POST':
		# check what type of submission we got
		if request.POST['action'] == 'search':
			search_results, addrelationshiptoexistingpersonform, addrelationshipform = \
				add_relationship_search(person,request)
		elif request.POST['action'] == 'editrelationships':
			add_relationship_editrelationships(person,request)
		elif request.POST['action'] == 'addrelationshiptonewperson':
			addrelationshipform, person_to = add_relationship_addrelationshiptonewperson(person,request)
			# redirect if we successfully created a new person
			if person_to:
				return redirect('/profile/' + str(person_to.pk))
	# update the existing relationships: there may be new ones
	relationships_to = get_relationships_to(person)
	# if there are existing relationships, create an edit form
	if relationships_to:
		# build the form
		editexistingrelationshipsform = EditExistingRelationshipsForm(
																		relationships=relationships_to,
																		from_person=person
																		)
		# and go through the relationships, adding the name of the select field and the hidden field
		for relationship_to in relationships_to:
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
	address_template = loader.get_template('people/address.html')
	# get the person
	person = Person.try_to_get(pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# set the search results
	search_results = []
	# and a blank page_list
	page_list = []
	page = 0
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
				search_results = Street.search(
												name__icontains=street,
												post_code__post_code__icontains=post_code
												).order_by('name')
				# figure out how many results we got
				search_number = len(search_results)
				# get the page number
				page = int(request.POST['page'])
				# figure out how many pages we have
				page_list = build_page_list(
								objects=search_results,
								page_length=results_per_page,
								attribute='name',
								length=3
								)
				# set the previous page
				previous_page = page - 1
				# sort and truncate the list of results
				search_results = search_results[previous_page*results_per_page:page*results_per_page]
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
				'this_page' : page,
				'house_name_or_number' : house_name_or_number,
				'street' : street,
				'post_code' : post_code
				})
	# return the response
	return HttpResponse(address_template.render(context=context, request=request))

@login_required
def address_to_relationships(request,person_id=0):
	# this view is used to set the address for a person, by searching on post code or street name
	# load the template
	person_template = loader.get_template('people/address_to_relationships.html')
	# get the person
	person = Person.try_to_get(pk=person_id)
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
def add_venue(request):
	# this view is used to create a venue
	# initialise variables
	add_venue_template = loader.get_template('people/add_venue.html')
	search_results = []
	page_list = []
	page = 0
	search_number = 0
	name = ''
	building_name_or_number = ''
	street = ''
	post_code = ''
	venue_type = ''
	venue_type_id = 0
	results_per_page = 25
	contact_name = ''
	phone = ''
	mobile_phone = ''
	email_address = ''
	website = ''
	price = ''
	facilities = ''
	opening_hours = ''
	# check whether this is a post
	if request.method == 'POST':
		# create a venue search form
		addvenueform = VenueForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] in ('search','create'):
			# validate the form
			if addvenueform.is_valid():
				# get the form details
				name = addvenueform.cleaned_data['name']
				venue_type_id = addvenueform.cleaned_data['venue_type']
				venue_type = Venue_Type.objects.get(id=venue_type_id)
				building_name_or_number = addvenueform.cleaned_data['building_name_or_number']
				street = addvenueform.cleaned_data['street']
				post_code = addvenueform.cleaned_data['post_code']
				contact_name = addvenueform.cleaned_data['contact_name']
				phone = addvenueform.cleaned_data['phone']
				mobile_phone = addvenueform.cleaned_data['mobile_phone']
				email_address = addvenueform.cleaned_data['email_address']
				website = addvenueform.cleaned_data['website']
				price = addvenueform.cleaned_data['price']
				facilities = addvenueform.cleaned_data['facilities']
				opening_hours = addvenueform.cleaned_data['opening_hours']
				# do the search if we have been asked to do a search
				if request.POST['action'] == 'search':
					# do the search
					search_results = Street.search(
													name__icontains=street,
													post_code__post_code__icontains=post_code
													).order_by('name')
					# do the pagination
					search_number = len(search_results)
					page = int(request.POST['page'])
					page_list = build_page_list(
									objects=search_results,
									page_length=results_per_page,
									attribute='name',
									length=3
									)
					previous_page = page - 1
					search_results = search_results[previous_page*results_per_page:page*results_per_page]
				# otherwise do the creation
				else:
					# get the other objects
					street = Street.objects.get(id=street)
					# create the object
					venue = Venue(
									name = name,
									venue_type = venue_type,
									street = street,
									building_name_or_number = building_name_or_number,
									contact_name = contact_name,
									phone = phone,
									mobile_phone = mobile_phone,
									email_address = email_address,
									website = website,
									price = price,
									facilities = facilities,
									opening_hours = opening_hours
									)
					# and save it
					venue.save()
					# and redirect to the venue page
					return redirect('/venue/' + str(venue.pk))
	# otherwise we didn't get a post
	else:
		# create a blank form
		addvenueform = VenueForm()
	# set the context from the person based on person id
	context = build_context({
				'addvenuesearchform' : addvenueform,
				'search_results' : search_results,
				'search_number' : search_number,
				'page_list' : page_list,
				'this_page' : page,
				'name' : name,
				'venue_type' : venue_type,
				'building_name_or_number' : building_name_or_number,
				'street' : street,
				'post_code' : post_code,
				'contact_name' : contact_name,
				'phone' : phone,
				'mobile_phone' : mobile_phone,
				'email_address' : email_address,
				'website' : website,
				'price' : price,
				'facilities' : facilities,
				'opening_hours' : opening_hours
				})
	# return the response
	return HttpResponse(add_venue_template.render(context=context, request=request))

@login_required
def edit_venue(request, venue_id=0):
	# this view is used to edit a venue
	# try to get the venue, crashing to a banner if unsuccessful
	venue = Venue.try_to_get(pk=venue_id)
	if not venue:
		return make_banner(request, 'Venue does not exist.')
	# initialise variables
	edit_venue_template = loader.get_template('people/edit_venue.html')
	search_results = []
	page_list = []
	page = 0
	search_number = 0
	name = venue.name
	building_name_or_number = venue.building_name_or_number
	street = venue.street.name
	post_code = venue.street.post_code.post_code
	venue_type = venue.venue_type
	contact_name = venue.contact_name
	phone = venue.phone
	mobile_phone = venue.mobile_phone
	email_address = venue.email_address
	website = venue.website
	price = venue.price
	facilities = venue.facilities
	opening_hours = venue.opening_hours
	venue_id = venue.pk
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a venue search form
		editvenueform = VenueForm(request.POST, venue_id=venue_id)
		# validate the form
		if editvenueform.is_valid():
			# get the form details
			name = editvenueform.cleaned_data['name']
			venue_type_id = editvenueform.cleaned_data['venue_type']
			venue_type = Venue_Type.objects.get(id=venue_type_id)
			building_name_or_number = editvenueform.cleaned_data['building_name_or_number']
			street = editvenueform.cleaned_data['street']
			post_code = editvenueform.cleaned_data['post_code']
			contact_name = editvenueform.cleaned_data['contact_name']
			phone = editvenueform.cleaned_data['phone']
			mobile_phone = editvenueform.cleaned_data['mobile_phone']
			email_address = editvenueform.cleaned_data['email_address']
			website = editvenueform.cleaned_data['website']
			price = editvenueform.cleaned_data['price']
			facilities = editvenueform.cleaned_data['facilities']
			opening_hours = editvenueform.cleaned_data['opening_hours']
			# do the search if the street or post code have changed
			if (request.POST['action'] == 'search' and 
					(street != venue.street.name or post_code != venue.street.post_code.post_code)):
				# do the search
				search_results = Street.search(
												name__icontains=street,
												post_code__post_code__icontains=post_code
												).order_by('name')
				# do the pagination
				search_number = len(search_results)
				page = int(request.POST['page'])
				page_list = build_page_list(
								objects=search_results,
								page_length=results_per_page,
								attribute='name',
								length=3
								)
				previous_page = page - 1
				search_results = search_results[previous_page*results_per_page:page*results_per_page]
			# otherwise do the update
			else:
				venue.name = name
				venue.venue_type = venue_type
				venue.building_name_or_number = building_name_or_number
				venue.street = Street.objects.get(id=street) if request.POST['action'] == 'update_address' \
																else venue.street
				venue.contact_name = contact_name
				venue.phone = phone
				venue.mobile_phone = mobile_phone
				venue.email_address = email_address
				venue.website = website
				venue.price = price
				venue.facilities = facilities
				venue.opening_hours = opening_hours
				venue.save()
				# and redirect to the venue page
				return redirect('/venue/' + str(venue.pk))
	# otherwise we didn't get a post
	else:
		# create a form initialised from the record
		editvenueform = VenueForm(
										{
											'name' : name,
											'venue_type' : venue_type.pk,
											'building_name_or_number' : building_name_or_number,
											'street' : street,
											'post_code' : post_code,
											'contact_name' : contact_name,
											'phone' : phone,
											'mobile_phone' : mobile_phone,
											'email_address' : email_address,
											'website' : website,
											'price' : price,
											'facilities' : facilities,
											'opening_hours' : opening_hours
										},
										venue_id = venue.pk
									)
	# set the context from the person based on person id
	context = build_context({
				'editvenueform' : editvenueform,
				'search_results' : search_results,
				'search_number' : search_number,
				'page_list' : page_list,
				'this_page' : page,
				'venue' : venue,
				'name' : name,
				'venue_type' : venue_type,
				'building_name_or_number' : building_name_or_number,
				'street' : street,
				'post_code' : post_code,
				'contact_name' : contact_name,
				'phone' : phone,
				'mobile_phone' : mobile_phone,
				'email_address' : email_address,
				'website' : website,
				'price' : price,
				'facilities' : facilities,
				'opening_hours' : opening_hours
				})
	# return the response
	return HttpResponse(edit_venue_template.render(context=context, request=request))

@login_required
def venue(request, venue_id=0):
	# load the template
	venue_template = loader.get_template('people/venue.html')
	# try to get the venue, crashing to a banner if unsuccessful
	venue = Venue.try_to_get(pk=venue_id)
	if not venue:
		return make_banner(request, 'Venue does not exist.')
	# get the additional data
	# TODO: get events
	# set the context
	context = build_context({
				'venue' : venue,
				'events' : venue.event_set.all()
				})
	# return the response
	return HttpResponse(venue_template.render(context=context, request=request))

@login_required
def venues(request):
	# this view searches for venues and displays a list
	# initialise variables
	venues = []
	pages = []
	page_list = []
	number_of_venues = 0
	this_page = 0
	search_attempted = False
	name = ''
	ward = 0
	area = 0
	venue_type = 0
	# set a blank search_error
	search_error = ''
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		venuesearchform = VenueSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# set the flag to show that a search was attempted
			search_attempted = True
			# validate the form
			venuesearchform.is_valid()
			# get the search terms
			name = venuesearchform.cleaned_data['name']
			ward = venuesearchform.cleaned_data['ward']
			area = venuesearchform.cleaned_data['area']
			venue_type = venuesearchform.cleaned_data['venue_type']
			# conduct a search
			venues = Venue.search(
									name__icontains=name,
									street__post_code__ward_id=ward,
									street__post_code__ward__area_id=area,
									venue_type_id=venue_type
									).order_by('name')
			# figure out how many people we got
			number_of_venues = len(venues)
			# do the pagination
			this_page = int(request.POST['page'])
			page_list = build_page_list(
										objects=venues,
										page_length=results_per_page,
										attribute='name',
										length=3
										)
			previous_page = this_page - 1
			venues = venues[previous_page*results_per_page:this_page*results_per_page]
	# otherwise set a bank form
	else:
		venuesearchform = VenueSearchForm()
	# get the template
	venues_template = loader.get_template('people/venues.html')
	# set the context
	context = build_context({
				'venuesearchform' : venuesearchform,
				'venues' : venues,
				'page_list' : page_list,
				'this_page' : this_page,
				'name' : name,
				'ward' : ward,
				'area' : area,
				'venue_type' : venue_type,
				'number_of_venues' : number_of_venues,
				'search_attempted' : search_attempted
				})
	# return the HttpResponse
	return HttpResponse(venues_template.render(context=context, request=request))

@login_required
def addevent(request):
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
								venue = addeventform.cleaned_data['venue'],
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
	event = Event.try_to_get(pk=event_id)
	# if the event doesn't exist, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# get the registrations for the event
	registrations = event.event_registration_set.all().order_by('person__last_name','person__first_name')
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
	venue = 0
	# get the calling url
	path = request.get_full_path()
	# set the grouping based on the path
	if 'type' in path:
		event_type = event_group
	elif 'category' in path:
		event_category = event_group
	elif 'ward' in path:
		ward = event_group
	# get the dashboard dates
	dashboard_dates = get_dashboard_dates()
	# set blank dates
	date_from = ''
	date_to = ''
	# set the dates, dependent on the url
	if 'this_month' in path:
		date_from = dashboard_dates['first_day_of_this_month'].strftime('%d/%m/%Y')
	elif 'last_month' in path:
		date_from = dashboard_dates['first_day_of_last_month'].strftime('%d/%m/%Y')
		date_to = dashboard_dates['last_day_of_last_month'].strftime('%d/%m/%Y')
	elif 'this_year' in path:
		date_from = dashboard_dates['first_day_of_this_year'].strftime('%d/%m/%Y')
	# copy the request
	copy_POST = request.POST.copy()
	# set search terms for an event search
	copy_POST['action'] = 'search'
	copy_POST['event_type'] = event_type
	copy_POST['event_category'] = event_category
	copy_POST['ward'] = ward
	copy_POST['venue'] = venue
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
	page = 0
	# and blank search terms
	name = ''
	event_type = 0
	event_category = 0
	date_from = 0
	date_to = 0
	ward = 0
	venue = 0
	search_attempted = False
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
			# set the flag to show that a search was attempted
			search_attempted = True
			# validate the form
			if eventsearchform.is_valid():
				# get the values
				name = eventsearchform.cleaned_data['name']
				date_from = eventsearchform.cleaned_data['date_from']
				date_to = eventsearchform.cleaned_data['date_to']
				event_type = eventsearchform.cleaned_data['event_type']
				event_category = eventsearchform.cleaned_data['event_category']
				ward = eventsearchform.cleaned_data['ward']
				venue = eventsearchform.cleaned_data['venue']
				# conduct a search
				events = Event.search(
										name__icontains=name,
										date__gte=date_from,
										date__lte=date_to,
										event_type_id=int(event_type),
										event_type__event_category_id=int(event_category),
										ward=int(ward),
										venue=int(venue)
										).order_by('-date')
				# set the number of results
				number_of_events = len(events)
				# get the page number
				page = int(request.POST['page'])
				# figure out how many pages we have
				page_list = build_page_list(
										objects=events,
										page_length=results_per_page,
										attribute='date',
										)
				# set the previous page
				previous_page = page - 1
				# sort and truncate the list of events
				events = events[previous_page*results_per_page:page*results_per_page]
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
				'venue' : venue,
				'date_from' : date_from,
				'date_to' : date_to,
				'page_list' : page_list,
				'search_error' : search_error,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y'),
				'number_of_events' : number_of_events,
				'this_page' : page,
				'search_attempted' : search_attempted
				})
	# return the HttpResponse
	return HttpResponse(events_template.render(context=context, request=request))

@login_required
def edit_event(request, event_id=0):
	# try to get the event
	event = Event.try_to_get(pk=event_id)
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
			# validate the event type, crashing to a banner if it doesn't exist
			event_type = Event_Type.try_to_get(pk=editeventform.cleaned_data['event_type'])
			if event_type:
				event.event_type = event_type
			else:
				return make_banner(request, 'Event type does not exist.')
			# validate the ward, crashing to a banner if it doesn't exist
			ward_id = editeventform.cleaned_data['ward']
			event.ward = Ward.try_to_get(pk=ward_id) if ward_id != '0' else None
			"""
			ward_id = editeventform.cleaned_data['ward']
			if ward_id != '0':
				ward = Ward.try_to_get(pk=ward_id)
				if ward:
					event.ward = ward
				else:
					return make_banner(request, 'Ward does not exist.')
			else:
				event.ward = None
			"""
			# get and set the venue
			venue_id = editeventform.cleaned_data['venue']
			if venue_id != '0':
				venue = Venue.try_to_get(pk=venue_id)
				if venue:
					event.venue = venue
				else:
					return make_banner(request, 'Venue does not exist.')
			else:
				event.venue = None
			# save the record
			event.save()
			# set a success message
			messages.success(request, str(event) + ' updated.')
			# get the dictionary
			area_dict = build_event_area_dict(editeventform.cleaned_data)
			# go through the areas, removing unchecked areas and adding checked areas
			for area_id in area_dict.keys():
				if not area_dict[area_id] and event.areas.filter(pk=area_id).exists():
					event.areas.remove(Area.objects.get(pk=area_id))
				if area_dict[area_id] or (event.ward and area_id == event.ward.area.pk):
					event.areas.add(Area.objects.get(pk=area_id))
			# send the user back to the main event page
			return redirect('/event/' + str(event.pk))
	else:
		# set the values for optional relationships
		ward_id = event.ward.pk if event.ward else 0
		venue_id = event.venue.pk if event.venue else 0
		# there is an event, so build a dictionary of initial values we want to set
		event_dict = {
						'name' : event.name,
						'description' : event.description,
						'location' : event.location,
						'ward' : ward_id,
						'venue' : venue_id,
						'date' : event.date,
						'start_time' : event.start_time,
						'end_time' : event.end_time,
						'event_type' : event.event_type.pk
						}
		# build the values for the areas
		for area in Area.objects.all():
			available_in_area = False
			if area in event.areas.all():
				available_in_area = True
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

	# SUBFUNCTIONS TO HANDLE ACTION TYPES
	def event_registration_search(event,request):
		# process the search
		# initialise variables
		search_keys = ''
		search_key_delimiter = ''
		addregistrationform = ''
		addpersonandregistrationform = ''
		# create a search form
		personsearchform = PersonNameSearchForm(request.POST)
		# validate the form
		if personsearchform.is_valid():
			# get the values from the form
			names = personsearchform.cleaned_data['names']
			include_people = personsearchform.cleaned_data['include_people']
			# conduct a search
			people = Person.search(
									names = names,
									include_people = include_people
									)
			# remove the people who already have a registration
			search_results = remove_existing_registrations(event, people)
			# if there are search results, create a form to create relationships from the search results
			if search_results:
				# create the form to add registrations
				addregistrationform = AddRegistrationForm(people=search_results)
			# add field names to each result, so that we know when to display them
			for result in search_results:
				# add the three field names
				result.role_type_field_name = 'role_type_' + str(result.pk)
				result.registered_field_name = 'registered_' + str(result.pk)
				result.apologies_field_name = 'apologies_' + str(result.pk)
				result.participated_field_name = 'participated_' + str(result.pk)
				# add the key of the search result to the string of keys
				search_keys += search_key_delimiter + str(result.pk)
				# and set the delimiter
				search_key_delimiter = ','
			# create the form to add a person and register that person if we have names
			if names:
				# get the first name and last name from the names search string
				first_name, last_name = split_names(names)
				# create a form to add the relationship
				addpersonandregistrationform = AddPersonAndRegistrationForm(
																			first_name = first_name,
																			last_name = last_name
																			)
		# return the forms and results
		return personsearchform, addregistrationform, addpersonandregistrationform, search_results, search_keys

	def event_registration_addregistration(event,request):
		# process the addition of registrations
		# get the list of search keys from the hidden field
		search_keys = request.POST['search_keys'].split(',')
		# go through the search keys
		for search_key in search_keys:
			# get the indicators of whether the person registered or participated, as well as the role type
			registered = check_checkbox(request.POST, 'registered_' + search_key)
			apologies = check_checkbox(request.POST, 'apologies_' + search_key)
			participated = check_checkbox(request.POST, 'participated_' + search_key)
			role_type_id = request.POST.get('role_type_' + search_key, False)
			# if the person participated or registered, we need to build a registration
			if registered or participated or apologies:
				# build the registration
				registration = build_registration(
													request = request,
													event = event,
													person_id = int(search_key),
													registered = registered,
													apologies = apologies,
													participated = participated,
													role_type_id = int(role_type_id)
													)

	def event_registration_editregistration(event,request):
		# get the list of registration keys from the hidden field
		registration_keys = request.POST['registration_keys'].split(',')
		# go through the keys
		for registration_key in registration_keys:
			# get the indicators of whether the person registered or participated, as well as the role type
			registered = check_checkbox(request.POST, 'registered_' + registration_key)
			apologies = check_checkbox(request.POST, 'apologies_' + registration_key)
			participated = check_checkbox(request.POST, 'participated_' + registration_key)
			role_type_id = request.POST.get('role_type_' + registration_key, False)
			# if the person participated or registered, we need to build a registration
			if registered or participated or apologies:
				# build the registration
				registration = build_registration(
													request = request,
													event = event,
													person_id = int(registration_key),
													registered = registered,
													apologies = apologies,
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

	def event_registration_registrations(event):
		# initialise variables
		registration_keys = ''
		registration_key_delimiter = ''
		editregistrationform = ''
		# update the existing registrations: there may be new ones
		registrations = event.event_registration_set.all()
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
				registration.apologies_field_name = 'apologies_' + str(registration.person.pk)
				registration.participated_field_name = 'participated_' + str(registration.person.pk)
				# add the key of the registered person to the string of keys
				registration_keys += registration_key_delimiter + str(registration.person.pk)
				# and set the delimiter
				registration_key_delimiter = ','
		# return the results
		return registrations, registration_keys, editregistrationform

	def event_registration_addpersonandregistration(event,request):
		# process the request to add a person and register them to this event
		# create a form
		addpersonandregistrationform = AddPersonAndRegistrationForm(request.POST)
		# validate the form
		if addpersonandregistrationform.is_valid():
			# create the person
			# we now need to create the person
			person = create_person(
									first_name = addpersonandregistrationform.cleaned_data['first_name'],
									last_name = addpersonandregistrationform.cleaned_data['last_name'],
									age_status_id = addpersonandregistrationform.cleaned_data['age_status']
									)
			# set a message to say that we have create a new person
			messages.success(request, str(person) + ' created.')
			# now build the registration
			registration = build_registration(
											request = request,
											event = event,
											person_id = person.pk,
											registered = addpersonandregistrationform.cleaned_data['registered'],
											apologies = addpersonandregistrationform.cleaned_data['apologies'],
											participated = addpersonandregistrationform.cleaned_data['participated'],
											role_type_id = addpersonandregistrationform.cleaned_data['role_type']
											)
			# blank out the form
			addpersonandregistrationform = ''
		# return the result
		return addpersonandregistrationform

	# MAIN VIEW PROCESSING
	# get the event
	event = Event.try_to_get(pk=event_id)
	# if the event doesn't exist, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# load the template
	event_registration_template = loader.get_template('people/event_registration.html')
	# initialise variables
	search_results = []
	search_keys = ''
	search_error = ''
	search_attempted = False
	# initalise forms
	addregistrationform = ''
	addpersonandregistrationform = ''
	personsearchform = PersonNameSearchForm()
	# check whether this is a post
	if request.method == 'POST':
		# process the POST depending on the action field:
		# search returns search results and builds the forms necessary to add and edit registrations
		# addregistration processes registration of new people for the event
		# editregistration processes changes to registration for existing people for the event
		if request.POST['action'] == 'search':
			personsearchform, addregistrationform, addpersonandregistrationform, search_results, search_keys = \
			event_registration_search(event,request)
			search_attempted = True
		elif request.POST['action'] == 'addregistration':
			event_registration_addregistration(event,request)
		elif request.POST['action'] == 'editregistration':
			event_registration_editregistration(event,request)
		elif request.POST['action'] == 'addpersonandregistration':
			addpersonandregistrationform = event_registration_addpersonandregistration(event,request)
	# build the form to edit registrations, along with an enriched list of existing registrations
	registrations, registration_keys, editregistrationform = event_registration_registrations(event)
	# set the context from the person based on person id
	context = build_context({
				'personsearchform' : personsearchform,
				'addregistrationform' : addregistrationform,
				'editregistrationform' : editregistrationform,
				'addpersonandregistrationform' : addpersonandregistrationform,
				'search_results' : search_results,
				'search_keys' : search_keys,
				'search_error' : search_error,
				'search_number' : len(search_results),
				'event' : event,
				'registrations' : registrations,
				'registration_keys' : registration_keys,
				'search_attempted' : search_attempted
				})
	# return the response
	return HttpResponse(event_registration_template.render(context=context, request=request))

@login_required
def answer_questions(request,person_id=0):
	# this view enables people to answer a dynamic set of questions from the database
	# load the template
	answer_questions_template = loader.get_template('people/answer_questions.html')
	# get the person
	person = Person.try_to_get(pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the questions, with the answers included as an attribute
	questions, answer_flag = get_questions_and_answers(person)
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
							'Activity Types' : {'file_class' : Activity_Type, 'field_name' : 'name'},
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
						'Relationships' : Relationships_File_Handler,
						'Events' : Events_File_Handler,
						'Registrations' : Registrations_File_Handler,
						'Questions' : Questions_File_Handler,
						'Options' : Options_File_Handler,
						'Answers' : Answers_File_Handler,
						'Answer Notes' : Answer_Notes_File_Handler,
						'Activities' : Activities_File_Handler,
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
	# define the records that need more complex file handlers
	file_handlers = {
						'People' : People_File_Handler,
						'Relationships' : Relationships_File_Handler,
						'Events' : Events_File_Handler,
						'Registrations' : Registrations_File_Handler,
						'Questions' : Questions_File_Handler,
						'Options' : Options_File_Handler,
						'Answers' : Answers_File_Handler,
						'Answer Notes' : Answer_Notes_File_Handler,
						'Activities' : Activities_File_Handler,
						'Event Summary' : Event_Summary_File_Handler,
					}
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		downloaddataform = DownloadDataForm(request.POST)
		# check whether the form is valid
		if downloaddataform.is_valid():
			# get the file type
			file_type = downloaddataform.cleaned_data['file_type']
			# get the file handler
			file_handler = file_handlers[file_type]()
			# and the keys
			fields = file_handler.fields
			# handle the download
			file_handler.handle_download()
			# get the records
			records = file_handler.download_records
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
				})
	# return the HttpResponse
	return HttpResponse(download_data_template.render(context=context, request=request))

@login_required
def activities(request,person_id=0):
	# allow the user to add or edit an activity for a person
	# load the template
	activities_template = loader.get_template('people/activities.html')
	# get the person
	person = Person.try_to_get(pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# check whether this is a post
	if request.method == 'POST':
		# create a form from the POST
		activityform = ActivityForm(request.POST)
		# validate the form
		if activityform.is_valid():
			# build the activity
			activity = build_activity(
										request,
										person = person,
										activity_type_id = activityform.cleaned_data['activity_type'],
										date = activityform.cleaned_data['date'],
										hours = activityform.cleaned_data['hours'],
										)
	else:
		# create a blank form
		activityform = ActivityForm()
	# set the context from the person based on person id
	context = build_context({
				'activityform' : activityform,
				'activities' : person.activity_set.order_by('-date'),
				'person' : person,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y')
				})
	# return the response
	return HttpResponse(activities_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def alpha_graph_dashboard(request):
	# create the list of charts
	charts = []
	# create the chart
	roles_chart = Chart(
						'Roles',
						queryset = get_role_types_with_people_counts(),
						label_attr = 'role_type_name',
						size_attr = 'count'
						)
	# build the chart
	figure, axes = plt.subplots()
	# build a pie chart
	axes.pie(roles_chart.sizes, labels=roles_chart.labels, autopct='%1.1f%%', startangle=90)
	# make the axes equal
	axes.axis('equal')
	# set the title
	plt.title(roles_chart.title)
	# and append to the list of charts
	charts.append(mpld3.fig_to_html(figure))
	# get the template
	dashboard_template = loader.get_template('people/dashboard.html')
	# set the context
	context = build_context({
				'charts' : charts
				})
	# return the HttpResponse
	return HttpResponse(dashboard_template.render(context=context, request=request))

@login_required
def dashboard(request,name=''):
	# initialise the variables
	dashboard = False
	dashboards = False
	# if we have a dashboard name, attempt to get the dashboard
	if name:
		dashboard = Dashboard.try_to_get(name=name)
		index_template = loader.get_template('people/dashboard.html')
	# if we don't have a dashboard, get the list of dashboards
	if not dashboard:
		dashboards = Dashboard.objects.all().order_by('title')
		index_template = loader.get_template('people/dashboards.html')
		# if the user is not a superuser, exclude all non-live dashboards
		if not request.user.is_superuser:
			dashboards = dashboards.exclude(live=False)
	# set the context
	context = build_context({
								'dashboard' : dashboard,
								'dashboards' : dashboards,
								'show_title' : True
								})
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))


