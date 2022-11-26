from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note, \
							Trained_Role, Activity_Type, Activity, Dashboard, Column, Panel, Panel_In_Column, \
							Panel_Column, Panel_Column_In_Panel, Filter_Spec, Column_In_Dashboard, \
							Venue, Venue_Type, Site, Invitation, Invitation_Step, Invitation_Step_Type, \
							Terms_And_Conditions, Profile, Chart, Document_Link, Project, Membership, \
							Project_Permission, Membership_Type, Project_Event_Type, Case_Notes, \
							Survey, Survey_Submission, Survey_Question_Type, Survey_Question, Survey_Answer, \
							Survey_Section, Survey_Series
import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.oath import totp
from django.utils import timezone
from django.core import mail
import json
from .test_functions import set_up_people_base_data, set_up_test_people, set_up_test_user, \
		set_up_test_project_permission, set_up_test_superuser, set_up_event_base_data, \
		set_up_relationship_base_data, set_up_address_base_data, set_up_test_post_codes, \
		set_up_test_streets, set_up_venue_base_data, set_up_test_events, set_up_test_questions, \
		set_up_test_options, project_login, set_up_relationship
import os

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
		self.assertEqual(profile.failed_login_attempts,1)

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
		self.assertEqual(profile.failed_login_attempts,0)

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
		self.assertEqual(profile.unsuccessful_otp_logins,1)
		self.assertEqual(profile.failed_login_attempts,1)

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
		self.assertEqual(profile.failed_login_attempts,1)

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
		self.assertEqual(profile.failed_login_attempts,0)

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
		self.assertEqual(profile.failed_login_attempts,0)

	def test_max_logins_invalid_password_no_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=False,
							max_login_attempts=3,
							)
		# attempt to login 4 times
		for attempt in range(4):
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
		self.assertEqual(profile.unsuccessful_logins,4)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)
		self.assertEqual(profile.failed_login_attempts,4)
		# attempt to login again
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Maximum login attempts exceeded: please contact administrator.')
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,5)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)
		self.assertEqual(profile.failed_login_attempts,5)

	def test_max_logins_valid_password_with_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True,
							max_login_attempts=3,
							)
		# attempt to login 4 times
		for attempt in range(4):
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
		self.assertEqual(profile.unsuccessful_logins,4)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,4)
		self.assertEqual(profile.failed_login_attempts,4)
		# attempt to login again
		totp_device = TOTPDevice.objects.get(name='test_totp')
		token = totp(totp_device.bin_key)
		response = self.client.post(
									reverse('login'),
									data = {
											'email_address' : 'test@test.com',
											'password' : 'testword',
											'token' : str(token)
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Maximum login attempts exceeded: please contact administrator.')
		# check the profile
		profile = Profile.objects.get(user__username='test@test.com')
		self.assertEqual(profile.unsuccessful_logins,5)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,5)
		self.assertEqual(profile.failed_login_attempts,5)

	def test_failed_attempts_reset_no_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=False,
							max_login_attempts=3,
							)
		# attempt to login twice
		for attempt in range(2):
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
		self.assertEqual(profile.unsuccessful_logins,2)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)
		self.assertEqual(profile.failed_login_attempts,2)
		# attempt to login again
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
		self.assertEqual(profile.unsuccessful_logins,2)
		self.assertEqual(profile.successful_logins,1)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,0)
		self.assertEqual(profile.failed_login_attempts,0)

	def test_failed_attempts_reset_with_otp(self):
		Site.objects.create(
							name='Test site',
							otp_required=True,
							max_login_attempts=3,
							)
		# attempt to login twice
		for attempt in range(2):
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
		self.assertEqual(profile.unsuccessful_logins,2)
		self.assertEqual(profile.successful_logins,0)
		self.assertEqual(profile.successful_otp_logins,0)
		self.assertEqual(profile.unsuccessful_otp_logins,2)
		self.assertEqual(profile.failed_login_attempts,2)
		# attempt to login again
		totp_device = TOTPDevice.objects.get(name='test_totp')
		token = totp(totp_device.bin_key)
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
		self.assertEqual(profile.unsuccessful_logins,2)
		self.assertEqual(profile.successful_logins,1)
		self.assertEqual(profile.successful_otp_logins,1)
		self.assertEqual(profile.unsuccessful_otp_logins,2)
		self.assertEqual(profile.failed_login_attempts,0)

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
		# and a test membership type
		test_membership_type = Membership_Type.objects.create(name='test_membership_type',default=True)

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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
		# and future leaving dates for another names
		today = datetime.date.today()
		people_to_include = Person.objects.filter(first_name__startswith='Another_Name_')
		for person in people_to_include:
			person.ABSS_end_date = today.replace(year=today.year+1)
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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

	def test_search_include_left_dont_include_future_leavers(self):
		# set past leaving dates for different names
		people_to_include = Person.objects.filter(first_name__startswith='Different_Name_')
		for person in people_to_include:
			person.ABSS_end_date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d')
			person.save()
		# and future leaving dates for another names
		today = datetime.date.today()
		people_to_include = Person.objects.filter(first_name__startswith='Another_Name_')
		for person in people_to_include:
			person.ABSS_end_date = today.replace(year=today.year+1)
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'keywords' : "'in project'",
											'role_type' : '0',
											'membership_type' : '0',
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
											'keywords' : "'in project'",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'keywords' : "'left project'",
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
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'keywords' : "'left project'",
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the error message
		self.assertContains(response,'Test_Role_1_0,Test_Role_1_0,,test@test.com,,,01/01/2000,Gender,test role 1,')
		self.assertContains(response,'Test_Role_1_49,Test_Role_1_49,,test@test.com,,,01/01/2000,Gender,test role 1,')

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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'keywords' : "'test role 1'",
											'role_type' : '0',
											'membership_type' : '0',
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
											'keywords' : "'test role 1'",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : '0',
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
											'keywords' : "'test role 2' second_test_ABSS_type",
											'role_type' : '0',
											'membership_type' : '0',
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
											'keywords' : "'test role 2' second_test_ABSS_type",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='Third test ABSS').pk),
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'keywords' : "'test role 2' child",
											'role_type' : '0',
											'membership_type' : '0',
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
											'keywords' : "'test role 2' child",
											'role_type' : '0',
											'membership_type' : '0',
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
											'keywords' : "'test role 2' second_test_ABSS_type child",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'keywords' : "'test role 1' adult",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'keywords' : "'Test ward'",
											'role_type' : '0',
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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
											'membership_type' : '0',
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

	def test_name_search_with_projects_active_no_results(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# create some extra people
		set_up_test_people('not_member_','test role 1',30)
		set_up_test_people('is_member_','test role 1',35,project=project)
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'not_member',
											'keywords' : '',
											'role_type' : '0',
											'membership_type' : '0',
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

	def test_name_search_with_projects_active_with_results(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# create some extra people
		set_up_test_people('not_member_','test role 1',30)
		set_up_test_people('is_member_','test role 1',35,project=project)
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'is_member',
											'keywords' : '',
											'role_type' : '0',
											'membership_type' : '0',
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

	def test_name_search_with_projects_active_with_results_second_page(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# create some extra people
		set_up_test_people('not_member_','test role 1',30)
		set_up_test_people('is_member_','test role 1',35,project=project)
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'Search',
											'names' : 'is_member',
											'keywords' : '',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '2'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_people'],35)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),10)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)

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

	def test_membership_type_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/membership_type/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/membership_type/1')

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
		response = self.client.get(reverse('membership_type',args=[ABSS_Type.objects.get(name='test_ABSS_type').pk]))
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
		response = self.client.get(reverse('membership_type',args=[test_ABSS_type.pk]))
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

	def test_role_type_search_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# create a new type
		test_role_type = Role_Type.objects.create(role_type_name='People Query Test',use_for_events=True,use_for_people=True)
		# create some extra people
		set_up_test_people('Role Type Query Test','People Query Test',30,'test_ABSS_type','Adult',project=project)
		set_up_test_people('Role Type Query Test','People Query Test',25,'test_ABSS_type','Adult')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		set_up_test_events('Test_Event_Type_4_', test_event_type_4,50)
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

	def test_search_ward(self):
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

	def test_search_name_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# get the event type
		event_type = Event_Type.objects.get(name='test_event_type_1')
		# create a project event type
		Project_Event_Type.objects.create(
											project=project,
											event_type=event_type
										)
		# set up some more events within the project
		set_up_test_events('Test_Event_Type_1_',event_type,50,project=project)
		# log the user in
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		event = Event.objects.get(name='Test_Event_Type_1_0')
		response = self.client.get(reverse('event',args=[event.pk]))
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
		event = Event.objects.get(name='Test_Event_Type_1_0')
		response = self.client.get(reverse('event',args=[event.pk]))
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
		event = Event.objects.get(name='Test_Event_Type_1_0')
		response = self.client.get(reverse('event',args=[event.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response,'WARNING')

	def test_pagination_default_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		event = Event.objects.get(name='Test_Event_Type_1_0')
		page = '/event/' + str(event.pk)
		response = self.client.get(page)
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),25)
		self.assertEqual(len(response.context['page_list']),3)

	def test_pagination_first_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		event = Event.objects.get(name='Test_Event_Type_1_0')
		page = '/event/' + str(event.pk) + '/1'
		response = self.client.get(page)
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),25)
		self.assertEqual(len(response.context['page_list']),3)

	def test_pagination_last_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		event = Event.objects.get(name='Test_Event_Type_1_0')
		page = '/event/' + str(event.pk) + '/3'
		response = self.client.get(page)
		# check the response
		self.assertEqual(response.status_code, 200)
		# and the contents
		self.assertEqual(len(response.context['registrations']),5)
		self.assertEqual(len(response.context['page_list']),3)

	def test_error_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get the events page
		response = self.client.get(reverse('event',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Event does not exist')

	def test_success_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# get the event and set the project
		event = Event.objects.get(name='Test_Event_Type_1_0')
		event.project = project
		event.save()
		# attempt to get the events page
		response = self.client.get(reverse('event',args=[event.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Test_Event_Type_1_0')

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

	def test_create_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		# check that the membership exists
		membership = Membership.objects.get(project=project,person=test_person)

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

	def test_invalid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# submit a post for a person who is not in the project
		response = self.client.get(reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person does not exist')

	def test_valid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person
		set_up_test_people('Person_','test_role_type',1,project=project)
		# submit a post for a person who is not in the project
		response = self.client.get(reverse('profile',args=[Person.objects.get(first_name='Person_0').pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person_0')

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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : '99',
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '',
											'date_left_project' : '01/01/2015',
											'membership_number' : '1',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Date left project can only be entered if date joined project is entered.')

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
											'role_type' : str(Role_Type.objects.get(role_type_name='age_test_role').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2016',
											'date_left_project' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Date left project must be after date joined project.')

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
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : '01/01/2012',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : tomorrow.strftime('%d/%m/%Y'),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'none',
											'trained_date_' + str(role_type.pk) : '01/01/2010',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'active',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'none',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role_' + str(role_type.pk) : 'active',
											'trained_date_' + str(role_type.pk) : '',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'trained_role_' + str(role_type.pk) : 'trained',
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
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

	def test_update_profile_with_projects_active(self):
		# log the user in
		project = project_login(self.client,username='testuser',password='testword')
		# create a person in a project
		set_up_test_people('Person_','test_role_type',1,project=project)
		# and an extra membership type
		Membership_Type.objects.create(name='new_membership_type')
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(Membership_Type.objects.get(name='new_membership_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		test_membership = Membership.objects.get(person=test_person,project=project)
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
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.age_status.status,'Default role age status')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.membership_number,0)
		self.assertEqual(test_membership.membership_type.name,'new_membership_type')
		self.assertEqual(test_membership.date_joined.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_membership.date_left.strftime('%d/%m/%Y'),'01/01/2015')

	def test_update_profile_with_projects_active_no_trained_roles(self):
		# log the user in
		project = project_login(self.client,username='testuser',password='testword')
		# set no trained roles for the project
		project.has_trained_roles = False
		# create a person in a project
		set_up_test_people('Person_','test_role_type',1,project=project)
		# and an extra membership type
		Membership_Type.objects.create(name='new_membership_type')
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'membership_type' : str(Membership_Type.objects.get(name='new_membership_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Default role age status').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'date_joined_project' : '01/01/2010',
											'date_left_project' : '01/01/2015',
											'membership_number' : '0',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='updated_first_name')
		test_membership = Membership.objects.get(person=test_person,project=project)
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
		self.assertEqual(test_person.ethnicity.description,'second_test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.age_status.status,'Default role age status')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.membership_number,0)
		self.assertEqual(test_membership.membership_type.name,'new_membership_type')
		self.assertEqual(test_membership.date_joined.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_membership.date_left.strftime('%d/%m/%Y'),'01/01/2015')

class TrainedRolesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_people_base_data()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/trained_roles/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/trained_roles/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('trained_roles',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_invalid_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('trained_roles',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_invalid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# submit a post for a person who is not in the project
		response = self.client.get(reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person does not exist')

	def test_valid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person
		set_up_test_people('Person_','test_role_type',1,project=project)
		# submit a post for a person who is not in the project
		response = self.client.get(reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person_0')

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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : '01/01/2012',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the records
		test_person = Person.objects.get(first_name='Person_0')
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : tomorrow.strftime('%d/%m/%Y'),
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'none',
											'trained_date_' + str(role_type.pk) : '01/01/2010',
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'active',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the records
		test_person = Person.objects.get(first_name='Person_0')
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'none',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(first_name='Person_0')
		# check that no trained role records exist
		self.assertEqual(test_person.trained_roles.all().exists(),False)

	def test_update_trained_role_blank_date(self):
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'active',
											'trained_date_' + str(role_type.pk) : '',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the records
		test_person = Person.objects.get(first_name='Person_0')
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		self.assertEqual(trained_role.date_trained,None)
		# check the active status
		self.assertEqual(trained_role.active,True)

	def test_update_trained_role_with_projects_active(self):
		# log the user in
		project = project_login(self.client,username='testuser',password='testword')
		project.has_trained_roles = True
		project.save()
		# create a person in a project
		set_up_test_people('Person_','test_role_type',1,project=project)
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : '01/01/2012',
											'action' : 'Submit'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the records
		test_person = Person.objects.get(first_name='Person_0')
		self.assertEqual(test_person.membership_number,0)
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		self.assertEqual(trained_role.date_trained.strftime('%d/%m/%Y'),'01/01/2012')
		# check the active status
		self.assertEqual(trained_role.active,False)

	def test_update_trained_role_with_project_without_trained_roles(self):
		# log the user in
		project = project_login(self.client,username='testuser',password='testword')
		project.has_trained_roles = False
		project.save()
		# create a person in a project
		set_up_test_people('Person_','test_role_type',1,project=project)
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
									reverse('trained_roles',args=[Person.objects.get(first_name='Person_0').pk]),
									data = { 
											'trained_role_' + str(role_type.pk) : 'trained',
											'trained_date_' + str(role_type.pk) : '01/01/2012',
											'action' : 'Submit'
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Trained roles not available for this project')


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

	def test_invalid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person
		set_up_test_people('Person_','test_role_type',1)
		# submit a post for a person who is not in the project
		response = self.client.get(reverse('add_relationship',args=[Person.objects.get(first_name='Person_0').pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person does not exist')

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

	def test_find_existing_person_for_relationship_in_project_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1,project=project)
		# create a person to add the relationships to
		set_up_test_people('Test_exists_','test_role_type',1,project=project)
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

	def test_add_relationship_to_new_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1,project=project)
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
		self.assertEqual(test_new_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_new_person.families.all().exists(),False)
		self.assertEqual(test_new_person.savs_id,None)
		self.assertEqual(test_new_person.age_status.status,'Adult')
		self.assertEqual(test_new_person.house_name_or_number,'')
		self.assertEqual(test_new_person.street,None)
		# check that the membership exists
		membership = Membership.objects.get(project=project,person=test_new_person)
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

	def test_find_existing_person_for_relationship_in_project_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create the person that we are connecting to
		set_up_test_people('Test_target_','test_role_type',1,project=project)
		# create a person to add the relationships to
		set_up_test_people('Test_exists_','test_role_type',1,project=project)
		# submit a post for a person who exists
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

	def test_add_relationship_to_new_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a person to add the relationships to
		set_up_test_people('Test_from_','test_role_type',1,project=project)
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
		self.assertEqual(test_new_person.ethnicity.description,'Prefer not to say')
		self.assertEqual(test_new_person.families.all().exists(),False)
		self.assertEqual(test_new_person.savs_id,None)
		self.assertEqual(test_new_person.age_status.status,'Adult')
		self.assertEqual(test_new_person.house_name_or_number,'')
		self.assertEqual(test_new_person.street,None)
		# check that the membership has been created
		membership = Membership.objects.get(person=test_new_person,project=project)
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
												'venue' : str(Venue.objects.get(name='test_venue').pk),
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
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_create_event_area_not_selected(self):
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
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_create_event_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# get the event type
		event_type = Event_Type.objects.get(name='test_event_type')
		# create a project event type
		Project_Event_Type.objects.create(
											project=project,
											event_type=event_type
										)
		# add an event
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testeventdesc',
												'venue' : str(Venue.objects.get(name='test_venue').pk),
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(event_type.pk),
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
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)
		self.assertEqual(test_event.project,project)

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
		self.assertContains(response,'Event does not exist')

	def test_invalid_event_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		test_event = Event.objects.get(name='test_event_0')
		# attempt to get an invalid event
		response = self.client.get(reverse('event_registration',args=[test_event.pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Event does not exist')

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

	def test_event_registration_search_no_results_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1,project=project)
		# create some people
		set_up_test_people('Found_name_','test_role_type',50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'Found'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],0)

	def test_event_registration_search_with_results_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1,project=project)
		# create some people
		set_up_test_people('Found_name_','test_role_type',50,project=project)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'names' : 'Found'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],50)

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
		self.assertContains(response,'Event does not exist')

	def test_invalid_event_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(name='test_event_type'),1)
		test_event = Event.objects.get(name='test_event_0')
		# attempt to get an invalid event
		response = self.client.get(reverse('edit_event',args=[test_event.pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Event does not exist')

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
											'venue' : str(Venue.objects.get(name='test_venue').pk),
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
		self.assertEqual(test_event.venue.name,'test_venue')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_edit_event_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event type
		event_type = Event_Type.objects.get(name='test_event_type')
		# create a project event type
		Project_Event_Type.objects.create(
											project=project,
											event_type=event_type
										)
		# create an event
		set_up_test_events('Event_',event_type,1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[Event.objects.get(name='Event_0').pk]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'venue' : str(Venue.objects.get(name='test_venue').pk),
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(event_type.pk),
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
		self.assertEqual(test_event.venue.name,'test_venue')
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
											'venue' : updated_venue.pk,
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
		self.assertEqual(test_event.venue.name,'updated_venue')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

	def test_edit_event_area_not_selected(self):
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
											'venue' : str(Venue.objects.get(name='test_venue').pk),
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
		self.assertEqual(test_event.venue.name,'test_venue')
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
		self.assertContains(response,'Person does not exist')

	def test_invalid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get an invalid person
		test_person = Person.objects.get(first_name='address_test0')
		response = self.client.get(reverse('address_to_relationships',args=[test_person.pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person does not exist')

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
		q_no_notes = Question.objects.get(question_text='q_no_notes0')
		set_up_test_options('q_no_notes_option_',question=q_no_notes,number=2)
		# create a question with notes
		set_up_test_questions('q_with_notes',notes=True)
		q_with_notes = Question.objects.get(question_text='q_with_notes0')
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

	def test_questions_if_logged_in_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# add project related data
		set_up_test_people('question_project_test',project=project)
		question = Question.objects.get(question_text='q_no_notes0')
		question.projects.add(project)
		# create a question for a different project
		set_up_test_questions('q_different_project')
		question = Question.objects.get(question_text='q_different_project0')
		set_up_test_options('q_no_notes_option_',question=question,number=2)
		different_project = Project.objects.create(name='different_project')
		question.projects.add(different_project)
		# log the user in
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get the events page
		response = self.client.get(reverse('answer_questions',args=[Person.objects.get(first_name='question_project_test0').pk]))
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the questions
		self.assertContains(response,'q_no_notes0')
		self.assertContains(response,'q_with_notes0')
		self.assertNotContains(response,'q_different_project0')

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

	def test_invalid_person_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# attempt to get an invalid person
		test_person = Person.objects.get(first_name='activities_test0')
		response = self.client.get(reverse('activities',args=[test_person.pk]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'Person does not exist')

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

	def test_new_activity_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create a test person
		set_up_test_people('project_test',number=1,project=project)
		person = Person.objects.get(first_name='project_test0')
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
		self.assertEqual(activity.project,project)

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

class ManageMembershipViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# set up an additional project
		project_2 = Project.objects.create(name='testproject_2')
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
		# create test membership types
		test_membership_type = Membership_Type.objects.create(name='test_membership_type',default=True)
		second_test_membership_type = Membership_Type.objects.create(name='second_test_membership_type')
		# create a test ABSS type
		test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type',membership_type=test_membership_type)
		# create a second test ABSS type
		second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type',membership_type=second_test_membership_type)
		# Create 50 of each type
		set_up_test_people('Parent_','Parent',50)
		set_up_test_people('Parent_Champion_','Parent Champion',50)
		set_up_test_people('Test_Role_1_','test role 1',50)
		set_up_test_people('Test_Role_2_','test role 2',50)
		# and 50 of each of the two test role types with different names
		set_up_test_people('Different_Name_','test role 1',50,project=project)
		set_up_test_people('Another_Name_','test role 2',50,project=project_2)
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
		response = self.client.get('/manage_membership')
		# check the response
		self.assertRedirects(response, '/people/login?next=/manage_membership')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/manage_membership')
		# check the response
		self.assertRedirects(response, '/')

	def test_empty_page_if_logged_in(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.get(reverse('manage_membership'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['people']),0)

	def test_search_with_no_criteria(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'page' : '1',
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
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
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

	def test_search_by_name(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Search',
											'names' : 'Another',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
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

	def test_search_by_keyword(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : 'parent',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
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

	def test_search_by_project(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Search',
											'names' : '',
											'keywords' : '',
											'project_id' : str(Project.objects.get(name='testproject').pk),
											'role_type' : '0',
											'membership_type' : '0',
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

	def test_move_into_project(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)

	def test_move_into_project_without_dates(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'without_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
			self.assertEqual(membership.date_joined,None)
			self.assertEqual(membership.date_left,None)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)

	def test_move_into_project_with_dates(self):
		# set the dates
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			person.ABSS_start_date = datetime.datetime.strptime('2012-01-01','%Y-%m-%d')
			person.ABSS_end_date = datetime.datetime.strptime('2025-01-01','%Y-%m-%d')
			person.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
			self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2012')
			self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2025')
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)

	def test_move_into_project_already_members(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)
		# and that we got the right text in the response
		self.assertContains(response,'10 people not added: already members')

	def test_remove_from_project(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'add',
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
		# go through the people and check that they have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertTrue(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),110)
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'remove',
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
		# go through the people and check that they don't have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertFalse(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),100)

	def test_remove_from_project_not_members(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_membership'),
									data = { 
											'action' : 'Move',
											'names' : 'short_set',
											'keywords' : '',
											'project_id' : '0',
											'role_type' : '0',
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'ward' : '0',
											'target_project_id' : str(Project.objects.get(name='testproject').pk),
											'date_type' : 'with_dates',
											'move_type' : 'remove',
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
		# go through the people and check that they don't have a membership
		project = Project.objects.get(name='testproject')
		for person in Person.objects.filter(first_name__startswith='Short_Set_'):
			membership = Membership.try_to_get(project=project,person=person)
			self.assertFalse(membership)
		# check that we have the right number of memberships
		self.assertEqual(Membership.objects.all().count(),100)
		# and that we got the right text in the response
		self.assertContains(response,'10 people not removed: not members')

class ManageProjectEventsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user and superuser
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# set up an additional project
		project_2 = Project.objects.create(name='testproject_2')
		# set up address base data
		set_up_address_base_data()
		# create an event category
		test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
		# and another couple of event categories
		test_event_category_2 = Event_Category.objects.create(name='test_event_category_2',description='category desc')
		test_event_category_3 = Event_Category.objects.create(name='test_event_category_3',description='category desc')
		# create a load of event types and add them to projects
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_1)
		Project_Event_Type.objects.create(project=project_2,event_type=test_event_type_1)	
		test_event_type_2 = Event_Type.objects.create(
														name = 'test_event_type_2',
														description = 'type desc',
														event_category = test_event_category_2)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_2)
		Project_Event_Type.objects.create(project=project_2,event_type=test_event_type_2)	
		test_event_type_3 = Event_Type.objects.create(
														name = 'test_event_type_3',
														description = 'type desc',
														event_category = test_event_category)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_3)
		Project_Event_Type.objects.create(project=project_2,event_type=test_event_type_3)	
		test_event_type_4 = Event_Type.objects.create(
														name = 'test_event_type_4',
														description = 'type desc',
														event_category = test_event_category)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_4)
		test_event_type_5 = Event_Type.objects.create(
														name = 'test_event_type_5',
														description = 'type desc',
														event_category = test_event_category)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_5)
		test_event_type_6 = Event_Type.objects.create(
														name = 'test_event_type_6',
														description = 'type desc',
														event_category = test_event_category_3)
		Project_Event_Type.objects.create(project=project,event_type=test_event_type_6)
		test_event_type_7 = Event_Type.objects.create(
														name = 'test_event_type_7',
														description = 'type desc',
														event_category = test_event_category)
		# Create 50 of each type
		set_up_test_events('Test_Event_Type_1_', test_event_type_1,50)
		set_up_test_events('Test_Event_Type_2_', test_event_type_2,50)
		set_up_test_events('Test_Event_Type_3_', test_event_type_3,50)
		set_up_test_events('Test_Event_Type_4_', test_event_type_4,50)
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
		response = self.client.get('/manage_project_events')
		# check the response
		self.assertRedirects(response, '/people/login?next=/manage_project_events')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/manage_project_events')
		# check the response
		self.assertRedirects(response, '/')

	def test_empty_page_if_logged_in(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.get(reverse('manage_project_events'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['events']),0)

	def test_search_with_no_criteria(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'event_type' : '0',
											'project_id' : '0',
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
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'event_type' : '0',
											'project_id' : '0',
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

	def test_search_by_name(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : 'Type_1',
											'event_type' : '0',
											'project_id' : '0',
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

	def test_search_by_event_type(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : '',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_1').pk),
											'project_id' : '0',
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

	def test_search_by_name_and_event_type(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : 'Type_1',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_1').pk),
											'project_id' : '0',
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

	def test_search_by_project(self):
		# add events to the project
		project = Project.objects.get(name='testproject')
		for event in Event.objects.filter(name__startswith='Test_Event_Type_1_'):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Search',
											'name' : 'Type_1',
											'event_type' : '0',
											'project_id' : str(project.pk),
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

	def test_add_to_project_invalid_event_type(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_7')
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'add',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the events still have blank projects
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,None)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not added: invalid event type')

	def test_add_to_project_registrations_not_in_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# create a person and register them to all relevant events
		set_up_people_base_data()
		set_up_test_people('Not_in_project_',number=1)
		person = Person.objects.get(first_name='Not_in_project_0')
		role_type=Role_Type.objects.get(role_type_name='test_role_type')
		for event in Event.objects.filter(event_type=event_type):
			Event_Registration.objects.create(
												event=event,
												person=person,
												role_type=role_type,
												registered=True,
												participated=False,
												apologies=False
												)
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'add',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the events still have blank projects
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,None)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not added: registrations not in project')

	def test_add_to_project_already_in_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# add the event to the project
		for event in Event.objects.filter(event_type=event_type):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'add',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events have not changed
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,project)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not added: already in project')

	def test_add_to_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'add',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events is correct
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,project)
		# and that we got the right text in the response
		self.assertContains(response,'30 events added to project')

	def test_move_between_projects_invalid_event_type(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# add the event to the project
		for event in Event.objects.filter(event_type=event_type):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'add',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events have not changed
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,project)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not added: invalid event type')

	def test_move_between_projects_registrations_not_in_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_3')
		# create a person
		set_up_people_base_data()
		set_up_test_people('Not_in_project_',number=1)
		person = Person.objects.get(first_name='Not_in_project_0')
		role_type=Role_Type.objects.get(role_type_name='test_role_type')
		# add each event to the project and register the person
		for event in Event.objects.filter(event_type=event_type):
			Event_Registration.objects.create(
												event=event,
												person=person,
												role_type=role_type,
												registered=True,
												participated=False,
												apologies=False
												)
			event.project = project
			event.save()
		# and add the person to the source project
		Membership.objects.create(
									person=person,
									project=project,
									membership_type=Membership_Type.objects.get(name='test_membership_type')
								)
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'add',
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
		# check that the events still have blank projects
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,project)
		# and that we got the right text in the response
		self.assertContains(response,'50 events not added: registrations not in project')

	def test_move_between_projects(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_3')
		# add the event to the project
		for event in Event.objects.filter(event_type=event_type):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'add',
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
		# check that the project for the events have not changed
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,target_project)
		# and that we got the right text in the response
		self.assertContains(response,'50 events added to project')

	def test_move_between_projects_with_registrations(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_3')
		# create a person
		set_up_people_base_data()
		set_up_test_people('Not_in_project_',number=1)
		person = Person.objects.get(first_name='Not_in_project_0')
		role_type=Role_Type.objects.get(role_type_name='test_role_type')
		# add each event to the project and register the person
		for event in Event.objects.filter(event_type=event_type):
			Event_Registration.objects.create(
												event=event,
												person=person,
												role_type=role_type,
												registered=True,
												participated=False,
												apologies=False
												)
			event.project = project
			event.save()
		# and add the person to the source project and the target project
		Membership.objects.create(
									person=person,
									project=project,
									membership_type=Membership_Type.objects.get(name='test_membership_type')
								)
		Membership.objects.create(
									person=person,
									project=target_project,
									membership_type=Membership_Type.objects.get(name='test_membership_type')
								)
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'add',
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
		# check that the events still have blank projects
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,target_project)
		# and that we got the right text in the response
		self.assertContains(response,'50 events added to project')

	def test_remove_from_project_not_in_any_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'remove',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events is correct
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,None)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not removed: not in project')

	def test_remove_from_project_not_in_target_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# add each event to the project and register the person
		for event in Event.objects.filter(event_type=event_type):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'remove',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events is correct
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,project)
		# and that we got the right text in the response
		self.assertContains(response,'30 events not removed: not in project')

	def test_remove_from_project_mixed_not_in_target_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		target_project = Project.objects.get(name='testproject_2')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# add each event to the project and register the person, adding three to a different project
		for event in Event.objects.filter(event_type=event_type):
			if event.name in ('Dates_0','Dates_1','Dates_2'):
				event.project = project
			else:
				event.project = target_project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(target_project.pk),
											'move_type' : 'remove',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events is correct
		for event in Event.objects.filter(event_type=event_type):
			if event.name in ('Dates_0','Dates_1','Dates_2'):
				self.assertEqual(event.project,project)
			else:
				self.assertEqual(event.project,None)
		# and that we got the right text in the response
		self.assertContains(response,'9 events not removed: not in project')
		self.assertContains(response,'21 events removed from project')

	def test_remove_from_project(self):
		# get the test records
		project = Project.objects.get(name='testproject')
		event_type = Event_Type.objects.get(name='test_event_type_6')
		# add each event to the project and register the person
		for event in Event.objects.filter(event_type=event_type):
			event.project = project
			event.save()
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('manage_project_events'),
									data = { 
											'action' : 'Move',
											'name' : '',
											'event_type' : str(event_type.pk),
											'project_id' : '0',
											'target_project_id' : str(project.pk),
											'move_type' : 'remove',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of people
		self.assertEqual(response.context['number_of_events'],30)
		# check how many we got for this page
		self.assertEqual(len(response.context['events']),25)
		# check that we got the right number of pages
		self.assertEqual(len(response.context['page_list']),2)
		# check that the project for the events is correct
		for event in Event.objects.filter(event_type=event_type):
			self.assertEqual(event.project,None)
		# and that we got the right text in the response
		self.assertContains(response,'30 events removed from project')

class AddCaseNotesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create a test person
		set_up_people_base_data()
		set_up_test_people('test_person_',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/add_case_notes/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/add_case_notes/1')

	def test_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		person = Person.objects.get(first_name='test_person_0')
		response = self.client.get(reverse('add_case_notes',args=[person.pk]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_error_person_does_not_exist(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('add_case_notes',args=[99]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Person does not exist')

	def test_add_case_notes(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the reference data
		person = Person.objects.get(first_name='test_person_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')

	def test_add_case_notes_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# set and get the reference data
		set_up_test_people('test_project_',number=1,project=project)
		person = Person.objects.get(first_name='test_project_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,project)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')

class EditCaseNotesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		user = set_up_test_user(username='otheruser')
		user = set_up_test_user(username='superuser',is_superuser=True)
		# create a test person
		set_up_people_base_data()
		set_up_test_people('test_person_',number=1)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/edit_case_notes/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/edit_case_notes/1')

	def test_error_case_notes_do_not_exist(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('edit_case_notes',args=[99]))
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'Case notes do not exist')

	def test_edit_case_notes_error_different_user(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the reference data
		person = Person.objects.get(first_name='test_person_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')
		# log in as a different user
		self.client.login(username='otheruser', password='testword')
		# submit the request
		response = self.client.post(
									reverse('edit_case_notes',args=[str(test_case_notes.pk)]),
									data = { 
												'title' : 'Test title change',
												'date' : '01/02/2010',
												'notes' : 'Test notes change',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'You do not have permission')

	def test_edit_case_notes(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the reference data
		person = Person.objects.get(first_name='test_person_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')
		# submit the request
		response = self.client.post(
									reverse('edit_case_notes',args=[str(test_case_notes.pk)]),
									data = { 
												'title' : 'Test title change',
												'date' : '01/02/2010',
												'notes' : 'Test notes change',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# check the record contents
		test_case_notes = Case_Notes.objects.get(person=person)
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title change')
		self.assertEqual(test_case_notes.notes,'Test notes change')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/02/2010')

	def test_edit_case_notes_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the reference data
		person = Person.objects.get(first_name='test_person_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')
		# log in as a superuser
		self.client.login(username='superuser', password='testword')
		# submit the request
		response = self.client.post(
									reverse('edit_case_notes',args=[str(test_case_notes.pk)]),
									data = { 
												'title' : 'Test title change',
												'date' : '01/02/2010',
												'notes' : 'Test notes change',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# check the record contents
		test_case_notes = Case_Notes.objects.get(person=person)
		self.assertEqual(test_case_notes.project,None)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title change')
		self.assertEqual(test_case_notes.notes,'Test notes change')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/02/2010')

	def test_edit_case_notes_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# set and get the reference data
		set_up_test_people('test_project_',number=1,project=project)
		person = Person.objects.get(first_name='test_project_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,project)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')
		# submit the request
		response = self.client.post(
									reverse('edit_case_notes',args=[str(test_case_notes.pk)]),
									data = { 
												'title' : 'Test title change',
												'date' : '01/02/2010',
												'notes' : 'Test notes change',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# check the record contents
		test_case_notes = Case_Notes.objects.get(person=person)
		self.assertEqual(test_case_notes.project,project)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title change')
		self.assertEqual(test_case_notes.notes,'Test notes change')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/02/2010')

	def test_edit_case_notes_with_projects_active_different_project(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testuser',project_name='testproject')
		set_up_test_project_permission(username='testuser',project_name='otherproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testuser', password='testword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# set and get the reference data
		set_up_test_people('test_project_',number=1,project=project)
		person = Person.objects.get(first_name='test_project_0')
		user = User.objects.get(username='testuser')
		# submit the request
		response = self.client.post(
									reverse('add_case_notes',args=[str(person.pk)]),
									data = { 
												'title' : 'Test title',
												'date' : '01/01/2010',
												'notes' : 'Test notes',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/view_case_notes/' + str(person.pk))
		# get the record
		test_case_notes = Case_Notes.objects.get(person=person)
		# check the record contents
		self.assertEqual(test_case_notes.project,project)
		self.assertEqual(test_case_notes.user,user)
		self.assertEqual(test_case_notes.title,'Test title')
		self.assertEqual(test_case_notes.notes,'Test notes')
		self.assertEqual(test_case_notes.date.strftime('%d/%m/%Y'),'01/01/2010')
		# swtich to a different project
		project = Project.objects.get(name='otherproject')
		session['project_id'] = project.pk
		session.save()
		# submit the request
		response = self.client.post(
									reverse('edit_case_notes',args=[str(test_case_notes.pk)]),
									data = { 
												'title' : 'Test title change',
												'date' : '01/02/2010',
												'notes' : 'Test notes change',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		self.assertContains(response,'You do not have permission')
		
class ManageUnassignedActivitiesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user and superuser
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# set up an additional project
		project_2 = Project.objects.create(name='testproject_2')
		# create base data for people
		set_up_people_base_data()
		# and a test person
		set_up_test_people('activities_test',number=1)
		# get the person
		person = Person.objects.get(first_name='activities_test0')
		# get a test activity type
		activity_type = Activity_Type.objects.get(name='Test activity type 1')
		# create an unassigned activity
		Activity.objects.create(
									person = person,
									activity_type = activity_type,
									date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
									hours = 1,
									project = None
								)
		# create two assigned activities
		Activity.objects.create(
									person = person,
									activity_type = activity_type,
									date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
									hours = 2,
									project = project_2
								)
		Activity.objects.create(
									person = person,
									activity_type = activity_type,
									date = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
									hours = 3,
									project = project
								)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/manage_unassigned_activities')
		# check the response
		self.assertRedirects(response, '/people/login?next=/manage_unassigned_activities')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/manage_unassigned_activities')
		# check the response
		self.assertRedirects(response, '/')

	def test_assign_activities(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# get the projects
		project = Project.objects.get(name='testproject')
		project_2 = Project.objects.get(name='testproject_2')
		# attempt to get the events page
		response = response = self.client.post(
									reverse('manage_unassigned_activities'),
									data = { 
											'project_id' : str(project.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that the activities are as expected
		activity = Activity.objects.get(hours=1)
		self.assertEqual(activity.project,project)
		activity = Activity.objects.get(hours=2)
		self.assertEqual(activity.project,project_2)
		activity = Activity.objects.get(hours=3)
		self.assertEqual(activity.project,project)

class SurveySeriesViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		# set up an additional project
		project_2 = Project.objects.create(name='testproject_2')

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/survey_series/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/survey_series/1')

	def test_invalid_survey_series(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get an invalid event
		response = self.client.get(reverse('survey_series',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/survey_series')
		# check the response
		self.assertRedirects(response, '/')

	def test_survey_series_create(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# attempt to create the survey series
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name')
		self.assertEqual(survey_series.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey_Series.objects.all().count(),1)

	def test_survey_series_duplicate_different_project(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# attempt to create the survey series
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name')
		self.assertEqual(survey_series.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey_Series.objects.all().count(),1)
		# switch to survey series to to a different project
		project_2 = Project.objects.get(name='testproject_2')
		survey_series.project = project_2
		survey_series.save()
		# attempt to create the survey again
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name',project=project)
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name')
		self.assertEqual(survey_series.description,'test description')
		# check that another record was created
		self.assertEqual(Survey_Series.objects.all().count(),2)

	def test_survey_series_duplicate(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# attempt to create the survey series
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name')
		self.assertEqual(survey_series.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey_Series.objects.all().count(),1)
		# attempt to create the survey again
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'Survey series with this name already exists for this project')
		# check that only one record still exists
		self.assertEqual(Survey_Series.objects.all().count(),1)

	def test_survey_series_update(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# attempt to create the survey series
		response = self.client.post(
									reverse('survey_series'),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name')
		self.assertEqual(survey_series.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey_Series.objects.all().count(),1)
		# attempt to create the survey again
		response = self.client.post(
									reverse('survey_series',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name update',
											'description' : 'test desc update',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series_list')
		# check that the survey series was created
		survey_series = Survey_Series.objects.get(name='test name update')
		# check that we got the right values
		self.assertEqual(survey_series.project,project)
		self.assertEqual(survey_series.name,'test name update')
		self.assertEqual(survey_series.description,'test desc update')
		# check that only one record was created
		self.assertEqual(Survey_Series.objects.all().count(),1)

class SurveyViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		# set up two survey series
		project = Project.objects.get(name='testproject')
		Survey_Series.objects.create(
										project = project,
										name = 'test survey series',
										description = 'test description'
									)
		Survey_Series.objects.create(
										project = project,
										name = 'test survey series 2',
										description = 'test description'
									)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/survey/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/survey/1')

	def test_invalid_survey(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get an invalid event
		response = self.client.get(reverse('survey',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/survey/1')
		# check the response
		self.assertRedirects(response, '/')

	def test_survey_create_no_existing_survey(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),1)

	def test_survey_create_with_existing_survey(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		# create an existing survey that the new survey will copy from
		today = datetime.date.today()
		today_one_year_ago = today.replace(year=today.year-1)
		old_survey = Survey.objects.create(
										name='existing survey',
										description = 'existing survey',
										survey_series = survey_series,
										date_created = today_one_year_ago
										)
		old_survey_section = Survey_Section.objects.create(
														name = 'existing section',
														survey = old_survey,
														order = 10
														)
		survey_question_type = Survey_Question_Type.objects.create(
															name = 'test question type',
															options_required = True,
															text_required = False
															)
		old_survey_question = Survey_Question.objects.create(
													question = 'test question',
													number = 1,
													options = 5,
													survey_section = old_survey_section,
													survey_question_type = survey_question_type
													)
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		self.assertEqual(survey.date_created,today)
		# now check the copied records
		survey_section = Survey_Section.objects.get(survey=survey)
		self.assertEqual(survey_section.name,old_survey_section.name)
		self.assertEqual(survey_section.order,old_survey_section.order)
		self.assertEqual(survey_section.order,old_survey_section.order)
		survey_question = Survey_Question.objects.get(survey_section=survey_section)
		self.assertEqual(survey_question.question,old_survey_question.question)
		self.assertEqual(survey_question.survey_question_type,old_survey_question.survey_question_type)
		self.assertEqual(survey_question.number,old_survey_question.number)
		# check that we have the right number of records
		self.assertEqual(Survey.objects.all().count(),2)
		self.assertEqual(Survey_Section.objects.all().count(),2)
		self.assertEqual(Survey_Question.objects.all().count(),2)

	def test_survey_create_with_latest_survey(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		# create an existing survey that the new survey will copy from
		today = datetime.date.today()
		today_one_year_ago = today.replace(year=today.year-1)
		old_survey = Survey.objects.create(
										name='existing survey',
										description = 'existing survey',
										survey_series = survey_series,
										date_created = today_one_year_ago
										)
		old_survey_section = Survey_Section.objects.create(
														name = 'existing section',
														survey = old_survey,
														order = 10
														)
		survey_question_type = Survey_Question_Type.objects.create(
															name = 'test question type',
															options_required = True,
															text_required = False
															)
		old_survey_question = Survey_Question.objects.create(
													question = 'test question',
													number = 1,
													options = 5,
													survey_section = old_survey_section,
													survey_question_type = survey_question_type
													)
		# create an existing survey that the new survey should not copy from
		today_two_years_ago = today.replace(year=today.year-2)
		very_old_survey = Survey.objects.create(
										name='existing survey',
										description = 'existing survey',
										survey_series = survey_series,
										date_created = today_two_years_ago
										)
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		self.assertEqual(survey.date_created,today)
		# now check the copied records
		survey_section = Survey_Section.objects.get(survey=survey)
		self.assertEqual(survey_section.name,old_survey_section.name)
		self.assertEqual(survey_section.order,old_survey_section.order)
		self.assertEqual(survey_section.order,old_survey_section.order)
		survey_question = Survey_Question.objects.get(survey_section=survey_section)
		self.assertEqual(survey_question.question,old_survey_question.question)
		self.assertEqual(survey_question.survey_question_type,old_survey_question.survey_question_type)
		self.assertEqual(survey_question.number,old_survey_question.number)
		# check that we have the right number of records
		self.assertEqual(Survey.objects.all().count(),3)
		self.assertEqual(Survey_Section.objects.all().count(),2)
		self.assertEqual(Survey_Question.objects.all().count(),2)

	def test_survey_create_duplicate_for_same_survey_series(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),1)
		# attempt to create another survey of the same name for the same series
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'Survey with this name already exists for this series')
		# check that only one record still exists
		self.assertEqual(Survey.objects.all().count(),1)

	def test_survey_create_duplicate_for_different_survey_series(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		survey_series_2 = Survey_Series.objects.get(name='test survey series 2')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),1)
		# attempt to create another survey of the same name for the same series
		response = self.client.post(
									reverse('survey',args=[str(survey_series_2.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series_2.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name',survey_series=survey_series_2)
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series_2)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),2)

	def test_survey_update(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk)]),
									data = { 
											'name' : 'test name',
											'description' : 'test description',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name')
		self.assertEqual(survey.description,'test description')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),1)
		# attempt to create another survey of the same name for the same series
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk), str(survey.pk)]),
									data = { 
											'name' : 'test name update',
											'description' : 'test description update',
											'action' : 'Submit',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey_series/' + str(survey_series.pk))
		# check that the survey series was created
		survey = Survey.objects.get(name='test name update')
		# check that we got the right values
		self.assertEqual(survey.survey_series,survey_series)
		self.assertEqual(survey.name,'test name update')
		self.assertEqual(survey.description,'test description update')
		# check that only one record was created
		self.assertEqual(Survey.objects.all().count(),1)

class SurveySectionViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		# set up a survey series
		project = Project.objects.get(name='testproject')
		survey_series = Survey_Series.objects.create(
														project = project,
														name = 'test survey series',
														description = 'test description'
														)
		# set up two surveys
		today = datetime.date.today()
		Survey.objects.create(
								name='test survey',
								description = 'test survey',
								survey_series = survey_series,
								date_created = today
								)
		Survey.objects.create(
								name='test survey 2',
								description = 'test survey 2',
								survey_series = survey_series,
								date_created = today
								)
			

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/survey_section/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/survey_section/1')

	def test_invalid_survey_section(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get an invalid event
		response = self.client.get(reverse('survey_section',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/survey_section/1')
		# check the response
		self.assertRedirects(response, '/')

	def test_survey_section_create(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey
		survey = Survey.objects.get(name='test survey')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),1)

	def test_survey_section_create_duplicate(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey
		survey = Survey.objects.get(name='test survey')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),1)
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'Survey section with this name already exists for this survey')
		# check that only one record still exists
		self.assertEqual(Survey_Section.objects.all().count(),1)

	def test_survey_section_create_duplicate_different_survey(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey
		survey = Survey.objects.get(name='test survey')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),1)
		# move the section to a different survey
		survey_2 = Survey.objects.get(name='test survey 2')
		survey_section.survey = survey_2
		survey_section.save()
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name',survey=survey)
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),2)

	def test_survey_section_update(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey
		survey = Survey.objects.get(name='test survey')
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk)]),
									data = { 
											'name' : 'test name',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name')
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),1)
		# attempt to create the survey
		response = self.client.post(
									reverse('survey_section',args=[str(survey.pk), str(survey_section.pk)]),
									data = {
											'name' : 'test name update',
											'order' : 10
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_section = Survey_Section.objects.get(name='test name update')
		# check that we got the right values
		self.assertEqual(survey_section.survey,survey)
		self.assertEqual(survey_section.name,'test name update')
		self.assertEqual(survey_section.order,10)
		# check that only one record was created
		self.assertEqual(Survey_Section.objects.all().count(),1)
	
class SurveyQuestionViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		# set up a survey series
		project = Project.objects.get(name='testproject')
		survey_series = Survey_Series.objects.create(
														project = project,
														name = 'test survey series',
														description = 'test description'
														)
		# set up a survey
		today = datetime.date.today()
		survey = Survey.objects.create(
										name='test survey',
										description = 'test survey',
										survey_series = survey_series,
										date_created = today
										)
		# set up two survey sections
		Survey_Section.objects.create(
										survey=survey,
										name = 'test survey section',
										order = 10
										)
		Survey_Section.objects.create(
										survey=survey,
										name = 'test survey section 2',
										order = 20
										)
		# set up two question types
		Survey_Question_Type.objects.create(
											name = 'test question type',
											options_required = True,
											text_required = False,
											)	
		Survey_Question_Type.objects.create(
											name = 'test question type 2',
											options_required = True,
											text_required = False,
											)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/survey_question/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/survey_question/1')

	def test_invalid_survey_question(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get an invalid event
		response = self.client.get(reverse('survey_question',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/survey_question/1')
		# check the response
		self.assertRedirects(response, '/')

	def test_survey_question_missing_options(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the owning objects
		survey_section = Survey_Section.objects.get(name='test survey section')
		survey_question_type = Survey_Question_Type.objects.get(name='test question type')
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'Options are mandatory for this question type')

	def test_survey_question_create(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the owning objects
		survey_section = Survey_Section.objects.get(name='test survey section')
		survey_question_type = Survey_Question_Type.objects.get(name='test question type')
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_question = Survey_Question.objects.get(question='test question')
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question')
		self.assertEqual(survey_question.number,1)
		self.assertEqual(survey_question.options,5)
		self.assertEqual(survey_question.survey_question_type,survey_question_type)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)

	def test_survey_question_create_duplicate(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the owning objects
		survey_section = Survey_Section.objects.get(name='test survey section')
		survey_question_type = Survey_Question_Type.objects.get(name='test question type')
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_question = Survey_Question.objects.get(question='test question')
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question')
		self.assertEqual(survey_question.number,1)
		self.assertEqual(survey_question.options,5)
		self.assertEqual(survey_question.survey_question_type,survey_question_type)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error
		self.assertContains(response,'This question already exists for this survey section')
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)

	def test_survey_question_create_duplicate_different_section(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the owning objects
		survey_section = Survey_Section.objects.get(name='test survey section')
		survey_question_type = Survey_Question_Type.objects.get(name='test question type')
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_question = Survey_Question.objects.get(question='test question')
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question')
		self.assertEqual(survey_question.number,1)
		self.assertEqual(survey_question.options,5)
		self.assertEqual(survey_question.survey_question_type,survey_question_type)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)
		# move the question to a different section
		survey_section_2 = Survey_Section.objects.get(name='test survey section 2')
		survey_question.survey_section = survey_section_2
		survey_question.save()
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey question was created
		survey_question = Survey_Question.objects.get(question='test question',survey_section=survey_section)
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question')
		self.assertEqual(survey_question.number,1)
		self.assertEqual(survey_question.options,5)
		self.assertEqual(survey_question.survey_question_type,survey_question_type)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),2)

	def test_survey_question_update(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the owning objects
		survey_section = Survey_Section.objects.get(name='test survey section')
		survey_question_type = Survey_Question_Type.objects.get(name='test question type')
		survey_question_type_2 = Survey_Question_Type.objects.get(name='test question type 2')
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk)]),
									data = { 
											'question' : 'test question',
											'number' : '1',
											'question_type' : str(survey_question_type.pk),
											'options' : '5',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey section was created
		survey_question = Survey_Question.objects.get(question='test question')
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question')
		self.assertEqual(survey_question.number,1)
		self.assertEqual(survey_question.options,5)
		self.assertEqual(survey_question.survey_question_type,survey_question_type)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)
		# attempt to create the survey question
		response = self.client.post(
									reverse('survey_question',args=[str(survey_section.pk),str(survey_question.pk)]),
									data = { 
											'question' : 'test question update',
											'number' : '2',
											'question_type' : str(survey_question_type_2.pk),
											'options' : '6',
											}
									)
		# check that we got a redirect response
		survey = survey_section.survey
		self.assertRedirects(response, '/survey/' + str(survey.survey_series.pk) + '/' + str(survey.pk))
		# check that the survey question was updated
		survey_question = Survey_Question.objects.get(question='test question update')
		# check that we got the right values
		self.assertEqual(survey_question.survey_section,survey_section)
		self.assertEqual(survey_question.question,'test question update')
		self.assertEqual(survey_question.number,2)
		self.assertEqual(survey_question.options,6)
		self.assertEqual(survey_question.survey_question_type,survey_question_type_2)
		# check that only one record was created
		self.assertEqual(Survey_Question.objects.all().count(),1)

class SubmitSurveyViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		# set up a survey series
		project = Project.objects.get(name='testproject')
		survey_series = Survey_Series.objects.create(
														project = project,
														name = 'test survey series',
														description = 'test description'
														)
		# set up a survey
		today = datetime.date.today()
		survey = Survey.objects.create(
										name='test survey',
										description = 'test survey',
										survey_series = survey_series,
										date_created = today
										)
		# set up two survey sections
		survey_section_1 = Survey_Section.objects.create(
										survey=survey,
										name = 'test survey section',
										order = 10
										)
		survey_section_2 = Survey_Section.objects.create(
										survey=survey,
										name = 'test survey section 2',
										order = 20
										)
		# set up two question types
		survey_question_type_1 = Survey_Question_Type.objects.create(
											name = 'test question type 1',
											options_required = True,
											text_required = False,
											)	
		survey_question_type_2 = Survey_Question_Type.objects.create(
											name = 'test question type 2',
											options_required = False,
											text_required = True,
											)
		# and two questions
		Survey_Question.objects.create(
										question = 'test question 1',
										number = 1,
										options = 5,
										survey_question_type = survey_question_type_1,
										survey_section = survey_section_1
										)
		Survey_Question.objects.create(
										question = 'test question 2',
										number = 2,
										options = 0,
										survey_question_type = survey_question_type_2,
										survey_section = survey_section_2
										)
		# and a test person
		set_up_people_base_data()
		set_up_test_people('survey_',project=project)

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/submit_survey/1/1')
		# check the response
		self.assertRedirects(response, '/people/login?next=/submit_survey/1/1')

	def test_invalid_survey_submission(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get an invalid event
		response = self.client.get(reverse('submit_survey',args=[9999,9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

	def test_submit_survey(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the objects
		survey = Survey.objects.get(name='test survey')
		person = Person.objects.get(first_name='survey_0')
		question_1 = Survey_Question.objects.get(question='test question 1')
		question_1_field_name = 'survey_question_' + str(question_1.pk)
		question_2 = Survey_Question.objects.get(question='test question 2')
		question_2_field_name = 'survey_question_' + str(question_2.pk)
		# attempt to create the survey question
		response = self.client.post(
									reverse('submit_survey',args=[str(person.pk),str(survey.pk)]),
									data = { 
											question_1_field_name : '3',
											question_2_field_name : 'test',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/person/' + str(person.pk))
		# check that the submission and answers were created
		survey_submission = Survey_Submission.objects.get(survey=survey,person=person)
		survey_answer_1 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_1)
		survey_answer_2 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_2)
		# check that we got the right values
		self.assertEqual(survey_submission.date,datetime.date.today())
		self.assertEqual(survey_answer_1.range_answer,3)
		self.assertEqual(survey_answer_1.text_answer,'')
		self.assertEqual(survey_answer_2.range_answer,0)
		self.assertEqual(survey_answer_2.text_answer,'test')
		# check that the right number of records were created
		self.assertEqual(Survey_Submission.objects.all().count(),1)
		self.assertEqual(Survey_Answer.objects.all().count(),2)

	def test_submit_survey_update(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the objects
		survey = Survey.objects.get(name='test survey')
		person = Person.objects.get(first_name='survey_0')
		question_1 = Survey_Question.objects.get(question='test question 1')
		question_1_field_name = 'survey_question_' + str(question_1.pk)
		question_2 = Survey_Question.objects.get(question='test question 2')
		question_2_field_name = 'survey_question_' + str(question_2.pk)
		# attempt to create the survey question
		response = self.client.post(
									reverse('submit_survey',args=[str(person.pk),str(survey.pk)]),
									data = { 
											question_1_field_name : '3',
											question_2_field_name : 'test',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/person/' + str(person.pk))
		# check that the submission and answers were created
		survey_submission = Survey_Submission.objects.get(survey=survey,person=person)
		survey_answer_1 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_1)
		survey_answer_2 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_2)
		# check that we got the right values
		self.assertEqual(survey_submission.date,datetime.date.today())
		self.assertEqual(survey_answer_1.range_answer,3)
		self.assertEqual(survey_answer_1.text_answer,'')
		self.assertEqual(survey_answer_2.range_answer,0)
		self.assertEqual(survey_answer_2.text_answer,'test')
		# check that the right number of records were created
		self.assertEqual(Survey_Submission.objects.all().count(),1)
		self.assertEqual(Survey_Answer.objects.all().count(),2)
		# attempt to update the survey question
		response = self.client.post(
									reverse('submit_survey',args=[str(person.pk),str(survey.pk)]),
									data = { 
											question_1_field_name : '5',
											question_2_field_name : 'test update',
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/person/' + str(person.pk))
		# check that the submission and answers were created
		survey_submission = Survey_Submission.objects.get(survey=survey,person=person)
		survey_answer_1 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_1)
		survey_answer_2 = Survey_Answer.objects.get(survey_submission=survey_submission,survey_question=question_2)
		# check that we got the right values
		self.assertEqual(survey_submission.date,datetime.date.today())
		self.assertEqual(survey_answer_1.range_answer,5)
		self.assertEqual(survey_answer_1.text_answer,'')
		self.assertEqual(survey_answer_2.range_answer,0)
		self.assertEqual(survey_answer_2.text_answer,'test update')
		# check that the right number of records were created
		self.assertEqual(Survey_Submission.objects.all().count(),1)
		self.assertEqual(Survey_Answer.objects.all().count(),2)

class ResolveAgeExceptionsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		superuser = set_up_test_superuser()
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# set up base data: first the ethnicity
		test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
		# and the capture type
		test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
		# create roles
		child_under_4_role = Role_Type.objects.create(role_type_name='Child under 4',use_for_events=True,use_for_people=True)
		child_over_3_role = Role_Type.objects.create(role_type_name='Child over 3',use_for_events=True,use_for_people=True)
		unknown_role = Role_Type.objects.create(role_type_name='UNKNOWN',use_for_events=True,use_for_people=True)
		parent_role = Role_Type.objects.create(role_type_name='Parent',use_for_events=True,use_for_people=True)
		# create test age statuses
		child_under_4_age_status = Age_Status.objects.create(status='Child under 4',minimum_age=0,maximum_age=3,default_role_type=child_under_4_role)
		child_under_4_age_status.role_types.add(child_under_4_role)
		child_over_3_age_status = Age_Status.objects.create(status='Child over 3',minimum_age=4,maximum_age=17,default_role_type=child_over_3_role)
		child_over_3_age_status.role_types.add(child_over_3_role)
		adult_age_status = Age_Status.objects.create(status='Adult',minimum_age=18,maximum_age=999,default_role_type=unknown_role)
		adult_age_status.role_types.add(parent_role)
		adult_age_status.role_types.add(unknown_role)
		adult_unknown_status = Age_Status.objects.create(status='Adult (unknown age)',minimum_age=18,maximum_age=999,default_role_type=unknown_role,use_for_automated_categorisation=False)
		adult_unknown_status.role_types.add(parent_role)
		adult_unknown_status.role_types.add(unknown_role)
		# create test membership types
		test_membership_type = Membership_Type.objects.create(name='test_membership_type',default=True)
		second_test_membership_type = Membership_Type.objects.create(name='second_test_membership_type')
		# create a test ABSS type
		test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type',membership_type=test_membership_type)
		# create a second test ABSS type
		second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type',membership_type=second_test_membership_type)
		# Create people
		set_up_test_people('child_under_4_','Child under 4',1,test_ABSS_type,'Child under 4',project)
		set_up_test_people('child_over_3_','Child under 4',1,test_ABSS_type,'Child under 4',project)
		set_up_test_people('adult_','Parent',1,test_ABSS_type,'Child over 3',project)
		set_up_test_people('adult_unknown_','UNKNOWN',1,test_ABSS_type,'Adult (unknown age)',project)
		# modfy the dates so that two people are in the wrong category
		today = datetime.date.today()
		person = Person.objects.get(first_name='child_under_4_0')
		person.date_of_birth = today.replace(year=today.year-2)
		person.save()
		person = Person.objects.get(first_name='child_over_3_0')
		person.date_of_birth = today.replace(year=today.year-6)
		person.save()
		person = Person.objects.get(first_name='adult_0')
		person.date_of_birth = today.replace(year=today.year-20)
		person.save()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/resolve_age_exceptions')
		# check the response
		self.assertRedirects(response, '/people/login?next=/resolve_age_exceptions')

	def test_redirect_if_not_superuser(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the response
		response = self.client.get('/resolve_age_exceptions')
		# check the response
		self.assertRedirects(response, '/')

	def test_review_age_exceptions(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.get(reverse('resolve_age_exceptions'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['people']),2)

	def test_resolve_age_exceptions(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# attempt to get the events page
		response = self.client.post(
									reverse('resolve_age_exceptions'),
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of results
		self.assertEqual(len(response.context['results']),2)
		# check how many people we got
		self.assertEqual(len(response.context['people']),0)
		# check the results
		person = Person.objects.get(first_name='child_under_4_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Child under 4'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Child under 4'))
		person = Person.objects.get(first_name='child_over_3_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Child over 3'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Child over 3'))
		person = Person.objects.get(first_name='adult_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Adult'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Parent'))
		person = Person.objects.get(first_name='adult_unknown_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Adult (unknown age)'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='UNKNOWN'))

	def test_resolve_age_exceptions_manual_action(self):
		# log the user in
		self.client.login(username='testsuper', password='superword')
		# add another adult age status
		unknown_role = Role_Type.objects.get(role_type_name='UNKNOWN')
		Age_Status.objects.create(status='Adult extra',minimum_age=18,maximum_age=999,default_role_type=unknown_role)
		# attempt to get the age page
		response = self.client.post(
									reverse('resolve_age_exceptions'),
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of results
		self.assertEqual(len(response.context['results']),2)
		# check how many people we got
		self.assertEqual(len(response.context['people']),1)
		# check the results
		person = Person.objects.get(first_name='child_under_4_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Child under 4'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Child under 4'))
		person = Person.objects.get(first_name='child_over_3_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Child over 3'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Child over 3'))
		person = Person.objects.get(first_name='adult_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Child over 3'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='Parent'))
		person = Person.objects.get(first_name='adult_unknown_0')
		self.assertEqual(person.age_status,Age_Status.objects.get(status='Adult (unknown age)'))
		self.assertEqual(person.default_role,Role_Type.objects.get(role_type_name='UNKNOWN'))
		self.assertContains(response,'manual')
