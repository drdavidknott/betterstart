from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note, \
							Trained_Role, Activity_Type, Activity, Dashboard, Column, Panel, Panel_In_Column, \
							Panel_Column, Panel_Column_In_Panel, Filter_Spec, Column_In_Dashboard, \
							Venue, Venue_Type, Site, Invitation, Invitation_Step, Invitation_Step_Type, \
							Terms_And_Conditions, Profile, Chart, Document_Link, Project, Membership, \
							Project_Permission, Membership_Type, Project_Event_Type, \
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

	def test_upload_people_data_cross_field_validation_in_project(self):
		# log the user in as a superuser
		project = project_login(self.client)
		# open the file
		valid_file = open('people/tests/data/people_cross_field_validation_in_project.csv')
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
		self.assertContains(response,'Date left without date joined not created: date left is provided but not date joined')
		self.assertContains(response,'Date left before date joined not created: date left is not greater than date joined')
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

	def test_upload_people_data_invalid_dates_in_project(self):
		# log the user in as a superuser
		project = project_login(self.client)
		# open the file
		valid_file = open('people/tests/data/people_invalid_dates_in_project.csv')
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
		self.assertContains(response,'Invalid date joined not created: date_joined 01/xx/2001 is invalid date or time')
		self.assertContains(response,'Invalid date left not created: date_left 01/xx/2005 is invalid date or time')
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

	def test_upload_people_data_invalid_integers(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/people_invalid_integers.csv')
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
		self.assertContains(response,'Invalid Membership No not created: integer field membership_number XYZ is not integer')
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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have two people
		self.assertEqual(Person.objects.all().count(),3)

	def test_upload_people_with_projects_active(self):
		# log the user in as a superuser
		project = project_login(self.client)
		# open the file
		valid_file = open('people/tests/data/people_in_project.csv')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# check that we have three people and three memberships
		self.assertEqual(Person.objects.all().count(),3)
		self.assertEqual(Membership.objects.all().count(),3)

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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.membership_number,12345)
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

	def test_upload_people_already_exist_in_same_project(self):
		# log the user in as a superuser
		project = project_login(self.client)
		# open the file
		valid_file = open('people/tests/data/people_in_project.csv')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# check that we have three people and three memberships
		self.assertEqual(Person.objects.all().count(),3)
		self.assertEqual(Membership.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/people_in_project.csv')
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
		# check that no additional people or memberships have been created
		self.assertEqual(Person.objects.all().count(),3)
		self.assertEqual(Membership.objects.all().count(),3)

	def test_upload_people_already_exist_in_different_project(self):
		# log the user in as a superuser
		project = project_login(self.client)
		# open the file
		valid_file = open('people/tests/data/people_in_project.csv')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# check that we have three people and three memberships
		self.assertEqual(Person.objects.all().count(),3)
		self.assertEqual(Membership.objects.all().count(),3)
		# close the file
		valid_file.close()
		# log out and long back in with a new project
		self.client.logout()
		project = project_login(self.client,project_name='newproject')
		# reopen the file
		valid_file = open('people/tests/data/people_in_project.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'People',
											'file' : valid_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the first person
		test_person = Person.objects.get(first_name='Test',last_name='Person',projects=project)
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# and the second person
		test_person = Person.objects.get(first_name='Test no dob',last_name='Person',projects=project)
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'999')
		self.assertEqual(test_person.street.name,'test_street_0')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# and the third person
		test_person = Person.objects.get(first_name='Test no street',last_name='Person',projects=project)
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
		self.assertEqual(test_person.ABSS_type.name,'ABSS beneficiary')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.ABSS_start_date,None)
		self.assertEqual(test_person.ABSS_end_date,None)
		self.assertEqual(test_person.emergency_contact_details,'test emergency contact details')
		self.assertEqual(test_person.membership_number,12345)
		# and the membership
		membership = Membership.objects.get(project=project,person=test_person)
		self.assertEqual(membership.membership_type.name,'test_membership_type')
		self.assertEqual(membership.date_joined.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(membership.date_left.strftime('%d/%m/%Y'),'01/01/2005')
		# check that we have three people and three memberships
		self.assertEqual(Person.objects.all().count(),6)
		self.assertEqual(Membership.objects.all().count(),6)

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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we only have two people
		self.assertEqual(Person.objects.all().count(),2)

class UpdatePeopleDataViewTest(TestCase):
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
		invalid_test_role = Role_Type.objects.create(role_type_name='invalid_test_role',use_for_events=True,use_for_people=True)
		# and some additional records
		test_age_status_limit = Age_Status.objects.create(
															status='Under five',
															default_role_type=Role_Type.objects.get(
																				role_type_name='test_role_type'),
															maximum_age=5
															)

	def test_update_people_no_match(self):
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have one person
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people_no_match.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'not updated')
		# get the person
		test_person = Person.objects.get(first_name='Test',last_name='Personz')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Personz')
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
		self.assertEqual(test_person.membership_number,12345)
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),4)

	def test_update_people_invalid_dob(self):
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have one person
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people_invalid_dob.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'is invalid date or time')
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),3)

	def test_update_people_invalid_role_type(self):
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have one person
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people_invalid_role_type.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
											'file' : valid_file
											}
									)
		# check that we got an error response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'not created: role type is not valid for age status')
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),3)

	def test_update_people(self):
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have one person
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
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
		self.assertEqual(test_person.email_address,'test emailz')
		self.assertEqual(test_person.home_phone,'1234567')
		self.assertEqual(test_person.mobile_phone,'7891234')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/1990')
		self.assertEqual(test_person.gender,'Female')
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
		self.assertEqual(test_person.membership_number,123456)
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),3)

	def test_update_people_single_field(self):
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have one person
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people_single_field.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
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
		self.assertEqual(test_person.membership_number,67890)
		# check that no additional people have been created
		self.assertEqual(Person.objects.all().count(),3)

	def test_update_people_invalid_middle(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# open the file
		valid_file = open('people/tests/data/update_people_for_invalid_middle.csv')
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
		self.assertEqual(test_person.membership_number,12345)
		# and the second person
		test_person = Person.objects.get(first_name='Test2',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test2')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/02/1990')
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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/03/1990')
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
		self.assertEqual(test_person.membership_number,12345)
		# check that we have three people
		self.assertEqual(Person.objects.all().count(),3)
		# close the file
		valid_file.close()
		# reopen the file
		valid_file = open('people/tests/data/update_people_invalid_middle.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update People',
											'file' : valid_file
											}
									)
		# check that we got a valid response
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
		self.assertEqual(test_person.membership_number,67890)
		# check that we got an error for the second person
		self.assertContains(response,'not created')
		# and check that the second person we not updated
		test_person = Person.objects.get(first_name='Test2',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test2')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
		self.assertEqual(test_person.other_names,'test other_names')
		self.assertEqual(test_person.default_role.role_type_name,'test_role_type')
		self.assertEqual(test_person.email_address,'test email')
		self.assertEqual(test_person.home_phone,'123456')
		self.assertEqual(test_person.mobile_phone,'789123')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/02/1990')
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
		self.assertEqual(test_person.membership_number,12345)
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
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/03/1990')
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
		self.assertEqual(test_person.membership_number,67890)
		# check that we have three people
		self.assertEqual(Person.objects.all().count(),3)

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
		person.membership_number = 12345
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
		# check that we got the right records
		self.assertContains(response,'test_adult_0,test_adult_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Adult,,,,test notes,,0,test_ABSS_type,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test other_names,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,test_ethnicity,Adult,123,ABC streets 10,ABC0,test notes,test ecd,12345,test_ABSS_type,01/01/2011,02/02/2012,Test ward')
		self.assertContains(response,'test_child_0,test_child_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Child under four,,,,test notes,,0,test_ABSS_type,,,')

	def test_download_people_with_projects_active(self):
		# add the user to a project, and set projects active
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create base data for addresses
		set_up_address_base_data()
		# create a bunch of post codes
		set_up_test_post_codes('ABC')
		# and a bunch of streets
		set_up_test_streets('ABC streets 1','ABC0')
		# create people in the project
		set_up_test_people('test_project_adult_',number=2,age_status='Adult',project=project)
		set_up_test_people('test_project_child_',number=1,age_status='Child under four',project=project)
		# get the second test person
		person = Person.objects.get(first_name='test_project_adult_1')
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
		person.membership_number = 12345
		# save the record
		person.save()
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
		self.assertContains(response,'test_project_adult_0,test_project_adult_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Adult,,,,test notes,,0,test_membership_type,,,')
		self.assertContains(response,'test_project_adult_1,test_project_adult_1,test other_names,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,test_ethnicity,Adult,123,ABC streets 10,ABC0,test notes,test ecd,12345,test_membership_type,,,Test ward')
		self.assertContains(response,'test_project_child_0,test_project_child_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Child under four,,,,test notes,,0,test_membership_type,,,')
		self.assertNotContains(response,'test_adult_0')
		self.assertNotContains(response,'test_adult_1')
		self.assertNotContains(response,'test_child_0')

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
		person.membership_number = 12345
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
											'membership_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'include_people' : 'all',
											'ward' : '0',
											'page' : '1'
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got the right records
		self.assertContains(response,'test_adult_0,test_adult_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Adult,,,,test notes,,0,test_ABSS_type,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test other_names,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,test_ethnicity,Adult,123,ABC streets 10,ABC0,test notes,test ecd,12345,test_ABSS_type,01/01/2011,02/02/2012,Test ward')
		self.assertContains(response,'test_child_0,test_child_0,,test@test.com,,,01/01/2000,Gender,False,,test_role_type,test_ethnicity,Child under four,,,,test notes,,0,test_ABSS_type,,,')

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
											'membership_type' : '0',
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

	def test_download_events_with_projects_active(self):
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create events in the project
		set_up_test_events(
							'test_project_event_',
							number=2,
							event_type=Event_Type.objects.get(name='test_event_type'),
							date='2019-01-01',
							project=project
							)
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
		self.assertContains(response,'test_project_event_0,Test event description,test_event_type,01/01/2019,10:00,11:00,Test location,,,')
		self.assertContains(response,'test_project_event_1,Test event description,test_event_type,01/01/2019,10:00,11:00,Test location,,,')
		self.assertNotContains(response,'test_event_0')
		self.assertNotContains(response,'test_event_1')

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

	def test_download_relationships(self):
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

	def test_download_relationship_with_projects_active_no_results(self):
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
		# log the user user
		self.client.logout()
		# create a project and log back in
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		self.assertNotContains(response,'test_parent_0')
		self.assertNotContains(response,'test_child_0')

	def test_download_relationship_with_projects_active_with_results(self):
		# create a project and log in
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# add people to the project
		# add the people and events to the project
		for person in Person.objects.all():
			membership = Membership(
									person=person,
									project=project,
									)
			membership.save()
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
		# get the relationship types
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
		# check that we got the right records
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

	def test_download_registrations_with_projects_active_no_results(self):
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
		# log the user out
		self.client.logout()
		# create a project and log back in
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		self.assertNotContains(response,'test_adult_0')
		self.assertNotContains(response,'test_adult_1')
		self.assertNotContains(response,'test_child_0')

	def test_download_registrations_with_projects_active_with_results(self):
		# create a project and log in
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# add the people and events to the project
		for person in Person.objects.all():
			membership = Membership(
									person=person,
									project=project,
									)
			membership.save()
		for event in Event.objects.all():
			event.project = project
			event.save()
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
		# check that we got the right results
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

	def test_download_summary_with_venue_with_projects_active_no_results(self):
		# log the user in as a superuser
		self.client.login(username='testsuper', password='superword')
		# create the venue and add it to the event
		set_up_address_base_data()
		set_up_venue_base_data()
		event = Event.objects.get(name='test_event_0')
		event.venue = Venue.objects.get(name='test_venue')
		event.save()
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
		# log out and log back in with a project
		self.client.logout()
		project = project_login(self.client)
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
		self.assertNotContains(response,'test_event_0')

	def test_download_summary_with_venue_with_projects_active_with_results(self):
		# create a project and log in
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
		# create the venue and add it to the event
		set_up_address_base_data()
		set_up_venue_base_data()
		event = Event.objects.get(name='test_event_0')
		event.venue = Venue.objects.get(name='test_venue')
		event.project = project
		event.save()
		# add the people to the project
		for person in Person.objects.all():
			Membership.objects.create(
										person=person,
										project=project
										)
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

	def test_download_answers_with_projects_active_no_results(self):
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
		# log out and log back in with a project
		self.client.logout()
		set_up_test_project_permission(username='testsuper',project_name='testproject')
		Site.objects.create(
							name='Test site',
							projects_active=True
							)
		project = Project.objects.get(name='testproject')
		# log the user in and set the project session variable
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		session['project_id'] = project.pk
		session.save()
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
		self.assertNotContains(response,'test_adult_0')

	def test_download_answers_with_projects_active_with_results(self):
		# log the user in as a superuser in a project
		project = project_login(self.client)
		# add the people to the project
		for person in Person.objects.all():
			Membership.objects.create(
										person=person,
										project=project
										)
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

class UpdateAnswersViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_superuser()
		# set up base data for people
		set_up_people_base_data()
		# and create an adult
		set_up_test_people('test_adult_',number=2,age_status='Adult')		

	def test_update_answers(self):
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
		valid_file = open('people/tests/data/options_for_update.csv')
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
		# open the file
		valid_file = open('people/tests/data/answers_update.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update Answers',
											'file' : valid_file
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# get the person, the question and the option for the updated answer
		person = Person.objects.get(first_name='test_adult_0')
		question = Question.objects.get(question_text='test question with notes')
		option = Option.objects.get(option_label='test label 2')
		# get the answer
		answer = Answer.objects.get(person=person)
		# check the results
		self.assertEqual(answer.question,question)
		self.assertEqual(answer.option,option)
		# get the person, the question and the option for the updated answer
		person = Person.objects.get(first_name='test_adult_1')
		question = Question.objects.get(question_text='test question with notes')
		option = Option.objects.get(option_label='test label')
		# get the answer
		answer = Answer.objects.get(person=person)
		# check the results
		self.assertEqual(answer.question,question)
		self.assertEqual(answer.option,option)
		# and that have the right number of records
		self.assertEqual(Answer.objects.all().count(),2)

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

	def test_download_answer_notes_with_projects_active_no_results(self):
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
		# logout and log back in again with a project
		self.client.logout()
		project = project_login(self.client)
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
		self.assertNotContains(response,'test_adult_0')

	def test_download_answer_notes_with_projects_active_with_results(self):
		# log the user in as a superuser in a project
		project = project_login(self.client)
		# add the people to the project
		for person in Person.objects.all():
			Membership.objects.create(
										project=project,
										person=person
									)
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

	def test_download_activities_with_projects_active_no_results(self):
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
		# log out and log back in with a project
		self.client.logout()
		project_login(self.client)
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
		self.assertNotContains(response,'test_adult_0')
		self.assertNotContains(response,'test_adult_1')

	def test_download_activities_with_projects_active_with_results(self):
		# log the user in as a superuser in a project
		project = project_login(self.client)
		# add the people to the project
		for person in Person.objects.all():
			Membership.objects.create(
										project=project,
										person=person
									)
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

class UpdatePostCodesViewTest(TestCase):
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

	def test_update_postcodes(self):
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
		# now update postcodes
		# open the file
		postcodes_file = open('people/tests/data/update_postcodes.csv')
		# submit the page to load the file
		response = self.client.post(
									reverse('uploaddata'),
									data = { 
											'file_type' : 'Update Post Codes',
											'file' : postcodes_file
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# get the results
		test_postcode_1 = Post_Code.objects.get(post_code = 'test pc 1')
		test_postcode_2 = Post_Code.objects.get(post_code = 'test pc 2')
		# check the ward
		self.assertEqual(test_postcode_1.ward,test_ward_2)
		self.assertEqual(test_postcode_2.ward,test_ward_2)
		# check that we got a ward does not exist
		self.assertContains(response,'ward does not exist')

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
		survey_date = datetime.datetime.strptime('2022-01-01','%Y-%m-%d')
		survey = Survey.objects.create(
										name='test survey',
										description = 'test survey',
										survey_series = survey_series,
										date_created = survey_date
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
		survey_question_1 = Survey_Question.objects.create(
										question = 'test question 1',
										number = 1,
										options = 5,
										survey_question_type = survey_question_type_1,
										survey_section = survey_section_1
										)
		survey_question_2 = Survey_Question.objects.create(
										question = 'test question 2',
										number = 2,
										options = 0,
										survey_question_type = survey_question_type_2,
										survey_section = survey_section_2
										)
		# and a test person
		set_up_people_base_data()
		set_up_test_people('survey_',project=project,number=2)
		person_1 = Person.objects.get(first_name='survey_0')
		person_2 = Person.objects.get(first_name='survey_1')
		# and two survey submissions with answers for the first and none for the second - to test defaults
		survey_submission_1 = Survey_Submission.objects.create(
																person = person_1,
																survey = survey,
																date = survey_date
																)
		Survey_Answer.objects.create(
										survey_submission = survey_submission_1,
										survey_question = survey_question_1,
										range_answer = 3,
										text_answer = ''
										)
		Survey_Answer.objects.create(
										survey_submission = survey_submission_1,
										survey_question = survey_question_2,
										range_answer = 0,
										text_answer = 'test answer'
										)
		Survey_Submission.objects.create(
											person = person_2,
											survey = survey,
											date = survey_date
											)


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

	def test_survey_download(self):
		# log the user in and set the project
		self.client.login(username='testsuper', password='superword')
		session = self.client.session
		project = Project.objects.get(name='testproject')
		session['project_id'] = project.pk
		session.save()
		# get the survey series
		survey_series = Survey_Series.objects.get(name='test survey series')
		survey = Survey.objects.get(name='test survey')
		# attempt to download the survey
		response = self.client.post(
									reverse('survey',args=[str(survey_series.pk), str(survey.pk)]),
									data = { 
											'name' : 'test name update',
											'description' : 'test description update',
											'action' : 'Download',
											}
									)
		# check that we got a success response
		self.assertEqual(response.status_code, 200)
		# check that we got an already exists message
		self.assertContains(response,'first_name,last_name,date,1. test question 1,2. test question 2')
		self.assertContains(response,'survey_0,survey_0,01/01/2022,3,test answer')
		self.assertContains(response,'survey_1,survey_1,01/01/2022,0,')
