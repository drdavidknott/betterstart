from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note, \
							Trained_Role
import datetime
from django.urls import reverse
from django.contrib.auth.models import User

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
	test_age_status_2 = Age_Status.objects.create(status='Child under four',default_role_type=test_role)
	# and a third test age status
	test_age_status_3 = Age_Status.objects.create(status='Default role age status',default_role_type=age_test_role,default_role_type_only=True)
	# allow the role type of each age status
	test_age_status.role_types.add(test_role)
	test_age_status.role_types.add(second_test_role)
	test_age_status.role_types.add(unknown_test_role)
	test_age_status.role_types.add(adult_test_role)
	test_age_status_2.role_types.add(test_role)
	test_age_status_2.role_types.add(second_test_role)
	test_age_status_2.role_types.add(unknown_test_role)

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
	Relationship_Type.objects.create(relationship_type='parent', relationship_counterpart='child')
	Relationship_Type.objects.create(relationship_type='child', relationship_counterpart='parent')
	Relationship_Type.objects.create(relationship_type='from', relationship_counterpart='to')
	Relationship_Type.objects.create(relationship_type='to', relationship_counterpart='from')

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

def set_up_test_questions(name_root,number=1,notes=False,notes_label=''):
	# set up the number of test questions asked for
	for n in range(number):
		# create a question
		test_question = Question.objects.create(
											 question_text = name_root + str(n),
											 notes = notes,
											 notes_label = notes_label
											)

def set_up_test_options(name_root,question,number=1):
	# set up the number of test options asked for
	for n in range(number):
		# create an option
		test_option = Option.objects.create(
											 option_label = name_root + str(n),
											 question = question
											)


class PeopleViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])

	def test_search_with_no_criteria_second_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])

	def test_search_for_parent_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the parent role type record
		parent_role_type = Role_Type.objects.get(role_type_name='Parent')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(parent_role_type.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_by_first_name_with_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'Test_Role_1',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_by_first_name_with_non_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'test_role_1',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_by_last_name_with_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : 'Test_Role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_by_last_name_with_non_matching_case(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : 'test_role_1',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
											'page' : '1'
											}
									)
		# check that we got a response
		self.assertEqual(response.status_code, 200)
		# check how many we got for this page
		self.assertEqual(len(response.context['people']),25)
		# check that we got the right number of pages
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_for_short_set(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'Short',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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

	def test_search_by_first_name_and_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'Different',
											'last_name' : '',
											'role_type' : str(test_role_type_1.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_by_first_name_last_name_and_role_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the test role type record
		test_role_type_1 = Role_Type.objects.get(role_type_name='test role 1')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'Different',
											'last_name' : 'Different',
											'role_type' : str(test_role_type_1.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_first_name_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'No results',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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

	def test_last_name_search_with_no_results(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : 'No results',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(test_role_type_4.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
											'action' : 'search',
											'first_name' : 'Test_Role_1_',
											'last_name' : '',
											'role_type' : str(test_role_type_3.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(test_role_type_5.pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_second_page_with_less_than_full_set_of_results_by_first_name(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'Pagination',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_ABSS_search_on_type(self):
		# create some extra people
		set_up_test_people('ABSS_test_','test role 1',30,'second_test_ABSS_type')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_ABSS_search_with_no_results(self):
		# create a new ABSS type
		ABSS_Type.objects.create(name='Third test ABSS')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : str(ABSS_Type.objects.get(name='Third test ABSS').pk),
											'age_status' : '0',
											'trained_role' : 'none',
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'none',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_age_status_search_with_no_results(self):
		# create a new age status
		age_status = Age_Status.objects.create(status='Third test age status')
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(age_status.pk),
											'trained_role' : 'none',
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'trained_' + str(role_type.pk),
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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Adult').pk),
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : str(Role_Type.objects.get(role_type_name='test role 2').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '0',
											'ABSS_type' : '0',
											'age_status' : '0',
											'trained_role' : 'active_' + str(role_type.pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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
		self.assertEqual(response.context['page_list'],[1,2])

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
		self.assertEqual(response.context['page_list'],[1,2])

class EventsViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
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
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21])

	def test_search_with_no_criteria_second_page(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21])

	def test_search_with_date_range(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_6').pk),
											'event_category' : '0',
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : '0',
											'event_category' : str(Event_Category.objects.get(name='test_event_category_3').pk),
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2])

	def test_search_with_date_from_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_6').pk),
											'event_category' : '0',
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '20/01/2019',
											'event_type' : str(Event_Type.objects.get(name='test_event_type_1').pk),
											'event_category' : '0',
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6])

	def test_search_with_date_to_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '20/01/2019',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])

	def test_search_with_date_range_and_event_type(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event type record
		test_event_type_6 = Event_Type.objects.get(name='test_event_type_6')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '20/02/2019',
											'event_type' : str(test_event_type_6.pk),
											'event_category' : '0',
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : str(test_event_category_2.pk),
											'ward' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5,6])

	def test_search_with_event_category_and_date(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# get the event category record
		test_event_category_3 = Event_Category.objects.get(name='test_event_category_3')
		# attempt to get the events page
		response = self.client.post(
									reverse('events'),
									data = { 
											'action' : 'search',
											'name' : '',
											'date_from' : '20/01/2019',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : str(test_event_category_3.pk),
											'ward' : '0',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
											'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
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
		self.assertEqual(response.context['page_list'],[1,2])

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

	def test_update_profile_blank_middle_name(self):
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
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'ethnicity' : str(Ethnicity.objects.get(description='second_test_ethnicity').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='second_test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Child under four').pk),
											'notes' : 'updated notes',
											'emergency_contact_details' : 'updated emergency contact details',
											'ABSS_start_date' : '01/01/2010',
											'ABSS_end_date' : '01/01/2015',
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
		self.assertEqual(test_person.age_status.status,'Child under four')
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)
		self.assertEqual(test_person.emergency_contact_details,'updated emergency contact details')
		self.assertEqual(test_person.ABSS_start_date.strftime('%d/%m/%Y'),'01/01/2010')
		self.assertEqual(test_person.ABSS_end_date.strftime('%d/%m/%Y'),'01/01/2015')

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
		# get the trained role record
		trained_role = Trained_Role.objects.get(person=test_person,role_type=role_type)
		# check the active status
		self.assertEqual(trained_role.active,False)

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
		# check that no trained role records exist
		self.assertEqual(test_person.trained_roles.all().exists(),False)

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
		# check that no trained role records exist
		self.assertEqual(test_person.trained_roles.all().exists(),False)

class AddEventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_event_base_data()
		# and set up base data for addresses
		set_up_address_base_data()

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

	def test_create_person(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('addevent'),
									data = { 
												'name' : 'Testevent',
												'description' : 'Testdescription',
												'location' : 'Testlocation',
												'ward' : str(Ward.objects.get(ward_name='Test ward').pk),
												'event_type' : str(Event_Type.objects.get(name='test_event_type_1').pk),
												'date' : '01/01/2019',
												'start_time' : '10:00',
												'end_time' : '11:00'
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/1')
		# get the record
		test_event = Event.objects.get(name='Testevent')
		# check the record contents
		self.assertEqual(test_event.name,'Testevent')
		self.assertEqual(test_event.description,'Testdescription')
		self.assertEqual(test_event.location,'Testlocation')
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.event_type.name,'test_event_type')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/01/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')

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

	def test_find_existing_person_for_relationship(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a person to add the relationships to
		set_up_test_people('Test_exists_','test_role_type',1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[Person.objects.get(first_name='Test_exists_0').pk]),
									data = { 
											'action' : 'search',
											'first_name' : 'Test_exists_0',
											'last_name' : 'Test_exists_0',
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
		# set up base data for events
		set_up_event_base_data()
		# and set up base data for addresses
		set_up_address_base_data()

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

	def test_event_registration_search_blank_search_error(self):
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
												'first_name' : '',
												'last_name' : '',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_error'],'First name or last name must be entered.')

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
												'first_name' : 'noresult',
												'last_name' : 'noresult',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],0)

	def test_event_registration_search_first_name(self):
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
												'first_name' : 'Found_name_',
												'last_name' : '',
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
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[Event.objects.get(name='test_event_0').pk]),
									data = {
												'action' : 'search',
												'first_name' : '',
												'last_name' : 'Found_name_',
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# check that we got the right number of events
		self.assertEqual(response.context['search_number'],17)

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
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
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
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=person_2,event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=person_3,event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
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
												'participated_' + str(person_1.pk) : 'on',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : '',
												'participated_' + str(person_2.pk) : 'on',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : '',
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
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,False)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,False)
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
												'participated_' + str(person_1.pk) : 'on',
												'role_type_' + str(person_1.pk) : str(test_role_1.pk),
												'registered_' + str(person_2.pk) : 'on',
												'participated_' + str(person_2.pk) : 'on',
												'role_type_' + str(person_2.pk) : str(test_role_2.pk),
												'registered_' + str(person_3.pk) : 'on',
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
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.participated,True)
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
											participated=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_1'),
											role_type=test_role_3,
											registered=True,
											participated=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_2'),
											role_type=test_role_3,
											registered=True,
											participated=False
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
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_2.pk),
												'registered_' + str(person_2.pk) : 'on',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_3.pk),
												'registered_' + str(person_3.pk) : 'on',
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
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
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
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=Person.objects.get(first_name='Registered_1'),
												role_type=test_role_1,
												registered=False,
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(name='test_event_0'),
												person=Person.objects.get(first_name='Registered_2'),
												role_type=test_role_1,
												registered=False,
												participated=True
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
													'participated_' + str(person_1.pk) : '',
													'role_type_' + str(person_1.pk) : str(test_role_1.pk),
													'registered_' + str(person_2.pk) : 'on',
													'participated_' + str(person_2.pk) : '',
													'role_type_' + str(person_2.pk) : str(test_role_1.pk),
													'registered_' + str(person_3.pk) : 'on',
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
			self.assertEqual(registration_1.participated,False)
			self.assertEqual(registration_1.role_type,test_role_1)
			# get the registration for the second person
			registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
			# check the values
			self.assertEqual(registration_2.registered,True)
			self.assertEqual(registration_2.participated,False)
			self.assertEqual(registration_2.role_type,test_role_1)
			# get the registration for the third person
			registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
			# check the values
			self.assertEqual(registration_3.registered,True)
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
											participated=True
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_1'),
											role_type=test_role_2,
											registered=False,
											participated=True
											)
		Event_Registration.objects.create(
											event=Event.objects.get(name='test_event_0'),
											person=Person.objects.get(first_name='Registered_2'),
											role_type=test_role_3,
											registered=False,
											participated=True
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
												'participated_' + str(person_1.pk) : '',
												'role_type_' + str(person_1.pk) : str(test_role_2.pk),
												'registered_' + str(person_2.pk) : 'on',
												'participated_' + str(person_2.pk) : '',
												'role_type_' + str(person_2.pk) : str(test_role_3.pk),
												'registered_' + str(person_3.pk) : 'on',
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
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_1'),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(first_name='Registered_2'),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_1)

class EditEventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for event
		set_up_event_base_data()
		# and set up base data for addresses
		set_up_address_base_data()

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
		self.assertEqual(test_event.ward,Ward.objects.get(ward_name='Test ward'))
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
		self.assertEqual(test_event.areas.filter(area_name='Test area').exists(),True)
		self.assertEqual(test_event.areas.filter(area_name='Test area 2').exists(),False)

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
		self.assertEqual(response.context['page_list'],[1,2,3,4,5])

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
		self.assertEqual(response.context['page_list'],[1,2])

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
		self.assertEqual(response.context['page_list'],[1,2,3])

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
		self.assertEqual(response.context['page_list'],[1,2,3])

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
							'Questions'
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
		test_street_1 = Street.objects.get(name = 'test street 1')
		test_street_2 = Street.objects.get(name = 'test street 2')
		# check the post codes for the streets
		self.assertEqual(test_street_1.post_code,test_postcode_1)
		self.assertEqual(test_street_2.post_code,test_postcode_2)

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
		test_street_1 = Street.objects.get(name = 'test street 1')
		test_street_2 = Street.objects.get(name = 'test street 2')
		# check the post codes for the streets
		self.assertEqual(test_street_1.post_code,test_postcode_1)
		self.assertEqual(test_street_2.post_code,test_postcode_2)
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
		self.assertEqual(Street.objects.all().count(),2)

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
		self.assertFalse(Person.objects.all().exists())

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
		# get the person
		test_person = Person.objects.get(first_name='Test',last_name='Person')
		# check the fields
		self.assertEqual(test_person.first_name,'Test')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person')
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
		# check that we only have one person
		self.assertEqual(Person.objects.all().count(),1)

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
		# check that we only have one person
		self.assertEqual(Person.objects.all().count(),1)
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
		# check that no additional event categories have been created
		self.assertEqual(Person.objects.all().count(),1)

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
		self.assertContains(response,'test_duplicate_0 test_duplicate_0 is parent of test_child_0 test_child_0 not created: from duplicate with name and age status')
		self.assertContains(response,'test_child_0 test_child_0 is child of test_duplicate_0 test_duplicate_0 not created: to duplicate with name and age status')
		self.assertContains(response,'missing from person from last name is parent of test_child_0 test_child_0 not created: from does not exist')
		self.assertContains(response,'test_parent_0 test_parent_0 is parent of missing to person to last name not created: to does not exist')
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
		self.assertContains(response,'invalid person last name (Adult) at test_event_0 not created: person does not exist')
		self.assertContains(response,'test_duplicate_0 test_duplicate_0 (Adult) at test_event_0 not created: person duplicate with name and age status')
		self.assertContains(response,'invalid event last name (Adult) at invalid not created: event does not exist')
		self.assertContains(response,'duplicate event last name (Adult) at test_duplicate_0 not created: multiple matching events exist')
		self.assertContains(response,'test_child_0 test_child_0 (Child under four) at test_event_0 not created: adult_test_role is not valid for Child under four')
		self.assertContains(response,'invalid registered participated last name (Adult) at test_event_0 not created: neither registered nor participated is True')
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
		self.assertEqual(registration_adult_0.role_type,second_role_type)
		self.assertEqual(registration_adult_0.registered,True)
		self.assertEqual(registration_adult_0.participated,False)
		# get the records
		registration_child_0 = Event_Registration.objects.get(person=child_0,event=event)
		# check the values
		self.assertEqual(registration_child_0.role_type,second_role_type)
		self.assertEqual(registration_child_0.registered,False)
		self.assertEqual(registration_child_0.participated,True)
		# check that the unmodified record hasn't changed
		registration_adult_1 = Event_Registration.objects.get(person=adult_1,event=event)
		# check the values
		self.assertEqual(registration_adult_1.role_type,role_type)
		self.assertEqual(registration_adult_1.registered,True)
		self.assertEqual(registration_adult_1.participated,True)
		# check the count
		self.assertEqual(Event_Registration.objects.all().count(),3)

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
		self.assertContains(response,'test_adult_0,test_adult_0,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,,,,test notes,,,')
		self.assertContains(response,'test_adult_1,test_adult_1,test@test.com,123456,789012,01/01/2000,Gender,True,01/01/2010,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Adult,123,ABC streets 10,ABC0,test notes,01/01/2011,02/02/2012,test ecd')
		self.assertContains(response,'test_child_0,test_child_0,test@test.com,,,01/01/2000,Gender,False,,test_role_type,')
		self.assertContains(response,'test_ethnicity,test_ABSS_type,Child under four,,,,test notes,,,')

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
		# and address data
		set_up_address_base_data()
		# and an extra area
		area_3 = Area.objects.create(area_name='Test area 3',use_for_events=True)
		# get the second event
		event = Event.objects.get(name='test_event_1')
		# set fields
		event.location = 'test location'
		event.description = 'test description'
		event.ward = Ward.objects.get(ward_name='Test ward')
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
		self.assertContains(response,'test_event_0,Test event description,test_event_type,01/01/2019,10:00,11:00,Test location,,')
		self.assertContains(response,'test_event_1,test description,test_event_type,01/01/2019,10:00,11:00,test location,Test ward,"Test area 2,Test area 3"')

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

	def test_download_events(self):
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
		self.assertContains(response,'test_adult_0,test_adult_0,Adult,test_event_0,01/01/2019,False,True,test_role_type')
		self.assertContains(response,'test_adult_1,test_adult_1,Adult,test_event_0,01/01/2019,True,True,test_role_type')
		self.assertContains(response,'test_child_0,test_child_0,Child under four,test_event_0,01/01/2019,True,False,test_role_type')

