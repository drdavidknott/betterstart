from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status, Area, Ward, Post_Code, Street, Question, Answer, Option, Answer_Note
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
	test_role = Role_Type.objects.create(role_type_name='test_role_type',use_for_events=True,use_for_people=True)
	# and a second test role type
	second_test_role = Role_Type.objects.create(role_type_name='second_test_role_type',use_for_events=True,use_for_people=True)
	# and an UNKNOWN role type
	unknown_test_role = Role_Type.objects.create(role_type_name='UNKNOWN',use_for_events=True,use_for_people=True)
	# create a test ABSS type
	test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
	# create a second test ABSS type
	second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
	# and another type
	test_ABSS_type = ABSS_Type.objects.create(name='ABSS beneficiary')
	# create a test age status
	test_age_status = Age_Status.objects.create(status='Adult')
	# create a second test age status
	test_age_status = Age_Status.objects.create(status='Child')

def set_up_test_people(
						name_root,
						role_type='test_role_type',
						number=1,
						ABSS_type='test_ABSS_type',
						age_status='Adult',
						trained_champion=False,
						active_champion=False
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
											trained_champion = trained_champion,
											active_champion = active_champion,
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
	area = Area.objects.create(area_name='Test area')
	ward = Ward.objects.create(ward_name='Test ward',area=area)

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

def set_up_test_events(name_root,event_type,number,date='2019-01-01'):
	# set up the number of people asked for
	# create the number of people needed
	for n in range(number):
		# create an event
		test_event = Event.objects.create(
											name = name_root + str(n),
											description = 'Test event description',
											event_type = event_type,
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
											'champions' : '0',
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
		set_up_test_people('trained_champion_test_','test role 1',30,'test_ABSS_type','Adult',True)
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
											'champions' : 'trained',
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
		set_up_test_people('trained_champion_test_','test role 1',30,'test_ABSS_type','Child',True)
		set_up_test_people('trained_champion_test_','test role 1',27,'test_ABSS_type','Adult',True)
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
											'champions' : 'trained',
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
		set_up_test_people('trained_test_find_','test role 1',30,'test_ABSS_type','Child',True)
		set_up_test_people('trained_not_found_','test role 1',30,'test_ABSS_type','Child',True)
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
											'champions' : 'trained',
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
		set_up_test_people('trained_test_role_2','test role 2',35,'test_ABSS_type','Adult',True)
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
											'champions' : 'trained',
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
		set_up_test_people('trained_test_find','test role 2',37,'test_ABSS_type','Adult',True)
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
											'champions' : '0',
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
		set_up_test_people('trained_test_find','test role 2',39,'second_test_ABSS_type','Child',True)
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
											'champions' : 'trained',
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
											'champions' : 'trained',
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
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Adult',True,True)
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
											'champions' : 'active',
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
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Adult',True,True)
		set_up_test_people('trained_champion_test_','test role 1',17,'test_ABSS_type','Adult',True)
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
											'champions' : 'active',
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
		set_up_test_people('active_champion_test_','test role 1',30,'test_ABSS_type','Child',True,True)
		set_up_test_people('active_champion_test_','test role 1',27,'test_ABSS_type','Adult',True,True)
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
											'champions' : 'active',
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
		set_up_test_people('active_test_find_','test role 1',30,'test_ABSS_type','Child',True,True)
		set_up_test_people('active_not_found_','test role 1',30,'test_ABSS_type','Child',True,True)
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
											'champions' : 'active',
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
		set_up_test_people('active_test_role_2','test role 2',35,'test_ABSS_type','Adult',True,True)
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
											'champions' : 'active',
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
		set_up_test_people('active_test_find','test role 2',37,'test_ABSS_type','Adult',True,True)
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
											'champions' : '0',
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
		set_up_test_people('active_test_find','test role 2',39,'second_test_ABSS_type','Adult',True,True)
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
											'champions' : 'active',
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
											'champions' : 'active',
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
											'action' : 'search',
											'name' : '',
											'date_from' : '',
											'date_to' : '',
											'event_type' : '0',
											'event_category' : '0',
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
		self.assertEqual(test_person.default_role.role_type_name,'UNKNOWN')
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
		self.assertEqual(test_person.trained_champion,False)
		self.assertEqual(test_person.active_champion,False)
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)

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
												'middle_names' : '',
												'last_name' : 'Person_0',
												'role_type' : str(Role_Type.objects.get(role_type_name='test_role_type').pk)
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
		self.assertEqual(test_person.default_role.role_type_name,'UNKNOWN')
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
		self.assertEqual(test_person.trained_champion,False)
		self.assertEqual(test_person.active_champion,False)
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)

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
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_champion' : True,
											'active_champion' : True
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
		self.assertEqual(test_person.notes,'test notes')
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
		self.assertEqual(test_person.age_status.status,'Child')
		self.assertEqual(test_person.trained_champion,True)
		self.assertEqual(test_person.active_champion,True)
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)

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
											'age_status' : str(Age_Status.objects.get(status='Child').pk),
											'trained_champion' : True,
											'active_champion' : True
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
		self.assertEqual(test_person.notes,'test notes')
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
		self.assertEqual(test_person.age_status.status,'Child')
		self.assertEqual(test_person.trained_champion,True)
		self.assertEqual(test_person.active_champion,True)
		self.assertEqual(test_person.house_name_or_number,'')
		self.assertEqual(test_person.street,None)

class AddEventViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# set up base data for people
		set_up_event_base_data()

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
											'email_address' : 'new_email_address@test.com',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'role_type' : str(Role_Type.objects.get(role_type_name='second_test_role_type').pk),
											'relationship_type' : str(Relationship_Type.objects.get(relationship_type='parent').pk),
											'ABSS_type' : str(ABSS_Type.objects.get(name='test_ABSS_type').pk),
											'age_status' : str(Age_Status.objects.get(status='Adult').pk)
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the newly created person record
		test_new_person = Person.objects.get(first_name='new_first_name')
		# check the record contents
		self.assertEqual(test_new_person.first_name,'new_first_name')
		self.assertEqual(test_new_person.middle_names,'new_middle_names')
		self.assertEqual(test_new_person.last_name,'new_last_name')
		self.assertEqual(test_new_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_new_person.gender,'Male')
		self.assertEqual(test_new_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
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
		self.assertEqual(test_new_person.ABSS_type.name,'test_ABSS_type')
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
												'date' : '01/02/2010',
												'start_time' : '10:00',
												'end_time' : '11:00',
												'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
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
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'01/02/2010')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'10:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'11:00')

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
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : str(Event_Type.objects.get(name='test_event_type').pk),
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
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')

class Address(TestCase):
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
			self.assertEqual(test_person.street.pk,1)
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

class Questions(TestCase):
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
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
		self.assertEqual(response.status_code, 200)
		# get one answer
		self.assertTrue(Answer.objects.filter(person=person,question=question_no_notes,option=option_no_notes).exists())
		# get the other answer
		self.assertFalse(Answer.objects.filter(person=person,question=question_with_notes,option=option_with_notes).exists())
		# get the notes
		answer_note = Answer_Note.objects.get(person=person,question=question_with_notes)
		# check the note is as expected
		self.assertEqual(answer_note.notes,'test_notes')

