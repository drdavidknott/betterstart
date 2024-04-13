from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note, \
							Trained_Role, Activity_Type, Activity, Dashboard, Column, Panel, Panel_In_Column, \
							Panel_Column, Panel_Column_In_Panel, Filter_Spec, Column_In_Dashboard, \
							Venue, Venue_Type, Site, Invitation, Invitation_Step, Invitation_Step_Type, \
							Terms_And_Conditions, Profile, Chart, Document_Link, Project, Membership, \
							Project_Permission, Membership_Type, Project_Event_Type
import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.oath import totp
from django.utils import timezone
from django.core import mail
import json


def set_up_people_base_data():
	# set up base data needed to do tests for people
	# first the ethnicities
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	second_test_ethnicity = Ethnicity.objects.create(description='second_test_ethnicity')
	test_ethnicity = Ethnicity.objects.create(description='Prefer not to say',default=True)
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
	# create test role types
	test_role = Role_Type.objects.create(role_type_name='test_role_type',
											use_for_events=True,
											use_for_people=True)
	second_test_role = Role_Type.objects.create(role_type_name='second_test_role_type',use_for_events=True,use_for_people=True)
	unknown_test_role = Role_Type.objects.create(role_type_name='UNKNOWN',use_for_events=True,use_for_people=True)
	age_test_role = Role_Type.objects.create(role_type_name='age_test_role',use_for_events=True,use_for_people=True)
	adult_test_role = Role_Type.objects.create(role_type_name='adult_test_role',use_for_events=True,use_for_people=True)
	# create test ABSS types
	test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
	second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
	test_ABSS_type = ABSS_Type.objects.create(name='ABSS beneficiary',default=True)
	# and a test membership type
	test_membership_type = Membership_Type.objects.create(name='test_membership_type',default=True)
	# create test age statuses
	test_age_status = Age_Status.objects.create(status='Adult',default_role_type=test_role)
	test_age_status_2 = Age_Status.objects.create(status='Child under four',default_role_type=test_role,maximum_age=4)
	test_age_status_3 = Age_Status.objects.create(status='Default role age status',default_role_type=age_test_role,default_role_type_only=True)
	child_over_four = Age_Status.objects.create(status='Child over four',default_role_type=age_test_role,default_role_type_only=True,maximum_age=18)
	# allow the role type of each age status
	test_age_status.role_types.add(test_role)
	test_age_status.role_types.add(second_test_role)
	test_age_status.role_types.add(unknown_test_role)
	test_age_status.role_types.add(adult_test_role)
	test_age_status_2.role_types.add(test_role)
	test_age_status_2.role_types.add(second_test_role)
	test_age_status_2.role_types.add(unknown_test_role)
	# set up test activity types
	test_activity_type_1 = Activity_Type.objects.create(name='Test activity type 1')
	test_activity_type_2 = Activity_Type.objects.create(name='Test activity type 2')

def set_up_test_people(
						name_root,
						role_type='test_role_type',
						number=1,
						ABSS_type='test_ABSS_type',
						age_status='Adult',
						project=False,
						):
	# create the number of people needed
	for n in range(number):
		# create a person
		test_person = Person.objects.create(
											first_name = name_root + str(n),
											middle_names = 'Middle Names',
											last_name = name_root + str(n),
											email_address = 'test@test.com',
											date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
											gender = 'Gender',
											notes = 'test notes',
											default_role = Role_Type.objects.get(role_type_name=role_type),
											pregnant = False,
											due_date = None,
											ABSS_type = ABSS_Type.objects.get(name=ABSS_type),
											age_status = Age_Status.objects.get(status=age_status),
											capture_type = Capture_Type.objects.get(capture_type_name='test_capture_type'),
											ethnicity = Ethnicity.objects.get(description='test_ethnicity')
											)
		# create a role history entry
		Role_History.objects.create(
									person = test_person,
									role_type = Role_Type.objects.get(role_type_name=role_type)
									)
		# add a membership if we have a project
		if project:
			Membership.objects.create(
										person=test_person,
										project=project,
										membership_type=Membership_Type.objects.get(default=True)
										)

def set_up_test_user(username='testuser',is_superuser=False):
	# create a test user and profile
	test_user = User.objects.create_user(
											username=username,
											password='testword',
											is_superuser=is_superuser,
										)
	profile = Profile.objects.create(user=test_user)
	# return the user
	return test_user

def set_up_test_project_permission(username,project_name,default=True):
	# get the user
	profile = Profile.objects.get(user__username=username)
	# create the project
	project = Project.objects.create(name=project_name)
	# add the membership
	Project_Permission.objects.create(
										profile=profile,
										project=project,
										default=default
									)

def set_up_test_superuser():
	# create a test superuser and profile
	test_superuser = User.objects.create_user(
												username='testsuper',
												first_name='test',
												last_name='super',
												password='superword',
												is_superuser=True
												)
	profile = Profile.objects.create(user=test_superuser)
	# return the user
	return test_superuser

def set_up_event_base_data():
	# create an event category
	test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
	# create an event type
	test_event_type = Event_Type.objects.create(
												name = 'test_event_type',
												description = 'type desc',
												event_category = test_event_category)

def set_up_relationship_base_data():
	# create test relationship type records
	Relationship_Type.objects.create(
										relationship_type='parent',
										relationship_counterpart='child',
										use_for_invitations=True,
										)
	Relationship_Type.objects.create(relationship_type='child', relationship_counterpart='parent')
	Relationship_Type.objects.create(relationship_type='from', relationship_counterpart='to')
	Relationship_Type.objects.create(relationship_type='to', relationship_counterpart='from')
	# allow the relationship type for each age status
	for age_status in Age_Status.objects.all():
		# go through the relationship types
		for relationship_type in Relationship_Type.objects.all():
			# add the relationship type to the age status
			age_status.relationship_types.add(relationship_type)

def set_up_address_base_data():
	# create records required for an post code and street
	area = Area.objects.create(area_name='Test area',use_for_events=True)
	area_2 = Area.objects.create(area_name='Test area 2',use_for_events=True)
	area_3 = Area.objects.create(area_name='Test area 3',use_for_events=True)
	ward = Ward.objects.create(ward_name='Test ward',area=area)
	ward_2 = Ward.objects.create(ward_name='Test ward 2',area=area_2)
	ward_3 = Ward.objects.create(ward_name='Unknown',area=area)

def set_up_test_post_codes(
						name_root,
						ward='Test ward',
						number=1
						):
	# create the number of post codes needed
	for n in range(number):
		# create a post code
		Post_Code.objects.create(
									post_code = name_root + str(n),
									ward = Ward.objects.get(ward_name=ward)
									)

def set_up_test_streets(
						name_root,
						post_code,
						number=1
						):
	# create the number of streets needed
	for n in range(number):
		# create a street
		Street.objects.create(
									name = name_root + str(n),
									post_code = Post_Code.objects.get(post_code=post_code)
									)

def set_up_venue_base_data():
	# create records for venues - depends on address base data having been set up first
	set_up_test_post_codes('TV1',number=1)
	set_up_test_streets('venue_street','TV10',1)
	test_venue_type = Venue_Type.objects.create(name='test_venue_type')
	test_venue = Venue.objects.create(
										name = 'test_venue',
										building_name_or_number = '123',
										venue_type = test_venue_type,
										street = Street.objects.get(name='venue_street0')
										)

def set_up_test_events(name_root,event_type,number,date='2019-01-01',ward=None,project=None):
	# set up the number of people asked for
	# create the number of people needed
	for n in range(number):
		# create an event
		test_event = Event.objects.create(
											name = name_root + str(n),
											description = 'Test event description',
											event_type = event_type,
											ward = ward,
											date = datetime.datetime.strptime(date,'%Y-%m-%d'),
											start_time = datetime.datetime.strptime('10:00','%H:%M'),
											end_time = datetime.datetime.strptime('11:00','%H:%M'),
											location = 'Test location',
											project = project,
											)

def set_up_test_questions(name_root,number=1,notes=False,notes_label='',use_for_invitations=False):
	# set up the number of test questions asked for
	for n in range(number):
		# create a question
		test_question = Question.objects.create(
											 question_text = name_root + str(n),
											 notes = notes,
											 notes_label = notes_label,
											 use_for_invitations = use_for_invitations
											)

def set_up_test_options(name_root,question,number=1):
	# set up the number of test options asked for
	for n in range(number):
		# create an option
		test_option = Option.objects.create(
											 option_label = name_root + str(n),
											 question = question
											)

def set_up_relationship(person_from,person_to,relationship_from,relationship_to):
	# create the relationships
	Relationship.objects.create(
									relationship_from=person_from,
									relationship_to=person_to,
									relationship_type=Relationship_Type.objects.get(relationship_type=relationship_from)
								)
	# and the other one
	Relationship.objects.create(
									relationship_from=person_to,
									relationship_to=person_from,
									relationship_type=Relationship_Type.objects.get(relationship_type=relationship_to)
								)

def project_login(client,username='testsuper',password='superword',project_name='testproject'):
	# create a project and permissions, and log the user into the project
	set_up_test_project_permission(
									username=username,
									project_name=project_name
									)
	Site.objects.create(
						name='Test site',
						projects_active=True
						)
	project = Project.objects.get(name=project_name)
	# log the user in and set the project session variable
	client.login(username=username, password=password)
	session = client.session
	session['project_id'] = project.pk
	session.save()
	# return the project
	return project

def add_person_to_project(person,project):
	# add a person to a project by creating a membership
	membership = Membership(
							person=person,
							project=project
							)
	membership.save()
	return