from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note, Site, Activity_Type, Activity, Dashboard, \
					Venue_Type, Venue, Invitation, Invitation_Step, Invitation_Step_Type, Profile, Chart, \
					Filter_Spec, Registration_Form, Printform_Data_Type, Printform_Data, Document_Link, Column, \
					Project, Membership, Membership_Type, Project_Permission, Project_Event_Type, \
					Question_Section, Case_Notes, Survey, Survey_Submission, Survey_Question_Type, \
					Survey_Question, Survey_Answer, Survey_Section, Survey_Series
import os
import csv
import copy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .forms import AddPersonForm, ProfileForm, PersonSearchForm, AddRelationshipForm, \
					AddRelationshipToExistingPersonForm, EditExistingRelationshipsForm, \
					AddAddressForm, AddressSearchForm, AddRegistrationForm, \
					EditRegistrationForm, LoginForm, EventSearchForm, EventForm, PersonNameSearchForm, \
					AnswerQuestionsForm, UpdateAddressForm, AddressToRelationshipsForm, UploadDataForm, \
					DownloadDataForm, PersonRelationshipSearchForm, ActivityForm, AddPersonAndRegistrationForm, \
					VenueForm, VenueSearchForm, ChangePasswordForm, ForgotPasswordForm, \
					ResetForgottenPasswordForm, DashboardDatesForm, SelectProjectForm, \
					ManageMembershipSearchForm, ManageProjectEventsSearchForm, CaseNotesForm, \
					SurveySeriesForm, SurveyForm, SurveySectionForm, SurveyQuestionForm, SubmitSurveyForm, \
					ResolveAgeExceptionsForm, TrainedRolesForm
from .utilities import get_page_list, make_banner, extract_id, build_page_list, Page, get_period_dates
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
							Event_Summary_File_Handler, Events_And_Registrations_File_Handler, \
							Venues_File_Handler, Venues_For_Events_File_Handler, People_Limited_Data_File_Handler, \
							Survey_Submissions_File_Handler
from .invitation_handlers import Terms_And_Conditions_Invitation_Handler, Personal_Details_Invitation_Handler, \
									Address_Invitation_Handler, Children_Invitation_Handler, \
									Questions_Invitation_Handler, Introduction_Invitation_Handler, \
									Signature_Invitation_Handler
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice
from django.utils import timezone
import qrcode
import qrcode.image.svg
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
import io
from jsignature.utils import draw_signature
from django.contrib.staticfiles import finders
from django.views.generic import ListView
from django.core import serializers
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

@login_required
def index(request):
	# get the template
	index_template = loader.get_template('people/dashboard.html')
	# if we have a dashboard for the site, load that, otherwise use the default dashboard
	site = Site.objects.all().first()
	if site:
		if site.dashboard:
			dashboard = site.dashboard
		else:
			# build a default dashboard and save it to the site
			dashboard = Dashboard.build_default_dashboard()
			site.dashboard = dashboard
			site.save()
	else:
		dashboard = Dashboard.try_to_get(name='default_dashboard')
		if not dashboard:
			dashboard = Dashboard.build_default_dashboard()
	# set the dummy dates and add the request
	dashboard.start_date = False
	dashboard.end_date = False
	dashboard.request = request
	# set the context
	context = build_context(request,{
								'dashboard' : dashboard,
								'show_title' : False
								})
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

# DATA ACCESS FUNCTIONS
# A set of functions which carry out simple and complex data access, filtering and updates.
# These functions are kept as simple as possible.

def get_relationships_to(person,project):
	# this function gets all the Person objects via the relationship_to relationship from Person
	# it returns a list of people with realtionship type added
	# get the relationships from a person, filtered by project if we have one
	if project:
		relationships = person.rel_from.filter(relationship_to__projects=project)
	else:
		relationships = person.rel_from.all()
	# set an empty list
	relationships_to = []
	# now go through the list and get the person
	for relationship in relationships:
		# get the person
		person = relationship.relationship_to
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

def get_relationships_from(person,project):
	# get the relationships from a person, filtered by project if we have one
	if project:
		return person.rel_from.filter(relationship_to__projects=project)
	else:
		return person.rel_from.all()

def get_trained_status(person,role_type):
	# determine whether a person is trained to perform this role and whether they are active
	trained_role = Trained_Role.try_to_get(person=person,role_type=role_type)
	# set the value depending on the status
	if not trained_role:
		trained_status = 'none'
	elif not trained_role.active:
		trained_status = 'trained'
	else:
		trained_status = 'active'
	# return the result
	return trained_status

def get_trained_date(person,role_type):
	# determine the trained date for a person if they are trained in this role
	trained_role = Trained_Role.try_to_get(person=person,role_type=role_type)
	if trained_role:
		return trained_role.date_trained
	else:
		return None

def get_parents_without_children(request):
	# initialise variables, including today's date and four year old date
	parents_with_no_children = []
	parents_with_no_children_under_four = []
	today = datetime.date.today()
	today_four_years_ago = today.replace(year=today.year-4)
	# attempt to get parents with no children
	parents = Person.search(
							project=Project.current_project(request.session),
							default_role__role_type_name__contains='Parent'
							)
	parents = parents.order_by('last_name','first_name')
	# now exclude those where we can find a child relationship
	for parent in parents:
		parent_relationships = parent.rel_from.filter(relationship_type__relationship_type='parent')
		if not parent_relationships:
			parents_with_no_children.append(parent)
		# otherwise check how old the children are
		else:
			child_under_four = False
			for relationship in parent_relationships:
				if relationship.relationship_to.date_of_birth != None:
					if relationship.relationship_to.date_of_birth >= today_four_years_ago:
						child_under_four = True
			if not child_under_four:
				parents_with_no_children_under_four.append(parent)
	# return the results
	return parents_with_no_children, parents_with_no_children_under_four

def get_streets_by_name_and_post_code(name='',post_code=''):
	# get the streets
	streets = Street.objects.all()
	# if there is a name, filter by name
	if name:
		streets = streets.filter(name__icontains=name)
	# if there is a post code, filter by post code
	if post_code:
		streets = streets.filter(post_code__post_code__icontains=post_code)
	# return the results
	return streets

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
			event_registrations = event_registrations.filter(event__date__gte=date_from)
			event_participations = event_participations.filter(event__date__gte=date_from)
		# if we have a before date, filter further
		if date_to:
			event_registrations = event_registrations.filter(event__date__lte=date_to)
			event_participations = event_participations.filter(event__date__lte=date_to)
		# set the counts
		event_category.registered_count = event_registrations.count()
		event_category.participated_count = event_participations.count()
	# return the results
	return event_categories

def get_role_types(events_or_people='all'):
	# get a list of the role type objects
	role_types = Role_Type.objects.all().order_by('role_type_name')
	if events_or_people == 'events':
		role_types.filter(use_for_events=True)
	elif events_or_people == 'people':
		role_types.filter(use_for_events=True)
	# return the results
	return role_types

def get_relationship(person_from, person_to):
	# try to get a relationship
	try:
		relationship = Relationship.objects.get(
												relationship_from=person_from.pk,
												relationship_to=person_to.pk
												)
	except Relationship.DoesNotExist:
		relationship = False
	# return the value
	return relationship

def get_relationship_from_and_to(person_from, person_to):
	# get both sides of a relationship
	relationship_from = get_relationship(person_from, person_to)
	relationship_to = get_relationship(person_to, person_from)
	# return the results
	return relationship_from, relationship_to

def get_question_sections_and_answers(person,project=None):
	# this function gets a list of questions, and adds the answers relevant to the person
	# set the flag to false to show whether we have answers for this person
	answer_flag = False
	question_sections = []
	mutliples_flag = False
	# get all the sections, add the questions, and then add the section to the list
	for question_section in Question_Section.objects.all().order_by('order'):
		question_section.questions = question_section.question_set.all().order_by('order')
		question_section.answers = False
		question_sections.append(question_section)
	# now add the questions that don't belong to a section to an empty section
	other_section = Question_Section(name='Other')
	other_section.questions = Question.objects.filter(question_section=None).order_by('order')
	other_section.answers = False
	question_sections.append(other_section)
	# now go through the sections again, filtering the questions by project and adding answers
	for question_section in question_sections:
		if project:
			question_section.questions = question_section.questions.filter(projects=None) | \
											question_section.questions.filter(projects=project)
		# get the options for each question
		for question in question_section.questions:
			# set defaults
			question.answer = 0
			question.answer_text = 'No answer'
			question.note = ''
			# get the options and stash them in the object
			question.options = question.option_set.all().order_by('option_label')
			# add the answer, if we already have one
			answer,message,multiples = Answer.try_to_get_just_one(
																	person=person,
																	question=question
																	)
			# procss a valid answer
			if answer:
				question.answer = answer.option.pk
				question.answer_text = answer.option.option_label
				answer_flag = True
				question_section.answers = True
			# deal with multiple answers for the same question
			elif multiples:
				question.answer = True
				answer_flag = True
				question_section.answers = True
				# build a string of answers
				answer_text_list = []
				for answer in Answer.objects.filter(person=person,question=question):
					answer_text_list.append(answer.option.option_label)
				question.answer_text = ' / '.join(answer_text_list)
			question.multiples = multiples
			# add notes, if we already have them 
			answer_note = Answer_Note.try_to_get(
												person=person,
												question=question
												)
			if answer_note:
				question.note = answer_note.notes
				answer_flag = True
				question_section.answers = True
	# return the results
	return question_sections, answer_flag

def create_person(
					request,
					first_name,
					last_name,
					middle_names='',
					age_status_id=0,
					):
	# attempt to get a project
	project = Project.current_project(request.session)
	# get the age status, defaulting to Adult if not supplied
	if not age_status_id:
		age_status = Age_Status.objects.get(status='Adult')
	else:
		age_status = Age_Status.try_to_get(pk=age_status_id)
	# and the default role for the age status
	default_role = age_status.default_role_type
	# handle ABSS if we don't have a project
	ABSS_type = ABSS_Type.objects.get(default=True)
	membership_type = Membership_Type.objects.get(default=True) if project else None
	# and get a membership if the ABSS type or project membership needs it, otherwise set it to zero
	if ABSS_type.membership_number_required or (membership_type and membership_type.membership_number_required):
		membership_number = Person.get_next_membership_number()
	else:
		membership_number = 0
	# create a person
	person = Person(
					first_name = first_name,
					middle_names = middle_names,
					last_name = last_name,
					default_role = default_role,
					ethnicity = Ethnicity.objects.get(default=True),
					age_status = age_status,
					ABSS_type = ABSS_type,
					membership_number = membership_number
						)
	person.save()
	# create the role history
	role_history = Role_History(
								person = person,
								role_type = default_role)
	role_history.save()
	# add the person to the current project through the membership, if we have a project
	if project:
		membership = Membership(
								person=person,
								project=project,
								membership_type=membership_type
								)
		membership.save()
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

def get_device(user):
	# get the device if the user has one, otherwise create a device
	try:
		device = TOTPDevice.objects.get(user=user)
	except (TOTPDevice.DoesNotExist):
		device = TOTPDevice.objects.create(
											user=user,
											name=user.username + ' device',
											tolerance=6,
											drift=2 
											)
	# return the device
	return device

def get_profile(user):
	# get the profile if the user has one, otherwise create a profile
	profile = Profile.try_to_get(user=user)
	if not profile:
		profile = Profile.objects.create(user=user)
	# return the device
	return profile

def get_survey_list_for_person(person,project):
	# get and return a list of surveys for a person, with the submission attached if there is one
	# get the list depending on whether we have a project or not
	if project:
		surveys = Survey.objects.filter(survey_series__project=project)
	else:
		surveys = Survey.objects.filter(survey_series__project__in=person.projects.all())
	# go through the surveys and add the submissions
	for survey in surveys:
		survey_submission = Survey_Submission.try_to_get(
															survey=survey,
															person=person
														)
		if survey_submission:
			survey.survey_submission = survey_submission
		else:
			survey.survey_submission = False
	# return the results
	return surveys

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
				venue,
				areas
				):
	# get the related objects
	event_type = Event_Type.try_to_get(pk=event_type_id)
	venue = Venue.try_to_get(pk=venue) if venue != '0' else None
	# get the project
	project = Project.current_project(request.session)
	project = project if project else None
	# create the event
	if event_type:
		# create the event
		event = Event(
						name = name,
						description = description,
						venue = venue,
						date = date,
						start_time = start_time,
						end_time = end_time,
						event_type = event_type,
						project = project
						)
		event.save()
		# set a message
		messages.success(request, 'New event (' + str(event) + ') created.')
		# got through the areas and add them
		for area_id in areas.keys():
			if (areas[area_id] == True) or (venue and venue.street.post_code.ward.area.pk == area_id):
				event.areas.add(Area.objects.get(id=area_id))
	# otherwise set a message
	else:
		messages.error(request, 'Event (' + name + ') could not be created: event type does not exist.')
	# return the event
	return event

def build_registration(request, event, person_id, registered, apologies, participated, role_type_id, show_messages=True):
	# get the project
	project = Project.current_project(request.session)
	# attempt to create a new registration, checking first that the registration does not exit
	# first get the person
	person = Person.try_to_get(projects=project,pk=person_id)
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
	# get the project
	project = Project.current_project(request.session)
	# attempt to remove a registration record, checking first that the registration exists
	# first get the person
	person = Person.try_to_get(projects=project,pk=person_id)
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
	# initialise variables
	answer = False
	# attempt to get the question
	question = Question.try_to_get(pk=question_id)
	# deal with exceptions if we didn't get a question
	if not question:
		messages.error(request,'Could not create answer: question' + str(question_id) + ' does not exist.')
		return False
	# check that we have a valid option
	if option_id:
		option = Option.try_to_get(pk=option_id)
		if not option:
			messages.error(request,'Could not create answer: option ' + str(option_id) + ' does not exist.')
			return False
	# clear out existing answers - or answers if we have more than one in error
	Answer.objects.filter(person=person,question=question).delete()
	# create a new answer if we have an option id
	if option_id:
		answer = Answer(
						person = person,
						option = option,
						question = question
						)
		answer.save()
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
					default_role_id,
					ethnicity_id,
					membership_type_id,
					date_joined_project,
					date_left_project,
					age_status_id,
					notes,
					membership_number
				):
	# find out whether we have a project
	project = Project.current_project(request.session)
	# set the role change flag to false: we don't know whether the role has changed
	role_change = False
	# attempt to set ethnicity
	ethnicity = Ethnicity.try_to_get(pk=ethnicity_id)
	if ethnicity:
		person.ethnicity = ethnicity
	else:
		messages.error(request, 'Ethnicity does not exist.')
	# attempt to set age status
	age_status = Age_Status.try_to_get(pk=age_status_id)
	if age_status:
		person.age_status = age_status
	else:
		messages.error(request, 'Age Status does not exist.')
	# attempt to set role type
	default_role = Role_Type.try_to_get(pk=default_role_id)
	if default_role:
		if person.default_role != default_role:
			role_change = True
		person.default_role = default_role
	else:
		messages.error(request, 'Role type does not exist.')
	# attempt to set ABSS details if we don't have a project
	if not project:
		person.ABSS_start_date = date_joined_project
		person.ABSS_end_date = date_left_project
		ABSS_type = ABSS_Type.try_to_get(pk=membership_type_id)
		if ABSS_type:
			person.ABSS_type = ABSS_type
		else:
			messages.error(request, 'ABSS Type does not exist.')
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
	person.notes = notes
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
	# update project membership details if we have a project
	if project:
		membership = Membership.try_to_get(person=person,project=project)
		if membership:
			membership.date_joined = date_joined_project
			membership.date_left = date_left_project
			membership_type = Membership_Type.try_to_get(pk=membership_type_id)
			if membership_type:
				membership.membership_type = membership_type
			else:
				messages.error(request, 'Membership Type does not exist.')
			# save the changes
			membership.save()
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

def build_trained_role(person,role_type_id,trained_status,date_trained):
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
			trained_role = Trained_Role(
										person=person,
										role_type=role_type,
										date_trained=date_trained
										)
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
	# get the project
	project = Project.current_project(request.session)
	project = project if project else None
	# attempt to get the activity type
	activity_type = Activity_Type.try_to_get(pk=activity_type_id)
	if not activity_type:
		messages.error(
						request,
						'Could not create activity: activity type' + str(activity_type_id) + ' does not exist.'
						)
		return False
	# see whether we already have an activity
	activity = Activity.try_to_get(person=person,activity_type=activity_type,date=date,project=project)
	# if we got an activity, check whether this is an update or delete
	if activity:
		if hours == 0:
			# zero hours means that we should delete
			activity_desc = str(activity)
			activity.delete()
			messages.success(request,activity_desc + ' - deleted successfully.')
		else:
			# non-zero hours means that we should update
			activity.hours = hours
			activity.save()
			messages.success(request,str(activity) + ' - updated successfully.')
	# otherwise we have a new activity
	else:
		if hours == 0:
			# zero hours means do nothing
			messages.success(request,'Activity not created - hours set to zero.')
		else:
			# non-zero hours means that we should create
			activity = Activity(
								person = person,
								activity_type = activity_type,
								date = date,
								hours = hours,
								project=project
								)
			activity.save()
			messages.success(request,str(activity) + ' - created successfully.')
	# and we're done
	return activity

def generate_invitation(person):
	# generate an invitation which can be used for a parent to enter their own details if one doesn't already exist
	# don't generate an invitation if one already exists
	invitation = Invitation.try_to_get(person=person,datetime_completed__isnull=True)
	if not invitation:
		invitation = Invitation.objects.create(
												person=person,
												code=Invitation.generate_code(),
												)
	# return the result
	return invitation

def validate_invitations(person):
	# mark all invitations which have been completed but not validated as valid
	invitations = Invitation.objects.filter(person=person,datetime_completed__isnull=False,validated=False)
	for invitation in invitations:
		invitation.validated = True
		invitation.save()

def build_memberships(people,project,action,with_dates):
	# initialise variables
	results = ''
	success = 0
	error = 0
	if action == 'add':
		default_membership_type = Membership_Type.try_to_get(default=True)
		if not default_membership_type:
			return 'ERROR: no default membership type.'
	# go through the people
	for person in people:
		membership = Membership.try_to_get(project=project,person=person)
		# process additionas
		if action == 'add':
			if membership:
				error += 1
			else:
				# set the values
				date_joined = person.ABSS_start_date if with_dates else None
				date_left = person.ABSS_end_date if with_dates else None
				if person.ABSS_type.membership_type:
					membership_type = person.ABSS_type.membership_type
				else: 
					membership_type = default_membership_type
				# create the membership
				Membership.objects.create(
											person=person,
											project=project,
											date_joined=date_joined,
											date_left=date_left,
											membership_type=membership_type
										)
				success += 1
		# process removals
		if action == 'remove':
			if not membership:
				error += 1
			else:
				membership.delete()
				success += 1
	# set the results
	if action == 'add':
		results = str(success) + ' people added to project'
		if error:
			results += '; ' + str(error) + ' people not added: already members'
	else:
		results = str(success) + ' people removed from project'
		if error:
			results += '; ' + str(error) + ' people not removed: not members'
	# return the results
	return results

def build_project_events(events,project,action):
	# initialise variables
	results = ''
	success = 0
	in_project_error = 0
	invalid_event_type = 0
	registration_error = 0
	# go through the events
	for event in events:
		# process additions
		if action == 'add':
			# check whether the event is already in the project
			if event.project == project:
				in_project_error += 1
			# check whether the event type is valid
			else:
				project_event_type = Project_Event_Type.try_to_get(
																	project=project,
																	event_type=event.event_type
																	)
				if not project_event_type:
					invalid_event_type += 1
				else:
					# check whether there are any registrations for people not in the project
					person_not_member = False
					for registration in event.event_registration_set.all():
						membership = Membership.try_to_get(
															person=registration.person,
															project=project
															)
						if not membership:
							person_not_member = True
					# deal with the result
					if person_not_member:
						registration_error += 1
					else:
						event.project = project
						event.save()
						success += 1
		# process removals
		if action == 'remove':
			# check whether the event is already in the project, and remove it if it is
			if event.project == project:
				event.project = None
				event.save()
				success += 1
			# otherwise set the error
			else:
				in_project_error += 1
	# set the results
	if action == 'add':
		results = str(success) + ' events added to project'
		if registration_error:
			results += '; ' + str(registration_error) + ' events not added: registrations not in project'
		if in_project_error:
			results += '; ' + str(in_project_error) + ' events not added: already in project'
		if invalid_event_type:
			results += '; ' + str(invalid_event_type) + ' events not added: invalid event type'
	else:
		results = str(success) + ' events removed from project'
		if in_project_error:
			results += '; ' + str(in_project_error) + ' events not removed: not in project'
	# return the results
	return results
				
def build_survey(survey_series,name,description):
	# build a survey, copying sections and questions from the last survey if they exist
	# get the latest survey in the series
	latest_survey = False
	if survey_series.survey_set.exists():
		latest_survey = survey_series.survey_set.first()
	# create the survey
	survey = Survey.objects.create(
									survey_series = survey_series,
									name = name,
									description = description,
									date_created = datetime.date.today()
									)
	# if there is a latest survey, go through and create the sections and questions
	if latest_survey:
		for latest_survey_section in latest_survey.survey_section_set.all():
			survey_section = Survey_Section.objects.create(
															survey = survey,
															name = latest_survey_section.name,
															order = latest_survey_section.order,
															)
			for latest_survey_question in latest_survey_section.survey_question_set.all():
				survey_question = Survey_Question.objects.create(
																	survey_section = survey_section,
																	survey_question_type = latest_survey_question.survey_question_type,
																	question = latest_survey_question.question,
																	number = latest_survey_question.number,												
																	)
	# return the results
	return survey

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
	# this function takes an and a list of people, and returns a list of only those people where
	# the person does not have an existing registration for that event
	# create an empty list
	people_without_existing_registrations = []
	# now got through the people
	for person in people:
		if not Event_Registration.try_to_get(person=person,event=event):
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

def build_context(request,context_dict):
	# take a context dictionary and add additional items
	# set the defaults
	site_name = 'test site'
	navbar_background = ''
	navbar_text = ''
	show_messages = True
	dob_offset = 0
	this_site = False
	# attempt to get the project
	project = Project.current_project(request.session)
	project_name = project.name if project else ''
	# attempt to get the site
	site = Site.objects.all().first()
	# if we have a site, set the details
	if site:
		site_name = site.name
		show_messages = site.messages
		dob_offset = site.dob_offset
		this_site = site
	# set the navbar colours depending on whether we have a site or a project
	if project:
		navbar_background = project.navbar_background
		navbar_text = project.navbar_text
	elif site:
		navbar_background = site.navbar_background 
		navbar_text = site.navbar_text
	# now set the dictionary
	context_dict['site_name'] = site_name
	context_dict['navbar_background'] = navbar_background
	context_dict['navbar_text'] = navbar_text
	context_dict['show_messages'] = show_messages
	context_dict['site'] = this_site
	context_dict['project_name'] = project_name
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

def verify_token(user,token):
	# function to check whether a token is valid for a user, using the django OTP library
	# initialise variables
	message = False
	verified = False
	# if the token contains the phrase 'EMERGENCY', use a static token, after stripping out the emergency text
	if 'EMERGENCY' in token:
		device_class = StaticDevice
		token = token.replace('EMERGENCY','')
	else:
		device_class = TOTPDevice
	# do the verification
	try:
		device = device_class.objects.get(user=user)
		if device.verify_token(token):
			verified = True
		else:
			message = 'Invalid token.'
	except (device_class.DoesNotExist):
		message = 'User does not have registered device.'
	# return the results
	return verified, message

def build_download_file(file_type,file_name=False,objects=None,project=False):
	# takes a class name and optional queryset and returns a file download response
	# initialise variables
	file_handlers = {
						'People' : People_File_Handler,
						'People Limited' : People_Limited_Data_File_Handler,
						'Relationships' : Relationships_File_Handler,
						'Events' : Events_File_Handler,
						'Registrations' : Registrations_File_Handler,
						'Questions' : Questions_File_Handler,
						'Options' : Options_File_Handler,
						'Answers' : Answers_File_Handler,
						'Answer Notes' : Answer_Notes_File_Handler,
						'Activities' : Activities_File_Handler,
						'Event Summary' : Event_Summary_File_Handler,
						'Events and Registrations' : Events_And_Registrations_File_Handler,
						'Venues' : Venues_File_Handler,
						'Survey Submissions' : Survey_Submissions_File_Handler,
					}
	# create the file handler
	file_handler = file_handlers[file_type](objects=objects,project=project)
	# build the download records
	file_handler.handle_download()
	records = file_handler.download_records
	# set the file name if we have one, otherwise use the file type
	file_name = file_name if file_name else file_type
	# create the http response
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="' + file_name + '.csv"'
	# use the csv writer to write the keys and then the records to the response
	writer = csv.writer(response)
	writer.writerow(file_handler.fields + file_handler.additional_download_fields)
	for record in records:
		writer.writerow(record)
	# return the result
	return response

def auth_log(
					user=False,
					username=False,
					success=False,
					otp=False,
					reset_requested=False,
					reset_successful=False,
					):
	# this function records authentication stats
	# if we've been passed a username, attempt to get the user, and return if there is no matching user
	if username:
		try:
			user = User.objects.get(username=username)
		except (User.DoesNotExist):
			return
	# get the profile
	profile = get_profile(user)
	# update the profile
	if success:
		profile.successful_logins += 1
		profile.failed_login_attempts = 0
	else:
		profile.unsuccessful_logins += 1
		profile.failed_login_attempts += 1
	if otp:
		if success:
			profile.successful_otp_logins += 1
		else:
			profile.unsuccessful_otp_logins += 1
	if reset_requested:
		profile.requested_resets += 1
	if reset_successful:
		profile.successful_resets += 1
	# save the record
	profile.save()

def determine_otp_login(site,form):
	# function to determine whether a real or practice otp login is needed
	if site and (
					site.otp_required or 
					(site.otp_practice and form.cleaned_data['token'])
					):
		otp_login = True
	else:
		otp_login = False
	# return the results
	return otp_login

def link_callback(uri, rel):
	"""
	Convert HTML URIs to absolute system paths so xhtml2pdf can access those
	resources
	"""
	result = finders.find(uri)
	if result:
			if not isinstance(result, (list, tuple)):
					result = [result]
			result = list(os.path.realpath(path) for path in result)
			path=result[0]
	else:
			sUrl = settings.STATIC_URL        # Typically /static/
			sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
			mUrl = settings.MEDIA_URL         # Typically /media/
			mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

			if uri.startswith(mUrl):
					path = os.path.join(mRoot, uri.replace(mUrl, ""))
			elif uri.startswith(sUrl):
					path = os.path.join(sRoot, uri.replace(sUrl, ""))
			else:
					return uri

	# make sure that file exists
	if not os.path.isfile(path):
			raise Exception(
					'media URI must start with %s or %s' % (sUrl, mUrl)
			)
	return path

# VIEW FUNCTIONS
# A set of functions which implement the functionality of the site and serve pages.

def old_log_user_in(request):
	# initialise variables
	successful_login = False
	site = Site.objects.all().first()
	otp_login = False
	password_reset_allowed = site.password_reset_allowed if site else False
	projects_active = site.projects_active if site else False
	# check whether user is already logged in
	if request.user.is_authenticated:
		successful_login = True
	else:
		# handle the login request
		login_template = loader.get_template('people/login.html')
		if request.method == 'POST':
			login_form = LoginForm(request.POST)
			if login_form.is_valid():
				# determine whether this is an otp login
				if site and (
								site.otp_required or 
								(site.otp_practice and login_form.cleaned_data['token'])
								):
					otp_login = True
				# check whether max login attempts have been exceeded
				profile = Profile.try_to_get(user__username = login_form.cleaned_data['email_address'])
				if profile and profile.login_attempts_exceeded():
					# set an error for the login failure
					login_form.add_error(None, 'Maximum login attempts exceeded: please contact administrator.')
					auth_log(
								username=login_form.cleaned_data['email_address'],
								otp=otp_login,
								success=False
								)
				else:
					# attempt to authenticate the user
					user = authenticate(
										request,
										username=login_form.cleaned_data['email_address'],
										password=login_form.cleaned_data['password']
										)
					# login the user if successful
					if user is not None:
						if otp_login:
							# check the token
							successful_login, message = verify_token(user,login_form.cleaned_data['token'])
							if successful_login:
								auth_log(user=user,success=True,otp=True)
							else:
								login_form.add_error(None,message)
								auth_log(user=user,success=False,otp=True)
						
							login(request,user)
							successful_login = True
							auth_log(user=user,success=True,otp=False)
					else:
						# set an error for the login failure
						login_form.add_error(None, 'Email address or password not recognised.')
						auth_log(
									username=login_form.cleaned_data['email_address'],
									otp=otp_login,
									success=False
									)
		else:
			# this is a first time submission, so create an empty form
			login_form = LoginForm()
	# if we logged in successfully, set a message, set the default project in the session, and redirect
	if successful_login:
		messages.success(request, 'Successfully logged in. Welcome back ' + str(request.user.first_name) + '!')
		project = Project.default_project(user)
		request.session['project_id'] = project.pk if project else 0
		return redirect('index')
	# otherwsise, set the context and output a form
	context = build_context(
								request,
								{
								'login_form' : login_form,
								'password_reset_allowed' : password_reset_allowed,
								}
								)
	# set the output
	return HttpResponse(login_template.render(context, request))

def log_user_in(request):
	# initialise variables
	successful_login = True
	site = Site.objects.all().first()
	password_reset_allowed = site.password_reset_allowed if site else False
	projects_active = site.projects_active if site else False
	project = False
	login_template = loader.get_template('people/login.html')
	# check whether user is already logged in
	if request.user.is_authenticated:
		return redirect('index')
	# if we haven't got a post, create an empty form
	if request.method != 'POST':
		login_form = LoginForm()
	# if we have got a post, do the validation
	else:
		# handle the login request
		login_form = LoginForm(request.POST)
		if login_form.is_valid():
			# determine whether otp login is required
			otp_login = determine_otp_login(site=site,form=login_form)
			# do basic authentication
			user = authenticate(
								request,
								username=login_form.cleaned_data['email_address'],
								password=login_form.cleaned_data['password']
								)
			if user is None:
				# set an error for the login failure
				login_form.add_error(None, 'Email address or password not recognised.')
				auth_log(
							username=login_form.cleaned_data['email_address'],
							otp=otp_login,
							success=False
							)
				successful_login = False
			else:
				# get the profile
				profile = get_profile(user)
				# check whether max logins have been exceeded
				if profile.login_attempts_exceeded():
					login_form.add_error(None, 'Maximum login attempts exceeded: please contact administrator.')
					successful_login = False
				else:
					# check the otp if we need to
					if otp_login:
						successful_otp, message = verify_token(user,login_form.cleaned_data['token'])
						if not successful_otp:
							login_form.add_error(None,message)
							successful_login = False
					# check whether the user needs and has access to a project
					if projects_active:
						project = Project.default_project(user)
						if not project and not user.is_superuser:
							# set an error for the login failure
							login_form.add_error(None, 'You do not have access to any projects.')
							successful_login = False
				# record the attempt
				auth_log(user=user,otp=otp_login,success=successful_login)
				# if successful, log the user in and set the project
				if successful_login:
					login(request,user)
					messages.success(request, 'Successfully logged in. Welcome back ' + str(request.user.first_name) + '!')
					if project:
						request.session['project_id'] = project.pk if project else 0
					return redirect('index')
	# set the context and output a form
	context = build_context(
								request,
								{
								'login_form' : login_form,
								'password_reset_allowed' : password_reset_allowed,
								}
								)
	# set the output
	return HttpResponse(login_template.render(context, request))

def forgot_password(request):
	# initialise variables
	request_submitted = False
	site = Site.objects.all().first()
	password_reset_allowed = site.password_reset_allowed if site else False
	# if the user is already logged in, redirect to the index page
	if request.user.is_authenticated or not password_reset_allowed:
		return redirect('index')
	# handle the login request
	if request.method == 'POST':
		request_submitted = True
		form = ForgotPasswordForm(request.POST)
		if form.is_valid():
			# get the form values
			email_address = form.cleaned_data['email_address']
			# determine whether the email address is valid
			try:
				user = User.objects.get(username=email_address)
			except (User.DoesNotExist):
				user = False
			# if we have a valid user, generate the code and the email
			if user:
				# generate and store the reset code
				profile = get_profile(user)
				profile.reset_code = Profile.generate_reset_code()
				profile.reset_timeout = Profile.generate_reset_timeout()
				profile.save()
				# generate the url and mail text, then send the mail
				reset_url = request.build_absolute_uri(reverse('reset_password',args=[profile.reset_code]))
				email_text = site.password_reset_email_text + '\r' + reset_url
				# use sendgrid API to send this email
				message = Mail(
								from_email=site.password_reset_email_from,
								to_emails=email_address,
								subject= site.password_reset_email_title,
								html_content=email_text)
				try:
					api_key = os.getenv('SENDGRID_API_KEY')
					sg = SendGridAPIClient(api_key)
					response = sg.send(message)
					print(response.status_code)
					print(response.body)
					print(response.headers)
				except Exception as e:
					print(e.message)
				# log the request
				auth_log(user=user,reset_requested=True)
	# otherwise create a blank form
	else:
		form = ForgotPasswordForm()
	# otherwsise, set the context and output a form
	context = build_context(request,{
								'forgotpasswordform' : form,
								'request_submitted' : request_submitted,
								})
	# set the output
	template = loader.get_template('people/forgot_password.html')
	return HttpResponse(template.render(context, request))

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
	membership_type = 0
	age_status = 0
	trained_role = 'none'
	ward = 0
	include_people = 'in_project'
	children_ages = ''
	project = Project.current_project(request.session)
	# set a blank search_error
	search_error = ''
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		personsearchform = PersonSearchForm(request.POST,user=request.user,download=True,project=project)
		# set the flag to show that a search was attempted
		search_attempted = True
		# validate the form
		if personsearchform.is_valid():
			# get the fields
			names = personsearchform.cleaned_data['names']
			keywords = personsearchform.cleaned_data['keywords']
			role_type = personsearchform.cleaned_data['role_type']
			age_status = personsearchform.cleaned_data['age_status']
			trained_role = personsearchform.cleaned_data['trained_role']
			ward = personsearchform.cleaned_data['ward']
			include_people = personsearchform.cleaned_data['include_people']
			children_ages = personsearchform.cleaned_data['children_ages']
			# set the membership type or ABSS type dependent on whether we have a project
			if project:
				membership_type = personsearchform.cleaned_data['membership_type']
			else:
				ABSS_type = personsearchform.cleaned_data['membership_type']
			# conduct a search
			people = Person.search(
									project=project,
									names=names,
									keywords=keywords,
									default_role_id=role_type,
									ABSS_type_id=ABSS_type,
									membership_type_id=membership_type,
									age_status_id=age_status,
									trained_role=trained_role,
									street__post_code__ward_id=ward,
									include_people=include_people,
									children_ages=children_ages,
									).order_by('last_name','first_name')
			# if we got a request for a search, do the pagination
			if personsearchform.cleaned_data['action'] == 'Search':
				number_of_people = len(people)
				this_page = int(request.POST['page'])
				page_list = build_page_list(
											objects=people,
											page_length=results_per_page,
											attribute='last_name',
											length=3
											)
				previous_page = this_page - 1
				people = people[previous_page*results_per_page:this_page*results_per_page]
				# add relationships to people, filtered by project if we have a project
				for person in people:
					person.relationships_from = get_relationships_from(person,project)
			# download summary data
			elif personsearchform.cleaned_data['action'] == 'Download':
				response = build_download_file('People Limited',objects=people,project=project)
				return response
			# download full data if permitted
			elif personsearchform.cleaned_data['action'] == 'Download Full Data':
				if not request.user.is_superuser:
					personsearchform.add_error(None, 'You do not have permission to download files.')
				else:
					response = build_download_file('People',objects=people,project=project)
					return response
	# otherwise set a blank form
	else:
		personsearchform = PersonSearchForm(project=project)
	# build and return the response
	people_template = loader.get_template('people/people.html')
	context = build_context(request,{
				'personsearchform' : personsearchform,
				'people' : people,
				'page_list' : page_list,
				'this_page' : this_page,
				'names' : names,
				'keywords' : keywords,
				'role_type' : role_type,
				'ABSS_type' : ABSS_type,
				'membership_type' : membership_type,
				'age_status' : age_status,
				'trained_role' : trained_role,
				'ward' : ward,
				'include_people' : include_people,
				'search_error' : search_error,
				'number_of_people' : number_of_people,
				'search_attempted' : search_attempted,
				'children_ages' : children_ages,
				'project' : project,
				})
	return HttpResponse(people_template.render(context=context, request=request))

@login_required
def people_query(request, id):
	# this function emulates a post from a search form
	# the criterion to be searched on is dependent on the url name
	# create a dictionary of items
	form_values = {
					'role_type' : '0',
					'membership_type' : '0',
					'age_status' : '0',
					'trained_role' : 'none',
					'ward' : '0'
					}
	# set the value based on the url
	form_values[resolve(request.path_info).url_name] = id
	# copy the request
	copy_POST = request.POST.copy()
	# set search terms for a people search
	copy_POST['action'] = 'Search'
	copy_POST['role_type'] = form_values['role_type']
	copy_POST['names'] = ''
	copy_POST['membership_type'] = form_values['membership_type']
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
	# get querysets and set template based on the type of call
	if 'parents_with_no_children' in path:
		parents, parents_with_no_children_under_four = get_parents_without_children(request)
		exceptions_template = loader.get_template('people/parents_without_children.html')
	elif 'parents_without_children_under_four' in path:
		parents_with_no_children, parents = get_parents_without_children(request)
		exceptions_template = loader.get_template('people/parents_without_children_under_four.html')
	# set other variables
	page_list = []
	results_per_page = 25
	page = int(page)
	# do pagination
	page_list = build_page_list(
								objects=parents,
								page_length=results_per_page,
								attribute='last_name',
								length=3
								)
	previous_page = page - 1
	parents = parents[previous_page*results_per_page:page*results_per_page]
	# set the context
	context = build_context(request,{
				'parents' : parents,
				'children' : children,
				'page_list' : page_list,
				'this_page' : page
				})
	# return the HttpResponse
	return HttpResponse(exceptions_template.render(context=context, request=request))

@login_required
def age_exceptions(request, age_status_id=0):
	# initialise variables
	project = Project.current_project(request.session)
	# load the template
	age_exceptions_template = loader.get_template('people/age_exceptions.html')
	# get the age status
	age_status = Age_Status.try_to_get(pk=age_status_id)
	# if the age status doesn't exist, crash to a banner
	if not age_status:
		return make_banner(request, 'Age status does not exist.')
	# get today's date
	today = datetime.date.today()
	earliest_date = today.replace(year=today.year-age_status.maximum_age)
	# get the exceptions
	age_exceptions = Person.search(
									age_status=age_status,
									date_of_birth__lt=earliest_date,
									project=project
									)
	# set the context from the person based on person id
	context = build_context(request,{
				'age_status' : age_status,
				'people' : age_exceptions,
				})
	# return the response
	return HttpResponse(age_exceptions_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def resolve_age_exceptions(request):
	# initialise variables
	project = Project.current_project(request.session)
	results = []
	# load the template
	resolve_age_exceptions_template = loader.get_template('people/resolve_age_exceptions.html')
	# create an empty Person queryset
	all_age_exceptions = Person.objects.none()
	# go through the age statuses
	for age_status in Age_Status.objects.all():
		# get today's date
		today = datetime.date.today()
		earliest_date = today.replace(year=today.year-(age_status.maximum_age + 1))
		earliest_date = earliest_date + datetime.timedelta(days=1)
		# get the exceptions
		age_exceptions = Person.search(
										age_status=age_status,
										date_of_birth__lt=earliest_date,
										project=project
										)
		# merge the exceptions with the previous queryset
		all_age_exceptions = all_age_exceptions | age_exceptions
	# if we got a POST, apply the recommendations, building a list of results
	if request.method == 'POST':
		for person in all_age_exceptions:
			recommended_age_status = person.recommended_age_status()
			if recommended_age_status:
				person.age_status = recommended_age_status
				person.default_role = person.recommended_role_type()
				person.save()
				results.append(
								person.full_name() + 
								' updated to ' + 
								person.age_status.status + 
								' as ' + 
								person.default_role.role_type_name
								)
				# remove the person from the exceptions queryset
				all_age_exceptions = all_age_exceptions.exclude(pk=person.pk)
			else:
				results.append(person.full_name() + ' not updated: resolve manually')
	# create the form
	resolveageexceptionsform = ResolveAgeExceptionsForm()
	# set the context from the person based on person id
	context = build_context(request,{
				'people' : all_age_exceptions,
				'resolveageexceptionsform' : resolveageexceptionsform,
				'results' : results
				})
	# return the response
	return HttpResponse(resolve_age_exceptions_template.render(context=context, request=request))

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
										request = request,
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
		matching_people = Person.search(
										project=Project.current_project(request.session),
										first_name=first_name,
										last_name=last_name
										)
		# if there aren't any matching people, also create the person
		if not matching_people:
			# create the person
			person = create_person(
									request = request,
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
	context = build_context(request,{
				'addpersonform' : addpersonform,
				'matching_people' : matching_people
				})
	# return the HttpResponse
	return HttpResponse(addperson_template.render(context=context, request=request))

@login_required
def person(request, person_id=0):
	# initialise variables
	completed_invitation_steps=False
	invitation_step_types=False
	invitation_url = False
	memberships = False
	project = Project.current_project(request.session)
	# load the template
	person_template = loader.get_template('people/person.html')
	# tey to get the person
	person = Person.try_to_get(projects=project,pk=person_id)
	if not person:
		return make_banner(request, 'Person does not exist.')
	# add the project to the person
	person.project = project
	# get additional info for the page
	person.relationships_from = get_relationships_from(person,project)
	question_sections, answer_flag = get_question_sections_and_answers(person,project=project)
	completed_invitations = person.invitation_set.filter(datetime_completed__isnull=False,validated=True)
	unvalidated_invitations = person.invitation_set.filter(datetime_completed__isnull=False,validated=False)
	trained_roles_allowed = person.age_status.role_types.filter(trained=True).exists()
	# get invitation data if an uncompleted invitation exists
	invitation = Invitation.try_to_get(person=person,datetime_completed__isnull=True)
	if invitation:
		completed_invitation_steps=Invitation_Step.objects.filter(invitation=invitation)
		invitation_step_types=Invitation_Step_Type.objects.filter(active=True).exclude(invitation=invitation)
		# get the absolute url for the invitation
		invitation_url = request.build_absolute_uri(reverse('invitation',args=[invitation.code]))
	# get additional data, and filter by project
	registrations = person.event_registration_set.order_by('-event__date')
	if project:
		registrations = registrations.filter(event__project=project)
	activities = person.activity_set.order_by('-date')
	if project:
		activities = activities.filter(project=project)
	if not project:
		memberships = person.membership_set.all()
	case_notes = person.case_notes_set.order_by('-date')
	if project:
		case_notes = case_notes.filter(project=project)
	surveys = get_survey_list_for_person(person=person,project=project)
	# set the context
	context = build_context(request,{
				'person' : person,
				'registrations' : registrations,
				'activities' : activities,
				'question_sections' : question_sections,
				'answer_flag' : answer_flag,
				'role_history' : person.role_history_set.all(),
				'invitation' : invitation,
				'completed_invitation_steps' : completed_invitation_steps,
				'invitation_step_types': invitation_step_types,
				'invitation_url' : invitation_url,
				'completed_invitations' : completed_invitations,
				'unvalidated_invitations' : unvalidated_invitations,
				'memberships' : memberships,
				'case_notes' : case_notes,
				'project' : project,
				'surveys' : surveys,
				'trained_roles_allowed' : trained_roles_allowed,
				})
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

def invitation(request, code):
	# initialise variables
	invitation_complete = False
	# build a dictionary to hold the classes for the invitation handlers
	invitation_step_dict = {
								'introduction' : Introduction_Invitation_Handler,
								'terms_and_conditions' : Terms_And_Conditions_Invitation_Handler,
								'personal_details' : Personal_Details_Invitation_Handler,
								'address' : Address_Invitation_Handler,
								'children' : Children_Invitation_Handler,
								'questions' : Questions_Invitation_Handler,
								'signature' : Signature_Invitation_Handler,
							}
	# try to get the invitation, returning a banner if it doesn't exist, or has been completed
	invitation = Invitation.try_to_get(code=code)
	if not invitation:
		return make_banner(request, 'Invitation code is not valid',public=True)
	if invitation.datetime_completed is not None:
		return make_banner(request, 'Invitation has been completed',public=True)
	# figure out which step we are supposed to be processing next
	next_step = invitation.incomplete_steps().first()
	# create the invitation handler and use it to process the request
	invitation_handler = invitation_step_dict[next_step.name](invitation,next_step)
	invitation_handler.handle_request(request)
	# if the step is now complete, get the next step and set up the form
	if invitation_handler.step_complete:
		incomplete_steps = invitation.incomplete_steps()
		if incomplete_steps.exists():
			return redirect('/invitation/' + invitation.code)
		else:
			# we have no more steps, so mark the implementation complete
			invitation.datetime_completed = timezone.now()
			invitation.save()
			invitation_complete = True
			next_step = False
	# load the template
	invitation_template = loader.get_template(invitation_handler.template)
	# set the context
	context = build_context(request,{
				'invitation' : invitation,
				'invitation_handler' : invitation_handler,
				'invitation_step_type' : next_step,
				'invitation_complete' : invitation_complete,
				'default_date' : invitation_handler.default_date,
				'default_date_of_birth' : invitation_handler.default_date_of_birth,
				})
	# return the response
	return HttpResponse(invitation_template.render(context=context, request=request))

@login_required
def review_invitation(request,invitation_id):
	# attempt to get the invitation
	invitation = Invitation.try_to_get(pk=invitation_id)
	if not invitation:
		return make_banner(request, 'Invitation does not exist.', public=True)
	# get the data
	invitation_url = request.build_absolute_uri(reverse('invitation', args=[invitation.code]))
	# load the template
	template = loader.get_template('people/review_invitation.html')
	# set the context
	context = build_context(request,{
								'invitation': invitation,
								'invitation_url' : invitation_url
							})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def print_invitation_form(request,invitation_id):
	# initialise vairables
	parental_responsibility = False
	# attempt to get the current registration form
	registration_form = Registration_Form.try_to_get(end_date=None)
	if not registration_form:
		return make_banner(request, 'No current registration form.')
	# attempt to get the invitation
	invitation = Invitation.try_to_get(pk=invitation_id)
	if not invitation:
		return make_banner(request, 'Invitation does not exist.')
	# check whether the invitation is complete and validated
	if not invitation.validated:
		return make_banner(request, 'Invitation has not been validated.')
	# create a dict to hold the step types, and the list of types we are looking for
	invitation_steps = {}
	invitation_step_types = (
								'personal_details',
								'address',
								'children',
								'questions',
								'signature'
							)
	# go through the steps and load them into the dict, crashing out to a banner if they don't exist
	for invitation_step_type in invitation_step_types:
		this_step = Invitation_Step.try_to_get(
												invitation_step_type__name=invitation_step_type,
												invitation = invitation
												)
		if not this_step:
			return make_banner(request, invitation_step_type + ' does not exist.')
		else:
			invitation_steps[invitation_step_type] = this_step
	# do the special processing for each step type
	personal_details_step = invitation_steps['personal_details']
	personal_details = personal_details_step.get_display_data()
	address = invitation_steps['address'].get_display_data()
	questions_step = invitation_steps['questions']
	signature_step = invitation_steps['signature']
	# get a list of dictionaries for the questions, then go through and set values for individually displayed questions
	questions = invitation_steps['questions'].get_dict_data()
	if questions:
		for question in questions:
			if 'parental responsibility' in question['Question']:
				parental_responsibility = question
			if 'legal guardian' in question['Question']:
				legal_guardian = question
	# build a new list of questions to be displayed in the 'additional information' section
	# check whether the question is to be used for additional info, and append a supplemented dict
	# to the list if it is
	additional_info_questions = []
	for question in questions:
		question_record = Question.try_to_get(
												question_text=question['Question'],
												use_for_invitations_additional_info=True
												)
		if question_record:
			question['notes_label'] = question_record.notes_label
			question['notes_required'] = question_record.notes
			additional_info_questions.append(question)
	# get the ethnicities, and indicate which one was selected
	ethnicities = Ethnicity.objects.all()
	for ethnicity in ethnicities:
		ethnicity.selected = True if ethnicity.description == personal_details['Ethnicity'] else False
	# get the list of children, converting a false response to an empty list
	children = invitation_steps['children'].get_dict_data()
	children = children if children else []
	for child in children:
		# initialise variables
		additional_needs = False
		additional_needs_notes = ''
		first_language = ''
		first_language_notes = ''
		# run through the dict, looking for specific questions
		for key in child.keys():
			# scan for an additional needs question
			if 'additional needs' in key:
				if not 'notes' in key:
					if child[key] == 'Yes':
						additional_needs = True
				else:
					additional_needs_notes = child[key]
			# scan for a first language question
			if 'first language' in key:
				if not 'notes' in key:
					first_language = child[key]
				else:
					first_language_notes = child[key]
		# augment the dictionary
		child['additional_needs'] = additional_needs
		child['additional_needs_notes'] = additional_needs_notes
		child['first_language'] = first_language
		child['first_language_notes'] = first_language_notes
	# add empty dictionaries to pad out the children dict to five entries if necessary
	while len(children) < 5:
		children.append({})
	# add numbers to the children
	child_number = 1
	for child in children:
		child['number'] = child_number
		child_number += 1
	# get lists of printform
	employment_statuses = Printform_Data.objects.filter(printform_data_type__name='employment status')
	benefits = Printform_Data.objects.filter(printform_data_type__name='benefit')
	# load the template
	template = loader.get_template('people/print_invitation_form.html')
	# set the context
	context = build_context(request,{
								'invitation': invitation,
								'registration_form' : registration_form,
								'personal_details' : personal_details,
								'personal_details_step' : personal_details_step,
								'address' : address,
								'parental_responsibility' : parental_responsibility,
								'legal_guardian' : legal_guardian,
								'ethnicities' : ethnicities,
								'children' : children,
								'children_step' : invitation_steps['children'],
								'additional_info_questions' : additional_info_questions,
								'questions_step' : questions_step,
								'employment_statuses' : employment_statuses,
								'benefits' : benefits,
								'signature_step' : signature_step,
							})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def validate_invitation(request,invitation_id):
	# attempt to get the invitation
	invitation = Invitation.try_to_get(pk=invitation_id)
	if not invitation:
		return make_banner(request, 'Invitation does not exist.', public=True)
	if invitation.validated:
		return make_banner(request, 'Invitation already validated.', public=True)
	# update the invitation
	invitation.validated = True
	invitation.save()
	# return the redirect
	return redirect('/person/' + str(invitation.person.pk))

@login_required
def display_signature(request,invitation_step_id):
	# attempt to get the invitation
	invitation_step = Invitation_Step.try_to_get(pk=invitation_step_id)
	if not invitation_step:
		return make_banner(request, 'Invitation step id is not valid.', public=True)
	if not invitation_step.signature:
		return make_banner(request, 'Invitation step has no signature.', public=True)
	# create the image and return it as a response
	img = invitation_step.get_signature()
	response = HttpResponse(content_type='image/png')
	img.save(response,'PNG')
	return response

@login_required
def profile(request, person_id=0):
	# get the project
	project = Project.current_project(request.session)
	# set the old role to false: this indicates that the role hasn't changed yet
	old_role = False
	# try to get the person
	person = Person.try_to_get(projects=project,pk=person_id)
	# if there isn't a person, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get membership if we have a project
	if project:
		membership = Membership.objects.get(person=person,project=project)
	else:
		membership = False
	# when the form is POSTed, validate it, then update the person
	if request.method == 'POST':
		profileform = ProfileForm(request.POST,user=request.user,person=person,project=project)
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
								default_role_id = profileform.cleaned_data['role_type'],
								ethnicity_id = profileform.cleaned_data['ethnicity'],
								membership_type_id = profileform.cleaned_data['membership_type'],
								date_joined_project = profileform.cleaned_data['date_joined_project'],
								date_left_project = profileform.cleaned_data['date_left_project'],
								age_status_id = profileform.cleaned_data['age_status'],
								notes = profileform.cleaned_data['notes'],
								membership_number = profileform.cleaned_data['membership_number']
									)
			# generate an invitation if we have been asked
			if 'Generate' in request.POST['action']:
				generate_invitation(person)
			# validate invitations if we have been asked
			if 'Validate' in request.POST['action']:
				validate_invitations(person)
			# send the user back to the main person page
			return redirect('/person/' + str(person.pk))
	else:
		# set the project membership and dates depending on whether we have a project
		if membership:
			date_joined_project = membership.date_joined
			date_left_project = membership.date_left
			membership_type = membership.membership_type.pk
		else:
			date_joined_project = person.ABSS_start_date
			date_left_project = person.ABSS_end_date
			membership_type = person.ABSS_type.pk
		# now build a dictionary of values for the from
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
						'membership_type' : membership_type,
						'date_joined_project' : date_joined_project,
						'date_left_project' : date_left_project,
						'age_status' : person.age_status.pk,
						'notes' : person.notes,
						'membership_number' : person.membership_number,
						}
		# create the form
		profileform = ProfileForm(profile_dict,user=request.user,person=person,project=project)
	# load the template
	profile_template = loader.get_template('people/profile.html')
	# set the context
	context = build_context(request,{
				'profileform' : profileform,
				'person' : person,
				})
	# return the response
	return HttpResponse(profile_template.render(context, request))

@login_required
def trained_roles(request, person_id=0):
	# get the project
	project = Project.current_project(request.session)
	# try to get the person
	person = Person.try_to_get(projects=project,pk=person_id)
	# if there isn't a person, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# if there is a project and the project does not have trained rolesm crash to a banner
	if project and not project.has_trained_roles:
		return make_banner(request, 'Trained roles not available for this project')
	# get membership if we have a project
	if project:
		membership = Membership.objects.get(person=person,project=project)
	else:
		membership = False
	# when the form is POSTed, validate it, then update the person
	if request.method == 'POST':
		trained_roles_form = TrainedRolesForm(request.POST,user=request.user,person=person,project=project)
		if trained_roles_form.is_valid():
			# process trained roles by deleting and then recreating
			person.trained_role_set.all().delete()
			for field_name in trained_roles_form.cleaned_data.keys():
				if 'trained_role_' in field_name:
					role_type_id = int(extract_id(field_name))
					build_trained_role(
										person=person,
										role_type_id=role_type_id,
										trained_status=trained_roles_form.cleaned_data[field_name],
										date_trained=trained_roles_form.cleaned_data['trained_date_' + str(role_type_id)],
										)
			# send the user back to the main person page
			return redirect('/person/' + str(person.pk))
	else:
		#  build a dictionary of values for the form
		profile_dict = {}
		# add the trained role values to the profile dictionary
		for trained_role in Role_Type.objects.filter(trained=True):
			# set the profile dictionary value
			profile_dict['trained_role_' + str(trained_role.pk)] = get_trained_status(person,trained_role)
			profile_dict['trained_date_' + str(trained_role.pk)] = get_trained_date(person,trained_role)
		# create the form
		trained_roles_form = TrainedRolesForm(profile_dict,user=request.user,person=person,project=project)
	# load the template
	trained_roles_template = loader.get_template('people/trained_roles.html')
	# set the context
	context = build_context(request,{
				'trained_roles_form' : trained_roles_form,
				'person' : person,
				})
	# return the response
	return HttpResponse(trained_roles_template.render(context, request))

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
									project=Project.current_project(request.session),
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
		# set the project
		project = Project.current_project(request.session)
		# go through the post
		for field_name, field_value in request.POST.items():
			# check whether this is a relevant field
			if field_name.startswith('relationship_type'):
				# try to find a person using the id at the end of the field name
				person_to = Person.try_to_get(projects=project,pk=int(extract_id(field_name)))
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
										request = request,
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
	# TO BE REFACTORED AND SIMPLIFIED
	addrelationshipform = ''
	addrelationshiptoexistingpersonform = ''
	editexistingrelationshipsform = ''
	project = Project.current_project(request.session)
	# load the template
	person_template = loader.get_template('people/add_relationship.html')
	# get the person
	person = Person.try_to_get(projects=project,pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get existing relationships
	relationships_to = get_relationships_to(person,project)
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
	relationships_to = get_relationships_to(person,project)
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
	context = build_context(request,{
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
	# get the project
	project = Project.current_project(request.session)
	# load the template
	address_template = loader.get_template('people/address.html')
	# get the person
	person = Person.try_to_get(projects=project,pk=person_id)
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
	context = build_context(request,{
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
	# set variables
	project = Project.current_project(request.session)
	# load the template
	person_template = loader.get_template('people/address_to_relationships.html')
	# get the person
	person = Person.try_to_get(projects=project,pk=person_id)
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
	for relationship_to in get_relationships_to(person,project):
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
	context = build_context(request,{
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
	# check whether this is a post
	if request.method == 'POST':
		# create a venue search form
		addvenueform = VenueForm(request.POST)
		# validate the form and check whether we got a create request
		if addvenueform.is_valid() and request.POST['action'] == ('Create'):
			# get the related objects
			venue_type = Venue_Type.objects.get(pk=addvenueform.cleaned_data['venue_type'])
			street = Street.objects.get(pk=addvenueform.cleaned_data['street'])
			# create the object
			venue = Venue(
							name = addvenueform.cleaned_data['name'],
							venue_type = venue_type,
							street = street,
							building_name_or_number = addvenueform.cleaned_data['building_name_or_number'],
							contact_name = addvenueform.cleaned_data['contact_name'],
							phone = addvenueform.cleaned_data['phone'],
							mobile_phone = addvenueform.cleaned_data['mobile_phone'],
							email_address= addvenueform.cleaned_data['email_address'],
							website = addvenueform.cleaned_data['website'],
							price = addvenueform.cleaned_data['price'],
							facilities = addvenueform.cleaned_data['facilities'],
							opening_hours = addvenueform.cleaned_data['opening_hours'],
							notes = addvenueform.cleaned_data['notes'],
							)
			venue.save()
			# and redirect to the venue page
			return redirect('/venue/' + str(venue.pk))
	# otherwise we didn't get a post
	else:
		# create a blank form
		addvenueform = VenueForm()
	# set the context from the person based on person id
	context = build_context(request,{
				'addvenueform' : addvenueform,
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
	# check whether this is a post
	if request.method == 'POST':
		# create a venue search form
		editvenueform = VenueForm(request.POST, venue_id=venue_id)
		# validate the form and check whether we got an update request
		if editvenueform.is_valid() and request.POST['action'] == 'Update':
			# get the related objects
			venue_type = Venue_Type.objects.get(id=editvenueform.cleaned_data['venue_type'])
			street = Street.objects.get(id=editvenueform.cleaned_data['street'])
			# update the venue
			venue.name = editvenueform.cleaned_data['name']
			venue.venue_type = venue_type
			venue.building_name_or_number = editvenueform.cleaned_data['building_name_or_number']
			venue.street = street
			venue.contact_name = editvenueform.cleaned_data['contact_name']
			venue.phone = editvenueform.cleaned_data['phone']
			venue.mobile_phone = editvenueform.cleaned_data['mobile_phone']
			venue.email_address = editvenueform.cleaned_data['email_address']
			venue.website = editvenueform.cleaned_data['website']
			venue.price = editvenueform.cleaned_data['price']
			venue.facilities = editvenueform.cleaned_data['facilities']
			venue.opening_hours = editvenueform.cleaned_data['opening_hours']
			venue.notes = editvenueform.cleaned_data['notes']
			venue.save()
			# and redirect to the venue page
			return redirect('/venue/' + str(venue.pk))
	# otherwise we didn't get a post
	else:
		# create a form initialised from the record
		editvenueform = VenueForm(
										{
											'name' : venue.name,
											'venue_type' : venue.venue_type.pk,
											'building_name_or_number' : venue.building_name_or_number,
											'street' : venue.street.pk,
											'street_name' : '',
											'post_code' : '',
											'contact_name' : venue.contact_name,
											'phone' : venue.phone,
											'mobile_phone' : venue.mobile_phone,
											'email_address' : venue.email_address,
											'website' : venue.website,
											'price' : venue.price,
											'facilities' : venue.facilities,
											'opening_hours' : venue.opening_hours,
											'notes' : venue.notes,
										},
										venue_id = venue.pk
									)
	# set the context from the person based on person id
	context = build_context(request,{
				'editvenueform' : editvenueform,
				'venue' : venue
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
	# set the context
	context = build_context(request,{
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
	context = build_context(request,{
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
	# get the project
	project = Project.current_project(request.session)
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		addeventform = EventForm(request.POST,project=project)
		# check whether the form is valid
		if addeventform.is_valid():
			# create the event
			event = build_event(
								request,
								name = addeventform.cleaned_data['name'],
								description = addeventform.cleaned_data['description'],
								venue = addeventform.cleaned_data['venue'],
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
		addeventform = EventForm(project=project)
	# get the template
	addevent_template = loader.get_template('people/addevent.html')
	# set the context
	context = build_context(request,{
				'addeventform' : addeventform,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y')
				})
	# return the HttpResponse
	return HttpResponse(addevent_template.render(context=context, request=request))

@login_required
def event(request, event_id=0, page=1):
	# initialise variables
	results_per_page = 25
	page = int(page)
	project = Project.current_project(request.session)
	# load the template
	event_template = loader.get_template('people/event.html')
	# get the event
	event = Event.try_to_get(project=project,pk=event_id)
	# if the event doesn't exist, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# get the registrations for the event, filtered by project
	registrations = event.event_registration_set.all().order_by('person__last_name','person__first_name')
	registrations = registrations.filter(person__projects=project) if project else registrations
	# do the pagination and check whether we have mandatory roles
	for registration in registrations:
		registration.last_name = registration.person.last_name
	page_list = build_page_list(
								objects=registrations,
								page_length=results_per_page,
								attribute='last_name',
								length=3
								)
	previous_page = page - 1
	registrations= registrations[previous_page*results_per_page:page*results_per_page]
	# set the context
	context = build_context(request,{
				'event' : event,
				'registrations' : registrations,
				'page_list' : page_list,
				'this_page' : page,
				'project' : project,
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
	elif 'venue' in path:
		venue = event_group
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
	copy_POST['action'] = 'Search'
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
	# get the project
	project = Project.current_project(request.session)
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
		eventsearchform = EventSearchForm(request.POST,user=request.user,project=project)
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
			action = eventsearchform.cleaned_data['action']
			# conduct a search
			events = Event.search(
									name__icontains=name,
									date__gte=date_from,
									date__lte=date_to,
									event_type_id=int(event_type),
									event_type__event_category_id=int(event_category),
									venue__street__post_code__ward=int(ward),
									venue=int(venue),
									project=project
									).order_by('-date')
			# if we got a request for a search, do the pagination and add the project to events
			if eventsearchform.cleaned_data['action'] == 'Search':
				number_of_events = len(events)
				page = int(request.POST['page'])
				page_list = build_page_list(
										objects=events,
										page_length=results_per_page,
										attribute='date',
										)
				previous_page = page - 1
				events = events[previous_page*results_per_page:page*results_per_page]
			# otherwise check whether we got a request for a download
			elif 'Download' in action:
				# only superusers are allowed to perform downloads
				if not request.user.is_superuser:
					eventsearchform.add_error(None, 'You do not have permission to download files.')
				else:
					if action == 'Download Events':
						# get a file response using the search results and return it
						response = build_download_file('Events',objects=events)
					elif action == 'Download Registrations':
						# create a new query set of registrations, and build a file from it
						registrations = Event_Registration.objects.filter(event__in=events)
						registrations = registrations.filter(person__projects=project) if project else registrations
						response = build_download_file('Events and Registrations',objects=registrations)
					return response
		# otherwise we have incorrect dates
		else:
			# set a search error
			search_error = 'Dates must be entered in DD/MM/YYYY format.'
	# otherwise set a bank form
	else:
		# create the blank form
		eventsearchform = EventSearchForm(project=project)
	# get the template
	events_template = loader.get_template('people/events.html')
	# set the context
	context = build_context(request,{
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
				'search_attempted' : search_attempted,
				'project' : project,
				})
	# return the HttpResponse
	return HttpResponse(events_template.render(context=context, request=request))

@login_required
def edit_event(request, event_id=0):
	# initiliase variables
	venue = None
	# get the project
	project = Project.current_project(request.session)
	# try to get the event
	event = Event.try_to_get(project=project,pk=event_id)
	# if there isn't an event, crash to a banner
	if not event:
		return make_banner(request, 'Event does not exist.')
	# check whether this is a post
	if request.method == 'POST':
		# create a form
		editeventform = EventForm(
									request.POST,
									project=project
									)
		# check whether the entry is valid
		if editeventform.is_valid():
			# update the event object
			event.name = editeventform.cleaned_data['name']
			event.description = editeventform.cleaned_data['description']
			event.date = editeventform.cleaned_data['date']
			event.start_time = editeventform.cleaned_data['start_time']
			event.end_time = editeventform.cleaned_data['end_time']
			# validate the event type, crashing to a banner if it doesn't exist
			event_type = Event_Type.try_to_get(pk=editeventform.cleaned_data['event_type'])
			if event_type:
				event.event_type = event_type
			else:
				return make_banner(request, 'Event type does not exist.')
			# get and set the venue
			venue_id = editeventform.cleaned_data['venue']
			if venue_id != '0':
				venue = Venue.try_to_get(pk=venue_id)
				if not venue:
					return make_banner(request, 'Venue does not exist.')
			event.venue = venue
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
				if area_dict[area_id] or (venue and venue.street.post_code.ward.area.pk == area_id):
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
									project=project
									)
	# load the template
	edit_event_template = loader.get_template('people/edit_event.html')
	# set the context
	context = build_context(request,{
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
		excess_search_results = False
		total_search_results = 0
		# create a search form
		personsearchform = PersonNameSearchForm(request.POST)
		# validate the form
		if personsearchform.is_valid():
			# get the values from the form
			names = personsearchform.cleaned_data['names']
			include_people = personsearchform.cleaned_data['include_people']
			# conduct a search
			people = Person.search(
									project=Project.current_project(request.session),
									names = names,
									include_people = include_people
									)
			# remove the people who already have a registration
			search_results = remove_existing_registrations(event, people)
			# if we have over a hundred results, truncate and set a flag
			total_search_results = len(search_results)
			if total_search_results >= 100:
				search_results = search_results[:100]
				excess_search_results = True
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
		return personsearchform, addregistrationform, addpersonandregistrationform, search_results, search_keys, \
				excess_search_results, total_search_results

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

	def event_registration_registrations(event,this_page):
		# initialise variables
		registration_keys = ''
		registration_key_delimiter = ''
		editregistrationform = ''
		page_list = []
		results_per_page = 25
		# update the existing registrations: there may be new ones
		registrations = event.event_registration_set.all().order_by('person__last_name','person__first_name')
		# if there are registrations, create the form
		if registrations:
			# clear the registration keys
			registration_keys = ''
			# create the form
			editregistrationform = EditRegistrationForm(registrations = registrations)
			# do the pagination
			page_list = build_page_list(
										objects=registrations,
										page_length=results_per_page,
										attribute='person.last_name',
										length=3
										)
			previous_page = this_page - 1
			registrations = registrations[previous_page*results_per_page:this_page*results_per_page]
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
		return registrations, registration_keys, editregistrationform, page_list

	def event_registration_addpersonandregistration(event,request):
		# process the request to add a person and register them to this event
		# create a form
		addpersonandregistrationform = AddPersonAndRegistrationForm(request.POST)
		# validate the form
		if addpersonandregistrationform.is_valid():
			# create the person
			# we now need to create the person
			person = create_person(
									request = request,
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
	# get the project
	project = Project.current_project(request.session)
	# try to get the event
	event = Event.try_to_get(project=project,pk=event_id)
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
	edit_page = 1
	names = ''
	include_people = ''
	excess_search_results = False
	total_search_results = 0
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
		# start by getting the page
		if 'edit_page' in request.POST.keys():
			edit_page = int(request.POST['edit_page'])
		# now do the requsted function
		if request.POST['action'] == 'search':
			personsearchform, addregistrationform, addpersonandregistrationform, search_results, search_keys, \
				excess_search_results, total_search_results = event_registration_search(event,request)
			search_attempted = True
		elif request.POST['action'] == 'addregistration':
			event_registration_addregistration(event,request)
		elif request.POST['action'] == 'editregistration':
			event_registration_editregistration(event,request)
		elif request.POST['action'] == 'addpersonandregistration':
			addpersonandregistrationform = event_registration_addpersonandregistration(event,request)
	# build the form to edit registrations, along with an enriched list of existing registrations
	registrations, registration_keys, editregistrationform, edit_page_list = \
		event_registration_registrations(event,edit_page)
	# set the context from the person based on person id
	context = build_context(request,{
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
				'search_attempted' : search_attempted,
				'edit_page_list' : edit_page_list,
				'edit_page' : edit_page,
				'excess_search_results' : excess_search_results,
				'total_search_results' : total_search_results,
				})
	# return the response
	return HttpResponse(event_registration_template.render(context=context, request=request))

@login_required
def answer_questions(request,person_id=0):
	# this view enables people to answer a dynamic set of questions from the database
	# get the project
	project = Project.current_project(request.session)
	# load the template
	answer_questions_template = loader.get_template('people/answer_questions.html')
	# try to get the person, crashing to a banner if unsuccessful
	person = Person.try_to_get(projects=project,pk=person_id)
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the questions, with the answers included as an attribute
	question_sections, answer_flag = get_question_sections_and_answers(person,project=project)
	# process the action
	if request.method == 'POST':
		answerquestionsform = AnswerQuestionsForm(request.POST,question_sections=question_sections)
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
		answerquestionsform = AnswerQuestionsForm(question_sections=question_sections)
	# set the context
	context = build_context(request,{
				'person' : person,
				'answerquestionsform' : answerquestionsform
				})
	# return the response
	return HttpResponse(answer_questions_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def uploaddata(request):
	# initialise variables
	file_handler = False
	project = Project.current_project(request.session)
	update = False
	# define the records that need simple file handlers
	simple_file_handlers = {
							'Areas' : {'file_class' : Area, 'field_name' : 'area_name'},
							'Age Statuses' : {'file_class' : Age_Status, 'field_name' : 'status'},
							'Ethnicities' : {'file_class' : Ethnicity, 'field_name' : 'description'},
							'ABSS Types' : {'file_class' : ABSS_Type, 'field_name' : 'name'},
							'Activity Types' : {'file_class' : Activity_Type, 'field_name' : 'name'},
							'Venue Types' : {'file_class' : Venue_Type, 'field_name' : 'name'},
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
						'Venues' : Venues_File_Handler,
						'Venues for Events' : Venues_For_Events_File_Handler,
					}
	# define the records that have update file handlers
	update_file_handlers = {
							'Update People' : People_File_Handler,
							'Update Events' : Events_File_Handler,
							'Update Answers' : Answers_File_Handler,
							'Update Post Codes' : Post_Codes_File_Handler,
							}
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		uploaddataform = UploadDataForm(request.POST, request.FILES)
		# check whether the form is valid
		if uploaddataform.is_valid():
			# get the file and file type from the request
			file = TextIOWrapper(request.FILES['file'], encoding=request.encoding, errors='ignore')
			file_type = uploaddataform.cleaned_data['file_type']
			# handle a simple file
			if file_type in simple_file_handlers.keys():
				file_handler_kwargs = simple_file_handlers[file_type]
				file_handler = File_Handler(**file_handler_kwargs,project=project)
				file_handler.handle_uploaded_file(file)
			elif file_type in update_file_handlers.keys():
				file_handler = update_file_handlers[file_type](project=project)
				file_handler.handle_update(file)
				update = True
			else:
				# handle a complex file
				file_handler = file_handlers[file_type](project=project)
				file_handler.handle_uploaded_file(file)
	# otherwise create a fresh form
	else:
		# create the fresh form
		uploaddataform = UploadDataForm()
	# get the template
	upload_data_template = loader.get_template('people/upload_data.html')
	# set the context
	context = build_context(request,{
				'uploaddataform' : uploaddataform,
				'file_handler' : file_handler,
				'update' : update,
				})
	# return the HttpResponse
	return HttpResponse(upload_data_template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def downloaddata(request):
	# handle a request to download a file, depending on the file type requests
	# if we got a post, validate the form and create the file response, 
	if request.method == 'POST':
		downloaddataform = DownloadDataForm(request.POST)
		if downloaddataform.is_valid():
			response = build_download_file(
											downloaddataform.cleaned_data['file_type'],
											project=Project.current_project(request.session)
											)
			return response
	# otherwise create and return a blank form and page
	else:
		downloaddataform = DownloadDataForm()
		download_data_template = loader.get_template('people/download_data.html')
		context = build_context(request,{
					'downloaddataform' : downloaddataform,
					})
		response = HttpResponse(download_data_template.render(context=context, request=request))
	# return the result
	return response

@login_required
def activities(request,person_id=0):
	# allow the user to add or edit an activity for a person
	# get the project
	project = Project.current_project(request.session)
	# load the template
	activities_template = loader.get_template('people/activities.html')
	# get the person
	person = Person.try_to_get(projects=project,pk=person_id)
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
	# get the current activities, filtering by project
	activities = person.activity_set.order_by('-date')
	if project:
		activities = activities.filter(project=project)
	# set the context from the person based on person id
	context = build_context(request,{
				'activityform' : activityform,
				'activities' : activities,
				'person' : person,
				'default_date' : datetime.date.today().strftime('%d/%m/%Y')
				})
	# return the response
	return HttpResponse(activities_template.render(context=context, request=request))

@login_required
def dashboard(request,name=''):
	# initialise the variables
	dashboard = False
	dashboards = False
	dashboard_dates_form = False
	# if we have a dashboard name, attempt to get the dashboard
	if name:
		dashboard = Dashboard.try_to_get(name=name)
		if dashboard:
			dashboard.start_date = False
			dashboard.end_date = False
			dashboard.request = request
			template = loader.get_template('people/dashboard.html')
			if dashboard.date_controlled:
				if request.method == 'POST':
					dashboard_dates_form = DashboardDatesForm(request.POST)
					if dashboard_dates_form.is_valid():
						dashboard.start_date = dashboard_dates_form.cleaned_data['start_date']
						dashboard.end_date = dashboard_dates_form.cleaned_data['end_date']
				else:
					start_date, end_date = dashboard.get_dates()
					dashboard_dates_form = DashboardDatesForm(
																start_date=start_date,
																end_date=end_date
																)
	# if we don't have a dashboard, get the list of dashboards
	if not dashboard:
		dashboards = Dashboard.objects.all().order_by('title')
		template = loader.get_template('people/dashboards.html')
		# if the user is not a superuser, exclude all non-live dashboards
		if not request.user.is_superuser:
			dashboards = dashboards.exclude(live=False)
	# set the context
	context = build_context(request,{
								'dashboard' : dashboard,
								'dashboards' : dashboards,
								'show_title' : True,
								'dashboarddatesform' : dashboard_dates_form
								})
	# return the HttpResponse
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def download_dashboard(request,name):
	# attempt to get the dashboard, crashing to a banner if it doesn't exist
	dashboard = Dashboard.try_to_get(name=name)
	if not dashboard:
		return make_banner(request, 'Dashboard does not exist.')
	# create the http response
	response = HttpResponse(dashboard.get_json(),content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="' + name + '.json"'
	# return the result
	return response

@login_required
def chart(request,name=''):
	# initialise the variables
	chart = False
	chart_display = False
	charts = False
	chart_dates_form = False
	start_date = False
	end_date = False
	# if we have a chart name, attempt to get the chart
	if name:
		chart = Chart.try_to_get(name=name)
		template = loader.get_template('people/chart.html')
		# figure out whether there are any date filters
		filters = chart.filters.filter(filter_type='period')
		super_filters = chart.super_filters.filter(filter_type='period')
		if filters.exists() or super_filters.exists():
			# because we have date filters, set up and process the date form 
			if request.method == 'POST':
				chart_dates_form = DashboardDatesForm(request.POST)
				if chart_dates_form.is_valid():
					start_date = chart_dates_form.cleaned_data['start_date']
					end_date = chart_dates_form.cleaned_data['end_date']
			else:
				# get the first period from the filters
				if filters.exists():
					this_filter = filters.first()
				else:
					this_filter = super_filters.first()
				start_date, end_date = get_period_dates(this_filter.period)
				chart_dates_form = DashboardDatesForm(
														start_date=start_date,
														end_date=end_date
														)
		# set the request
		chart.request = request
		# get the chart to display
		chart_display = chart.get_chart(start_date=start_date,end_date=end_date)
	# if we don't have a chart, get the list of charts
	if not chart:
		charts = Chart.objects.all().order_by('title','name')
		template = loader.get_template('people/charts.html')
	# set the context
	context = build_context(request,{
								'chart' : chart,
								'charts' : charts,
								'chart_display' : chart_display,
								'chartdatesform' : chart_dates_form,
								})
	# return the HttpResponse
	return HttpResponse(template.render(context=context, request=request))

@login_required
def settings(request,):
	# get the project
	project = Project.current_project(request.session)
	# get the profile
	profile = Profile.try_to_get(user=request.user)
	# load the template
	template = loader.get_template('people/settings.html')
	# set the context
	context = build_context(
							request,
								{
								'profile' : profile,
								'site' : Site.objects.all().first(),
								'project' : project,
								}
							)
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def display_qrcode(request,):
	# initialise variables
	user = request.user
	device = get_device(user)
	# load the template
	template = loader.get_template('people/display_qrcode.html')
	# create a url for the qrcode image
	qrcode_image_url = reverse('display_qrcode_image')
	# set the context
	context = build_context(request,{
								'device' : device,
								'qrcode_image_url' : qrcode_image_url
							})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def display_qrcode_image(request,):
	# initialise variables
	user = request.user
	device = get_device(user)
	# create the image and return it as a response
	img = qrcode.make(device.config_url,image_factory=qrcode.image.svg.SvgImage)
	response = HttpResponse(content_type='image/svg+xml')
	img.save(response)
	return response
	
@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def login_data(request,):
	# load the template
	template = loader.get_template('people/login_data.html')
	# set the context
	context = build_context(request,{
								'profiles' : Profile.objects.all().order_by('user__username'),
							})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def change_password(request):
	# this view is used to change a user's password
	# initialise variables
	template = loader.get_template('people/change_password.html')
	user = request.user
	# process the post
	if request.method == 'POST':
		changepasswordform = ChangePasswordForm(request.POST,user=user)
		# validate the form
		if changepasswordform.is_valid():
			# update the password for the user
			user.set_password(changepasswordform.cleaned_data['new_password'])
			user.save()
			# and redirect to the home page
			return redirect('index')
	# otherwsie create a fresh form
	else:
		changepasswordform = ChangePasswordForm(user=user)
	# set the context from the person based on person id
	context = build_context(request,{
				'changepasswordform' : changepasswordform,
				'user' : user
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

def reset_password(request,reset_code):
	# this view is used to reset a user's password via a link sent by mail
	# initialise variables
	reset = False
	# check that the code is valid and has not timed out
	profile = Profile.try_to_get(reset_code=reset_code)
	if not profile:
		return make_banner(request, 'The link is not valid',public=True)
	if profile.reset_timeout and timezone.now() > profile.reset_timeout:
		return make_banner(request, 'The link is no longer valid',public=True)
	# process the post
	if request.method == 'POST':
		form = ResetForgottenPasswordForm(request.POST,reset_code=reset_code)
		# validate the form
		if form.is_valid():
			# update the password for the user and clear the reset variables
			user = profile.user
			user.set_password(form.cleaned_data['new_password'])
			user.save()
			profile.reset_code = ''
			profile.reset_timeout = None
			profile.save()
			# and flag success
			reset = True
			auth_log(user=user,reset_successful=True)
	# otherwise create a fresh form
	else:
		form = ResetForgottenPasswordForm(reset_code=reset_code)
	# set the context from the person based on person id
	context = build_context(request,{
				'resetpasswordform' : form,
				'reset' : reset,
				})
	# build and return the response
	template = loader.get_template('people/reset_password.html')
	return HttpResponse(template.render(context=context, request=request))

@method_decorator(login_required, name='dispatch')
class Document_Link_List(ListView):
	model = Document_Link
	template_name = 'people/document_links.html'
	context_object_name = 'document_links'

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		# add in the standard extra context
		context = build_context(self.request,context)
		return context

@login_required
def select_project(request):
	# see whether we got a post or not
	if request.method == 'POST':
		# load and validate form
		selectprojectform = SelectProjectForm(request.POST,user=request.user,all_projects=True)
		# if the form is valid, set the project id in the session
		if selectprojectform.is_valid():
			request.session['project_id'] = selectprojectform.cleaned_data['project_id']
			# redirect to the home page in the new project
			return redirect('index')
	# otherwise create a fresh form
	else:
		# create the fresh form
		selectprojectform = SelectProjectForm(user=request.user,all_projects=True)
	# get the template
	template = loader.get_template('people/select_project.html')
	# set the context
	context = build_context(request,{
				'selectprojectform' : selectprojectform,
				})
	# return the HttpResponse
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def manage_membership(request):
	# return a banner if projects are not active
	site = Site.objects.first()
	if not site.projects_active:
		return make_banner(request, 'Projects are not active for this site')
	# set a blank list
	people = []
	# and a blank page_list
	pages = []
	page_list = []
	# and zero search results
	number_of_people = 0
	this_page = 0
	search_attempted = False
	build_results = False
	# and blank search terms
	names = ''
	keywords = ''
	role_type = 0
	ABSS_type = 0
	membership_type = 0
	age_status = 0
	trained_role = 'none'
	ward = 0
	include_people = 'in_project'
	children_ages = ''
	project_id = 0
	# set a blank search_error
	search_error = ''
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		personsearchform = PersonSearchForm(request.POST,user=request.user,membership=True)
		# set the flag to show that a search was attempted
		search_attempted = True
		# validate the form
		if personsearchform.is_valid():
			# get the fields
			names = personsearchform.cleaned_data['names']
			keywords = personsearchform.cleaned_data['keywords']
			role_type = personsearchform.cleaned_data['role_type']
			age_status = personsearchform.cleaned_data['age_status']
			trained_role = personsearchform.cleaned_data['trained_role']
			ward = personsearchform.cleaned_data['ward']
			include_people = personsearchform.cleaned_data['include_people']
			children_ages = personsearchform.cleaned_data['children_ages']
			project_id = personsearchform.cleaned_data['project_id']
			project = Project.try_to_get(pk=project_id)
			# set the membership type or ABSS type dependent on whether we have a project
			if project:
				membership_type = personsearchform.cleaned_data['membership_type']
			else:
				ABSS_type = personsearchform.cleaned_data['membership_type']
			# conduct a search
			people = Person.search(
									project=project,
									names=names,
									keywords=keywords,
									default_role_id=role_type,
									ABSS_type_id=ABSS_type,
									membership__membership_type_id=membership_type,
									age_status_id=age_status,
									trained_role=trained_role,
									street__post_code__ward_id=ward,
									include_people=include_people,
									children_ages=children_ages,
									).order_by('last_name','first_name')
			# if we got a request for a move, do the move
			if personsearchform.cleaned_data['action'] == 'Move':
				target_project = Project.try_to_get(pk=personsearchform.cleaned_data['target_project_id'])
				with_dates = True if personsearchform.cleaned_data['date_type'] == 'with_dates' else False
				build_results = build_memberships(
													people=people,
													project = target_project,
													action = personsearchform.cleaned_data['move_type'],
													with_dates= with_dates,
													)
			# do the pagination
			number_of_people = len(people)
			this_page = int(request.POST['page'])
			page_list = build_page_list(
										objects=people,
										page_length=results_per_page,
										attribute='last_name',
										length=3
										)
			previous_page = this_page - 1
			people = people[previous_page*results_per_page:this_page*results_per_page]
	# otherwise set a blank form
	else:
		personsearchform = PersonSearchForm(membership=True)
	# build and return the response
	template = loader.get_template('people/manage_membership.html')
	context = build_context(request,{
				'managemembershipsearchform' : personsearchform,
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
				'search_attempted' : search_attempted,
				'children_ages' : children_ages,
				'project_id' : project_id,
				'build_results' : build_results
				})
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def manage_unassigned_activities(request):
	# initialise variables
	activities_assigned = 0
	project = None
	# if we got a post, validate the form and update the activities
	if request.method == 'POST':
		# load and validate form
		selectprojectform = SelectProjectForm(request.POST,user=request.user,all_projects=False)
		# if the form is valid, get the project and assign the activities to the project
		if selectprojectform.is_valid():
			project = Project.objects.get(id=int(selectprojectform.cleaned_data['project_id']))
			for activity in Activity.objects.filter(project=None):
				activity.project = project
				activity.save()
				activities_assigned += 1
	# otherwise create a fresh form
	else:
		selectprojectform = SelectProjectForm(user=request.user,all_projects=False)
	# get the template
	template = loader.get_template('people/manage_unassigned_activities.html')
	# set the context
	context = build_context(request,{
				'selectprojectform' : selectprojectform,
				'activities_assigned' : activities_assigned,
				'unassigned_activities' : Activity.objects.filter(project=None).count(),
				'project' : project,
				})
	# return the HttpResponse
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def manage_project_events(request):
	# return a banner if projects are not active
	site = Site.objects.first()
	if not site.projects_active:
		return make_banner(request, 'Projects are not active for this site')
	# get the project
	project = Project.current_project(request.session)
	# set a blank list
	events = []
	# and a blank page_list
	page_list = []
	page = 0
	# and blank search terms
	name = ''
	event_type = 0
	search_attempted = False
	build_results = False
	# set a blank search_error
	search_error = ''
	# and a zero number of results
	number_of_events = 0
	# set the results per page
	results_per_page = 25
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		form = ManageProjectEventsSearchForm(request.POST,user=request.user)
		# set the flag to show that a search was attempted
		search_attempted = True
		# validate the form
		if form.is_valid():
			# get the values
			name = form.cleaned_data['name']
			event_type = form.cleaned_data['event_type']
			project_id = form.cleaned_data['project_id']
			project = Project.try_to_get(pk=project_id) if project_id else ''
			action = form.cleaned_data['action']
			# conduct a search
			events = Event.search(
									name__icontains=name,
									event_type_id=int(event_type),
									project=project
									).order_by('name')
			# if we got a request for a move, do the move
			if form.cleaned_data['action'] == 'Move':
				target_project = Project.try_to_get(pk=form.cleaned_data['target_project_id'])
				build_results = build_project_events(
													events=events,
													project = target_project,
													action = form.cleaned_data['move_type'],
													)
			# do the pagination
			number_of_events = len(events)
			page = int(request.POST['page'])
			page_list = build_page_list(
									objects=events,
									page_length=results_per_page,
									attribute='name',
									length=3
									)
			previous_page = page - 1
			events = events[previous_page*results_per_page:page*results_per_page]
	else:
		# create the blank form
		form = ManageProjectEventsSearchForm()
	# get the template
	events_template = loader.get_template('people/manage_project_events.html')
	# set the context
	context = build_context(request,{
				'events' : events,
				'manageprojecteventssearchform' : form,
				'name' : name,
				'event_type' : event_type,
				'page_list' : page_list,
				'search_error' : search_error,
				'build_results' : build_results,
				'number_of_events' : number_of_events,
				'this_page' : page,
				'search_attempted' : search_attempted
				})
	# return the HttpResponse
	return HttpResponse(events_template.render(context=context, request=request))

@login_required
def add_case_notes(request,person_id=0):
	# this view is used to create new case notes for a person
	# get the project
	project = Project.current_project(request.session)
	# load the template
	template = loader.get_template('people/case_notes.html')
	# get the person
	person = Person.try_to_get(projects=project,pk=person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		casenotesform = CaseNotesForm(request.POST)
		if casenotesform.is_valid():
			title = casenotesform.cleaned_data['title']
			date = casenotesform.cleaned_data['date']
			notes = casenotesform.cleaned_data['notes']
			case_notes = Case_Notes(
									person = person,
									project = project if project else None,
									user = request.user,
									title = title,
									notes = notes,
									date = date
									)
			case_notes.save()
			# redirect to the profile of the person
			return redirect('/view_case_notes/' + str(person.pk))
	# otherwise we didn't get a post
	else:
		# create a blank form
		casenotesform = CaseNotesForm()
	# set the context
	context = build_context(request,{
				'casenotesform' : casenotesform,
				'person' : person,
				'action_desc' : 'Add'
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def edit_case_notes(request,case_notes_id=0):
	# this view is used to create new case notes for a person
	# get the project
	project = Project.current_project(request.session)
	# load the template
	template = loader.get_template('people/case_notes.html')
	# get the case notes record
	case_notes = Case_Notes.try_to_get(pk=case_notes_id)
	# if the case notes doesn't exist, crash to a banner
	if not case_notes:
		return make_banner(request, 'Case notes do not exist.')
	# check whether the user is in the right project and has permissions to access the case note
	if ( ( project and case_notes.project != project ) or
			( request.user != case_notes.user and not request.user.is_superuser ) ):
		return make_banner(request, 'You do not have permission to edit this case note.')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		casenotesform = CaseNotesForm(request.POST)
		if casenotesform.is_valid():
			case_notes.title = casenotesform.cleaned_data['title']
			case_notes.date = casenotesform.cleaned_data['date']
			case_notes.notes = casenotesform.cleaned_data['notes']
			case_notes.save()
			# redirect to the profile of the person
			return redirect('/view_case_notes/' + str(case_notes.person.pk))
	# otherwise we didn't get a post
	else:
		# create a form, passing existing values as a dict
		case_notes_dict = {
							'title' : case_notes.title,
							'date' : case_notes.date,
							'notes' : case_notes.notes
							}
		casenotesform = CaseNotesForm(case_notes_dict)
	# set the context
	context = build_context(request,{
				'casenotesform' : casenotesform,
				'person' : person,
				'action_desc' : 'Edit'
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def view_case_notes(request,person_id=0):
	# this view is used to view all case notes
	# get the project
	project = Project.current_project(request.session)
	# load the template
	template = loader.get_template('people/view_case_notes.html')
	# attempt to get the person, crashing to a banner on failure
	person = Person.try_to_get(projects=project,pk=person_id)
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the case notes, filtered by project if necessary
	if project:
		case_notes = Case_Notes.objects.filter(person=person,project=project)
	else:
		case_notes = Case_Notes.objects.filter(person=person)
	# set the context
	context = build_context(request,{
				'person' : person,
				'case_notes' : case_notes,
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def survey_series(request,survey_series_id=0):
	# this view is used to create or amend a survey series
	# this view can only be called if a current project is selected
	project = Project.current_project(request.session)
	if not project:
		return make_banner(request, 'No project selected: survey series can only be created within a project.')
	# if we have a survey series, then it must be valid
	survey_series = False
	action_desc = 'Add'
	if survey_series_id:
		survey_series = Survey_Series.try_to_get(project=project,pk=survey_series_id)
		action_desc = 'Edit'
		if not survey_series:
			return make_banner(request, 'Survey series does not exist.')
	# load the template
	template = loader.get_template('people/survey_series.html')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		surveyseriesform = SurveySeriesForm(request.POST)
		if surveyseriesform.is_valid(project=project,survey_series=survey_series):
			name = surveyseriesform.cleaned_data['name']
			description = surveyseriesform.cleaned_data['description']
			if survey_series:
				survey_series.name = name
				survey_series.description = description
			else:
				survey_series = Survey_Series(
												name = name,
												project = project,
												description = description,
												date_created = datetime.date.today(),
												)
			survey_series.save()
			# redirect to the survey series page
			return redirect('/survey_series_list')
	# otherwise we didn't get a post
	else:
		# create a blank or filled form depending on whether we are editing or creating
		if survey_series:
			# create a form, passing existing values as a dict
			survey_series_dict = {
								'name' : survey_series.name,
								'description' : survey_series.description,
								}
			surveyseriesform = SurveySeriesForm(survey_series_dict)
		else:
			surveyseriesform = SurveySeriesForm()
	# set the context
	context = build_context(request,{
				'surveyseriesform' : surveyseriesform,
				'survey_series' : survey_series,
				'action_desc' : action_desc
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def survey_series_list(request):
	# this view is used to create or amend a survey series
	# this view can only be called if a current project is selected
	project = Project.current_project(request.session)
	if not project:
		return make_banner(request, 'No project selected: survey series can only be viewed within a project.')
	# get the survey series list
	survey_series_list = Survey_Series.objects.filter(project=project)
	# load the template
	template = loader.get_template('people/survey_series_list.html')
	# set the context
	context = build_context(request,{
				'survey_series_list' : survey_series_list,
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def survey(request,survey_series_id=0,survey_id=0):
	# this view is used to create or amend a survey
	# this view can only be called if a current project is selected
	project = Project.current_project(request.session)
	if not project:
		return make_banner(request, 'No project selected: survey can only be created within a project.')
	# we need a valid survey series
	survey_series = Survey_Series.try_to_get(project=project,pk=survey_series_id)
	if not survey_series:
		return make_banner(request, 'Survey series does not exist.')
	# if we have a survey id it must be valid
	survey = False
	action_desc = 'Add'
	if survey_id:
		survey = Survey.try_to_get(survey_series=survey_series,pk=survey_id)
		action_desc = 'Edit'
		if not survey:
			return make_banner(request, 'Survey does not exist.')
	# load the template
	template = loader.get_template('people/survey.html')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		surveyform = SurveyForm(request.POST,survey=survey,user=request.user)
		if surveyform.is_valid(survey_series=survey_series,survey=survey):
			if surveyform.cleaned_data['action'] == 'Submit':
				name = surveyform.cleaned_data['name']
				description = surveyform.cleaned_data['description']
				if survey:
					survey.name = name
					survey.description = description
					survey.save()
				else:
					survey = build_survey(
											name = name,
											survey_series = survey_series,
											description = description,
											)
				# redirect to the survey series page
				return redirect('/survey_series/' + str(survey_series.pk))
			# if we have a download request, also 
			elif surveyform.cleaned_data['action'] == 'Download':
				if not request.user.is_superuser:
					surveyform.add_error(None, 'You do not have permission to download files.')
				else:
					response = build_download_file(
													'Survey Submissions',
													file_name = str(survey),
													objects=survey.survey_submission_set.all()
													)
					return response
	# otherwise we didn't get a post
	else:
		# create a blank or filled form depending on whether we are editing or creating
		if survey:
			# create a form, passing existing values as a dict
			survey_dict = {
								'name' : survey.name,
								'description' : survey.description,
								}
			surveyform = SurveyForm(survey_dict,survey=survey,user=request.user)
		else:
			surveyform = SurveyForm(user=request.user)
	# set the context
	context = build_context(request,{
										'surveyform' : surveyform,
										'action_desc' : action_desc,
										'survey_series' : survey_series,
										'survey' : survey			
										})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def survey_section(request,survey_id=0,survey_section_id=0):
	# this view is used to create or amend a survey section
	# this view can only be called if a current project is selected
	project = Project.current_project(request.session)
	if not project:
		return make_banner(request, 'No project selected: survey can only be managed within a project.')
	# we need a valid survey
	survey = Survey.try_to_get(survey_series__project=project,pk=survey_id)
	if not survey_series:
		return make_banner(request, 'Survey series does not exist.')
	# if we have a survey section id it must be valid
	survey_section = False
	action_desc = 'Add'
	if survey_section_id:
		survey_section = Survey_Section.try_to_get(survey=survey,pk=survey_section_id)
		action_desc = 'Edit'
		if not survey_section:
			return make_banner(request, 'Survey section does not exist.')
	# load the template
	template = loader.get_template('people/survey_section.html')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		surveysectionform = SurveySectionForm(request.POST)
		if surveysectionform.is_valid(survey=survey,survey_section=survey_section):
			name = surveysectionform.cleaned_data['name']
			order = surveysectionform.cleaned_data['order']
			if survey_section:
				survey_section.name = name
				survey_section.order = order
				survey_section.save()
			else:
				survey_section = Survey_Section.objects.create(
																name = name,
																survey = survey,
																order = order,
																)
			# redirect to the survey page
			return redirect('/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
	# otherwise we didn't get a post
	else:
		# create a blank or filled form depending on whether we are editing or creating
		if survey_section:
			# create a form, passing existing values as a dict
			survey_section_dict = {
									'name' : survey_section.name,
									'order' : survey_section.order,
									}
			surveysectionform = SurveySectionForm(survey_section_dict)
		else:
			surveysectionform = SurveySectionForm()
	# set the context
	context = build_context(request,{
				'surveysectionform' : surveysectionform,
				'action_desc' : action_desc,
				'survey_section' : survey_section,
				'survey' : survey
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
@user_passes_test(lambda user: user.is_superuser, login_url='/', redirect_field_name='')
def survey_question(request,survey_section_id=0,survey_question_id=0):
	# this view is used to create or amend a survey question
	# this view can only be called if a current project is selected
	project = Project.current_project(request.session)
	if not project:
		return make_banner(request, 'No project selected: survey can only be managed within a project.')
	# we need a valid survey section
	survey_section = Survey_Section.try_to_get(survey__survey_series__project=project,pk=survey_section_id)
	if not survey_section:
		return make_banner(request, 'Survey section does not exist.')
	# if we have a survey question id it must be valid
	survey_question = False
	action_desc = 'Add'
	if survey_question_id:
		survey_question = Survey_Question.try_to_get(survey_section=survey_section,pk=survey_question_id)
		action_desc = 'Edit'
		if not survey_question:
			return make_banner(request, 'Survey question does not exist.')
	# load the template
	template = loader.get_template('people/survey_question.html')
	# if this is a post, validate the form and attempt to create the record
	if request.method == 'POST':
		surveyquestionform = SurveyQuestionForm(request.POST)
		if surveyquestionform.is_valid(survey_section=survey_section,survey_question=survey_question):
			question = surveyquestionform.cleaned_data['question']
			number = surveyquestionform.cleaned_data['number']
			options = surveyquestionform.cleaned_data['options']
			survey_question_type = Survey_Question_Type.objects.get(pk=surveyquestionform.cleaned_data['question_type'])
			if survey_question:
				survey_question.question = question
				survey_question.number = number
				survey_question.survey_question_type = survey_question_type
				survey_question.options = options
				survey_question.save()
			else:
				survey_question = Survey_Question.objects.create(
																survey_section = survey_section,
																question = question,
																number = number,
																survey_question_type = survey_question_type,
																options = options,
																)
			# redirect to the survey page
			return redirect('/survey/' + str(survey_section.survey.survey_series.pk) + '/' + str(survey_section.survey.pk))
	# otherwise we didn't get a post
	else:
		# create a blank or filled form depending on whether we are editing or creating
		if survey_question:
			# create a form, passing existing values as a dict
			survey_question_dict = {
									'question' : survey_question.question,
									'number' : survey_question.number,
									'question_type' : str(survey_question.survey_question_type.pk),
									'options' : survey_question.options,
									}
			surveyquestionform = SurveyQuestionForm(survey_question_dict)
		else:
			surveyquestionform = SurveyQuestionForm()
	# set the context
	context = build_context(request,{
				'surveyquestionform' : surveyquestionform,
				'action_desc' : action_desc,
				'survey_question' : survey_question,
				'survey_section' : survey_section,
				'survey' : survey_section.survey,
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

@login_required
def submit_survey(request,person_id=0,survey_id=0):
	# this view enables people to answer a dynamic set of questions from the database
	# get the project
	project = Project.current_project(request.session)
	# load the template
	template = loader.get_template('people/submit_survey.html')
	# try to get the person adn the survey, crashing to a banner if unsuccessful
	person = Person.try_to_get(projects=project,pk=person_id)
	if not person:
		return make_banner(request, 'Person does not exist.')
	survey = Survey.try_to_get(survey_series__project=project,pk=survey_id)
	if not survey:
		return make_banner(request, 'Survey does not exist.')
	# get a previous survey submission if there was one
	survey_submission = Survey_Submission.try_to_get(person=person,survey=survey)
	# process the action
	if request.method == 'POST':
		submitsurveyform = SubmitSurveyForm(request.POST,survey=survey,survey_submission=survey_submission)
		# if we don't have a survey submssion, create one
		if not survey_submission:
			survey_submission = Survey_Submission.objects.create(
																	survey = survey,
																	person = person,
																	date =datetime.date.today()
																	)
		# go through the fields
		for field in submitsurveyform.fields:
			# get the question from the id in the field name
			survey_question_id = int(extract_id(field))
			survey_question = Survey_Question.objects.get(pk=survey_question_id)
			# set the answer value
			if survey_question.survey_question_type.options_required:
				range_answer = int(submitsurveyform.data[field])
				text_answer = ''
			else:
				text_answer = submitsurveyform.data[field]
				range_answer = 0
			# check whether we have an existing answer, then update if we do, or create if we don't
			survey_answer = Survey_Answer.try_to_get(
														survey_submission=survey_submission,
														survey_question=survey_question,
													)
			if survey_answer:
				survey_answer.range_answer = range_answer
				survey_answer.text_answer = text_answer
				survey_answer.save()
			else:
				survey_answer = Survey_Answer.objects.create(
																survey_submission=survey_submission,
																survey_question=survey_question,
																range_answer=range_answer,
																text_answer=text_answer,
																)
		# send the user back to the main person page
		return redirect('/person/' + str(person.pk))
	# otherwise create an empty form
	else:
		submitsurveyform = SubmitSurveyForm(survey=survey,survey_submission=survey_submission)
	# set the context
	context = build_context(request,{
				'person' : person,
				'survey' : survey,
				'submitsurveyform' : submitsurveyform
				})
	# return the response
	return HttpResponse(template.render(context=context, request=request))

