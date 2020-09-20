from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note, \
							Trained_Role, Activity_Type, Activity, Dashboard, Column, Panel, Panel_In_Column, \
							Panel_Column, Panel_Column_In_Panel, Filter_Spec, Column_In_Dashboard, \
							Venue, Venue_Type, Site, Invitation, Invitation_Step, Invitation_Step_Type, \
							Terms_And_Conditions, Profile, Chart, Document_Link
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
	# first the ethnicity
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	# and a second test ethnicity
	second_test_ethnicity = Ethnicity.objects.create(description='second_test_ethnicity')
	# and another ethnicity
	test_ethnicity = Ethnicity.objects.create(description='Prefer not to say')
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
	# create a test role
	test_role = Role_Type.objects.create(role_type_name='test_role_type',
											use_for_events=True,
											use_for_people=True)
	# and a second test role type
	second_test_role = Role_Type.objects.create(role_type_name='second_test_role_type',use_for_events=True,use_for_people=True)
	# and an UNKNOWN role type
	unknown_test_role = Role_Type.objects.create(role_type_name='UNKNOWN',use_for_events=True,use_for_people=True)
	# and a test role for an age status default
	age_test_role = Role_Type.objects.create(role_type_name='age_test_role',use_for_events=True,use_for_people=True)
	# and a test role for adults only
	adult_test_role = Role_Type.objects.create(role_type_name='adult_test_role',use_for_events=True,use_for_people=True)
	# create a test ABSS type
	test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
	# create a second test ABSS type
	second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
	# and another type
	test_ABSS_type = ABSS_Type.objects.create(name='ABSS beneficiary')
	# create a test age status
	test_age_status = Age_Status.objects.create(status='Adult',default_role_type=test_role)
	# create a second test age status
	test_age_status_2 = Age_Status.objects.create(status='Child under four',default_role_type=test_role,maximum_age=4)
	# and a third test age status
	test_age_status_3 = Age_Status.objects.create(status='Default role age status',default_role_type=age_test_role,default_role_type_only=True)
	# and a child over foud
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

def set_up_test_user():
	# create a test user
	test_user = User.objects.create_user(username='testuser', password='testword')
	# return the user
	return test_user

def set_up_test_superuser():
	# create a test superuser
	test_superuser = User.objects.create_user(username='testsuper', password='superword', is_superuser=True)
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

def set_up_test_events(name_root,event_type,number,date='2019-01-01',ward=None):
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
											location = 'Test location'
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

class LoginViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = User.objects.create_user(
										username='test@test.com',
										password='testword'
										)
		# set up a TOTP device and a static device
		totp_device = TOTPDevice.objects.create(
													user=user,
													name='test_totp'
													)
		static_device = StaticDevice.objects.create(
													user=user,
													name='test_static'
													)
		static_token = StaticToken.objects.create(
													device=static_device,
													token='123456'
													)
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_login_invalid_user_name_no_otp(self):
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'invalid@invalid.com',
											'password' : 'testword'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Email address or password not recognised')
		# check the profile
		self.assertEqual(Profile.objects.all().exists(),False)

	def test_login_invalid_password_no_otp(self):
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'invalid'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Email address or password not recognised')
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,1)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)

	def test_login_success_no_otp(self):
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword'
											}
									)
		# check the response
		self.assertRedirects(response, '/')
		self.assertEqual(response.status_code, 302)
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,0)
		self.assertEqual(profile.successful_logins,1)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)

	def test_login_invalid_user_name_with_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True
							)
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'invalid@invalid.com',
											'password' : 'testword',
											'token' : '123456'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Email address or password not recognised')
		# check the profile
		self.assertEqual(Profile.objects.all().exists(),False)

	def test_login_invalid_password_with_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True
							)
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'invalid',
											'token' : '123456'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Email address or password not recognised')
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,1)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)

	def test_login_invalid_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True
							)
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword',
											'token' : '123456'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Invalid token')
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,1)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,1)

	def test_login_valid_totp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True
							)
		totp_device = TOTPDevice.objects.get(name='test_totp')
		token = totp(totp_device.bin_key)
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword',
											'token' : str(token)
											}
									)
		# check the response
		self.assertRedirects(response, '/')
		self.assertEqual(response.status_code, 302)
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,0)
		self.assertEqual(profile.successful_logins,1)
		self.assertEqual(profile.successful_otp_logins,1)
		self.assertEqual(profile.unsuccessful_otp_logins,0)

	def test_login_emergency_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True
							)
		# attempt to get the event page
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword',
											'token' : 'EMERGENCY123456'
											}
									)
		# check the response
		self.assertRedirects(response, '/')
		self.assertEqual(response.status_code, 302)
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,0)
		self.assertEqual(profile.successful_logins,1)
		self.assertEqual(profile.successful_otp_logins,1)
		self.assertEqual(profile.unsuccessful_otp_logins,0)

class DisplayQRCodeViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = User.objects.create_user(
										username='test@test.com',
										password='testword'
										)
		# set up a TOTP device
		totp_device = TOTPDevice.objects.create(
													user=user,
													name='test_totp'
													)
		# and another user without a device
		user = User.objects.create_user(
										username='test@test.com2',
										password='testword'
										)

	def test_display_qrcode_existing_device(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('display_qrcode'),
									data = {},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertEqual(TOTPDevice.objects.all().count(),1)

	def test_display_qrcode_no_device(self):
		# log the user in
		self.client.login(username='test@test.com2', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('display_qrcode'),
									data = {},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertEqual(TOTPDevice.objects.all().count(),2)

class ChangePasswordViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = User.objects.create_user(
										username='test@test.com',
										password='testword'
										)

	def test_incorrect_old_password(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('change_password'),
									data = {
											'old_password' : 'invalid',
											'new_password' : 'test',
											'new_password_confirmation' : 'test'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'Password is not correct')

	def test_weak_new_password(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('change_password'),
									data = {
											'old_password' : 'testword',
											'new_password' : 'test',
											'new_password_confirmation' : 'test'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'short')
		self.assertContains(response,'common')

	def test_passwords_dont_match(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('change_password'),
									data = {
											'old_password' : 'testword',
											'new_password' : '8aPquVd@4kDmXAK',
											'new_password_confirmation' : 'doesnotmatch'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'Passwords do not match')

	def test_password_change(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('change_password'),
									data = {
											'old_password' : 'testword',
											'new_password' : '8aPquVd@4kDmXAK',
											'new_password_confirmation' : '8aPquVd@4kDmXAK'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# log the user in
		self.client.login(username='test@test.com', password='8aPquVd@4kDmXAK')
		# attempt to get the index page
		response = self.client.get(reverse('index'))
		# check the response
		self.assertEqual(response.status_code, 200)

class ForgotPasswordViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = User.objects.create_user(
										username='test@test.com',
										password='testword'
										)
		# set up a site
		site = Site.objects.create(
									name='Test Site',
									password_reset_allowed=True,
									password_reset_email_from='from@test.com',
									password_reset_email_cc='bcc@test.com',
									password_reset_email_title='Test Title',
									password_reset_email_text='test email text',
									password_reset_timeout=15
									)

	def test_already_authenticated(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the page
		response = self.client.get(
									reverse('forgot_password'),
									)
		# check the response
		self.assertEqual(response.status_code, 302)

	def test_reset_not_allowed(self):
		# set the not allowed flag on the site
		site = Site.objects.get(name='Test Site')
		site.password_reset_allowed=False
		site.save()
		# attempt to get the page
		response = self.client.get(
									reverse('forgot_password'),
									)
		# check the response
		self.assertEqual(response.status_code, 302)

	def test_invalid_email_address(self):
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('forgot_password'),
									data = {
											'email_address' : 'invalid@invalid.com',
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that no mail was sent out
		self.assertEqual(len(mail.outbox), 0)

	def test_forgot_password(self):
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('forgot_password'),
									data = {
											'email_address' : 'test@test.com',
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that no mail was sent out
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'Test Title')
		self.assertEqual(mail.outbox[0].from_email,'from@test.com')
		self.assertEqual(mail.outbox[0].bcc,['bcc@test.com'])
		self.assertEqual(mail.outbox[0].to,['test@test.com'])
		self.assertEqual(mail.outbox[0].body[:15],'test email text')

	def test_forgot_password_no_bcc(self):
		# update the site
		site = Site.objects.all().first()
		site.password_reset_email_cc = ''
		site.save()
		# attempt to get the qrcode page
		response = self.client.post(
									reverse('forgot_password'),
									data = {
											'email_address' : 'test@test.com',
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that no mail was sent out
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'Test Title')
		self.assertEqual(mail.outbox[0].from_email,'from@test.com')
		self.assertEqual(mail.outbox[0].bcc,[])
		self.assertEqual(mail.outbox[0].to,['test@test.com'])
		self.assertEqual(mail.outbox[0].body[:15],'test email text')

class ResetPasswordViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = User.objects.create_user(
										username='test@test.com',
										password='testword'
										)
		# set up a profile
		profile = Profile.objects.create(
											user=user,
											reset_code='123456',
											reset_timeout=timezone.now() + datetime.timedelta(minutes=15),
											)
		# set up a site
		site = Site.objects.create(
									name='Test Site',
									password_reset_allowed=True,
									password_reset_email_from='from@test.com',
									password_reset_email_title='Test Title',
									password_reset_email_text='test email text',
									password_reset_timeout=15
									)

	def test_incorrect_code(self):
		# attempt to get the qrcode page
		response = self.client.get('/reset_password/456789')
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'The link is not valid')

	def test_timeout(self):
		# set an expired timeout
		profile = Profile.objects.first()
		profile.reset_timeout = timezone.now() - datetime.timedelta(minutes=60)
		profile.save()
		# attempt to get the page
		response = self.client.get('/reset_password/123456')
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'The link is no longer valid')

	def test_weak_new_password(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the page
		response = self.client.post(
									reverse('reset_password',args=['123456']),
									data = {
											'email_address' : 'test@test.com',
											'new_password' : 'test',
											'new_password_confirmation' : 'test'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'short')
		self.assertContains(response,'common')

	def test_passwords_dont_match(self):
		# log the user in
		self.client.login(username='test@test.com', password='testword')
		# attempt to get the page
		response = self.client.post(
									reverse('reset_password',args=['123456']),
									data = {
											'email_address' : 'test@test.com',
											'new_password' : '8aPquVd@4kDmXAK',
											'new_password_confirmation' : 'test'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the results
		self.assertContains(response,'Passwords do not match')

	def test_password_change(self):
		# attempt to get the page
		response = self.client.post(
									reverse('reset_password',args=['123456']),
									data = {
											'email_address' : 'test@test.com',
											'new_password' : '8aPquVd@4kDmXAK',
											'new_password_confirmation' : '8aPquVd@4kDmXAK'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# log the user in
		self.client.login(username='test@test.com', password='8aPquVd@4kDmXAK')
		# attempt to get the index page
		response = self.client.get(reverse('index'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that the profile has been updated
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.reset_code,'')
		self.assertEqual(profile.reset_timeout,None)

	def test_password_change_no_reset_timeout(self):
		# remove the reset timeout from the profile
		profile = Profile.objects.get(user__username='test@test.com')
		profile.reset_timeout = None
		profile.save()
		# attempt to get the page
		response = self.client.post(
									reverse('reset_password',args=['123456']),
									data = {
											'email_address' : 'test@test.com',
											'new_password' : '8aPquVd@4kDmXAK',
											'new_password_confirmation' : '8aPquVd@4kDmXAK'
											},
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# log the user in
		self.client.login(username='test@test.com', password='8aPquVd@4kDmXAK')
		# attempt to get the index page
		response = self.client.get(reverse('index'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that the profile has been updated
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.reset_code,'')
		self.assertEqual(profile.reset_timeout,None)		

class PeopleViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# set up base data: first the ethnicity
		test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
		# and the capture type
		test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
		# create the Parent role
		parent_role = Role_Type.objects.create(role_type_name='Parent',use_for_events=True,use_for_people=True)
		# and the parent champion role
		parent_champion_role = Role_Type.objects.create(role_type_name='Parent Champion',use_for_events=True,use_for_people=True)
		# create a test age status
		test_age_status = Age_Status.objects.create(status='Adult')
		# create a second test age status
		test_age_status = Age_Status.objects.create(status='Child')
		# and four more test role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		test_role_4 = Role_Type.objects.create(role_type_name='test role 4',use_for_events=True,use_for_people=True)
		test_role_5 = Role_Type.objects.create(role_type_name='test role 5',use_for_events=True,use_for_people=True)
		# create a test ABSS type
		test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
		# create a second test ABSS type
		second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
		# Create 50 of each type
		set_up_test_people('Parent_','Parent',50)
		set_up_test_people('Parent_Champion_','Parent Champion',50)
		set_up_test_people('Test_Role_1_','test role 1',50)
		set_up_test_people('Test_Role_2_','test role 2',50)
		# and 50 of each of the two test role types with different names
		set_up_test_people('Different_Name_','test role 1',50)
		set_up_test_people('Another_Name_','test role 2',50)
		# and more with the roles swapped over
		set_up_test_people('Different_Name_','test role 2',50)
		set_up_test_people('Another_Name_','test role 1',50)
		# and a short set to test a result set with less than a page
		set_up_test_people('Short_Set_','test role 3',10)
		# create 25 ex-parent champions
		set_up_test_people('Ex_Parent_Champion_','Parent Champion',50)
		# and a set that doesn't exactly fit two pagaes
		set_up_test_people('Pagination_','test role 5',32)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/listpeople')
		# check the response
		self.assertRedirects(response, '/people/login?next=/listpeople')

	def test_empty_page_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('listpeople'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['people']),0)

	def test_search_with_no_criteria(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],492)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),20)

	def test_search_with_no_criteria_second_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],492)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),20)

	def test_search_include_all(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'all',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],492)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),20)

	def test_search_include_all_second_page(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'all',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],492)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),20)

	def test_search_dont_include_all(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'in_project',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],392)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),16)

	def test_search_dont_include_all_second_page(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'in_project',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],392)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),16)

	def test_search_include_left(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'left_project',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],100)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),4)

	def test_search_include_left_second_page(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : 'left_project',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],100)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),4)

	def test_search_for_parent_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the parent role type record
		parent_role_type = Role_Type.objects.get(role_type_name='Parent')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(parent_role_type.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_dont_include_all_keywords(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'in project',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],392)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),16)

	def test_search_dont_include_all_second_page_keywords(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'in project',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],392)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),16)

	def test_search_include_left_keywords(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'keywords' : 'left project',
											'include_people' : 'all',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],100)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),4)

	def test_search_include_left_second_page_keywords(self):
		# set the ABSS dates for the different names
		people_to_exclude = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_to_exclude:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'keywords' : 'left project',
											'include_people' : 'all',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],100)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),4)

	def test_search_for_parent_role_type_keywords(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the parent role type record
		parent_role_type = Role_Type.objects.get(role_type_name='Parent')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'parent',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_first_name_with_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Test_Role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_download_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Download Full Data',
											'names' : 'Test_Role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'You do not have permission to download files')

	def test_download_is_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Download Full Data',
											'names' : 'Test_Role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'Test_Role_1_0,Test_Role_1_0,,test@test.com,,,01/01/2000,Gender,False,,test role 1,')
		self.assertContains(response,'Test_Role_1_49,Test_Role_1_49,,test@test.com,,,01/01/2000,Gender,False,,test role 1,')

	def test_download_limited(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Download',
											'names' : 'Test_Role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'Test_Role_1_0,Test_Role_1_0,,test@test.com,,,,')
		self.assertContains(response,'Test_Role_1_49,Test_Role_1_49,,test@test.com,,,,')

	def test_search_by_first_name_with_non_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'test_role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_last_name_with_matching_case(self):
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the date
			person.last_name = 'name_search'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'name_search',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_last_name_with_matching_case(self):
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the date
			person.last_name = 'name_search'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'NAME_SEARCH',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_other_names(self):
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the other name
			person.other_names = 'name_search'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'name_search',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_membership_number(self):
		# set different last names
		last_person = Person.objects.filter(first_name__startswith='Test_Role_1').last()
		# update the membership number for the last person
		last_person.membership_number = 999
		last_person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '999',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),1)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],1)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_by_email_address(self):
		# set different last names
		last_person = Person.objects.filter(first_name__startswith='Test_Role_1').last()
		# update the membership number for the last person
		last_person.email_address = 'test_email@mail.com'
		last_person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'email',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),1)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],1)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_by_multiple_terms_first_name_last_name(self):
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.first_name = 'first'
			person.last_name = 'last'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'first last',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_multiple_terms_other_names_first_name(self):
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.other_names = 'other'
			person.first_name = 'first'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'first other',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_multiple_terms_exclude_partial_match(self):
		# set different names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_1')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.other_names = 'other'
			person.first_name = 'first'
			# and save the record
			person.save()
		# set different names
		people_to_include = Person.objects.filter(first_name__startswith='Test_Role_2')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.other_names = 'other'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'first other',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_for_short_set(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Short',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],10)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),10)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_by_names_and_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Different',
											'role_type' : str(test_role_type_1.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_multiple_names_and_role_type(self):
		# set different names
		people_to_include = Person.objects.filter(first_name__startswith='Different')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.last_name = 'difflast'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Different difflast',
											'role_type' : str(test_role_type_1.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_names_and_role_type_keywords(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Different',
											'keywords' : 'test role 1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_by_multiple_names_and_role_type_keywords(self):
		# set different names
		people_to_include = Person.objects.filter(first_name__startswith='Different')
		# go through them and set the date
		for person in people_to_include:
			# set the names
			person.last_name = 'difflast'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Different difflast',
											'keywords' : 'test role 1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_name_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'No_results',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_role_type_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_4 = Role_Type.objects.get(role_type_name='test role 4')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(test_role_type_4.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_first_name_and_role_type_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_3 = Role_Type.objects.get(role_type_name='test role 3')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Test_Role_1_',
											'role_type' : str(test_role_type_3.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_second_page_with_less_than_full_set_of_results_by_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_5 = Role_Type.objects.get(role_type_name='test role 5')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(test_role_type_5.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],32)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),7)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_second_page_with_less_than_full_set_of_results_by_first_name(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'Pagination',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],32)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),7)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type(self):
		# create some extra people
		set_up_test_people('ABSS_test_','test role 1',30,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_keywords(self):
		# create some extra people
		set_up_test_people('ABSS_test_','test role 1',30,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'second_test_ABSS_type',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_and_name(self):
		# create some extra people
		set_up_test_people('ABSS_test_find_','test role 1',30,'second_test_ABSS_type')
		set_up_test_people('ABSS_not_found_','test role 1',30,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_role(self):
		# create some extra people
		set_up_test_people('ABSS_test_role_1','test role 1',30,'test_ABSS_type')
		set_up_test_people('ABSS_test_role_2','test role 2',35,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_and_name_and_role(self):
		# create some extra people
		set_up_test_people('ABSS_test_role_1','test role 1',30,'second_test_ABSS_type')
		set_up_test_people('ABSS_test_role_2','test role 2',35,'second_test_ABSS_type')
		set_up_test_people('ABSS_test_find','test role 2',37,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_and_name_keywords(self):
		# create some extra people
		set_up_test_people('ABSS_test_find_','test role 1',30,'second_test_ABSS_type')
		set_up_test_people('ABSS_not_found_','test role 1',30,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'keywords' : 'second_test_ABSS_type',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_role_keywords(self):
		# create some extra people
		set_up_test_people('ABSS_test_role_1','test role 1',30,'test_ABSS_type')
		set_up_test_people('ABSS_test_role_2','test role 2',35,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'test role 2 second_test_ABSS_type',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_on_type_and_name_and_role_keywords(self):
		# create some extra people
		set_up_test_people('ABSS_test_role_1','test role 1',30,'second_test_ABSS_type')
		set_up_test_people('ABSS_test_role_2','test role 2',35,'second_test_ABSS_type')
		set_up_test_people('ABSS_test_find','test role 2',37,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'keywords' : 'test role 2 second_test_ABSS_type',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_search_with_no_results(self):
		# create a new ABSS type
		ABSS_Type.objects.create(name='Third test ABSS')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='Third test ABSS').pk),
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_age_status_on_type(self):
		# create some extra people
		set_up_test_people('age_status_test_','test role 1',30,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name(self):
		# create some extra people
		set_up_test_people('age_test_find_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_not_found_','test role 1',30,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_role(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name_and_role(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_find','test role 2',37,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name_and_role_and_ABSS(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_3','test role 3',37,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_find','test role 2',39,'second_test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],39)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_on_type_keywords(self):
		# create some extra people
		set_up_test_people('age_status_test_','test role 1',30,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'child',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name_keywords(self):
		# create some extra people
		set_up_test_people('age_test_find_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_not_found_','test role 1',30,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'keywords' : 'child',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_role_keywords(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'test role 2 child',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name_and_role_keywords(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_find','test role 2',37,'test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'keywords' : 'test role 2 child',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_on_type_and_name_and_role_and_ABSS_keywords(self):
		# create some extra people
		set_up_test_people('age_status_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_role_3','test role 3',37,'test_ABSS_type','Child')
		set_up_test_people('age_status_test_find','test role 2',39,'second_test_ABSS_type','Child')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'keywords' : 'test role 2 second_test_ABSS_type child',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],39)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search_with_no_results(self):
		# create a new age status
		age_status = Age_Status.objects.create(status='Third test age status')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(age_status.pk),
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_trained_champions(self):
		# create some extra people
		set_up_test_people('trained_champion_test_','test role 1',30,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_champions_keywords(self):
		# create some extra people
		set_up_test_people('trained_champion_test_','test role 1',30,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'test role 1 adult',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_champion_and_age_status(self):
		# create some extra people
		set_up_test_people('trained_champion_test_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('trained_champion_test_','test role 1',27,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_champion_search_on_champion_and_name(self):
		# create some extra people
		set_up_test_people('trained_test_find_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('trained_not_found_','test role 1',30,'test_ABSS_type','Child')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_search_on_role(self):
		# create some extra people
		set_up_test_people('trained_test_role_1','test role 1',30,'test_ABSS_type','Adult')
		set_up_test_people('trained_test_role_2','test role 2',35,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_test_role_2'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = {
											'action' : 'Search',
											'names' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_search_on_and_name_and_role(self):
		# create some extra people
		set_up_test_people('trained_test_role_1','test role 1',30,'test_ABSS_type','Adult')
		set_up_test_people('trained_test_role_2','test role 2',35,'test_ABSS_type','Adult')
		set_up_test_people('trained_test_find','test role 2',37,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_test_find'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_search_on_type_and_name_and_role_and_ABSS(self):
		# create some extra people
		set_up_test_people('trained_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('trained_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('trained_test_role_3','test role 3',37,'test_ABSS_type','Child')
		set_up_test_people('trained_test_find','test role 2',39,'second_test_ABSS_type','Child')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_test_find'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],39)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_trained_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_active_champions(self):
		# create some extra people
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_champions_only(self):
		# create some extra people
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Adult')
		set_up_test_people('trained_champion_test_','test role 1',17,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create active status for the new people
		for person in Person.objects.filter(first_name__startswith='active_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='trained_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_champion_and_age_status(self):
		# create some extra people
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('active_champion_test_','test role 1',27,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_champion_test_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_champion_search_on_champion_and_name(self):
		# create some extra people
		set_up_test_people('active_test_find_','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('active_not_found_','test role 1',30,'test_ABSS_type','Child')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_search_on_role(self):
		# create some extra people
		set_up_test_people('active_test_role_1','test role 1',30,'test_ABSS_type','Adult')
		set_up_test_people('active_test_role_2','test role 2',35,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_test_role_2'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_search_on_and_name_and_role(self):
		# create some extra people
		set_up_test_people('active_test_role_1','test role 1',30,'test_ABSS_type','Adult')
		set_up_test_people('active_test_role_2','test role 2',35,'test_ABSS_type','Adult')
		set_up_test_people('active_test_find','test role 2',37,'test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_test_find'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],37)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_search_on_type_and_name_and_role_and_ABSS(self):
		# create some extra people
		set_up_test_people('active_test_role_1','test role 1',30,'test_ABSS_type','Child')
		set_up_test_people('active_test_role_2','test role 2',35,'test_ABSS_type','Child')
		set_up_test_people('active_test_role_3','test role 3',37,'test_ABSS_type','Child')
		set_up_test_people('active_test_find','test role 2',39,'second_test_ABSS_type','Adult')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 2')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# create trained status for the new people
		for person in Person.objects.filter(first_name__startswith='active_test_find'):
			# set up the trained role
			Trained_Role.objects.create(person=person,role_type=role_type,active=True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'find',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],39)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_active_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_on_ward(self):
		# create some extra people
		set_up_test_people('test_ward',role_type='test role 1',number=30)
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=1)
		# and a bunch of streets
		set_up_test_streets('ABC street ','ABC0',number=1)
		# get the street
		street = Street.objects.get(name='ABC street 0')
		# set up the addresses for the people
		for person in Person.objects.filter(first_name__startswith='test_ward'):
			# set the street
			person.street = street
			# save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_on_ward_keywords(self):
		# create some extra people
		set_up_test_people('test_ward',role_type='test role 1',number=30)
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=1)
		# and a bunch of streets
		set_up_test_streets('ABC street ','ABC0',number=1)
		# get the street
		street = Street.objects.get(name='ABC street 0')
		# set up the addresses for the people
		for person in Person.objects.filter(first_name__startswith='test_ward'):
			# set the street
			person.street = street
			# save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'Test ward',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_on_ward_no_results(self):
		# create some extra people
		set_up_test_people('test_ward',role_type='test role 1',number=30)
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=1)
		# and a bunch of streets
		set_up_test_streets('ABC street ','ABC0',number=1)
		# get the street
		street = Street.objects.get(name='ABC street 0')
		# set up the addresses for the people
		for person in Person.objects.filter(first_name__startswith='test_ward'):
			# set the street
			person.street = street
			# save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : str(Ward.objects.get(ward_name='Test ward 2').pk),
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_question(self):
		# create the test question and option
		question = Question.objects.create(question_text = 'test question')
		option = Option.objects.create(
								option_label = 'test option',
								question = question,
								keyword = 'keyword'
								)
		# create and get an extra person
		set_up_test_people('test_answer_',role_type='test role 1',number=1)
		person = Person.objects.get(first_name='test_answer_0')
		# answer the question
		answer = Answer.objects.create(
										option=option,
										person=person,
										question=question
										)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'keyword',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],1)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),1)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_question_no_results(self):
		# create the test question and option
		question = Question.objects.create(question_text = 'test question')
		option = Option.objects.create(
								option_label = 'test option',
								question = question,
								keyword = 'keyword'
								)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'keyword',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_keyword_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'invalid',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_ethnicity_keywords(self):
		# create a new test ethnicity
		test_ethnicity = Ethnicity.objects.create(description='test_ethnicity_2')
		# set the ABSS dates for the different names
		people_for_search = Person.objects.filter(first_name__startswith='Different_Name_')
		# go through them and set the date
		for person in people_for_search:
			# set the date
			person.ethnicity = test_ethnicity
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'test_ethnicity_2',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],100)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),4)

class PeopleAgeSearchViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_people_base_data()
		set_up_relationship_base_data()
		# create the Parent role
		parent_role = Role_Type.objects.create(role_type_name='Parent',use_for_events=True,use_for_people=True)
		child_role = Role_Type.objects.create(role_type_name='Child',use_for_events=True,use_for_people=True)
		# and the parent champion role
		parent_champion_role = Role_Type.objects.create(role_type_name='Parent Champion',use_for_events=True,use_for_people=True)
		# build sets of people with different ages
		today = datetime.date.today()
		for age in range(5):
			# creat a set of people with that age
			name_root = 'age_' + str(age) + '_'
			set_up_test_people(
								name_root = name_root,
								age_status = 'Child under four',
								number = 50 + age
								)
			for person in Person.objects.filter(first_name__startswith=name_root):
				person.date_of_birth = today.replace(year=today.year-age)
				person.save()
		# create parents and link to children
		set_up_test_people(
							name_root = 'parent_',
							age_status = 'Adult',
							number = 3
							)
		# parent with one child, aged 1
		parent = Person.objects.get(first_name__startswith='parent_0')
		child = Person.objects.get(first_name__startswith='age_1_0')
		set_up_relationship(parent,child,'parent','child')
		# parent with one child, aged 4
		parent = Person.objects.get(first_name__startswith='parent_1')
		child = Person.objects.get(first_name__startswith='age_4_0')
		set_up_relationship(parent,child,'parent','child')
		# parent with four children, aged 0,1,2,3 and 4
		parent = Person.objects.get(first_name__startswith='parent_2')
		for age in range(5):
			child_name = 'age_' + str(age) + '_1'
			child = Person.objects.get(first_name=child_name)
			set_up_relationship(parent,child,'parent','child')
		
	def test_search_children_ages_specific_age(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],53)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),3)

	def test_search_children_ages_second_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '2',
											'children_ages' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],53)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),3)

	def test_search_children_ages_age_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '1-3'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],158)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),7)

	def test_search_children_ages_specific_age_and_age_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '1-2,4'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],160)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),7)

	def test_search_children_ages_parent_specific_age(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],2)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),2)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_children_ages_parent_age_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '2-4'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],2)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),2)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_children_ages_parent_specific_age_and_age_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'none',
											'ward' : '0',
											'include_people' : '',
											'page' : '1',
											'children_ages' : '1,3-5'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],3)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),3)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)


class PeopleQueryTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up people base data
		set_up_people_base_data()

	def test_role_type_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/role_type/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/role_type/1')

	def test_ABSS_type_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/ABSS_type/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/ABSS_type/1')

	def test_age_status_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/age_status/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/age_status/1')

	def test_role_type_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('role_type',args=[Role_Type.objects.get(role_type_name='test_role_type').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_ABSS_type_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('ABSS_type',args=[ABSS_Type.objects.get(name='test_ABSS_type').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_age_status_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('age_status',args=[Age_Status.objects.get(status='Adult').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_role_type_search(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a new type
		test_role_type = Role_Type.objects.create(role_type_name='People Query Test',use_for_events=True,use_for_people=True)
		# create some extra people
		set_up_test_people('Role Type Query Test','People Query Test',30,'test_ABSS_type','Adult')
		# attempt to get the people page
		response = self.client.get(reverse('role_type',args=[test_role_type.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ABSS_type_search(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a new type
		test_ABSS_type = ABSS_Type.objects.create(name='People Query Test')
		# create some extra people
		set_up_test_people('ABSS Type Query Test','test_role_type',30,'People Query Test','Adult')
		# attempt to get the people page
		response = self.client.get(reverse('ABSS_type',args=[test_ABSS_type.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_age_status_search(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a new status
		test_age_status = Age_Status.objects.create(status='Age Status Test')
		# create some extra people
		set_up_test_people('Age Status Query Test','test_role_type',30,'test_ABSS_type','Age Status Test')
		# attempt to get the people page
		response = self.client.get(reverse('age_status',args=[test_age_status.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_ward_search(self):
		# create some extra people
		set_up_test_people('test_ward',role_type='test_role_type',number=30)
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=1)
		# and a bunch of streets
		set_up_test_streets('ABC street ','ABC0',number=1)
		# get the street
		street = Street.objects.get(name='ABC street 0')
		# set up the addresses for the people
		for person in Person.objects.filter(first_name__startswith='test_ward'):
			# set the street
			person.street = street
			# save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('ward',args=[str(Ward.objects.get(ward_name='Test ward').pk)]))
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

class EventsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user and superuser
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# set up address base data
		set_up_address_base_data()
		# create an event category
		test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
		# and another couple of event categories
		test_event_category_2 = Event_Category.objects.create(name='test_event_category_2',description='category desc')
		test_event_category_3 = Event_Category.objects.create(name='test_event_category_3',description='category desc')
		# create a load of event types
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_2 = Event_Type.objects.create(
														name = 'test_event_type_2',
														description = 'type desc',
														event_category = test_event_category_2)
		test_event_type_3 = Event_Type.objects.create(
														name = 'test_event_type_3',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_4 = Event_Type.objects.create(
														name = 'test_event_type_4',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_5 = Event_Type.objects.create(
														name = 'test_event_type_5',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_6 = Event_Type.objects.create(
														name = 'test_event_type_6',
														description = 'type desc',
														event_category = test_event_category_3)
		test_event_type_7 = Event_Type.objects.create(
														name = 'test_event_type_7',
														description = 'type desc',
														event_category = test_event_category)
		# Create 50 of each type
		set_up_test_events('Test_Event_Type_1_', test_event_type_1,50)
		set_up_test_events('Test_Event_Type_2_', test_event_type_2,50)
		set_up_test_events('Test_Event_Type_3_', test_event_type_3,50)
		set_up_test_events('Test_Event_Type_4_', test_event_type_4,50,ward=Ward.objects.get(ward_name='Test ward'))
		# and 50 of each of the two test event types with different names
		set_up_test_events('Different_Name_',test_event_type_1,50)
		set_up_test_events('Another_Name_',test_event_type_2,50)
		# and more with the types swapped over
		set_up_test_events('Different_Name_',test_event_type_1,50)
		set_up_test_events('Another_Name_',test_event_type_2,50)
		# and a short set to test a result set with less than a page
		set_up_test_events('Short_Set_',test_event_type_4,10)
		# and a set that doesn't exactly fit two pagaes
		set_up_test_events('Pagination_',test_event_type_5,32)
		# and three sets with different dates
		set_up_test_events('Dates_',test_event_type_6,10,date='2019-01-01')
		set_up_test_events('Dates_',test_event_type_6,10,date='2019-02-01')
		set_up_test_events('Dates_',test_event_type_6,10,date='2019-03-01')
		# and three more
		set_up_test_events('Dates_',test_event_type_7,10,date='2019-01-01')
		set_up_test_events('Dates_',test_event_type_7,10,date='2019-02-01')
		set_up_test_events('Dates_',test_event_type_7,10,date='2019-03-01')

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/events')
		# check the response
		self.assertRedirects(response, '/people/login?next=/events')

	def test_empty_page_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('events'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['events']),0)

	def test_search_with_no_criteria(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],502)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),21)

	def test_search_with_no_criteria_second_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],502)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),21)

	def test_search_with_date_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],20)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),20)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_with_date_range_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_6').pk),
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],10)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),10)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_with_date_range_and_event_category(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : '0',
											'event_category' : str(Event_Category.objects.get(name='test_event_category_3').pk),
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],10)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),10)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_with_date_from(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],40)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_with_date_from_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_6').pk),
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],20)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),20)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_with_date_to(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '20/01/2019',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_1').pk),
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],150)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),6)

	def test_search_with_date_to_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '20/01/2019',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],462)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),19)

	def test_search_with_date_range_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event type record
		test_event_type_6 = Event_Type.objects.get(name='test_event_type_6')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : str(test_event_type_6.pk),
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],10)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),10)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_with_event_category(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event category record
		test_event_category_2 = Event_Category.objects.get(name='test_event_category_2')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : str(test_event_category_2.pk),
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],150)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),6)

	def test_search_with_event_category_and_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event category record
		test_event_category_3 = Event_Category.objects.get(name='test_event_category_3')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : str(test_event_category_3.pk),
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],20)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),20)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],False)

	def test_search_ward(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_venue(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create venue data
		set_up_venue_base_data()
		# associate events with venues
		venue = Venue.objects.get(name='test_venue')
		for event in Event.objects.filter(name__startswith='Test_Event_Type_3_'):
			event.venue = venue
			event.save()
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : str(venue.pk),
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_name(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Search',
											'name' : 'Test_Event_Type_1_',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],50)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_download_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Download Events',
											'name' : 'Test_Event_Type_1_',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'You do not have permission to download files')

	def test_download_events_is_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Download Events',
											'name' : 'Test_Event_Type_1_',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'Test_Event_Type_1_0,Test event description,test_event_type_1,')
		self.assertContains(response,'Test_Event_Type_1_49,Test event description,test_event_type_1,')

	def test_download_registrations_is_superuser(self):
		# set up test data
		set_up_people_base_data()
		set_up_test_people('test_reg_',number=1)
		Event_Registration.objects.create(
											person = Person.objects.first(),
											event = Event.objects.get(name='Test_Event_Type_1_0'),
											role_type = Role_Type.objects.get(role_type_name='test_role_type'),
											registered = True,
											apologies = False,
											participated = True
											)
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'Download Registrations',
											'name' : 'Test_Event_Type_1_',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
											'venue' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'Test_Event_Type_1_0,Test event description,test_event_type_1,')
		self.assertContains(response,'test_reg_0,test_reg_0,Adult,True,False,True,test_role_type')

class EventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create an event category
		test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
		# create a load of event types
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		# Create a test event
		set_up_test_events('Test_Event_Type_1_', test_event_type_1,1)
		test_event = Event.objects.first()
		# create and register test people
		set_up_people_base_data()
		set_up_test_people('test_person_',number=55)
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		for person in Person.objects.all():
			Event_Registration.objects.create(
				person = person,
				event = test_event,
				role_type = test_role_1,
				participated = True,
				registered = True,
				apologies = False
				)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/event/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/event/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('event',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_warning_no_mandatory_roles(self):
		# set up the data
		role_type = Role_Type.objects.get(role_type_name='second_test_role_type')
		role_type.mandatory = True
		role_type.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('event',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Event does not have a registration from a person with a role of second_test_role_type')

	def test_warning_has_mandatory_role(self):
		# set up the data
		role_type = Role_Type.objects.get(role_type_name='test role 1')
		role_type.mandatory = True
		role_type.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('event',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response,'WARNING')

	def test_pagination_default_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get('/event/1')
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),25)
		self.assertEqual(len(response.context['page_list']),3)

	def test_pagination_first_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get('/event/1/1')
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),25)
		self.assertEqual(len(response.context['page_list']),3)

	def test_pagination_last_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get('/event/1/3')
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),5)
		self.assertEqual(len(response.context['page_list']),3)

class DashboardViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create an event category
		test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
		# create two test event types
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_2 = Event_Type.objects.create(
														name = 'test_event_type_2',
														description = 'type desc',
														event_category = test_event_category)
		# Create 10 test events for each type
		set_up_test_events('Test_Event_Type_1_', test_event_type_1,10)
		set_up_test_events('Test_Event_Type_2_', test_event_type_2,10)
		# create the dashboard
		test_dashboard = Dashboard.objects.create(
													name='test_dashboard',
													title='Test Dashboard',
													margin=1,
													)
		# create a column
		test_column = Column.objects.create(
											name='test_column',
											)
		# connect the column to the dashboard
		Column_In_Dashboard.objects.create(
											dashboard=test_dashboard,
											column=test_column
											)
		# create a panel
		test_panel = Panel.objects.create(
											name='test_panel',
											title='Test Panel',
											row_name_field='name',
											totals=True,
											model='Event_Type',
											)
		# add the panel to the column
		Panel_In_Column.objects.create(
										column=test_column,
										panel=test_panel
										)
		# create a panel column
		test_panel_column = Panel_Column.objects.create(
														name='test_panel_column',
														count_field='event_set',
														)
		# add the column to the panel
		Panel_Column_In_Panel.objects.create(
												panel=test_panel,
												panel_column=test_panel_column
												)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/dashboard')
		# check the response
		self.assertRedirects(response, '/people/login?next=/dashboard')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_default_rows_included(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		dashboard = response.context['dashboard']
		for column in dashboard.get_columns():
			for panel in column.get_panels():
				for row in panel.get_rows():
					for value in row.values:
						self.assertEqual(value,10)
		self.assertContains(response,'test_event_type_1')
		self.assertContains(response,'test_event_type_2')

	def test_panel_model_error(self):
		# change the panel model to an invalid value
		test_panel = Panel.objects.get(name='test_panel')
		test_panel.model = 'invalid'
		test_panel.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'MODEL DOES NOT EXIST')

	def test_panel_sort_field_error(self):
		# change the panel model to an invalid value
		test_panel = Panel.objects.get(name='test_panel')
		test_panel.sort_field = 'invalid'
		test_panel.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'SORT FIELD DOES NOT EXIST')

	def test_panel_sort_field_method_instead_of_field_error(self):
		# change the panel model to an invalid value
		test_panel = Panel.objects.get(name='test_panel')
		test_panel.sort_field = '__str__'
		test_panel.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'SORT FIELD DOES NOT EXIST')

	def test_panel_row_name_field_error(self):
		# change the panel model to an invalid value
		test_panel = Panel.objects.get(name='test_panel')
		test_panel.row_name_field = 'invalid'
		test_panel.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'ROW NAME FIELD DOES NOT EXIST')

	def test_panel_row_parameter_field_error(self):
		# change the panel model to an invalid value
		test_panel = Panel.objects.get(name='test_panel')
		test_panel.row_parameter_name = 'invalid'
		test_panel.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'ROW PARAMETER FIELD DOES NOT EXIST')

	def test_panel_column_count_field_error(self):
		# change the panel model to an invalid value
		test_panel_column = Panel_Column.objects.get(name='test_panel_column')
		test_panel_column.query_type = 'query_from_many'
		test_panel_column.count_model = 'invalid'
		test_panel_column.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'COUNT MODEL DOES NOT EXIST')

	def test_panel_column_count_model_error(self):
		# change the panel model to an invalid value
		test_panel_column = Panel_Column.objects.get(name='test_panel_column')
		test_panel_column.count_field = 'invalid'
		test_panel_column.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('dashboard',args=['test_dashboard']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'COUNT FIELD DOES NOT EXIST')

class IndexViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# and a site
		Site.objects.create(
							name='test_site'
							)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('')
		# check the response
		self.assertRedirects(response, '/people/login?next=/')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('index'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_default_dashboard_create(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get('')
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that the dashboard was created
		dashboard = Dashboard.objects.get(name='default_dashboard')
		site = Site.objects.get(name='test_site')
		self.assertEqual(site.dashboard,dashboard)

	def test_default_dashboard_no_create_if_exists(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get('')
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that the dashboard was created
		dashboard = Dashboard.objects.get(name='default_dashboard')
		site = Site.objects.get(name='test_site')
		self.assertEqual(site.dashboard,dashboard)
		# count the number of panels
		panel_count = Panel.objects.all().count()
		# attempt to get the page again
		response = self.client.get(reverse('index'))
		# check that there are no extra panels
		self.assertEqual(panel_count,Panel.objects.all().count())

class ChartViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create an event category
		test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
		# create two test event types
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_2 = Event_Type.objects.create(
														name = 'test_event_type_2',
														description = 'type desc',
														event_category = test_event_category)
		# Create 10 test events for each type
		set_up_test_events('Test_Event_Type_1_', test_event_type_1,10)
		set_up_test_events('Test_Event_Type_2_', test_event_type_2,10)
		# create the chart
		test_chart = Chart.objects.create(
											name='test_chart',
											title='Test Chart',
											chart_type='pie',
											model='Event_Type',
											label_field='name',
											sort_field='name',
											count_field='event_set',
											query_type='query from one',
											)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/chart/test_chart')
		# check the response
		self.assertRedirects(response, '/people/login?next=/chart/test_chart')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_pie_chart(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertNotContains(response,'ERROR')

	def test_bar_chart(self):
		# change to a bar chart
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.chart_type = 'bar'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertNotContains(response,'ERROR')

	def test_month_bar_chart(self):
		# change to a bar chart
		test_chart = Chart.objects.get(name='test_chart')
		model = 'Event'
		test_chart.chart_type = 'month_bar'
		date_field = 'date'
		months=12
		label_field=None
		sort_field=None
		count_field=None
		query_type='query from one'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertNotContains(response,'ERROR')

	def test_model_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.model = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'invalid is not a valid model')

	def test_many_model_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.many_model = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'invalid is not a valid model')

	def test_stack_model_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.stack_model = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'invalid is not a valid model')

	def test_label_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.label_field = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'invalid is not a valid attribute')

	def test_label_missing_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.label_field = ''
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Label not provided')

	def test_count_and_sum_and_group_by_missing_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.count_field = ''
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Count or sum or group by not provided')

	def test_group_by_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.group_by_field = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'invalid is not a valid attribute')

	def test_count_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.count_field = 'invalid'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Invalid is not a valid model')

	def test_count_model_error(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		test_chart.count_field = 'invalid_set'
		test_chart.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Invalid is not a valid model')

	def test_invalid_super_filter(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		# create the filter
		test_filter = Filter_Spec.objects.create(
											term='invalid',
											filter_type='string',
											string_value='test',
											)
		test_filter.save()
		test_chart.super_filters.add(test_filter)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Invalid filter')

	def test_invalid_filter(self):
		# change the model to an invalid value
		test_chart = Chart.objects.get(name='test_chart')
		# create the filter
		test_filter = Filter_Spec.objects.create(
											term='invalid',
											filter_type='string',
											string_value='test',
											)
		test_filter.save()
		test_chart.filters.add(test_filter)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('chart',args=['test_chart']))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check the values in the response
		self.assertContains(response,'Invalid filter')

class AddPersonViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_people_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/addperson')
		# check the response
		self.assertRedirects(response, '/people/login?next=/addperson')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('addperson'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_create_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addperson'),
									data = { 
												'first_name' : 'Testfirst',
												'last_name' : 'Testlast',
												'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/profile/' + str(Person.objects.get(first_name='Testfirst').pk))
		# get the record
		test_person = Person.objects.get(first_name='Testfirst')
		# check the record contents
		self.assertEqual(test_person.first_name,'Testfirst')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Testlast')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		# check the record contents which have not been set yet
		self.assertEqual(test_person.email_address,'')
		self.assertEqual(test_person.home_phone,'')
		self.assertEqual(test_person.mobile_phone,'')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'')
		self.assertEqual(test_person.notes,'')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.membership_number,0)

	def test_create_person_increment_membership_number(self):
		# set the ABSS beneficiary record to require a membership number
		ABSS_type = ABSS_Type.objects.get(name='ABSS beneficiary')
		ABSS_type.membership_number_required = True
		ABSS_type.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addperson'),
									data = { 
												'first_name' : 'Testfirst',
												'last_name' : 'Testlast',
												'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/profile/' + str(Person.objects.get(first_name='Testfirst').pk))
		# get the record
		test_person = Person.objects.get(first_name='Testfirst')
		# check the record contents
		self.assertEqual(test_person.first_name,'Testfirst')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Testlast')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		# check the record contents which have not been set yet
		self.assertEqual(test_person.email_address,'')
		self.assertEqual(test_person.home_phone,'')
		self.assertEqual(test_person.mobile_phone,'')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'')
		self.assertEqual(test_person.notes,'')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.membership_number,1)

	def test_person_already_exists(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who aready exists
		set_up_test_people('Person_','test_role_type',1)
		# submit the form
		response = self.client.post(
									reverse('addperson'),
									data = { 
												'first_name' : 'Person_0',
												'last_name' : 'Person_0',
												'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'WARNING')

	def test_confirmation_of_new_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		set_up_test_people('Person_exists_','test_role_type',1)
		# submit the form
		response = self.client.post(
									reverse('addperson'),
									data = {
												'action' : 'CONFIRM',
												'first_name' : 'Person_0',
												'last_name' : 'Person_0',
												'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/profile/' + str(Person.objects.get(first_name='Person_0').pk))
		# get the record
		test_person = Person.objects.get(first_name='Person_0')
		# check the record contents
		self.assertEqual(test_person.first_name,'Person_0')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person_0')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		# check the record contents which have not been set yet
		self.assertEqual(test_person.email_address,'')
		self.assertEqual(test_person.home_phone,'')
		self.assertEqual(test_person.mobile_phone,'')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'')
		self.assertEqual(test_person.notes,'')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)

class ProfileViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_people_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/profile/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/profile/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('profile',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('profile',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_update_profile(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'other_names' : 'updated other_names',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.other_names,'updated other_names')
		self.assertEqual(test_person.default_role.role_type_name,'age_test_role')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Default role age status')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)

	def test_update_profile_blank_other_names_prior_names(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the record
		test_person = Person.objects.get(first_name='Person_0')
		# set the other_names and prior names
		test_person.other_names = 'test other_names'
		test_person.prior_names = 'test prior names'
		# now save
		test_person.save()
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : '',
											'last_name' : 'updated_last_name',
											'other_names' : '',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.other_names,'')
		self.assertEqual(test_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)

	def test_update_profile_age_status_default_only(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : '',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : '99',
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'age_test_role')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Default role age status')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)

	def test_update_profile_age_status_multiple_choices(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','age_test_role',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : '',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '1',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Select a valid role for this age status.')

	def test_update_profile_ABSS_end_date_no_start_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','age_test_role',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : '',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '1',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'ABSS end date can only be entered if ABSS start date is entered.')

	def test_update_profile_ABSS_end_date_before_start_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','age_test_role',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : '',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2016',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'ABSS end date must be after ABSS start date.')

	def test_update_profile_trained_role(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		# check the active status
		self.assertEqual(trained_role.active,False)

	def test_update_profile_trained_role_with_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : '01/01/2012',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		self.assertEqual(trained_role.date_trained.strftime('%d/%m/%Y'),'01/01/2012')
		# check the active status
		self.assertEqual(trained_role.active,False)

	def test_update_profile_trained_role_with_future_date(self):
		# set a future date
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : tomorrow.strftime('%d/%m/%Y'),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Date must not be in the future.')

	def test_update_profile_trained_date_not_trained(self):
		# set a future date
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'none',
											'trained_date_' + str(role_type.pk) : '01/01/2010',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Person is not trained.')

	def test_update_profile_trained_role_active(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'active',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		# check the active status
		self.assertEqual(trained_role.active,True)

	def test_update_profile_remove_trained_role(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'none',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# check that no trained role records exist
		self.assertEqual(test_person.trained_roles.all().exists(),False)

	def test_update_profile_trained_role_blank_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(
									person=Person.objects.get(first_name='Person_0'),
									date_trained=datetime.datetime.strptime('2012-01-01','%Y-%m-%d'),
									role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'active',
											'trained_date_' + str(role_type.pk) : '',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		self.assertEqual(trained_role.date_trained,None)
		# check the active status
		self.assertEqual(trained_role.active,True)

	def test_update_profile_change_age_status_no_trained_roles(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# get the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# set the role type trained status
		role_type.trained = True
		# and save it
		role_type.save()
		# set up the trained role
		Trained_Role.objects.create(person=Person.objects.get(first_name='Person_0'),role_type=role_type)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'home_phone' : '123456',
											'mobile_phone' : '678901',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'age_test_role')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'678901')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'updated notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'second_test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Default role age status')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')
		self.assertEqual(test_person.membership_number,0)
		# check that no trained role records exist
		self.assertEqual(test_person.trained_roles.all().exists(),False)

class AddRelationshipViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_people_base_data()
		# set up base data for relationships
		set_up_relationship_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/add_relationship/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/add_relationship/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('add_relationship',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_find_existing_person_for_relationship_in_project(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1)
		# create a person to add the relationships to
		set_up_test_people('Test_exists_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_target_0').pk]),
									data = { 
											'action' : 'search',
											'names' : 'Test_exists_0',
											'include_people' : 'in_project'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# test that the result is contained within the response
		self.assertContains(response,'Test_exists_0')

	def test_find_existing_person_for_relationship_in_project_exclude_self(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1)
		# create a person to add the relationships to
		set_up_test_people('Test_exists_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_target_0').pk]),
									data = { 
											'action' : 'search',
											'names' : 'Test',
											'include_people' : 'in_project'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# test that the result is contained within the response
		self.assertContains(response,'of Test_exists_0')
		# test that the person we are connecting to is not included
		self.assertNotContains(response,'of Test_target_0')

	def test_find_existing_person_for_relationship_left_project(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1)
		# create a person in the project
		set_up_test_people('Test_in_project_','test_role_type',1)
		# create a person who has left the project
		set_up_test_people('Test_left_project_','test_role_type',1)
		# get the person
		person = Person.objects.get(first_name='Test_left_project_0')
		# set the date
		person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
		# and save the record
		person.save()
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_target_0').pk]),
									data = { 
											'action' : 'search',
											'names' : 'project',
											'include_people' : 'left_project'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# test that the result is contained within the response
		self.assertContains(response,'Test_left_project_0')
		self.assertNotContains(response,'Test_in_project_0')

	def test_find_existing_person_for_relationship_include_all(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1)
		# create a person in the project
		set_up_test_people('Test_in_project_','test_role_type',1)
		# create a person who has left the project
		set_up_test_people('Test_left_project_','test_role_type',1)
		# get the person
		person = Person.objects.get(first_name='Test_left_project_0')
		# set the date
		person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
		# and save the record
		person.save()
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_target_0').pk]),
									data = { 
											'action' : 'search',
											'names' : 'project',
											'include_people' : 'all'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# test that the result is contained within the response
		self.assertContains(response,'Test_left_project_0')
		self.assertContains(response,'Test_in_project_0')

	def test_add_relationship_to_new_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_from_0').pk]),
									data = { 
											'action' : 'addrelationshiptonewperson',
											'first_name' : 'new_first_name',
											'middle_names' : 'new_middle_names',
											'last_name' : 'new_last_name',
											'relationship_type' : str(Relationship_Type.objects.get(relationship_type='parent').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the newly created person record
		test_new_person = Person.objects.get(first_name='new_first_name')
		# check the record contents
		self.assertEqual(test_new_person.first_name,'new_first_name')
		self.assertEqual(test_new_person.middle_names,'new_middle_names')
		self.assertEqual(test_new_person.last_name,'new_last_name')
		# check the record contents which have not been set yet
		self.assertEqual(test_new_person.email_address,'')
		self.assertEqual(test_new_person.home_phone,'')
		self.assertEqual(test_new_person.mobile_phone,'')
		self.assertEqual(test_new_person.notes,'')
		self.assertEqual(test_new_person.relationships.all().exists(),True)
		self.assertEqual(test_new_person.children_centres.all().exists(),False)
		self.assertEqual(test_new_person.events.all().exists(),False)
		self.assertEqual(test_new_person.pregnant,False)
		self.assertEqual(test_new_person.due_date,None)
		self.assertEqual(test_new_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_new_person.families.all().exists(),False)
		self.assertEqual(test_new_person.savs_id,None)
		self.assertEqual(test_new_person.age_status.status,'Adult')
		self.assertEqual(test_new_person.house_name_or_number,'')
		self.assertEqual(test_new_person.street,None)
		# get the original person
		test_original_person = Person.objects.get(first_name='Test_from_0')
		# get the relationship from 
		relationship_from_original = Relationship.objects.get(relationship_from=test_original_person)
		# check the contents
		self.assertEqual(relationship_from_original.relationship_type.relationship_type,'parent')
		self.assertEqual(relationship_from_original.relationship_to,test_new_person)
		# get the relationship to 
		relationship_from_new = Relationship.objects.get(relationship_from=test_new_person)
		# check the contents
		self.assertEqual(relationship_from_new.relationship_type.relationship_type,'child')
		self.assertEqual(relationship_from_new.relationship_to,test_original_person)

	def test_add_relationship_to_existing_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_from_0').pk]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_' + str(Person.objects.get(first_name='Test_to_0').pk) : \
												str(Relationship_Type.objects.get(relationship_type='parent').pk),
											}
									)
		# get the from person
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# get the 
		relationship_from = Relationship.objects.get(relationship_from=test_from_person)
		# check the contents
		self.assertEqual(relationship_from.relationship_type.relationship_type,'parent')
		self.assertEqual(relationship_from.relationship_to,test_to_person)
		# get the relationship to 
		relationship_to = Relationship.objects.get(relationship_from=test_to_person)
		# check the contents
		self.assertEqual(relationship_to.relationship_type.relationship_type,'child')
		self.assertEqual(relationship_to.relationship_to,test_from_person)

	def test_edit_existing_relationship(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# get the from person
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='parent')
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='child')
			)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[test_from_person.pk]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_' + str(Person.objects.get(first_name='Test_to_0').pk) : \
												str(Relationship_Type.objects.get(relationship_type='from').pk),
											}
									)
		# get the 
		relationship_from = Relationship.objects.get(relationship_from=test_from_person)
		# check the contents
		self.assertEqual(relationship_from.relationship_type.relationship_type,'from')
		self.assertEqual(relationship_from.relationship_to,test_to_person)
		# get the relationship to 
		relationship_to = Relationship.objects.get(relationship_from=test_to_person)
		# check the contents
		self.assertEqual(relationship_to.relationship_type.relationship_type,'to')
		self.assertEqual(relationship_to.relationship_to,test_from_person)

	def test_delete_existing_relationship(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# get the from person
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='parent')
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='child')
			)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[test_from_person.pk]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_' + str(Person.objects.get(first_name='Test_to_0').pk) : \
												'0'
											}
									)
		# check that all relationships have gone
		self.assertEqual(Relationship.objects.all().exists(),False)

class AddEventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/addevent')
		# check the response
		self.assertRedirects(response, '/people/login?next=/addevent')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('addevent'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_create_event(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testeventdesc',
												'location' : 'Testeventloc',
												'venue' : str(Venue.objects.get(name='test_venue').pk),
												'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
												'area_' + str(Area.objects.get(area_name='Test area').pk) : 'on',
												'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/' + str(Event.objects.get(name='Testevent').pk))
		# get the record
		test_event = Event.objects.get(name='Testevent')
		# check the record contents
		self.assertEqual(test_event.name,'Testevent')
		self.assertEqual(test_event.description,'Testeventdesc')
		self.assertEqual(test_event.location,'Testeventloc')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_create_event_no_ward(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testeventdesc',
												'location' : 'Testeventloc',
												'venue' : str(Venue.objects.get(name='test_venue').pk),
												'ward' : '0',
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
												'area_' + str(Area.objects.get(area_name='Test area').pk) : '',
												'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/' + str(Event.objects.get(name='Testevent').pk))
		# get the record
		test_event = Event.objects.get(name='Testevent')
		# check the record contents
		self.assertEqual(test_event.name,'Testevent')
		self.assertEqual(test_event.description,'Testeventdesc')
		self.assertEqual(test_event.location,'Testeventloc')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,None)
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),False)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_create_event_no_ward_with_area(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testeventdesc',
												'location' : 'Testeventloc',
												'venue' : str(Venue.objects.get(name='test_venue').pk),
												'ward' : '0',
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
												'area_' + str(Area.objects.get(area_name='Test area').pk) : 'on',
												'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/' + str(Event.objects.get(name='Testevent').pk))
		# get the record
		test_event = Event.objects.get(name='Testevent')
		# check the record contents
		self.assertEqual(test_event.name,'Testevent')
		self.assertEqual(test_event.description,'Testeventdesc')
		self.assertEqual(test_event.location,'Testeventloc')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,None)
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_create_event_ward_area_not_selected(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testeventdesc',
												'location' : 'Testeventloc',
												'venue' : str(Venue.objects.get(name='test_venue').pk),
												'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
												'area_' + str(Area.objects.get(area_name='Test area').pk) : '',
												'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/' + str(Event.objects.get(name='Testevent').pk))
		# get the record
		test_event = Event.objects.get(name='Testevent')
		# check the record contents
		self.assertEqual(test_event.name,'Testevent')
		self.assertEqual(test_event.description,'Testeventdesc')
		self.assertEqual(test_event.location,'Testeventloc')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

class EventRegistrationViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for events
		set_up_event_base_data()
		# and for people
		set_up_people_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/event_registration/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/event_registration/1')

	def test_invalid_event(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('event_registration',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_successful_response_if_logged_in(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an event
		response = self.client.get(reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_event_registration_search_no_results(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('Found_name_','test_role_type',50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'noresult'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],0)

	def test_event_registration_search_names(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('Found_name_',number=17)
		set_up_test_people('Lost_name_',number=19)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'Found_name_'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],17)

	def test_event_registration_search_last_name(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('Found_name_',number=17)
		set_up_test_people('Lost_name_',number=19)
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Found_name_')
		# go through them and set the date
		for person in people_to_include:
			# set the date
			person.last_name = 'name_search'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'name_search',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],17)

	def test_event_registration_search_names_multiple_terms(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('Found_name_',number=17)
		set_up_test_people('Lost_name_',number=19)
		# set different last names
		people_to_include = Person.objects.filter(first_name__startswith='Found_name_')
		# go through them and set the date
		for person in people_to_include:
			# set the date
			person.last_name = 'name_search'
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'Found_name name_search',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],17)

	def test_event_registration_search_names_in_project(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('In_project',number=17)
		set_up_test_people('Left_project',number=19)
		# set left project date
		people_left_project = Person.objects.filter(first_name__startswith='Left_project')
		# go through them and set the date
		for person in people_left_project:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'project',
												'include_people' : 'in_project'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],17)

	def test_event_registration_search_names_left_project(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('In_project',number=17)
		set_up_test_people('Left_project',number=19)
		# set left project date
		people_left_project = Person.objects.filter(first_name__startswith='Left_project')
		# go through them and set the date
		for person in people_left_project:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'project',
												'include_people' : 'left_project'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],19)

	def test_event_registration_search_names_include_all(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('In_project',number=17)
		set_up_test_people('Left_project',number=19)
		# set left project date
		people_left_project = Person.objects.filter(first_name__startswith='Left_project')
		# go through them and set the date
		for person in people_left_project:
			# set the date
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			# and save the record
			person.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'project',
												'include_people' : 'all'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],36)

	def test_event_registration_search_names_over_100(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some people
		set_up_test_people('test person',number=200)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'test',
												'include_people' : 'all'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertContains(response,'More than 100 search results found: please refine search')

	def test_event_registration_register_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=person_2,event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=person_3,event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_participate_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : '',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : 'on',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : '',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : 'on',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : '',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : 'on',
												'role_type_' + str(person_3.pk) : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,False)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,False)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,False)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,True)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_register_participate_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : 'on',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : 'on',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : 'on',
												'role_type_' + str(person_3.pk) : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,True)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_register_apologies_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : 'on',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : 'on',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : 'on',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,True)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,True)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_register_change_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# create some registrations
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_0'),
											role_type=test_role_1,
											registered=True,
											participated=False,
											apologies=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_1'),
											role_type=test_role_3,
											registered=True,
											participated=False,
											apologies=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_2'),
											role_type=test_role_3,
											registered=True,
											participated=False,
											apologies=False
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_2.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_3.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_edit_second_page(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=50)
		# create the registrations and the data for the submission
		keys = ''
		data = { 'action' : 'editregistration' }
		for n in range(50):
			person = Person.objects.get(first_name='Registered_' + str(n))
			# create some registrations
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=person,
												role_type=test_role_1,
												registered=False,
												participated=True,
												apologies=False
												)
			# build the data for the second page
			if n >= 24:
				key = str(person.pk)
				keys = keys = ','.join([keys,key]) if keys else key
				data['registered_' + key] = 'on'
				data['apologies_' + key] = ''
				data['participated_' + key] = ''
				data['role_type_' + key] =  str(test_role_1.pk)
		data['registration_keys'] = keys
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = data,
									edit_page = '2'
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# check the results
		for n in range(50):
			registration = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_' + str(n)),event=event)
			if n >= 24:
				self.assertEqual(registration.registered,True)
				self.assertEqual(registration.apologies,False)
				self.assertEqual(registration.participated,False)
				self.assertEqual(registration.role_type,test_role_1)
			else:
				self.assertEqual(registration.registered,False)
				self.assertEqual(registration.apologies,False)
				self.assertEqual(registration.participated,True)
				self.assertEqual(registration.role_type,test_role_1)

	def test_event_registration_apologies_change_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# create some registrations
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_0'),
											role_type=test_role_1,
											registered=False,
											participated=False,
											apologies=True
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_1'),
											role_type=test_role_3,
											registered=False,
											participated=False,
											apologies=True
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_2'),
											role_type=test_role_3,
											registered=False,
											participated=False,
											apologies=True
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_2.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_3.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_register_change_registered_and_participated(self):
			# create an event
			set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
			# create some role types
			test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
			# create some people
			set_up_test_people('Registered_',number=3)
			# get the people
			person_1 = Person.objects.get(first_name='Registered_0')
			person_2 = Person.objects.get(first_name='Registered_1')
			person_3 = Person.objects.get(first_name='Registered_2')
			# create some registrations
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=Person.objects.get(first_name='Registered_0'),
												role_type=test_role_1,
												registered=False,
												participated=True,
												apologies=False
												)
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=Person.objects.get(first_name='Registered_1'),
												role_type=test_role_1,
												registered=False,
												participated=True,
												apologies=False
												)
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=Person.objects.get(first_name='Registered_2'),
												role_type=test_role_1,
												registered=False,
												participated=True,
												apologies=False
												)
			# log the user in
			self.client.login(username='testuser', password='testword')
			# set the keys
			keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
							str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
							str(Person.objects.get(first_name='Registered_2').pk)
			# do a search
			response = self.client.post(
										reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
										data = {
													'action' : 'editregistration',
													'registration_keys' : keys,
													'registered_' + str(person_1.pk) : 'on',
													'apologies_' + str(person_1.pk) : '',
													'participated_' + str(person_1.pk) : '',
													'role_type_' + str(person_1.pk) : str(test_role_1.pk),
													'registered_' + str(person_2.pk) : 'on',
													'apologies_' + str(person_2.pk) : '',
													'participated_' + str(person_2.pk) : '',
													'role_type_' + str(person_2.pk) : str(test_role_1.pk),
													'registered_' + str(person_3.pk) : 'on',
													'apologies_' + str(person_3.pk) : '',
													'participated_' + str(person_3.pk) : '',
													'role_type_' + str(person_3.pk) : str(test_role_1.pk),
												}
										)
			# check the response
			self.assertEqual(response.status_code, 200)
			# get the event
			event = Event.objects.get(name='test_event_0')
			# get the registration for the first person
			registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
			# check the values
			self.assertEqual(registration_1.registered,True)
			self.assertEqual(registration_1.apologies,False)
			self.assertEqual(registration_1.participated,False)
			self.assertEqual(registration_1.role_type,test_role_1)
			# get the registration for the second person
			registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
			# check the values
			self.assertEqual(registration_2.registered,True)
			self.assertEqual(registration_2.apologies,False)
			self.assertEqual(registration_2.participated,False)
			self.assertEqual(registration_2.role_type,test_role_1)
			# get the registration for the third person
			registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
			# check the values
			self.assertEqual(registration_3.registered,True)
			self.assertEqual(registration_3.apologies,False)
			self.assertEqual(registration_3.participated,False)
			self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_register_change_registered_and_participated_and_role(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# create some registrations
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_0'),
											role_type=test_role_1,
											registered=False,
											participated=True,
											apologies=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_1'),
											role_type=test_role_2,
											registered=False,
											participated=True,
											apologies=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_2'),
											role_type=test_role_3,
											registered=False,
											participated=True,
											apologies=False
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_2.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_3.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_0'),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_add_person_invalid_age_status(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# get the records we need for the test
		event = Event.objects.get(name='test_event_0')
		age_status = Age_Status.objects.get(status='Child under four')
		role_type = Role_Type.objects.get(role_type_name='adult_test_role')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# try to add the person
		response = self.client.post(
									reverse('event_registration',args=[event.pk]),
									data = {
												'action' : 'addpersonandregistration',
												'first_name' : 'test',
												'last_name' : 'invalid',
												'age_status' : str(age_status.pk),
												'role_type' : str(role_type.pk),
												'registered' : 'on',
												'apologies' : '',
												'participated' : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check tha we got an error
		self.assertContains(response,'Role type is not valid for age status')

	def test_event_registration_add_person_no_flags_selected(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# get the records we need for the test
		event = Event.objects.get(name='test_event_0')
		age_status = Age_Status.objects.get(status='Adult')
		role_type = Role_Type.objects.get(role_type_name='adult_test_role')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# try to add the person
		response = self.client.post(
									reverse('event_registration',args=[event.pk]),
									data = {
												'action' : 'addpersonandregistration',
												'first_name' : 'test',
												'last_name' : 'invalid',
												'age_status' : str(age_status.pk),
												'role_type' : str(role_type.pk),
												'registered' : '',
												'apologies' : '',
												'participated' : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check tha we got an error
		self.assertContains(response,'At least one of registered, apologies or participated must be selected')

	def test_event_registration_add_person_registered(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# get the records we need for the test
		event = Event.objects.get(name='test_event_0')
		age_status = Age_Status.objects.get(status='Adult')
		role_type = Role_Type.objects.get(role_type_name='adult_test_role')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# try to add the person
		response = self.client.post(
									reverse('event_registration',args=[event.pk]),
									data = {
												'action' : 'addpersonandregistration',
												'first_name' : 'test',
												'last_name' : 'registration',
												'age_status' : str(age_status.pk),
												'role_type' : str(role_type.pk),
												'registered' : 'on',
												'apologies' : '',
												'participated' : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the registration for the first person
		registration = Event_Registration.objects.get(person=Person.objects.get(first_name='test'),event=event)
		# check the values
		self.assertEqual(registration.registered,True)
		self.assertEqual(registration.apologies,False)
		self.assertEqual(registration.participated,False)
		self.assertEqual(registration.role_type,role_type)

	def test_event_registration_register_trained_role_not_active(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True,trained=True)
		# create  a person
		set_up_test_people('Registered_',number=1)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		# create a trained role with an inactive status
		trained_role = Trained_Role.objects.create(person=person_1,role_type=test_role_1,active=False)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the trained role
		trained_role = Trained_Role.objects.get(person=person_1,role_type=test_role_1)
		# check the values
		self.assertEqual(trained_role.active,True)

	def test_event_registration_edit_trained_role_not_active(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True,trained=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		# create  a person
		set_up_test_people('Registered_',number=1)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		# create a trained role with an inactive status
		trained_role = Trained_Role.objects.create(person=person_1,role_type=test_role_1,active=False)
		# and a registration
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_0'),
											role_type=test_role_2,
											registered=True,
											participated=False,
											apologies=False
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the trained role
		trained_role = Trained_Role.objects.get(person=person_1,role_type=test_role_1)
		# check the values
		self.assertEqual(trained_role.active,True)

	def test_event_registration_edit_trained_role_already_active(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True,trained=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		# create  a person
		set_up_test_people('Registered_',number=1)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		# create a trained role with an inactive status
		trained_role = Trained_Role.objects.create(person=person_1,role_type=test_role_1,active=True)
		# and a registration
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_0'),
											role_type=test_role_2,
											registered=True,
											participated=False,
											apologies=False
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the trained role
		trained_role = Trained_Role.objects.get(person=person_1,role_type=test_role_1)
		# check the values
		self.assertEqual(trained_role.active,True)

	def test_event_registration_register_people_no_mandatory_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True,mandatory=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_2.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Event does not have a registration from a person with a role of test role 3')
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=person_2,event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=person_3,event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_2)

	def test_event_registration_register_people_with_mandatory_role(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1',use_for_events=True,use_for_people=True)
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2',use_for_events=True,use_for_people=True)
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3',use_for_events=True,use_for_people=True,mandatory=True)
		# create some people
		set_up_test_people('Registered_',number=3)
		# get the people
		person_1 = Person.objects.get(first_name='Registered_0')
		person_2 = Person.objects.get(first_name='Registered_1')
		person_3 = Person.objects.get(first_name='Registered_2')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# set the keys
		keys = str(Person.objects.get(first_name='Registered_0').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_1').pk) + ',' + \
						str(Person.objects.get(first_name='Registered_2').pk)
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'addregistration',
												'search_keys' : keys,
												'registered_' + str(person_1.pk) : 'on',
												'apologies_' + str(person_1.pk) : '',
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'apologies_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
												'apologies_' + str(person_3.pk) : '',
												'participated_' + str(person_3.pk) : '',
												'role_type_' + str(person_3.pk) : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response,'WARNING')
		# get the event
		event = Event.objects.get(name='test_event_0')
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=person_1,event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.apologies,False)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=person_2,event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.apologies,False)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=person_3,event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.apologies,False)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_3)

class EditEventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/edit_event/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/edit_event/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the event page
		response = self.client.get(reverse('edit_event',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_invalid_event(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('edit_event',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_edit_event(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create an event
		set_up_test_events('Event_',Event_Type.objects.get(name='test_event_type'),1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[Event.objects.get(name='Event_0').pk]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'location' : 'updated_location',
											'venue' : str(Venue.objects.get(name='test_venue').pk),
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
											'area_' + str(Area.objects.get(area_name='Test area').pk) : 'on',
											'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# get the record
		test_event = Event.objects.get(name='updated_name')
		# check the record contents
		self.assertEqual(test_event.name,'updated_name')
		self.assertEqual(test_event.description,'updated_description')
		self.assertEqual(test_event.location,'updated_location')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_edit_event_updated_venue(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create an event and a new venue
		set_up_test_events('Event_',Event_Type.objects.get(name='test_event_type'),1)
		updated_venue = Venue.objects.create(
												name = 'updated_venue',
												building_name_or_number = '456',
												venue_type = Venue_Type.objects.get(name='test_venue_type'),
												street = Street.objects.get(name='venue_street0')
												)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[Event.objects.get(name='Event_0').pk]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'location' : 'updated_location',
											'venue' : updated_venue.pk,
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
											'area_' + str(Area.objects.get(area_name='Test area').pk) : 'on',
											'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# get the record
		test_event = Event.objects.get(name='updated_name')
		# check the record contents
		self.assertEqual(test_event.name,'updated_name')
		self.assertEqual(test_event.description,'updated_description')
		self.assertEqual(test_event.location,'updated_location')
		self.assertEqual(test_event.venue.name,'updated_venue')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_edit_event_no_ward(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create an event
		set_up_test_events('Event_',Event_Type.objects.get(name='test_event_type'),1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[Event.objects.get(name='Event_0').pk]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'location' : 'updated_location',
											'venue' : str(Venue.objects.get(name='test_venue').pk),
											'ward' : '0',
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
											'area_' + str(Area.objects.get(area_name='Test area').pk) : '',
											'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# get the record
		test_event = Event.objects.get(name='updated_name')
		# check the record contents
		self.assertEqual(test_event.name,'updated_name')
		self.assertEqual(test_event.description,'updated_description')
		self.assertEqual(test_event.location,'updated_location')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,None)
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),False)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_edit_event_ward_area_not_selected(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create an event
		set_up_test_events('Event_',Event_Type.objects.get(name='test_event_type'),1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[Event.objects.get(name='Event_0').pk]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'location' : 'updated_location',
											'venue' : str(Venue.objects.get(name='test_venue').pk),
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
											'area_' + str(Area.objects.get(area_name='Test area').pk) : '',
											'area_' + str(Area.objects.get(area_name='Test area 2').pk) : ''
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# get the record
		test_event = Event.objects.get(name='updated_name')
		# check the record contents
		self.assertEqual(test_event.name,'updated_name')
		self.assertEqual(test_event.description,'updated_description')
		self.assertEqual(test_event.location,'updated_location')
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

class AddVenueViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/addvenue')
		# check the response
		self.assertRedirects(response, '/people/login?next=/addvenue')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the event page
		response = self.client.get(reverse('addvenue'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_venue_search_without_street_or_post_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addvenue'),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : '',
											'street' : '',
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertContains(response,'Either post code or street name must be entered')

	def test_venue_search_with_matching_name(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addvenue'),
									data = { 
											'name' : 'test_venue',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : '',
											'street' : '',
											'post_code' : 'TV10',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertContains(response,'Venue with this name already exists')

	def test_venue_search_with_results(self):
		# create test streets
		set_up_test_streets('test_street_','TV10',50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addvenue'),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : 'test_street',
											'street' : '',
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(len(response.context['addvenueform'].fields['street'].choices),50)

	def test_venue_create(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addvenue'),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : 'venue_street0',
											'street' : str(Street.objects.get(name='venue_street0').pk),
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Create',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# check the results
		venue = Venue.objects.get(name='test venue name')
		self.assertEqual(venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(venue.building_name_or_number,'123')
		self.assertEqual(venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(venue.contact_name,'test contact name')
		self.assertEqual(venue.phone,'12345')
		self.assertEqual(venue.mobile_phone,'67890')
		self.assertEqual(venue.email_address,'test@test.com')
		self.assertEqual(venue.website,'website.com')
		self.assertEqual(venue.price,'test price')
		self.assertEqual(venue.facilities,'test facilities')
		self.assertEqual(venue.opening_hours,'test opening hours')
		self.assertEqual(venue.notes,'test notes')

class EditVenueViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/edit_venue/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/edit_venue/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the event page
		response = self.client.get(reverse('edit_venue',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_invalid_venue(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('edit_venue',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_venue_search_without_street_or_post_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_venue',args=[Venue.objects.get(name='test_venue').pk]),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : '',
											'street' : '',
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertContains(response,'Either post code or street name must be entered')

	def test_venue_search_with_matching_name_to_self(self):
		# create test streets
		set_up_test_streets('test_street_','TV10',50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_venue',args=[Venue.objects.get(name='test_venue').pk]),
									data = { 
											'name' : 'test_venue',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : 'test_street',
											'street' : '',
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(len(response.context['editvenueform'].fields['street'].choices),50)

	def test_venue_search_with_matching_name_to_other(self):
		# create a venue
		Venue.objects.create(
								name='matching_name',
								venue_type=Venue_Type.objects.get(name='test_venue_type'),
								street=Street.objects.get(name='venue_street0')
								)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_venue',args=[Venue.objects.get(name='test_venue').pk]),
									data = { 
											'name' : 'matching_name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street' : '',
											'street_name' : '',
											'post_code' : 'TV10',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Search',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertContains(response,'Venue with this name already exists')

	def test_venue_update_address(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_venue',args=[Venue.objects.get(name='test_venue').pk]),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street_name' : 'venue_street0',
											'street' : str(Street.objects.get(name='venue_street0').pk),
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Update',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# check the results
		venue = Venue.objects.get(name='test venue name')
		self.assertEqual(venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(venue.building_name_or_number,'123')
		self.assertEqual(venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(venue.contact_name,'test contact name')
		self.assertEqual(venue.phone,'12345')
		self.assertEqual(venue.mobile_phone,'67890')
		self.assertEqual(venue.email_address,'test@test.com')
		self.assertEqual(venue.website,'website.com')
		self.assertEqual(venue.price,'test price')
		self.assertEqual(venue.facilities,'test facilities')
		self.assertEqual(venue.opening_hours,'test opening hours')
		self.assertEqual(venue.notes,'test notes')

	def test_venue_update(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_venue',args=[Venue.objects.get(name='test_venue').pk]),
									data = { 
											'name' : 'test venue name',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'building_name_or_number' : '123',
											'street' : str(Street.objects.get(name='venue_street0').pk),
											'street_name' : 'venue_street0',
											'post_code' : '',
											'contact_name' : 'test contact name',
											'phone' : '12345',
											'mobile_phone' : '67890',
											'email_address' : 'test@test.com',
											'website' : 'website.com',
											'price' : 'test price',
											'facilities' : 'test facilities',
											'opening_hours' : 'test opening hours',
											'action' : 'Update',
											'notes' : 'test notes',
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# check the results
		venue = Venue.objects.get(name='test venue name')
		self.assertEqual(venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(venue.building_name_or_number,'123')
		self.assertEqual(venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(venue.contact_name,'test contact name')
		self.assertEqual(venue.phone,'12345')
		self.assertEqual(venue.mobile_phone,'67890')
		self.assertEqual(venue.email_address,'test@test.com')
		self.assertEqual(venue.website,'website.com')
		self.assertEqual(venue.price,'test price')
		self.assertEqual(venue.facilities,'test facilities')
		self.assertEqual(venue.opening_hours,'test opening hours')
		self.assertEqual(venue.notes,'test notes')

class VenuesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data
		set_up_event_base_data()
		set_up_address_base_data()
		# set up a set of post codes and streets
		Post_Code.objects.create(
									post_code = 'WD',
									ward = Ward.objects.get(ward_name='Test ward')
									)
		Post_Code.objects.create(
									post_code = 'W2',
									ward = Ward.objects.get(ward_name='Test ward 2')
									)
		Post_Code.objects.create(
									post_code = 'W3',
									ward = Ward.objects.get(ward_name='Unknown')
									)
		Street.objects.create(
									name = 'WD street',
									post_code = Post_Code.objects.get(post_code='WD')
									)
		Street.objects.create(
									name = 'W2 street',
									post_code = Post_Code.objects.get(post_code='W2')
									)
		Street.objects.create(
									name = 'W3 street',
									post_code = Post_Code.objects.get(post_code='W3')
									)
		# and venue type and venues
		test_venue_type = Venue_Type.objects.create(name='test_venue_type')
		test_venue_type_2 = Venue_Type.objects.create(name='test_venue_type_2')
		for n in range(25):
			Venue.objects.create(
									name = 'test_venuez',
									building_name_or_number = '123',
									venue_type = test_venue_type,
									street = Street.objects.get(name='WD street')
									)
		for n in range(25):
			Venue.objects.create(
									name = 'test_venue',
									building_name_or_number = '123',
									venue_type = test_venue_type_2,
									street = Street.objects.get(name='WD street')
									)
		for n in range(15):
			Venue.objects.create(
									name = 'test_venuez',
									building_name_or_number = '123',
									venue_type = test_venue_type,
									street = Street.objects.get(name='W2 street')
									)
		for n in range(15):
			Venue.objects.create(
									name = 'test_venue',
									building_name_or_number = '123',
									venue_type = test_venue_type_2,
									street = Street.objects.get(name='W2 street')
									)
		for n in range(10):
			Venue.objects.create(
									name = 'test_venuez',
									building_name_or_number = '123',
									venue_type = test_venue_type,
									street = Street.objects.get(name='W3 street')
									)
		for n in range(10):
			Venue.objects.create(
									name = 'test_venue',
									building_name_or_number = '123',
									venue_type = test_venue_type_2,
									street = Street.objects.get(name='W3 street')
									)
		# and an additional set of venues

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/venues')
		# check the response
		self.assertRedirects(response, '/people/login?next=/venues')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the event page
		response = self.client.get(reverse('venues'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_search_with_no_criteria(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' : '0',
											'area' : '0',
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],100)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),4)
		self.assertContains(response,'100 found')

	def test_search_with_no_criteria(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' : '0',
											'area' : '0',
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],100)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),4)
		self.assertContains(response,'100 found')

	def test_search_by_name(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : 'venuez',
											'ward' : '0',
											'area' : '0',
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],50)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),2)
		self.assertContains(response,'50 found')

	def test_search_by_ward(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' :  str(Ward.objects.get(ward_name='Test ward').pk),
											'area' : '0',
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],50)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),2)
		self.assertContains(response,'50 found')

	def test_search_by_area(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' : '0',
											'area' : str(Area.objects.get(area_name='Test area').pk),
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],70)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),3)
		self.assertContains(response,'70 found')

	def test_search_by_venue_type(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' : '0',
											'area' : '0',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],50)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),2)
		self.assertContains(response,'50 found')

	def test_search_short_set(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : 'venuez',
											'ward' : str(Ward.objects.get(ward_name='Test ward 2').pk),
											'area' : '0',
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],15)
		self.assertEqual(len(response.context['venues']),15)
		self.assertEqual(response.context['page_list'],False)
		self.assertContains(response,'15 found')

	def test_search_multiple_criteria(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : 'venuez',
											'ward' : str(Ward.objects.get(ward_name='Test ward 2').pk),
											'area' : str(Area.objects.get(area_name='Test area 2').pk),
											'venue_type' : '0',
											'action' : 'search',
											'page' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],15)
		self.assertEqual(len(response.context['venues']),15)
		self.assertEqual(response.context['page_list'],False)
		self.assertContains(response,'15 found')

	def test_pagination(self):
		# log the user in	
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('venues'),
									data = { 
											'name' : '',
											'ward' : '0',
											'area' : '0',
											'venue_type' : str(Venue_Type.objects.get(name='test_venue_type').pk),
											'action' : 'search',
											'page' : '2'
											}
									)
		# check the response
		self.assertEqual(response.status_code,200)
		# check the results
		self.assertEqual(response.context['number_of_venues'],50)
		self.assertEqual(len(response.context['venues']),25)
		self.assertEqual(len(response.context['page_list']),2)
		self.assertContains(response,'50 found')

class InvitationViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=50)
		set_up_test_post_codes('XYZ',number=75)
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0',number=50)
		set_up_test_streets('ABC streets 2','ABC0',number=60)
		set_up_test_streets('XYZ streets','XYZ0',number=35)
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('invitation_test',number=1)
		test_person = Person.objects.get(first_name__startswith='invitation')
		# and terms and conditions
		tandcs = Terms_And_Conditions.objects.create(
														name='test_t_and_c',
														start_date=datetime.date.today(),
														notes='test terms and conditions'
														)
		# and invitation steps
		invitation_step_types = {
									'introduction' : 'Introduction',
									'terms_and_conditions' : 'Terms and Conditions',
									'personal_details' : 'Personal Details',
									'address' : 'Address',
									'children' : 'Children',
									'questions' : 'Questions',
									'signature' : 'Signature',
								}
		order = 10
		for invitation_step_type in invitation_step_types.keys():
			terms = tandcs if invitation_step_type == 'terms_and_conditions' else None
			Invitation_Step_Type.objects.create(
												name=invitation_step_type,
												display_name=invitation_step_types[invitation_step_type],
												order=order,
												active=True,
												terms_and_conditions=terms,
												)
			order += 10
		# create test relationship types
		Relationship_Type.objects.create(
											relationship_type='Other carer',
											relationship_counterpart='Cared for child',
											use_for_invitations=True
											)
		Relationship_Type.objects.create(relationship_type='Cared for child', relationship_counterpart='Other carer')
		# and questions
		set_up_test_questions('q_no_notes',use_for_invitations=True)
		q_no_notes = Question.objects.get(question_text='q_no_notes0')
		set_up_test_options('q_no_notes_option_',question=q_no_notes,number=2)
		set_up_test_questions('q_with_notes',notes=True,use_for_invitations=True)
		q_with_notes = Question.objects.get(question_text='q_with_notes0')
		set_up_test_options('q_with_notes_option_',question=q_with_notes,number=2)
		# and an invitation
		Invitation.objects.create(
									code = '123456',
									person = test_person,
									)

	def test_invalid_code(self):
		# get the response
		response = self.client.get('/invitation/56789')
		# check the response
		self.assertContains(response,'Invitation code is not valid')

	def test_completed(self):
		# complete the invitation
		invitation = Invitation.objects.get(code='123456')
		invitation.datetime_completed = timezone.now()
		invitation.save()
		# get the response
		response = self.client.get('/invitation/123456')
		# check the response
		self.assertContains(response,'Invitation has been completed')

	def test_introduction(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to complete the step
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = {}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and that it contains the right data
		invitation_step_type = Invitation_Step_Type.objects.get(name='introduction')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=invitation_step_type)
		self.assertEqual(invitation_step.step_data,'Introduction acknowledged')
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Terms and Conditions')

	def test_terms_and_conditions(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='terms_and_conditions')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to complete the step
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'accept_conditions' : 'on'
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created
		invitation_step_type = Invitation_Step_Type.objects.get(name='terms_and_conditions')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		self.assertEqual(invitation_step.step_data, 'test_t_and_c accepted')
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Personal Details')

	def test_personal_details_future_dob(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='personal_details')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# set future date of birth
		today = datetime.datetime.today()
		future_dob = today.replace(year=today.year+1)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to complete the step
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name' : 'first',
											'last_name' : 'last',
											'email_address' : 'testing@test.com',
											'home_phone' : '12345678',
											'mobile_phone' : '78901234',
											'emergency_contact_details' : 'EMERGENCY',
											'date_of_birth' : future_dob.strftime('%d/%m/%Y'),
											'gender' : 'Female',
											'ethnicity' : str(ethnicity.pk),
											'pregnant' : True,
											'due_date' : '01/01/2021',
											'accept_conditions' : True,
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Must not be in the future')

	def test_personal_details(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='personal_details')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to complete the step
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name' : 'first',
											'last_name' : 'last',
											'email_address' : 'testing@test.com',
											'home_phone' : '12345678',
											'mobile_phone' : '78901234',
											'emergency_contact_details' : 'EMERGENCY',
											'date_of_birth' : '01/01/2003',
											'gender' : 'Female',
											'ethnicity' : str(ethnicity.pk),
											'pregnant' : True,
											'due_date' : '01/01/2021',
											'accept_conditions' : True,
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		self.assertIn('{"First Name": "first", "Last Name": "last",', invitation_step.step_data)
		self.assertIn('"Email Address": "testing@test.com", "Home Phone": "12345678",', invitation_step.step_data)
		self.assertIn('"Mobile Phone": "78901234", "Emergency Contact Details": "EMERGENCY",', invitation_step.step_data)
		self.assertIn('"Date of Birth": "2003-01-01", "Gender": "Female", "Ethnicity": "test_ethnicity",', invitation_step.step_data)
		self.assertIn('"Pregnant": "True", "Due Date": "2021-01-01"}', invitation_step.step_data)
		self.assertEqual(invitation_step.special_category_accepted,True)
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Address')
		# check the updated person
		test_person = Person.objects.get(first_name__startswith='first')
		self.assertEqual(test_person.email_address,'testing@test.com')
		self.assertEqual(test_person.home_phone,'12345678')
		self.assertEqual(test_person.mobile_phone,'78901234')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2003')
		self.assertEqual(test_person.gender,'Female')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2021')
		self.assertEqual(test_person.emergency_contact_details,'EMERGENCY')

	def test_personal_details_dont_overwrite_values(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='personal_details')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to complete the step
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name' : 'first',
											'last_name' : 'last',
											'email_address' : 'testing@test.com',
											'home_phone' : '',
											'mobile_phone' : '78901234',
											'emergency_contact_details' : '',
											'date_of_birth' : '',
											'gender' : 'Female',
											'ethnicity' : str(ethnicity.pk),
											'pregnant' : True,
											'due_date' : '',
											'accept_conditions' : True,
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Address')
		# check the updated person
		test_person = Person.objects.get(first_name__startswith='first')
		self.assertEqual(test_person.first_name,'first')
		self.assertEqual(test_person.last_name,'last')
		self.assertEqual(test_person.email_address,'testing@test.com')
		self.assertEqual(test_person.home_phone,'')
		self.assertEqual(test_person.mobile_phone,'78901234')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2000')
		self.assertEqual(test_person.gender,'Female')
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.emergency_contact_details,'')

	def test_address_search_mandatory_fields_missing(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Search',
											'house_name_or_number' : '55',
											'street_name' : '',
											'post_code' : '',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Either post code or street name must be entered.')

	def test_address_search_street_name_with_results(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Search',
											'house_name_or_number' : '55',
											'street_name' : 'ABC',
											'post_code' : '',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ABC streets 1')
		self.assertContains(response,'ABC streets 2')
		self.assertNotContains(response,'XYZ')

	def test_address_search_post_code_with_results(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Search',
											'house_name_or_number' : '55',
											'street_name' : '',
											'post_code' : 'ABC0',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ABC streets 1')
		self.assertContains(response,'ABC streets 2')
		self.assertNotContains(response,'XYZ')

	def test_address_no_street(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Enter',
											'house_name_or_number' : '55',
											'street_name' : 'ABC',
											'post_code' : '',
											'street' : ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Street must be selected')

	def test_address_no_street(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Enter',
											'house_name_or_number' : '55',
											'street_name' : 'ABC',
											'post_code' : '',
											'street' : ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Street must be selected')

	def test_address(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='address')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'action' : 'Enter',
											'house_name_or_number' : '55',
											'street_name' : 'ABC',
											'post_code' : '',
											'street' : str(Street.objects.get(name='ABC streets 10').pk),
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and contains the right data
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		self.assertEqual('55 ABC streets 10 ABC0', invitation_step.step_data)
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Children')
		# get the record
		test_person = Person.objects.get(first_name__startswith='invitation')
		# check the record contents
		self.assertEqual(test_person.house_name_or_number,'55')
		self.assertEqual(test_person.street.pk,Street.objects.get(name='ABC streets 10').pk)

	def test_children_incomplete_entry(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name_0' : 'Test',
											'accept_conditions' : 'on',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'All fields must be entered')

	def test_children_incomplete_entry_relationship_type(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'relationship_type_0' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'accept_conditions' : 'on',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'All fields must be entered')

	def test_children_too_old(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name_0' : 'Test',
											'last_name_0' : 'Child',
											'date_of_birth_0' : '01/01/1960',
											'gender_0' : 'Male',
											'ethnicity_0' : str(ethnicity.pk),
											'relationship_type_0' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'accept_conditions' : 'on',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Must be less than 18 years old')

	def test_children_future_dob(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# set future date of birth
		today = datetime.datetime.today()
		future_dob = today.replace(year=today.year+1)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name_0' : 'Test',
											'last_name_0' : 'Child',
											'date_of_birth_0' : future_dob.strftime('%d/%m/%Y'),
											'gender_0' : 'Male',
											'ethnicity_0' : str(ethnicity.pk),
											'relationship_type_0' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'accept_conditions' : 'on',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Must not be in the future')

	def test_children(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# allow the relationship type for each age status
		for age_status in Age_Status.objects.all():
			for relationship_type in Relationship_Type.objects.all():
				age_status.relationship_types.add(relationship_type)
		# set a date older than child under four
		age_status = Age_Status.objects.get(status='Child under four')
		today = datetime.datetime.today()
		over_four_age = today.replace(year=today.year-(age_status.maximum_age + 1))
		under_four_age = today.replace(year=today.year-(age_status.maximum_age - 1))
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name_0' : 'Test',
											'last_name_0' : 'Underfour',
											'date_of_birth_0' : under_four_age.strftime('%d/%m/%Y'),
											'gender_0' : 'Male',
											'ethnicity_0' : str(ethnicity.pk),
											'relationship_type_0' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'first_name_1' : 'Testing',
											'last_name_1' : 'Overfour',
											'date_of_birth_1' : over_four_age.strftime('%d/%m/%Y'),
											'gender_1' : 'Female',
											'ethnicity_1' : str(ethnicity.pk),
											'relationship_type_1' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'accept_conditions' : 'on'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and contains the right data
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		data_dict = {}
		data_dict['headers'] = (
									'First Name',
									'Last Name',
									'Date of Birth',
									'Age Status',
									'Gender',
									'Ethnicity',
									'Relationship'
									)
		data_dict['rows'] = (
								(
									'Test',
									'Underfour',
									under_four_age.strftime('%Y-%m-%d'),
									'Child under four',
									'Male',
									'test_ethnicity',
									'Other carer'
								),
								(
									'Testing',
									'Overfour',
									over_four_age.strftime('%Y-%m-%d'),
									'Child over four',
									'Female',
									'test_ethnicity',
									'Other carer'
								),
							)
		json_data = json.dumps(data_dict)
		self.assertEqual(invitation_step.step_data,json_data)
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Questions')
		# test the person under four
		test_person = Person.objects.get(last_name__startswith='Under')
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.last_name,'Underfour')
		self.assertEqual(test_person.date_of_birth,under_four_age.date())
		self.assertEqual(test_person.age_status.status,'Child under four')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.ethnicity,ethnicity)
		test_relationship = Relationship.objects.get(relationship_to=test_person)
		self.assertEqual(test_relationship.relationship_type.relationship_type,'Other carer')
		# test the person over four
		test_person = Person.objects.get(last_name__startswith='Over')
		self.assertEqual(test_person.first_name,'Testing')
		self.assertEqual(test_person.last_name,'Overfour')
		self.assertEqual(test_person.date_of_birth,over_four_age.date())
		self.assertEqual(test_person.age_status.status,'Child over four')
		self.assertEqual(test_person.gender,'Female')
		self.assertEqual(test_person.ethnicity,ethnicity)
		test_relationship = Relationship.objects.get(relationship_to=test_person)
		self.assertEqual(test_relationship.relationship_type.relationship_type,'Other carer')

	def test_children_with_question(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='children')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		ethnicity = Ethnicity.objects.get(description='test_ethnicity')
		# get the question, set it for use in the children form, and get the related option
		question = Question.objects.get(question_text='q_with_notes0')
		question.use_for_children_form = True
		question.save()
		option = Option.objects.get(option_label='q_with_notes_option_0')
		# allow the relationship type for each age status
		for age_status in Age_Status.objects.all():
			for relationship_type in Relationship_Type.objects.all():
				age_status.relationship_types.add(relationship_type)
		# set a date older than child under four
		age_status = Age_Status.objects.get(status='Child under four')
		today = datetime.datetime.today()
		over_four_age = today.replace(year=today.year-(age_status.maximum_age + 1))
		under_four_age = today.replace(year=today.year-(age_status.maximum_age - 1))
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# attempt to get the invitation page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'first_name_0' : 'Test',
											'last_name_0' : 'Underfour',
											'date_of_birth_0' : under_four_age.strftime('%d/%m/%Y'),
											'gender_0' : 'Male',
											'ethnicity_0' : str(ethnicity.pk),
											'relationship_type_0' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'question_' + str(question.pk) + '_0' : str(option.pk),
											'notes_' + str(question.pk) + '_0' : 'test_notes',
											'first_name_1' : 'Testing',
											'last_name_1' : 'Overfour',
											'date_of_birth_1' : over_four_age.strftime('%d/%m/%Y'),
											'gender_1' : 'Female',
											'ethnicity_1' : str(ethnicity.pk),
											'relationship_type_1' : str(Relationship_Type.objects.get(relationship_type='Other carer').pk),
											'question_' + str(question.pk) + '_1' : str(option.pk),
											'notes_' + str(question.pk) + '_1' : 'test_notes',
											'accept_conditions' : 'on'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and contains the right data
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		data_dict = {}
		data_dict['headers'] = (
									'First Name',
									'Last Name',
									'Date of Birth',
									'Age Status',
									'Gender',
									'Ethnicity',
									'Relationship',
									'q_with_notes0',
									'q_with_notes0: notes'
									)
		data_dict['rows'] = (
								(
									'Test',
									'Underfour',
									under_four_age.strftime('%Y-%m-%d'),
									'Child under four',
									'Male',
									'test_ethnicity',
									'Other carer',
									'q_with_notes_option_0',
									'test_notes'
								),
								(
									'Testing',
									'Overfour',
									over_four_age.strftime('%Y-%m-%d'),
									'Child over four',
									'Female',
									'test_ethnicity',
									'Other carer',
									'q_with_notes_option_0',
									'test_notes'
								),
							)
		json_data = json.dumps(data_dict)
		self.assertEqual(invitation_step.step_data,json_data)
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response,'Questions')
		# test the person under four
		test_person = Person.objects.get(last_name__startswith='Under')
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.last_name,'Underfour')
		self.assertEqual(test_person.date_of_birth,under_four_age.date())
		self.assertEqual(test_person.age_status.status,'Child under four')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.ethnicity,ethnicity)
		test_relationship = Relationship.objects.get(relationship_to=test_person)
		self.assertEqual(test_relationship.relationship_type.relationship_type,'Other carer')
		# check the answers and the notes
		self.assertTrue(Answer.objects.filter(person=test_person,question=question,option=option).exists())
		answer_note = Answer_Note.objects.get(person=test_person,question=question)
		self.assertEqual(answer_note.notes,'test_notes')
		# test the person over four
		test_person = Person.objects.get(last_name__startswith='Over')
		self.assertEqual(test_person.first_name,'Testing')
		self.assertEqual(test_person.last_name,'Overfour')
		self.assertEqual(test_person.date_of_birth,over_four_age.date())
		self.assertEqual(test_person.age_status.status,'Child over four')
		self.assertEqual(test_person.gender,'Female')
		self.assertEqual(test_person.ethnicity,ethnicity)
		test_relationship = Relationship.objects.get(relationship_to=test_person)
		self.assertEqual(test_relationship.relationship_type.relationship_type,'Other carer')
		# check the answers and the notes
		self.assertTrue(Answer.objects.filter(person=test_person,question=question,option=option).exists())
		answer_note = Answer_Note.objects.get(person=test_person,question=question)
		self.assertEqual(answer_note.notes,'test_notes')

	def test_questions_no_answers(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='questions')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# attempt to get the events page
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'question_' + str(question_no_notes.pk): '0',
											'question_' + str(question_with_notes.pk): '0',
											'notes_' + str(question_with_notes.pk): '',
											'accept_conditions' : 'on'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and contains the right data
		invitation_step = Invitation_Step.objects.get(invitation=invitation, invitation_step_type=this_step)
		self.assertEqual(invitation_step.step_data,'')
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response, 'Signature')
		# check that the invitation step was created
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		# check that we don't have any answers
		self.assertEqual(Answer.objects.all().exists(),False)

	def test_questions(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='questions')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes',
											'accept_conditions' : 'on',
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that the invitation step was created and contains the right data
		invitation_step = Invitation_Step.objects.get(invitation=invitation, invitation_step_type=this_step)
		self.assertEqual(invitation_step.step_data,'{"headers": ["Question", "Answer", "Notes"], "rows": [["q_no_notes0", "q_no_notes_option_0", "No notes"], ["q_with_notes0", "q_with_notes_option_0", "test_notes"]]}')
		# check that if we call it again, we get the next step
		response = self.client.get('/invitation/123456')
		self.assertContains(response, 'Signature')
		# check that the invitation step was created
		invitation_step = Invitation_Step.objects.get(invitation=invitation,invitation_step_type=this_step)
		# check the answers and the notes
		self.assertTrue(Answer.objects.filter(person=test_person,question=question_no_notes,option=option_no_notes).exists())
		self.assertTrue(Answer.objects.filter(person=test_person,question=question_with_notes,option=option_with_notes).exists())
		answer_note = Answer_Note.objects.get(person=test_person,question=question_with_notes)
		self.assertEqual(answer_note.notes,'test_notes')

	def test_signature_blank(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='signature')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
											invitation_step_type=prior_step,
											invitation=invitation
											)
		# submit the page with no signature
		response = self.client.post(
									reverse('invitation',args=['123456']),
									data = {
											'signature' : '[]'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response, 'required')

	def test_signature(self):
		# get the test data
		this_step = Invitation_Step_Type.objects.get(name='signature')
		test_person = Person.objects.get(first_name__startswith='invitation')
		invitation = Invitation.objects.get(person=test_person)
		# mark the previous steps complete
		for prior_step in Invitation_Step_Type.objects.filter(order__lt=this_step.order):
			Invitation_Step.objects.create(
				invitation_step_type=prior_step,
				invitation=invitation
			)
		# define the signature image
		signature = '[{"x":[145,154,163,176,200,222,239,261,278,287,294,298,300],"y":[89,90,94,101,116,132,145,161,173,180,186,190,193]},{"x":[162,163,166,171,177,191,214,228,245,256,267,272,277,280],"y":[184,180,173,165,155,136,108,95,80,73,66,63,60,58]}]'
		# submit the page
		response = self.client.post(
			reverse('invitation', args=['123456']),
			data={
				'signature': signature
			}
		)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the invitation is complete
		invitation = Invitation.objects.get(person=test_person)
		self.assertNotEqual(invitation.datetime_completed,None)
		# check that the invitation step was created
		invitation_step = Invitation_Step.objects.get(invitation=invitation, invitation_step_type=this_step)
		# check the answers and the notes
		self.assertTrue(invitation_step.signature,signature)

class ReviewInvitationViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC', number=50)
		set_up_test_post_codes('XYZ', number=75)
		# and a bunch of streets
		set_up_test_streets('ABC streets 1', 'ABC0', number=50)
		set_up_test_streets('ABC streets 2', 'ABC0', number=60)
		set_up_test_streets('XYZ streets', 'XYZ0', number=35)
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('invitation_test', number=1)
		test_person = Person.objects.get(first_name__startswith='invitation')
		# and terms and conditions
		tandcs = Terms_And_Conditions.objects.create(
			name='test_t_and_c',
			start_date=datetime.date.today(),
			notes='test terms and conditions'
		)
		# and invitation steps
		invitation_step_types = {
			'introduction': 'Introduction',
			'terms_and_conditions': 'Terms and Conditions',
			'personal_details': 'Personal Details',
			'address': 'Address',
			'children': 'Children',
			'questions': 'Questions',
			'signature': 'Signature',
		}
		order = 10
		for invitation_step_type in invitation_step_types.keys():
			terms = tandcs if invitation_step_type == 'terms_and_conditions' else None
			Invitation_Step_Type.objects.create(
				name=invitation_step_type,
				display_name=invitation_step_types[invitation_step_type],
				order=order,
				active=True,
				terms_and_conditions=terms,
			)
			order += 10
		# and an invitation
		Invitation.objects.create(
			code='123456',
			person=test_person,
		)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/review_invitation/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/review_invitation/1')

	def test_invalid_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/review_invitation/56789')
		# check the response
		self.assertContains(response, 'Invitation does not exist')

	def test_not_completed(self):
		# complete the invitation
		invitation = Invitation.objects.get(code='123456')
		invitation.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/review_invitation/' + str(invitation.pk))
		# check the response
		self.assertNotContains(response, 'Validate')

	def test_completed(self):
		# complete the invitation
		invitation = Invitation.objects.get(code='123456')
		invitation.datetime_completed = timezone.now()
		invitation.save()
		# mark the steps complete
		for step in Invitation_Step_Type.objects.all():
			Invitation_Step.objects.create(
				invitation_step_type=step,
				invitation=invitation
			)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/review_invitation/' + str(invitation.pk))
		# check the response
		self.assertContains(response, 'Validate')

class ValidateInvitationViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC', number=50)
		set_up_test_post_codes('XYZ', number=75)
		# and a bunch of streets
		set_up_test_streets('ABC streets 1', 'ABC0', number=50)
		set_up_test_streets('ABC streets 2', 'ABC0', number=60)
		set_up_test_streets('XYZ streets', 'XYZ0', number=35)
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('invitation_test', number=1)
		test_person = Person.objects.get(first_name__startswith='invitation')
		# and terms and conditions
		tandcs = Terms_And_Conditions.objects.create(
			name='test_t_and_c',
			start_date=datetime.date.today(),
			notes='test terms and conditions'
		)
		# and invitation steps
		invitation_step_types = {
			'introduction': 'Introduction',
			'terms_and_conditions': 'Terms and Conditions',
			'personal_details': 'Personal Details',
			'address': 'Address',
			'children': 'Children',
			'questions': 'Questions',
			'signature': 'Signature',
		}
		order = 10
		for invitation_step_type in invitation_step_types.keys():
			terms = tandcs if invitation_step_type == 'terms_and_conditions' else None
			Invitation_Step_Type.objects.create(
				name=invitation_step_type,
				display_name=invitation_step_types[invitation_step_type],
				order=order,
				active=True,
				terms_and_conditions=terms,
			)
			order += 10
		# and an invitation
		Invitation.objects.create(
			code='123456',
			person=test_person,
		)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/validate_invitation/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/validate_invitation/1')

	def test_invalid_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/validate_invitation/56789')
		# check the response
		self.assertContains(response, 'Invitation does not exist')

	def test_already_validated(self):
		# validate the invitation
		invitation = Invitation.objects.get(code='123456')
		invitation.validated = True
		invitation.save()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/validate_invitation/' + str(invitation.pk))
		# check the response
		self.assertContains(response, 'Invitation already validated')

	def test_validate(self):
		# complete the invitation
		invitation = Invitation.objects.get(code='123456')
		invitation.datetime_completed = timezone.now()
		invitation.save()
		# mark the steps complete
		for step in Invitation_Step_Type.objects.all():
			Invitation_Step.objects.create(
				invitation_step_type=step,
				invitation=invitation
			)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/validate_invitation/' + str(invitation.pk))
		# check the response
		self.assertRedirects(response, '/person/' + str(invitation.person.pk))
		# check that the invitation was updated
		invitation = Invitation.objects.get(code='123456')
		self.assertTrue(invitation.validated)

class AddressViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC',number=50)
		set_up_test_post_codes('XYZ',number=75)
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0',number=50)
		set_up_test_streets('ABC streets 2','ABC0',number=60)
		set_up_test_streets('XYZ streets','XYZ0',number=35)
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('address_test',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/address/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/address/1')

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('address',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_empty_search_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('address',args=[Person.objects.get(first_name='address_test0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the search results should be empty
		self.assertEqual(response.context['search_number'],0)

	def test_search_without_street_or_post_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : '',
											'post_code' : '',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Either post code or street must be entered.')

	def test_search_on_street(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : 'ABC',
											'post_code' : '',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['search_number'],110)
		# check how many we got for this page
		self.assertEqual(len(response.context['search_results']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),5)

	def test_search_on_post_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : '',
											'post_code' : 'XYZ',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['search_number'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['search_results']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

	def test_search_on_street_and_post_code(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : 'ABC streets 2',
											'post_code' : 'ABC',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['search_number'],60)
		# check how many we got for this page
		self.assertEqual(len(response.context['search_results']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),3)

	def test_search_on_street_and_post_code_partial_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : 'ABC streets 2',
											'post_code' : 'ABC',
											'page' : '3'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['search_number'],60)
		# check how many we got for this page
		self.assertEqual(len(response.context['search_results']),10)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),3)

	def test_search_on_street_and_post_code_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'search',
											'house_name_or_number' : '55',
											'street' : 'XYZ',
											'post_code' : 'ABC streets 2',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['search_number'],0)
		# check how many we got for this page
		self.assertEqual(len(response.context['search_results']),0)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],[])

	def test_add_address(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit an address creation
		response = self.client.post(
									reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
									data = { 
											'action' : 'update',
											'house_name_or_number' : '55',
											'street_id' : str(Street.objects.get(name='ABC streets 10').pk),
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='address_test0')
		# check the record contents
		self.assertEqual(test_person.house_name_or_number,'55')
		self.assertEqual(test_person.street.pk,Street.objects.get(name='ABC streets 10').pk)

	def test_update_address(self):
			# log the user in
			self.client.login(username='testuser', password='testword')
			# submit an address creation
			response = self.client.post(
										reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
										data = { 
												'action' : 'update',
												'house_name_or_number' : '55',
												'street_id' : str(Street.objects.get(name='ABC streets 10').pk),
												}
										)
			# check that we got a response
			self.assertEqual(response.status_code, 302)
			# get the record
			test_person = Person.objects.get(first_name='address_test0')
			# check the record contents
			self.assertEqual(test_person.house_name_or_number,'55')
			self.assertEqual(test_person.street.pk,Street.objects.get(name='ABC streets 10').pk)
			# submit an address update
			response = self.client.post(
										reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
										data = { 
												'action' : 'update',
												'house_name_or_number' : '99',
												'street_id' : str(Street.objects.get(name='ABC streets 11').pk),
												}
										)
			# check that we got a response
			self.assertEqual(response.status_code, 302)
			# get the record
			test_person = Person.objects.get(first_name='address_test0')
			# check the record contents
			self.assertEqual(test_person.house_name_or_number,'99')
			self.assertEqual(test_person.street.pk,Street.objects.get(name='ABC streets 11').pk)

	def test_remove_address(self):
			# log the user in
			self.client.login(username='testuser', password='testword')
			# submit an address creation
			response = self.client.post(
										reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
										data = { 
												'action' : 'update',
												'house_name_or_number' : '55',
												'street_id' : str(Street.objects.get(name='ABC streets 10').pk)
												}
										)
			# check that we got a response
			self.assertEqual(response.status_code, 302)
			# get the record
			test_person = Person.objects.get(first_name='address_test0')
			# check the record contents
			self.assertEqual(test_person.house_name_or_number,'55')
			self.assertEqual(test_person.street,Street.objects.get(name='ABC streets 10'))
			# submit an address update
			response = self.client.post(
										reverse('address',args=[Person.objects.get(first_name='address_test0').pk]),
										data = { 
												'action' : 'remove',
												}
										)
			# check that we got a response
			self.assertEqual(response.status_code, 302)
			# get the record
			test_person = Person.objects.get(first_name='address_test0')
			# check the record contents
			self.assertEqual(test_person.house_name_or_number,'')
			self.assertEqual(test_person.street,None)

class AddressToRelationshipsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for events
		set_up_event_base_data()
		# and for people
		set_up_people_base_data()
		# and for addresses
		set_up_address_base_data()
		# and the relationship date
		set_up_relationship_base_data()
		# create a person
		set_up_test_people('address_test',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/address_to_relationships/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/address_to_relationships/1')

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('address_to_relationships',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_successful_response_if_logged_in(self):
		# create a person
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get a person
		response = self.client.get(reverse('address_to_relationships',args=[Person.objects.get(first_name='address_test0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_address_to_relationship_no_relationships(self):
		# create some people
		set_up_test_people('No_relationships',number=1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get a person
		response = self.client.get(reverse('address_to_relationships',args=[Person.objects.get(first_name='No_relationships0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['people_at_same_address'],[])
		self.assertEqual(response.context['people_not_at_same_address'],[])
		self.assertEqual(response.context['addresstorelationshipsform'],'')

	def test_apply_address(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# get the people
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='parent')
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='child')
			)
		# set up a test post code
		set_up_test_post_codes('Test PC')
		# and a test street
		set_up_test_streets('Test Street','Test PC0')
		# update the person
		test_from_person.house_name_or_number = '25'
		test_from_person.street = Street.objects.get(name='Test Street0')
		# seve the record
		test_from_person.save()
		# update the address
		response = self.client.post(
									reverse('address_to_relationships',args=[Person.objects.get(first_name='Test_from_0').pk]),
									data = {
												'action' : 'apply_address',
												'application_keys' : str(Person.objects.get(first_name='Test_to_0').pk),
												'apply_' + str(Person.objects.get(first_name='Test_to_0').pk) : 'on',
											}
									)
		# check the record contents
		test_to_person = Person.objects.get(first_name='Test_to_0')
		self.assertEqual(test_to_person.house_name_or_number,'25')
		self.assertEqual(test_to_person.street,Street.objects.get(name='Test Street0'))

	def test_no_update_to_address(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# get the people
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='parent')
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='child')
			)
		# set up a test post code
		set_up_test_post_codes('Test PC')
		# and a test street
		set_up_test_streets('Test Street','Test PC0')
		# update the person
		test_from_person.house_name_or_number = '25'
		test_from_person.street = Street.objects.get(name='Test Street0')
		# seve the record
		test_from_person.save()
		# update the address
		response = self.client.post(
									reverse('address_to_relationships',args=[Person.objects.get(first_name='Test_from_0').pk]),
									data = {
												'action' : 'apply_address',
												'application_keys' : str(Person.objects.get(first_name='Test_to_0').pk),
												'apply_' + str(Person.objects.get(first_name='Test_to_0').pk) : '',
											}
									)
		# check the record contents
		test_to_person = Person.objects.get(first_name='Test_to_0')
		self.assertEqual(test_to_person.house_name_or_number,'')
		self.assertEqual(test_to_person.street,None)

	def test_apply_address_to_person_with_existing_address(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1)
		set_up_test_people('Test_to_','test_role_type',1)
		# get the people
		test_from_person = Person.objects.get(first_name='Test_from_0')
		# and the to person
		test_to_person = Person.objects.get(first_name='Test_to_0')
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='parent')
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(relationship_type='child')
			)
		# set up a test post code
		set_up_test_post_codes('Test PC')
		# and a test street
		set_up_test_streets('Test Street','Test PC0')
		# and another test street
		set_up_test_streets('To Street','Test PC0')
		# update the from person
		test_from_person.house_name_or_number = '25'
		test_from_person.street = Street.objects.get(name='Test Street0')
		# seve the record
		test_from_person.save()
		# and the to person
		test_to_person.house_name_or_number = '73'
		test_to_person.street = Street.objects.get(name='To Street0')
		# seve the record
		test_from_person.save()
		# update the address
		response = self.client.post(
									reverse('address_to_relationships',args=[Person.objects.get(first_name='Test_from_0').pk]),
									data = {
												'action' : 'apply_address',
												'application_keys' : str(Person.objects.get(first_name='Test_to_0').pk),
												'apply_' + str(Person.objects.get(first_name='Test_to_0').pk) : 'on',
											}
									)
		# check the record contents
		test_to_person = Person.objects.get(first_name='Test_to_0')
		self.assertEqual(test_to_person.house_name_or_number,'25')
		self.assertEqual(test_to_person.street,Street.objects.get(name='Test Street0'))

class QuestionsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create a question without notes
		set_up_test_questions('q_no_notes')
		# get the question
		q_no_notes = Question.objects.get(question_text='q_no_notes0')
		# create the options
		set_up_test_options('q_no_notes_option_',question=q_no_notes,number=2)
		# create a question with notes
		set_up_test_questions('q_with_notes',notes=True)
		# get the question
		q_with_notes = Question.objects.get(question_text='q_with_notes0')
		# create the options
		set_up_test_options('q_with_notes_option_',question=q_with_notes,number=2)
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('question_test',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/answer_questions/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/answer_questions/1')

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('answer_questions',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_questions_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('answer_questions',args=[Person.objects.get(first_name='question_test0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the questions
		self.assertContains(response,'q_no_notes0')
		self.assertContains(response,'q_with_notes0')

	def test_questions_no_answers(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): '0',
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): '0',
											'notes_' + str(question_with_notes.pk): ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# check that we don't have any answers
		self.assertEqual(Answer.objects.all().exists(),False)

	def test_questions_answer_without_notes(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get an option for the question with no notes
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): '0',
											'notes_' + str(question_with_notes.pk): ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get the answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())

	def test_questions_answer_with_notes(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get an option for the question with no notes
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): '0',
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get the answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')

	def test_questions_multiple_answers(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')

	def test_questions_note_change(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'new_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'new_notes')

	def test_questions_note_removal(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# check that the note has gone
		self.assertFalse(Answer_Note.objects.all().exists())

	def test_questions_answer_and_note_removal(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): '0',
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): ''
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertFalse(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# check that the note has gone
		self.assertFalse(Answer_Note.objects.all().exists())

	def test_questions_remove_question_keep_note(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='question_test0')
		# get the questions
		question_no_notes = Question.objects.get(question_text='q_no_notes0')
		question_with_notes = Question.objects.get(question_text='q_with_notes0')
		# get options
		option_no_notes = Option.objects.get(option_label='q_no_notes_option_0')
		option_with_notes = Option.objects.get(option_label='q_with_notes_option_0')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): str(option_with_notes.pk),
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')
		# submit the page with no answers
		response = self.client.post(
									reverse('answer_questions',args=[person.pk]),
									data = { 
											'question_' + str(question_no_notes.pk): str(option_no_notes.pk),
											'spacer_' + str(question_no_notes.pk): 'spacer',
											'question_' + str(question_with_notes.pk): '0',
											'notes_' + str(question_with_notes.pk): 'test_notes'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 302)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertFalse(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')

class UploadDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# and a test superuser
		superuser = set_up_test_superuser()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/uploaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/uploaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/uploaddata')
		# check the response
		self.assertRedirects(response, '/')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/uploaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_invalid_file_formats(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# go through each of the file types
		for file_type in [
							'Event Categories',
							'Event Types',
							'Areas',
							'Wards',
							'Post Codes',
							'Streets',
							'Role Types',
							'Relationship Types',
							'ABSS Types',
							'Ethnicities',
							'Age Statuses',
							'People',
							'Events',
							'Relationships',
							'Registrations',
							'Questions',
							'Options',
							'Answers',
							'Answer Notes',
							'Activity Types',
							'Venue Types',
							'Venues',
							'Venues for Events'
							]:
			# open the file
			invalid_file = open('people/tests/data/invalid.csv')
			# submit the page to load the file
			response = self.client.post(
										reverse('uploaddata'),
										data = { 
												'file_type' : file_type,
												'file' : invalid_file
												}
										)
			# check that we got a response
			self.assertEqual(response.status_code, 200)
			# check that we got an error in the page
			self.assertContains(response,'File cannot be loaded as it does not contain the right fields.')
			# close the file
			invalid_file.close()

	def test_upload_event_categories(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/event_categories.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_category_1 = Event_Category.objects.get(name='test event category 1')
		test_event_category_2 = Event_Category.objects.get(name='test event category 2')
		# check that the data is correct
		self.assertEqual(test_event_category_1.description,'event category 1 description')
		self.assertEqual(test_event_category_2.description,'event category 2 description')

	def test_upload_event_categories_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/event_categories_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		self.assertContains(response,' not created: mandatory field name not provided')
		self.assertContains(response,'Missing description not created: mandatory field description not provided')
		# check that no records have been created
		self.assertFalse(Event_Category.objects.all().exists())

	def test_upload_event_categories_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/event_categories.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_category_1 = Event_Category.objects.get(name='test event category 1')
		test_event_category_2 = Event_Category.objects.get(name='test event category 2')
		# check that the data is correct
		self.assertEqual(test_event_category_1.description,'event category 1 description')
		self.assertEqual(test_event_category_2.description,'event category 2 description')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/event_categories.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event categories have been created
		self.assertEqual(Event_Category.objects.all().count(),2)

	def test_upload_activity_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activity_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activity Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_activity_type_1 = Activity_Type.objects.get(name='test activity type 1')
		test_activity_type_2 = Activity_Type.objects.get(name='test activity type 2')

	def test_upload_activity_types_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activity_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activity Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_activity_type_1 = Activity_Type.objects.get(name='test activity type 1')
		test_activity_type_2 = Activity_Type.objects.get(name='test activity type 2')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/activity_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activity Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event categories have been created
		self.assertEqual(Activity_Type.objects.all().count(),2)

	def test_upload_venue_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venue_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venue Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test recirds that should have been loaded
		test_venue_type_1 = Venue_Type.objects.get(name='test venue type 1')
		test_venue_type_2 = Venue_Type.objects.get(name='test venue type 2')

	def test_upload_venue_types_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venue_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venue Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test records that should have been loaded
		test_venue_type_1 = Venue_Type.objects.get(name='test venue type 1')
		test_venue_type_2 = Venue_Type.objects.get(name='test venue type 2')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/venue_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venue Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event categories have been created
		self.assertEqual(Venue_Type.objects.all().count(),2)

	def test_upload_areas(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/areas.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')

	def test_upload_areas_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/areas.csv')
		# submit the page with no answers
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/areas.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event types have been created
		self.assertEqual(Area.objects.all().count(),2)

	def test_upload_wards_invalid_areas(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_invalid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'area does not exist')
		# check that no additional event types have been created
		self.assertEqual(Ward.objects.all().exists(),False)

	def test_upload_wards_valid_areas(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)

	def test_upload_wards_valid_areas_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# close the file
		wards_file.close()
		# reopen the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event types have been created
		self.assertEqual(Ward.objects.all().count(),2)

	def test_upload_postcodes_invalid_wards(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_invalid_wards.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'ward does not exist')
		# check that no additional event types have been created
		self.assertEqual(Post_Code.objects.all().exists(),False)

	def test_upload_postcodes_valid_wards(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the area
		self.assertEqual(test_postcode_1.ward,test_ward_1)
		self.assertEqual(test_postcode_2.ward,test_ward_2)

	def test_upload_postcodes_valid_wards_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the area
		self.assertEqual(test_postcode_1.ward,test_ward_1)
		self.assertEqual(test_postcode_2.ward,test_ward_2)
		# close the file
		postcodes_file.close()
		# reopen the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event types have been created
		self.assertEqual(Post_Code.objects.all().count(),2)

	def test_upload_streets_invalid_postcodes(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the area
		self.assertEqual(test_postcode_1.ward,test_ward_1)
		self.assertEqual(test_postcode_2.ward,test_ward_2)
		# now try to load streets
		# open the file
		streets_file = open('people/tests/data/streets_with_invalid_post_codes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Streets',
											'file' : streets_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'Post_Code invalid pc does not exist')
		# check that no additional event types have been created
		self.assertEqual(Street.objects.all().exists(),False)

	def test_upload_streets_valid_postcodes(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the area
		self.assertEqual(test_postcode_1.ward,test_ward_1)
		self.assertEqual(test_postcode_2.ward,test_ward_2)
		# now try to load streets
		# open the file
		streets_file = open('people/tests/data/streets_with_valid_post_codes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Streets',
											'file' : streets_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_street_1 = Street.objects.get(name = 'test street 1',post_code__post_code='test pc 1')
		test_street_2 = Street.objects.get(name = 'test street 2')
		test_street_3 = Street.objects.get(name = 'test street 1',post_code__post_code='test pc 2')

		# check the post codes for the streets
		self.assertEqual(test_street_1.post_code,test_postcode_1)
		self.assertEqual(test_street_2.post_code,test_postcode_2)
		self.assertEqual(test_street_3.post_code,test_postcode_2)
		# check that we have the right number of records
		self.assertEqual(Street.objects.all().count(),3)

	def test_upload_streets_valid_postcodes_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		areas_file = open('people/tests/data/areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Areas',
											'file' : areas_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test areas that should have been loaded
		test_area_1 = Area.objects.get(area_name='test area 1')
		test_area_2 = Area.objects.get(area_name='test area 2')
		# now load wards
		# open the file
		wards_file = open('people/tests/data/wards_with_valid_areas.csv')
		# load areas first
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Wards',
											'file' : wards_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_ward_1 = Ward.objects.get(ward_name = 'test ward 1')
		test_ward_2 = Ward.objects.get(ward_name = 'test ward 2')
		# check the area
		self.assertEqual(test_ward_1.area,test_area_1)
		self.assertEqual(test_ward_2.area,test_area_2)
		# now load postcodes
		# open the file
		postcodes_file = open('people/tests/data/postcodes_with_valid_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the area
		self.assertEqual(test_postcode_1.ward,test_ward_1)
		self.assertEqual(test_postcode_2.ward,test_ward_2)
		# now try to load streets
		# open the file
		streets_file = open('people/tests/data/streets_with_valid_post_codes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Streets',
											'file' : streets_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_street_1 = Street.objects.get(name = 'test street 1',post_code__post_code='test pc 1')
		test_street_2 = Street.objects.get(name = 'test street 2')
		test_street_3 = Street.objects.get(name = 'test street 1',post_code__post_code='test pc 2')
		# check the post codes for the streets
		self.assertEqual(test_street_1.post_code,test_postcode_1)
		self.assertEqual(test_street_2.post_code,test_postcode_2)
		self.assertEqual(test_street_3.post_code,test_postcode_2)
		# close the file
		streets_file.close()
		# reopen the file
		streets_file = open('people/tests/data/streets_with_valid_post_codes.csv')
		# submit the page to load the file again
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Streets',
											'file' : streets_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event types have been created
		self.assertEqual(Street.objects.all().count(),3)

	def test_upload_role_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/role_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Role Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test role types that should have been loaded
		test_role_type_events_and_people = Role_Type.objects.get(role_type_name='test role events and people')
		test_role_type_events_only = Role_Type.objects.get(role_type_name='test role events only')
		test_role_type_people_only = Role_Type.objects.get(role_type_name='test role people only')
		test_trained_role_type = Role_Type.objects.get(role_type_name='test trained role')
		# check that the data is correct
		self.assertEqual(test_role_type_events_and_people.use_for_events,True)
		self.assertEqual(test_role_type_events_and_people.use_for_people,True)
		self.assertEqual(test_role_type_events_and_people.trained,False)
		self.assertEqual(test_role_type_events_only.use_for_events,True)
		self.assertEqual(test_role_type_events_only.use_for_people,False)
		self.assertEqual(test_role_type_people_only.use_for_events,False)
		self.assertEqual(test_role_type_people_only.use_for_people,True)
		self.assertEqual(test_trained_role_type.trained,True)

	def test_upload_role_types_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/role_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Role Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test role types that should have been loaded
		test_role_type_events_and_people = Role_Type.objects.get(role_type_name='test role events and people')
		test_role_type_events_only = Role_Type.objects.get(role_type_name='test role events only')
		test_role_type_people_only = Role_Type.objects.get(role_type_name='test role people only')
		test_trained_role_type = Role_Type.objects.get(role_type_name='test trained role')
		# check that the data is correct
		self.assertEqual(test_role_type_events_and_people.use_for_events,True)
		self.assertEqual(test_role_type_events_and_people.use_for_people,True)
		self.assertEqual(test_role_type_events_and_people.trained,False)
		self.assertEqual(test_role_type_events_only.use_for_events,True)
		self.assertEqual(test_role_type_events_only.use_for_people,False)
		self.assertEqual(test_role_type_people_only.use_for_events,False)
		self.assertEqual(test_role_type_people_only.use_for_people,True)
		self.assertEqual(test_trained_role_type.trained,True)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/role_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Role Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event categories have been created
		self.assertEqual(Role_Type.objects.all().count(),4)

	def test_upload_relationship_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationship_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationship Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test relationship types that should have been loaded
		test_relationship_type_1 = Relationship_Type.objects.get(relationship_type='test relationship type 1')
		test_relationship_type_2 = Relationship_Type.objects.get(relationship_type='test relationship type 2')
		test_relationship_type_3 = Relationship_Type.objects.get(relationship_type='test relationship type 3')
		# check that the data is correct
		self.assertEqual(test_relationship_type_1.relationship_counterpart,'test relationship type 2')
		self.assertEqual(test_relationship_type_2.relationship_counterpart,'test relationship type 1')
		self.assertEqual(test_relationship_type_3.relationship_counterpart,'test relationship type 3')

	def test_upload_relationship_types_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationship_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationship Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test relationship types that should have been loaded
		test_relationship_type_1 = Relationship_Type.objects.get(relationship_type='test relationship type 1')
		test_relationship_type_2 = Relationship_Type.objects.get(relationship_type='test relationship type 2')
		test_relationship_type_3 = Relationship_Type.objects.get(relationship_type='test relationship type 3')
		# check that the data is correct
		self.assertEqual(test_relationship_type_1.relationship_counterpart,'test relationship type 2')
		self.assertEqual(test_relationship_type_2.relationship_counterpart,'test relationship type 1')
		self.assertEqual(test_relationship_type_3.relationship_counterpart,'test relationship type 3')
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/relationship_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationship Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event categories have been created
		self.assertEqual(Relationship_Type.objects.all().count(),3)

	def test_upload_ethnicities(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/ethnicities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Ethnicities',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(Ethnicity.objects.filter(description='test_ethnicity').exists(),True)

	def test_upload_ethnicities_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/ethnicities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Ethnicities',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(Ethnicity.objects.filter(description='test_ethnicity').exists(),True)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/ethnicities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Ethnicities',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional records have been created
		self.assertEqual(Ethnicity.objects.all().count(),1)

	def test_upload_age_statuses(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/age_statuses.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Age Statuses',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(Age_Status.objects.filter(status='test_age_status').exists(),True)

	def test_upload_age_statuses_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/age_statuses.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Age Statuses',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(Age_Status.objects.filter(status='test_age_status').exists(),True)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/age_statuses.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Age Statuses',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional records have been created
		self.assertEqual(Age_Status.objects.all().count(),1)

	def test_upload_ABSS_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/ABSS_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'ABSS Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(ABSS_Type.objects.filter(name='test_ABSS_type').exists(),True)

	def test_upload_ABSS_types_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/ABSS_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'ABSS Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that the records have been created
		self.assertEqual(ABSS_Type.objects.filter(name='test_ABSS_type').exists(),True)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/ABSS_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'ABSS Types',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional records have been created
		self.assertEqual(ABSS_Type.objects.all().count(),1)

	def test_upload_event_types(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load some event categories first
		# open the file
		event_categories_file = open('people/tests/data/event_categories.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : event_categories_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_category_1 = Event_Category.objects.get(name='test event category 1')
		test_event_category_2 = Event_Category.objects.get(name='test event category 2')
		# check that the data is correct
		self.assertEqual(test_event_category_1.description,'event category 1 description')
		self.assertEqual(test_event_category_2.description,'event category 2 description')
		# now load event types
		event_types_file = open('people/tests/data/event_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Types',
											'file' : event_types_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_type_1 = Event_Type.objects.get(name='test event type 1')
		test_event_type_2 = Event_Type.objects.get(name='test event type 2')
		# check that the data is correct
		self.assertEqual(test_event_type_1.description,'event type 1 description')
		self.assertEqual(test_event_type_2.description,'event type 2 description')
		self.assertEqual(test_event_type_1.event_category,test_event_category_1)
		self.assertEqual(test_event_type_2.event_category,test_event_category_2)

	def test_upload_event_types_already_exist(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load some event categories first
		# open the file
		event_categories_file = open('people/tests/data/event_categories.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Categories',
											'file' : event_categories_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_category_1 = Event_Category.objects.get(name='test event category 1')
		test_event_category_2 = Event_Category.objects.get(name='test event category 2')
		# check that the data is correct
		self.assertEqual(test_event_category_1.description,'event category 1 description')
		self.assertEqual(test_event_category_2.description,'event category 2 description')
		# now load event types
		event_types_file = open('people/tests/data/event_types.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Types',
											'file' : event_types_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the test event categories that should have been loaded
		test_event_type_1 = Event_Type.objects.get(name='test event type 1')
		test_event_type_2 = Event_Type.objects.get(name='test event type 2')
		# check that the data is correct
		self.assertEqual(test_event_type_1.description,'event type 1 description')
		self.assertEqual(test_event_type_2.description,'event type 2 description')
		self.assertEqual(test_event_type_1.event_category,test_event_category_1)
		self.assertEqual(test_event_type_2.event_category,test_event_category_2)
		# close the file
		event_types_file.close()
		# now load event types again
		event_types_file = open('people/tests/data/event_types.csv')
		# submit the page with no answers
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Event Types',
											'file' : event_types_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional event types have been created
		self.assertEqual(Event_Type.objects.all().count(),2)

	def test_upload_questions_with_errors(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/questions_with_errors.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' not created: mandatory field question_text not provided')
		self.assertContains(response,'missing notes not created: mandatory field notes not provided')
		self.assertContains(response,'notes with no label not created: questions has notes but no notes label')
		# check that no records have been created
		self.assertFalse(Question.objects.all().exists())

	def test_upload_questions(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes created')
		self.assertContains(response,'test question without notes created')
		# get the records
		question_with_notes = Question.objects.get(question_text='test question with notes')
		question_without_notes = Question.objects.get(question_text='test question without notes')
		# check the records
		self.assertEqual(question_with_notes.notes,True)
		self.assertEqual(question_with_notes.notes_label,'test label')
		self.assertEqual(question_without_notes.notes,False)
		self.assertEqual(question_without_notes.notes_label,'')

	def test_download_questions(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes created')
		self.assertContains(response,'test question without notes created')
		# get the records
		question_with_notes = Question.objects.get(question_text='test question with notes')
		question_without_notes = Question.objects.get(question_text='test question without notes')
		# check the records
		self.assertEqual(question_with_notes.notes,True)
		self.assertEqual(question_with_notes.notes_label,'test label')
		self.assertEqual(question_without_notes.notes,False)
		self.assertEqual(question_without_notes.notes_label,'')
		# close the file
		valid_file.close()
		# download the question data we have just created
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Questions',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes,True,test label')
		self.assertContains(response,'test question without notes,False,')

	def test_upload_options_with_errors(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/options_with_errors.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'- missing question not created: mandatory field question not provided')
		self.assertContains(response,'missing label -  not created: mandatory field option_label not provided')
		self.assertContains(response,'question does not exist - test label not created: Question question does not exist does not exist')
		# check that no records have been created
		self.assertFalse(Option.objects.all().exists())

	def test_upload_options(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes created')
		self.assertContains(response,'test question without notes created')
		# get the records
		question_with_notes = Question.objects.get(question_text='test question with notes')
		question_without_notes = Question.objects.get(question_text='test question without notes')
		# check the records
		self.assertEqual(question_with_notes.notes,True)
		self.assertEqual(question_with_notes.notes_label,'test label')
		self.assertEqual(question_without_notes.notes,False)
		self.assertEqual(question_without_notes.notes_label,'')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes - test label created')
		# test that the record exists
		self.assertTrue(Option.objects.filter(question__question_text='test question with notes',option_label='test label').exists())
		# check that there is only one record
		self.assertEqual(Option.objects.all().count(),1)

	def test_upload_options_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes created')
		self.assertContains(response,'test question without notes created')
		# get the records
		question_with_notes = Question.objects.get(question_text='test question with notes')
		question_without_notes = Question.objects.get(question_text='test question without notes')
		# check the records
		self.assertEqual(question_with_notes.notes,True)
		self.assertEqual(question_with_notes.notes_label,'test label')
		self.assertEqual(question_without_notes.notes,False)
		self.assertEqual(question_without_notes.notes_label,'')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes - test label created')
		# test that the record exists
		self.assertTrue(Option.objects.filter(question__question_text='test question with notes',option_label='test label').exists())
		# check that there is only one record
		self.assertEqual(Option.objects.all().count(),1)
		# close the file
		valid_file.close()
		# now try it again
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes - test label not created: option already exists')
		# check that there is only one record
		self.assertEqual(Option.objects.all().count(),1)

	def test_download_options(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes created')
		self.assertContains(response,'test question without notes created')
		# get the records
		question_with_notes = Question.objects.get(question_text='test question with notes')
		question_without_notes = Question.objects.get(question_text='test question without notes')
		# check the records
		self.assertEqual(question_with_notes.notes,True)
		self.assertEqual(question_with_notes.notes_label,'test label')
		self.assertEqual(question_without_notes.notes,False)
		self.assertEqual(question_without_notes.notes_label,'')
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes - test label created')
		# test that the record exists
		self.assertTrue(Option.objects.filter(question__question_text='test question with notes',option_label='test label').exists())
		# check that there is only one record
		self.assertEqual(Option.objects.all().count(),1)
		# close the file
		valid_file.close()
		# download the option data we have just created
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Options',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test question with notes,test label')

class UploadPeopleDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and other base data
		set_up_address_base_data()
		set_up_test_post_codes('test_pc_')
		set_up_test_streets('test_street_','test_pc_0')
		# and some additional records
		test_age_status_limit = Age_Status.objects.create(
															status='Under five',
															default_role_type=Role_Type.objects.get(
																				role_type_name='test_role_type'),
															maximum_age=5
															)

	def test_upload_people_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' No first name not created: mandatory field first_name not provided')
		self.assertContains(response,'No last name  not created: mandatory field last_name not provided')
		self.assertContains(response,'No age status not created: mandatory field age_status not provided')
		self.assertContains(response,'No ABSS type not created: mandatory field ABSS_type not provided')
		self.assertContains(response,'No ethnicity not created: mandatory field ethnicity not provided')
		# check that no records have been created
		self.assertFalse(Person.objects.all().exists())

	def test_upload_people_data_missing_corresponding_records(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_missing_corresponding_records.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got a does not exist
		self.assertContains(response,'Missing age status not created: Age_Status missing age status does not exist')
		self.assertContains(response,'Missing role type not created: Role_Type missing role type does not exist')
		self.assertContains(response,'Missing ethnicity not created: Ethnicity missing ethnicity does not exist')
		self.assertContains(response,'Missing ABSS type not created: ABSS_Type missing ABSS type does not exist')
		self.assertContains(response,'Missing street not created: Street missing street does not exist')
		self.assertContains(response,'Missing post code not created: Post_Code missing pc does not exist')
		# check that no records have been created
		self.assertFalse(Person.objects.all().exists())

	def test_upload_people_data_cross_field_validation(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_cross_field_validation.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'Address missing house number not created: all of post code, street and name/number needed for address')
		self.assertContains(response,'Address missing street not created: all of post code, street and name/number needed for address')
		self.assertContains(response,'Address missing post code not created: all of post code, street and name/number needed for address')
		self.assertContains(response,'Pregnant missing due date not created: has no due date but is pregnant')
		self.assertContains(response,'Not pregnant with due date not created: has due date but is not pregnant')
		self.assertContains(response,'Role invalid for age status not created: role type is not valid for age status')
		self.assertContains(response,'Too old for age status not created: too old for age status')
		self.assertContains(response,'ABSS end date without start date not created: ABSS end date is provided but not ABSS start date')
		self.assertContains(response,'ABSS end date before start date not created: ABSS end date is not greater than ABSS start date')
		# check that no records have been created
		self.assertFalse(Person.objects.all().exists())

	def test_upload_people_data_invalid_dates(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_invalid_dates.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'Invalid date of birth not created: date_of_birth 01/01/19xx is invalid date or time')
		self.assertContains(response,'Invalid due date not created: due_date 01/01/19xx is invalid date or time')
		self.assertContains(response,'Invalid ABSS start date not created: ABSS_start_date 01/xx/2001 is invalid date or time')
		self.assertContains(response,'Invalid ABSS end date not created: ABSS_end_date 01/xx/2005 is invalid date or time')
		# check that no records have been created
		self.assertFalse(Person.objects.all().exists())

	def test_upload_people_data_invalid_lengths(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_invalid_lengths.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'123456789012345678901234567890123456789012345678901234567890 Person not created: first_name 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		self.assertContains(response,'Test 123456789012345678901234567890123456789012345678901234567890 not created: last_name 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		self.assertContains(response,'Test Person not created: email_address 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		self.assertContains(response,'Test Person not created: home_phone 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		self.assertContains(response,'Test Person not created: mobile_phone 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		self.assertContains(response,'Test Person not created: gender 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 25')
		self.assertContains(response,'Test Person not created: house_name_or_number 123456789012345678901234567890123456789012345678901234567890 is longer than maximum length of 50')
		# check that no records have been created
		self.assertFalse(Person.objects.all().exists())

	def test_upload_people(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the first person
		test_person = Person.objects.get(first_name='Test',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/1990')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# and the second person
		test_person = Person.objects.get(first_name='Test no dob',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test no dob')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# and the third person
		test_person = Person.objects.get(first_name='Test no street',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test no street')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# check that we have two people
		self.assertEqual(Person.objects.all().count(),3)

	def test_upload_people_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the person
		test_person = Person.objects.get(first_name='Test',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/1990')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# and the second person
		test_person = Person.objects.get(first_name='Test no dob',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test no dob')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# and the third person
		test_person = Person.objects.get(first_name='Test no street',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test no street')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# check that we have two people
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/people.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),3)

	def test_upload_people_same_name_different_age_status(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_same_name_different_age_status.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the first person
		test_person = Person.objects.get(first_name='Test',last_name='Person',age_status__status='Adult')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/1990')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,True)
		self.assertEqual(test_person.due_date.strftime('%d/%m/%Y'),'01/01/2020')
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# get the second person
		test_person = Person.objects.get(first_name='Test',last_name='Person',age_status__status='Child under four')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2019')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Child under four')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2005')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		# check that we only have two people
		self.assertEqual(Person.objects.all().count(),2)

class UploadEventsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_event_base_data()
		# and other base data
		set_up_address_base_data()
		set_up_venue_base_data()

	def test_upload_events_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' not created: mandatory field name not provided')
		self.assertContains(response,'No description not created: mandatory field description not provided')
		self.assertContains(response,'No date not created: mandatory field date not provided')
		self.assertContains(response,'No start time not created: mandatory field start_time not provided')
		self.assertContains(response,'No end time not created: mandatory field end_time not provided')
		# check that no records have been created
		self.assertFalse(Event.objects.all().exists())

	def test_upload_events_data_missing_corresponding_records(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events_missing_corresponding_records.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check the message
		self.assertContains(response,'Missing event type not created: Event_Type missing_test_event_type does not exist')
		self.assertContains(response,'Missing ward not created: Ward Missing test ward does not exist')
		self.assertContains(response,'Missing area not created: area Missing test area 2 does not exist')
		self.assertContains(response,'Missing venue not created: Venue missing_venue does not exist')
		# check that no records have been created
		self.assertFalse(Event.objects.all().exists())

	def test_upload_events_invalid_dates_and_times(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events_invalid_dates_and_times.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check the message
		self.assertContains(response,'Invalid date not created: date 01/01/201xx is invalid date or time')
		self.assertContains(response,'Invalid start time not created: start_time 10:xx is invalid date or time')
		self.assertContains(response,'Invalid end time not created: end_time 11:xx is invalid date or time')
		# check that no records have been created
		self.assertFalse(Event.objects.all().exists())

	def test_upload_events(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got a valid result
		self.assertEqual(response.status_code, 200)
		# get the record
		event = Event.objects.get(name='test event')
		# check the fields
		self.assertEqual(event.description,'test event description')
		self.assertEqual(event.event_type.name,'test_event_type')
		self.assertEqual(event.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(event.location,'Test location')
		self.assertEqual(event.venue.name,'test_venue')
		self.assertEqual(event.ward.ward_name,'Test ward 2')
		# check that the area connections exist
		self.assertTrue(event.areas.filter(area_name='Test area'))
		self.assertTrue(event.areas.filter(area_name='Test area 2'))
		# check that we only have one event
		self.assertEqual(Event.objects.all().count(),1)

	def test_upload_events_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got a valid result
		self.assertEqual(response.status_code, 200)
		# get the record
		event = Event.objects.get(name='test event')
		# check the fields
		self.assertEqual(event.description,'test event description')
		self.assertEqual(event.event_type.name,'test_event_type')
		self.assertEqual(event.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(event.location,'Test location')
		self.assertEqual(event.venue.name,'test_venue')
		self.assertEqual(event.ward.ward_name,'Test ward 2')
		# check that the area connections exist
		self.assertTrue(event.areas.filter(area_name='Test area'))
		self.assertTrue(event.areas.filter(area_name='Test area 2'))
		# check that we only have one event
		self.assertEqual(Event.objects.all().count(),1)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/events.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got a valid result
		self.assertEqual(response.status_code, 200)
		# check the response
		self.assertContains(response,'test event not created: event already exists')
		# check that we still only have one event
		self.assertEqual(Event.objects.all().count(),1)

	def test_upload_events_no_wards(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/events_no_wards.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Events',
											'file' : valid_file
											}
									)
		# check that we got a valid result
		self.assertEqual(response.status_code, 200)
		# get the record
		event = Event.objects.get(name='test event no ward no area')
		# check the fields
		self.assertEqual(event.description,'test event description')
		self.assertEqual(event.event_type.name,'test_event_type')
		self.assertEqual(event.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(event.location,'Test location')
		self.assertEqual(event.ward,None)
		# check that the area connections don't exist
		self.assertFalse(event.areas.all().exists())
		# get the record
		event = Event.objects.get(name='test event no ward with area')
		# check the fields
		self.assertEqual(event.description,'test event description')
		self.assertEqual(event.event_type.name,'test_event_type')
		self.assertEqual(event.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(event.location,'Test location')
		self.assertEqual(event.ward,None)
		# check that the area connections don't exist
		self.assertTrue(event.areas.filter(area_name='Test area').exists())
		# check that we only have two events
		self.assertEqual(Event.objects.all().count(),2)

class UploadRelationshipsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create a parent
		set_up_test_people('test_parent_',number=1,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')

	def test_upload_relationship_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationships_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationships',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' missing from first name is parent of to first name to last name not created: mandatory field from_first_name not provided')
		self.assertContains(response,'missing from last name  is parent of to first name to last name not created: mandatory field from_last_name not provided')
		self.assertContains(response,'missing from age status from last name is parent of to first name to last name not created: mandatory field from_age_status not provided')
		self.assertContains(response,'missing to first name from last name is parent of  to last name not created: mandatory field to_first_name not provided')
		self.assertContains(response,'missing to last name from last name is parent of to first name  not created: mandatory field to_last_name not provided')
		self.assertContains(response,'missing relationship type from last name is  of to first name to last name not created: mandatory field relationship_type not provided')
		# check that no records have been created
		self.assertFalse(Relationship.objects.all().exists())

	def test_upload_relationship_duplicates_and_missing_records(self):
		# create multiple people records
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationships_duplicate_and_missing_records.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationships',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_duplicate_0 test_duplicate_0 is parent of test_child_0 test_child_0 not created: from multiple matching Person records exist')
		self.assertContains(response,'test_child_0 test_child_0 is child of test_duplicate_0 test_duplicate_0 not created: to multiple matching Person records exist')
		self.assertContains(response,'missing from person from last name is parent of test_child_0 test_child_0 not created: from matching Person record does not exist')
		self.assertContains(response,'test_parent_0 test_parent_0 is parent of missing to person to last name not created: to matching Person record does not exist')
		self.assertContains(response,'test_parent_0 test_parent_0 is missing relationship type of test_child_0 test_child_0 not created: Relationship_Type missing relationship type does not exist')
		# check that no records have been created
		self.assertFalse(Relationship.objects.all().exists())

	def test_upload_relationships(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationships.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationships',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we have two records
		self.assertEqual(Relationship.objects.all().count(),2)
		# get the people
		parent = Person.objects.get(first_name='test_parent_0')
		child = Person.objects.get(first_name='test_child_0')
		# get the reletaionship types
		parent_relationship_type = Relationship_Type.objects.get(relationship_type='parent')
		child_relationship_type = Relationship_Type.objects.get(relationship_type='child')
		# get the from relationship
		parent_relationship = Relationship.objects.get(relationship_from=parent,relationship_to=child)
		# check the relationship type
		self.assertEqual(parent_relationship.relationship_type,parent_relationship_type)
		# get the to relationship
		child_relationship = Relationship.objects.get(relationship_from=child,relationship_to=parent)
		# check the relationship type
		self.assertEqual(child_relationship.relationship_type,child_relationship_type)

class UploadRegistrationsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)

	def test_upload_registration_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' missing first name (Adult) at test_event_0 not created: mandatory field first_name not provided')
		self.assertContains(response,'missing last name  (Adult) at test_event_0 not created: mandatory field last_name not provided')
		self.assertContains(response,'missing age status last name () at test_event_0 not created: mandatory field age_status not provided')
		self.assertContains(response,'missing event name last name (Adult) at  not created: mandatory field event_name not provided')
		self.assertContains(response,'missing event date last name (Adult) at test_event_0 not created: mandatory field event_date not provided')
		self.assertContains(response,'missing role type last name (Adult) at test_event_0 not created: mandatory field role_type not provided')
		# check that no records have been created
		self.assertFalse(Event_Registration.objects.all().exists())

	def test_upload_registration_data_invalid_fields(self):
		# create multiple people records
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		# create multiple event records
		set_up_test_events(
							'test_duplicate_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)
		set_up_test_events(
							'test_duplicate_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations_invalid_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'invalid age status last name (invalid) at test_event_0 not created: Age_Status invalid does not exist')
		self.assertContains(response,'invalid event date last name (Adult) at test_event_0 not created: event_date 01/xx/2019 is invalid date or time')
		self.assertContains(response,'invalid role type last name (Adult) at test_event_0 not created: Role_Type invalid does not exist')
		self.assertContains(response,'invalid person last name (Adult) at test_event_0 not created: matching Person record does not exist')
		self.assertContains(response,'test_duplicate_0 test_duplicate_0 (Adult) at test_event_0 not created: multiple matching Person records exist')
		self.assertContains(response,'invalid event last name (Adult) at invalid not created: matching Event record does not exist')
		self.assertContains(response,'duplicate event last name (Adult) at test_duplicate_0 not created: multiple matching Event records exist')
		self.assertContains(response,'test_child_0 test_child_0 (Child under four) at test_event_0 not created: adult_test_role is not valid for Child under four')
		self.assertContains(response,'invalid registered participated apologies last name (Adult) at test_event_0 not created: none of registered, apologies or participated is True')
		# check that no records have been created
		self.assertFalse(Event_Registration.objects.all().exists())

	def test_upload_registrations(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.apologies,True)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.apologies,False)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_adult_0.apologies,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)

	def test_upload_registrations_modified(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.apologies,True)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.apologies,False)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_child_0.apologies,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)
		# close the file
		valid_file.close()
		# process the modified file
		# open the file
		valid_file = open('people/tests/data/registrations_updated.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		second_role_type = Role_Type.objects.get(role_type_name='second_test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.apologies,True)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_0.apologies,True)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_child_0.apologies,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)

class UploadDownloadVenuesDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for venues
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()
		# get rid of the test venue
		test_venue = Venue.objects.get(name='test_venue')
		test_venue.delete()

	def test_upload_venues_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' not created: mandatory field name not provided')
		self.assertContains(response,'Missing venue type not created: mandatory field venue_type not provided')
		self.assertContains(response,'Missing building name or number not created: mandatory field building_name_or_number not provided')
		self.assertContains(response,'Missing street not created: mandatory field street not provided')
		self.assertContains(response,'Missing post code not created: mandatory field post_code not provided')
		# check that no records have been created
		self.assertFalse(Venue.objects.all().exists())

	def test_upload_venues_data_missing_corresponding_records(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_missing_corresponding_records.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got a does not exist
		self.assertContains(response,'Missing venue type not created: Venue_Type invalid does not exist')
		self.assertContains(response,'Missing street not created: Street invalid does not exist')
		self.assertContains(response,'Missing post code not created: Post_Code invalid does not exist')
		# check that no records have been created
		self.assertFalse(Venue.objects.all().exists())

	def test_upload_venues(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the first venue
		test_venue = Venue.objects.get(name='Test Venue')
		# check the fields
		self.assertEqual(test_venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(test_venue.building_name_or_number,'123')
		self.assertEqual(test_venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(test_venue.street.post_code,Post_Code.objects.get(post_code='TV10'))
		self.assertEqual(test_venue.contact_name,'contact')
		self.assertEqual(test_venue.phone,'phone')
		self.assertEqual(test_venue.mobile_phone,'mobile')
		self.assertEqual(test_venue.email_address,'test@test.com')
		self.assertEqual(test_venue.website,'website')
		self.assertEqual(test_venue.price,'price')
		self.assertEqual(test_venue.facilities,'facilities')
		self.assertEqual(test_venue.opening_hours,'opening_hours')
		self.assertEqual(test_venue.notes,'notes')
		# get the second venue
		test_venue = Venue.objects.get(name='Test Venue 2')
		# check the fields
		self.assertEqual(test_venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(test_venue.building_name_or_number,'456')
		self.assertEqual(test_venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(test_venue.street.post_code,Post_Code.objects.get(post_code='TV10'))
		self.assertEqual(test_venue.contact_name,'contact2')
		self.assertEqual(test_venue.phone,'phone2')
		self.assertEqual(test_venue.mobile_phone,'mobile2')
		self.assertEqual(test_venue.email_address,'test@test.com2')
		self.assertEqual(test_venue.website,'website2')
		self.assertEqual(test_venue.price,'price2')
		self.assertEqual(test_venue.facilities,'facilities2')
		self.assertEqual(test_venue.opening_hours,'opening_hours2')
		self.assertEqual(test_venue.notes,'notes2')
		# check that we have two people
		self.assertEqual(Venue.objects.all().count(),2)

	def test_upload_venues_already_exists(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the first venue
		test_venue = Venue.objects.get(name='Test Venue')
		# check the fields
		self.assertEqual(test_venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(test_venue.building_name_or_number,'123')
		self.assertEqual(test_venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(test_venue.street.post_code,Post_Code.objects.get(post_code='TV10'))
		self.assertEqual(test_venue.contact_name,'contact')
		self.assertEqual(test_venue.phone,'phone')
		self.assertEqual(test_venue.mobile_phone,'mobile')
		self.assertEqual(test_venue.email_address,'test@test.com')
		self.assertEqual(test_venue.website,'website')
		self.assertEqual(test_venue.price,'price')
		self.assertEqual(test_venue.facilities,'facilities')
		self.assertEqual(test_venue.opening_hours,'opening_hours')
		self.assertEqual(test_venue.notes,'notes')
		# get the second venue
		test_venue = Venue.objects.get(name='Test Venue 2')
		# check the fields
		self.assertEqual(test_venue.venue_type,Venue_Type.objects.get(name='test_venue_type'))
		self.assertEqual(test_venue.building_name_or_number,'456')
		self.assertEqual(test_venue.street,Street.objects.get(name='venue_street0'))
		self.assertEqual(test_venue.street.post_code,Post_Code.objects.get(post_code='TV10'))
		self.assertEqual(test_venue.contact_name,'contact2')
		self.assertEqual(test_venue.phone,'phone2')
		self.assertEqual(test_venue.mobile_phone,'mobile2')
		self.assertEqual(test_venue.email_address,'test@test.com2')
		self.assertEqual(test_venue.website,'website2')
		self.assertEqual(test_venue.price,'price2')
		self.assertEqual(test_venue.facilities,'facilities2')
		self.assertEqual(test_venue.opening_hours,'opening_hours2')
		self.assertEqual(test_venue.notes,'notes2')
		# check that we have two people
		self.assertEqual(Venue.objects.all().count(),2)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/venues.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'already exists')
		# check that no additional people have been created
		self.assertEqual(Venue.objects.all().count(),2)

	def test_download_venues(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# get the first venue
		test_venue = Venue.objects.get(name='Test Venue')
		# check that we have two people
		self.assertEqual(Venue.objects.all().count(),2)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Venues',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'Test Venue,test_venue_type,123,venue_street0,TV10,contact,phone,mobile,test@test.com,website,price,facilities,opening_hours,notes')
		self.assertContains(response,'Test Venue 2,test_venue_type,456,venue_street0,TV10,contact2,phone2,mobile2,test@test.com2,website2,price2,facilities2,opening_hours2,notes2')

class UploadVenuesForEventsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up test data
		set_up_event_base_data()
		set_up_address_base_data()
		set_up_venue_base_data()
		set_up_test_events(
							'test_event_',
							number=2,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)
		Venue.objects.create(
								name = 'test_venue_2',
								building_name_or_number = '123',
								venue_type = Venue_Type.objects.get(name='test_venue_type'),
								street = Street.objects.get(name='venue_street0')
								)

	def test_upload_venues_for_events_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_for_events_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues for Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' on 01/01/2019 at missing event name not created: mandatory field event_name not provided')
		self.assertContains(response,'missing date on  at test_venue not created: mandatory field event_date not provided')
		self.assertContains(response,'missing venue name on 01/01/2019 at  not created: mandatory field venue_name not provided')

	def test_upload_venues_for_events_invalid_dates(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_for_events_invalid_dates.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues for Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check the message
		self.assertContains(response,'test_event_0 on 01/01/20xx at test_venue not created: event_date 01/01/20xx is invalid date or time')

	def test_upload_venues_data_missing_corresponding_records(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_for_events_missing_corresponding_records.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues for Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got a does not exist
		self.assertContains(response,'invalid on 01/01/2019 at test_venue not created: matching Event record does not exist')
		self.assertContains(response,'test_event_0 on 01/01/2020 at test_venue not created: matching Event record does not exist')
		self.assertContains(response,'test_event_0 on 01/01/2019 at invalid not created: Venue invalid does not exist')

	def test_upload_venues_for_events(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/venues_for_events.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Venues for Events',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# test the events
		event = Event.objects.get(name='test_event_0')
		self.assertEqual(event.venue,Venue.objects.get(name='test_venue'))
		event = Event.objects.get(name='test_event_1')
		self.assertEqual(event.venue,Venue.objects.get(name='test_venue_2'))

class DownloadPeopleDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/downloaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_download_people(self):
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC')
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0')
		# get the second test person
		person = Person.objects.get(first_name='test_adult_1')
		# set the values
		person.other_names = 'test other_names'
		person.home_phone = '123456'
		person.mobile_phone = '789012'
		person.pregnant = True
		person.due_date = datetime.datetime.strptime('2010-01-01','%Y-%m-%d')
		person.house_name_or_number = '123'
		person.ABSS_start_date = datetime.datetime.strptime('2011-01-01','%Y-%m-%d')
		person.ABSS_end_date = datetime.datetime.strptime('2012-02-02','%Y-%m-%d')
		person.emergency_contact_details = 'test ecd'
		person.street = Street.objects.get(name='ABC streets 10')
		# save the record
		person.save()
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'People',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,,,,test notes,,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test other_names,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,123,ABC streets 10,ABC0,test notes,01/01/2011,02/02/2012,test ecd,Test ward')
		self.assertContains(response,'test_child_0,test_child_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Child under four,,,,test notes,,,,')

	def test_download_people_via_search(self):
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC')
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0')
		# get the second test person
		person = Person.objects.get(first_name='test_adult_1')
		# set the values
		person.other_names = 'test other_names'
		person.home_phone = '123456'
		person.mobile_phone = '789012'
		person.pregnant = True
		person.due_date = datetime.datetime.strptime('2010-01-01','%Y-%m-%d')
		person.house_name_or_number = '123'
		person.ABSS_start_date = datetime.datetime.strptime('2011-01-01','%Y-%m-%d')
		person.ABSS_end_date = datetime.datetime.strptime('2012-02-02','%Y-%m-%d')
		person.emergency_contact_details = 'test ecd'
		person.street = Street.objects.get(name='ABC streets 10')
		# save the record
		person.save()
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# submit a Download request to the people search page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Download Full Data',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'include_people' : 'all',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,,,,test notes,,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test other_names,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,123,ABC streets 10,ABC0,test notes,01/01/2011,02/02/2012,test ecd,Test ward')
		self.assertContains(response,'test_child_0,test_child_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Child under four,,,,test notes,,,,')

	def test_download_people_limited_via_search(self):
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC')
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0')
		# get the second test person
		person = Person.objects.get(first_name='test_adult_1')
		# set the values
		person.other_names = 'test other_names'
		person.home_phone = '123456'
		person.mobile_phone = '789012'
		person.pregnant = True
		person.due_date = datetime.datetime.strptime('2010-01-01','%Y-%m-%d')
		person.house_name_or_number = '123'
		person.ABSS_start_date = datetime.datetime.strptime('2011-01-01','%Y-%m-%d')
		person.ABSS_end_date = datetime.datetime.strptime('2012-02-02','%Y-%m-%d')
		person.emergency_contact_details = 'test ecd'
		person.street = Street.objects.get(name='ABC streets 10')
		# save the record
		person.save()
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# submit a Download request to the people search page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Download',
											'names' : '',
											'keywords' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'include_people' : 'all',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,,test@test.com,,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test other_names,test@test.com,123456,789012,123 ABC streets 10 ABC0,Test ward')
		self.assertContains(response,'test_child_0,test_child_0,,test@test.com,,,,')

class DownloadEventsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=2,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)
		# and other data
		set_up_address_base_data()
		set_up_venue_base_data()
		# and an extra area
		area_3 = Area.objects.create(area_name='Test area 3',use_for_events=True)
		# get the second event
		event = Event.objects.get(name='test_event_1')
		# set fields
		event.location = 'test location'
		event.description = 'test description'
		event.ward = Ward.objects.get(ward_name='Test ward')
		event.venue = Venue.objects.get(name='test_venue')
		# save the event
		event.save()
		# and add an area
		event.areas.add(Area.objects.get(area_name='Test area 2'))
		event.areas.add(area_3)


	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/downloaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_download_events(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Events',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_event_0,Test event description,test_event_type,01/01/2019,10:00,11:00,Test location,,,')
		self.assertContains(response,'test_event_1,test description,test_event_type,01/01/2019,10:00,11:00,test location,test_venue,Test ward,"Test area 2,Test area 3"')

class DownloadRelationshipsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create a parent
		set_up_test_people('test_parent_',number=1,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/downloaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_download_events(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/relationships.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Relationships',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we have two records
		self.assertEqual(Relationship.objects.all().count(),2)
		# get the people
		parent = Person.objects.get(first_name='test_parent_0')
		child = Person.objects.get(first_name='test_child_0')
		# get the reletaionship types
		parent_relationship_type = Relationship_Type.objects.get(relationship_type='parent')
		child_relationship_type = Relationship_Type.objects.get(relationship_type='child')
		# get the from relationship
		parent_relationship = Relationship.objects.get(relationship_from=parent,relationship_to=child)
		# check the relationship type
		self.assertEqual(parent_relationship.relationship_type,parent_relationship_type)
		# get the to relationship
		child_relationship = Relationship.objects.get(relationship_from=child,relationship_to=parent)
		# check the relationship type
		self.assertEqual(child_relationship.relationship_type,child_relationship_type)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Relationships',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_parent_0,test_parent_0,Adult,test_child_0,test_child_0,Child under four,parent')
		self.assertContains(response,'test_child_0,test_child_0,Child under four,test_parent_0,test_parent_0,Adult,child')

class DownloadRegistrationsDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/downloaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_download_registrations(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Registrations',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,test_event_0,01/01/2019,False,True,True,test_role_type')
		self.assertContains(response,'test_adult_1,test_adult_1,Adult,test_event_0,01/01/2019,True,False,True,test_role_type')
		self.assertContains(response,'test_child_0,test_child_0,Child under four,test_event_0,01/01/2019,True,True,False,test_role_type')

class DownloadEventSummaryDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/downloaddata')
		# check the response
		self.assertRedirects(response, '/people/login?next=/downloaddata')

	def test_no_redirect_if_superuser(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the response
		response = self.client.get('/downloaddata')
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)

	def test_download_summary(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Event Summary',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_event_0,01/01/2019,Test location,,2,2,2,3')

	def test_download_summary_with_venue(self):
		# create the venue and add it to the event
		set_up_address_base_data()
		set_up_venue_base_data()
		event = Event.objects.get(name='test_event_0')
		event.venue = Venue.objects.get(name='test_venue')
		event.save()
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/registrations.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Registrations',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and event records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		event = Event.objects.get(name='test_event_0')
		# and the role type
		role_type = Role_Type.objects.get(role_type_name='test_role_type')
		# get the records
		registration_adult_0 = Event_Registration.objects.get(person=adult_0,event=event)
		# check the values
		self.assertEqual(registration_adult_0.role_type,role_type)
		self.assertEqual(registration_adult_0.registered,False)
		self.assertEqual(registration_adult_0.participated,True)
		# get the records
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.participated,True)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,role_type)
		self.assertEqual(registration_child_0.registered,True)
		self.assertEqual(registration_child_0.participated,False)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Event Summary',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_event_0,01/01/2019,Test location,test_venue,2,2,2,3')

class UploadDownloadAnswersViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')		

	def test_upload_answers_with_errors(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers_with_errors.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'missing first name (Adult) - test question with notes - test label not created: mandatory field first_name not provided')
		self.assertContains(response,'missing last name  (Adult) - test question with notes - test label not created: mandatory field last_name not provided')
		self.assertContains(response,'missing age status last name () - test question with notes - test label not created: mandatory field age_status not provided')
		self.assertContains(response,'missing question last name (Adult) -  - test label not created: mandatory field question not provided')
		self.assertContains(response,'missing option last name (Adult) - test question with notes -  not created: mandatory field option not provided')
		self.assertContains(response,'person does not exist last name (Adult) - test question with notes - test label not created: matching Person record does not exist')
		self.assertContains(response,'age status does not exist last name (invalid age status) - test question with notes - test label not created: Age_Status invalid age status does not exist')
		self.assertContains(response,'question does not exist last name (Adult) - invalid question - test label not created: Question invalid question does not exist')
		self.assertContains(response,'option does not exist last name (Adult) - test question with notes - invalid label not created: matching Option record does not exist')

	def test_upload_answers(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		option = Option.objects.get(option_label='test label')
		# get the answer
		answer = Answer.objects.get(person=person)
		# check the results
		self.assertEqual(answer.question,question)
		self.assertEqual(answer.option,option)
		# and that we only have one record
		self.assertEqual(Answer.objects.all().count(),1)

	def test_upload_answers_duplicate(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		option = Option.objects.get(option_label='test label')
		# get the answer
		answer = Answer.objects.get(person=person)
		# check the results
		self.assertEqual(answer.question,question)
		self.assertEqual(answer.option,option)
		# and that we only have one record
		self.assertEqual(Answer.objects.all().count(),1)
		# close the file
		valid_file.close()
		# and go again
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'test_adult_0 test_adult_0 (Adult) - test question with notes - test label not created: answer already exists')
		# and that we only have one record
		self.assertEqual(Answer.objects.all().count(),1)

	def test_download_answers(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		option = Option.objects.get(option_label='test label')
		# get the answer
		answer = Answer.objects.get(person=person)
		# check the results
		self.assertEqual(answer.question,question)
		self.assertEqual(answer.option,option)
		# and that we only have one record
		self.assertEqual(Answer.objects.all().count(),1)
		# download the answer data we have just created
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Answers',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,test question with notes,test label')

class UploadDownloadAnswerNotesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')		

	def test_upload_answer_notes_with_errors(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answer_notes_with_errors.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'missing first name (Adult) - test question with notes - test notes not created: mandatory field first_name not provided')
		self.assertContains(response,'missing last name  (Adult) - test question with notes - test notes not created: mandatory field last_name not provided')
		self.assertContains(response,'missing age status last name () - test question with notes - test notes not created: mandatory field age_status not provided')
		self.assertContains(response,'missing question last name (Adult) -  - test notes not created: mandatory field question not provided')
		self.assertContains(response,'missing notes last name (Adult) - test question with notes -  not created: mandatory field notes not provided')
		self.assertContains(response,'person does not exist last name (Adult) - test question with notes - test notes not created: matching Person record does not exist')
		self.assertContains(response,'age status does not exist last name (invalid age status) - test question with notes - test notes not created: Age_Status invalid age status does not exist')
		self.assertContains(response,'question does not exist last name (Adult) - invalid question - test notes not created: Question invalid question does not exist')
		self.assertContains(response,'test_adult_0 test_adult_0 (Adult) - test question with notes - test notes not created: person has not answered this question')

	def test_upload_answer_notes(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answer_notes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		# get the answer
		answer_note = Answer_Note.objects.get(person=person)
		# check the results
		self.assertEqual(answer_note.notes,'test notes')
		# and that we only have one record
		self.assertEqual(Answer_Note.objects.all().count(),1)

	def test_upload_answer_notes_duplicate(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answer_notes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		# get the answer
		answer_note = Answer_Note.objects.get(person=person)
		# check the results
		self.assertEqual(answer_note.notes,'test notes')
		# and that we only have one record
		self.assertEqual(Answer_Note.objects.all().count(),1)
		# close the file
		valid_file.close()
		# and go again
		# open the file
		valid_file = open('people/tests/data/answer_notes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'test_adult_0 test_adult_0 (Adult) - test question with notes - test notes not created: answer note already exists')
		# and that we only have one record
		self.assertEqual(Answer.objects.all().count(),1)

	def test_download_answer_notes(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# load a file to create the questions
		valid_file = open('people/tests/data/questions.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Questions',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/options.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Options',
											'file' : valid_file
											}
									)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answers.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answers',
											'file' : valid_file
											}
									)
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/answer_notes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# download the answer note data we have just created
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Answer Notes',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,test question with notes,test notes')

class ActivitiesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('activities_test',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/activities/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/activities/1')

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('activities',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_new_activity(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,1)

	def test_activity_not_created_zero_hours(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '0'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have no activities
		self.assertEqual(Activity.objects.all().count(),0)
		# check that we got a message
		self.assertContains(response,'zero')

	def test_update_to_activity(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,1)
		# make an update
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,2)

	def test_different_activity_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		test_activity_type_2 = Activity_Type.objects.get(name='Test activity type 2')
		# submit the page
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,1)
		# make an update
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_2.pk),
											'date' : '01/01/2018',
											'hours' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),2)
		# get the activity
		activity = Activity.objects.get(person=person,activity_type=test_activity_type_2)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_2)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,2)

	def test_activity_deletion(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,1)
		# make an update
		# submit the page with no answers
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '0'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),0)

	def test_different_date_for_activity(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		test_activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		# submit the page
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/01/2018',
											'hours' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),1)
		# get the activity
		activity = Activity.objects.get(person=person)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/01/2018')
		self.assertEqual(activity.hours,1)
		# make an update
		response = self.client.post(
									reverse('activities',args=[person.pk]),
									data = { 

											'activity_type' : str(test_activity_type_1.pk),
											'date' : '01/02/2018',
											'hours' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we only have one activity
		self.assertEqual(Activity.objects.all().count(),2)
		# get the activity
		activity = Activity.objects.get(person=person,hours=2)
		# check that it has the right values
		self.assertEqual(activity.person,person)
		self.assertEqual(activity.activity_type,test_activity_type_1)
		self.assertEqual(activity.date.strftime('%d/%m/%Y'),'01/02/2018')
		self.assertEqual(activity.hours,2)
		
class UploadActivitiesDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)

	def test_upload_activity_data_missing_mandatory_fields(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activities_missing_mandatory_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,' missing first name (Adult), Test activity type 1 on 01/01/2019 not created: mandatory field first_name not provided')
		self.assertContains(response,'missing last name  (Adult), Test activity type 1 on 01/01/2019 not created: mandatory field last_name not provided')
		self.assertContains(response,'missing age status last name (), Test activity type 1 on 01/01/2019 not created: mandatory field age_status not provided')
		self.assertContains(response,'missing activity type last name (Adult),  on 01/01/2019 not created: mandatory field activity_type not provided')
		self.assertContains(response,'missing date last name (Adult), Test activity type 1 on  not created: mandatory field date not provided')
		self.assertContains(response,'missing hours last name (Adult), Test activity type 1 on 01/01/2019 not created: mandatory field hours not provided')
		# check that no records have been created
		self.assertFalse(Activity.objects.all().exists())	

	def test_upload_activities_data_invalid_fields(self):
		# create multiple people records
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		set_up_test_people('test_duplicate_',number=1,age_status='Adult')
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activities_invalid_fields.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'invalid age status last name (invalid), Test activity type 1 on 01/01/2019 not created: Age_Status invalid does not exist')
		self.assertContains(response,'invalid date last name (Adult), Test activity type 1 on 01/xx/2019 not created: date 01/xx/2019 is invalid date or time')
		self.assertContains(response,'invalid activity type last name (Adult), invalid on 01/01/2019 not created: Activity_Type invalid does not exist')
		self.assertContains(response,'invalid person last name (Adult), Test activity type 1 on 01/01/2019 not created: matching Person record does not exist')
		self.assertContains(response,'test_duplicate_0 test_duplicate_0 (Adult), Test activity type 1 on 01/01/2019 not created: multiple matching Person records exist')
		# check that no records have been created
		self.assertFalse(Event_Registration.objects.all().exists())

	def test_upload_activities(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and activity records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		activity_type_2 = Activity_Type.objects.get(name='Test activity type 2')
		# set the dates
		date_1 = datetime.datetime.strptime('2019-01-01','%Y-%m-%d')
		date_2 = datetime.datetime.strptime('2019-02-01','%Y-%m-%d')
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,4)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_2)
		# check the values
		self.assertEqual(activity.hours,3)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_2,date=date_1)
		# check the values
		self.assertEqual(activity.hours,2)
		# get the record to test
		activity = Activity.objects.get(person=adult_1,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,5)
		# get the record to test
		activity = Activity.objects.get(person=child_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,1)
		# check the count
		self.assertEqual(Activity.objects.all().count(),5)

	def test_upload_activities_updated(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and activity records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		activity_type_2 = Activity_Type.objects.get(name='Test activity type 2')
		# set the dates
		date_1 = datetime.datetime.strptime('2019-01-01','%Y-%m-%d')
		date_2 = datetime.datetime.strptime('2019-02-01','%Y-%m-%d')
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,4)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_2)
		# check the values
		self.assertEqual(activity.hours,3)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_2,date=date_1)
		# check the values
		self.assertEqual(activity.hours,2)
		# get the record to test
		activity = Activity.objects.get(person=adult_1,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,5)
		# get the record to test
		activity = Activity.objects.get(person=child_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,1)
		# check the count
		self.assertEqual(Activity.objects.all().count(),5)
		# close the file
		valid_file.close()
		# open the file
		valid_file = open('people/tests/data/activities_updated.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and activity records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		activity_type_2 = Activity_Type.objects.get(name='Test activity type 2')
		# set the dates
		date_1 = datetime.datetime.strptime('2019-01-01','%Y-%m-%d')
		date_2 = datetime.datetime.strptime('2019-02-01','%Y-%m-%d')
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,8)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_2)
		# check the values
		self.assertEqual(activity.hours,6)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_2,date=date_1)
		# check the values
		self.assertEqual(activity.hours,4)
		# get the record to test
		activity = Activity.objects.get(person=adult_1,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,10)
		# get the record to test
		activity = Activity.objects.get(person=child_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,2)
		# check the count
		self.assertEqual(Activity.objects.all().count(),5)

class DownloadActivitiesDataViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and relationship data
		set_up_relationship_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')
		# and a child
		set_up_test_people('test_child_',number=1,age_status='Child under four')
		# and event base data
		set_up_event_base_data()
		# and an event
		set_up_test_events(
							'test_event_',
							number=1,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01'
							)

	def test_download_activities(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/activities.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Activities',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the people and activity records
		adult_0 = Person.objects.get(first_name='test_adult_0')
		adult_1 = Person.objects.get(first_name='test_adult_1')
		child_0 = Person.objects.get(first_name='test_child_0')
		activity_type_1 = Activity_Type.objects.get(name='Test activity type 1')
		activity_type_2 = Activity_Type.objects.get(name='Test activity type 2')
		# set the dates
		date_1 = datetime.datetime.strptime('2019-01-01','%Y-%m-%d')
		date_2 = datetime.datetime.strptime('2019-02-01','%Y-%m-%d')
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,4)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_1,date=date_2)
		# check the values
		self.assertEqual(activity.hours,3)
		# get the record to test
		activity = Activity.objects.get(person=adult_0,activity_type=activity_type_2,date=date_1)
		# check the values
		self.assertEqual(activity.hours,2)
		# get the record to test
		activity = Activity.objects.get(person=adult_1,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,5)
		# get the record to test
		activity = Activity.objects.get(person=child_0,activity_type=activity_type_1,date=date_1)
		# check the values
		self.assertEqual(activity.hours,1)
		# check the count
		self.assertEqual(Activity.objects.all().count(),5)
		# submit the page to download the file
		response = self.client.post(
									reverse('downloaddata'),
									data = { 
											'file_type' : 'Activities',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,Test activity type 1,01/01/2019,4')
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,Test activity type 1,01/02/2019,3')
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,Test activity type 2,01/01/2019,2')
		self.assertContains(response,'test_child_0,test_child_0,Child under four,Test activity type 1,01/01/2019,1')
		self.assertContains(response,'test_adult_1,test_adult_1,Adult,Test activity type 1,01/01/2019,5')

class DocumentLinksViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/document_links')
		# check the response
		self.assertRedirects(response, '/people/login?next=/document_links')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('document_links'))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_no_documents(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('document_links'))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'No documents')

	def test_document_links(self):
		# create a document link
		Document_Link.objects.create(
										name='test document',
										description='test desc',
										link='test url',
										order=10
									)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('document_links'))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'test document')
		self.assertContains(response,'test desc')
		self.assertContains(response,'test url')