from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History, Relationship_Type, Relationship, ABSS_Type, \
							Age_Status
import datetime
from django.urls import reverse
from django.contrib.auth.models import User

def set_up_people_base_data():
	# set up base data needed to do tests for people
	# first the ethnicity
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	# and a second test ethnicity
	second_test_ethnicity = Ethnicity.objects.create(description='second_test_ethnicity')
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
	# create a test role
	test_role = Role_Type.objects.create(role_type_name='test_role_type')
	# and a second test role type
	second_test_role = Role_Type.objects.create(role_type_name='second_test_role_type')
	# and an UNKNOWN role type
	unknown_test_role = Role_Type.objects.create(role_type_name='UNKNOWN')
	# create a test ABSS type
	test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
	# create a second test ABSS type
	second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
	# create a test age status
	test_age_status = Age_Status.objects.create(status='Adult')
	# create a second test age status
	test_age_status = Age_Status.objects.create(status='Child')

def set_up_test_people(
						name_root,
						role_type_id=1,
						number=1,
						ABSS_type_id=1,
						age_status_id=1,
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
											default_role = Role_Type.objects.get(id=role_type_id),
											english_is_second_language = False,
											pregnant = False,
											due_date = None,
											ABSS_type = ABSS_Type.objects.get(id=ABSS_type_id),
											age_status = Age_Status.objects.get(id=age_status_id),
											trained_champion = trained_champion,
											active_champion = active_champion
											)
		# create a role history entry
		Role_History.objects.create(
									person = test_person,
									role_type = Role_Type.objects.get(id=role_type_id)
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

class PeopleViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create the Parent role
		parent_role = Role_Type.objects.create(role_type_name='Parent')
		# and the parent champion role
		parent_champion_role = Role_Type.objects.create(role_type_name='Parent Champion')
		# create a test age status
		test_age_status = Age_Status.objects.create(status='Adult')
		# create a second test age status
		test_age_status = Age_Status.objects.create(status='Child')
		# and four more test role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		test_role_4 = Role_Type.objects.create(role_type_name='test role 4')
		test_role_5 = Role_Type.objects.create(role_type_name='test role 5')
		# create a test ABSS type
		test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
		# create a second test ABSS type
		second_test_ABSS_type = ABSS_Type.objects.create(name='second_test_ABSS_type')
		# Create 50 of each type
		set_up_test_people('Parent_',parent_role.pk,50)
		set_up_test_people('Parent_Champion_',parent_champion_role.pk,50)
		set_up_test_people('Test_Role_1_',test_role_1.pk,50)
		set_up_test_people('Test_Role_2_',test_role_2.pk,50)
		# and 50 of each of the two test role types with different names
		set_up_test_people('Different_Name_',test_role_1.pk,50)
		set_up_test_people('Another_Name_',test_role_2.pk,50)
		# and more with the roles swapped over
		set_up_test_people('Different_Name_',test_role_2.pk,50)
		set_up_test_people('Another_Name_',test_role_1.pk,50)
		# and a short set to test a result set with less than a page
		set_up_test_people('Short_Set_',test_role_3.pk,10)
		# create 25 ex-parent champions
		set_up_test_people('Ex_Parent_Champion_',parent_champion_role.pk,50)
		# and a set that doesn't exactly fit two pagaes
		set_up_test_people('Pagination_',test_role_5.pk,32)
		# now go through them and update their role and role history
		ex_parent_champions = Person.objects.filter(first_name__icontains='Ex')
		# go through the list
		for ex_parent_champion in ex_parent_champions:
			# update the role
			ex_parent_champion.default_role = test_role_1
			# and set the history
			Role_History.objects.create(
							person = ex_parent_champion,
							role_type = test_role_1
							)

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

	def test_search_for_people_who_have_ever_been_a_parent_champion(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : 'Has ever been a Parent Champion',
											'ABSS_type' : '0',
											'age_status' : '0',
											'champions' : '0',
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
		self.assertEqual(response.context['page_list'],[1,2,3,4])

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
		set_up_test_people('ABSS_test_',1,30,2)
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
											'ABSS_type' : '2',
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
		set_up_test_people('ABSS_test_find_',1,30,2)
		set_up_test_people('ABSS_not_found_',1,30,2)
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
											'ABSS_type' : '2',
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
		set_up_test_people('ABSS_test_role_1',1,30,2)
		set_up_test_people('ABSS_test_role_2',2,35,2)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '2',
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
		set_up_test_people('ABSS_test_role_1',1,30,2)
		set_up_test_people('ABSS_test_role_2',2,35,2)
		set_up_test_people('ABSS_test_find',2,37,2)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '2',
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
											'ABSS_type' : '3',
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
		set_up_test_people('age_status_test_',1,30,1,2)
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
											'age_status' : '2',
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
		set_up_test_people('age_test_find_',1,30,1,2)
		set_up_test_people('age_not_found_',1,30,1,2)
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
											'age_status' : '2',
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
		set_up_test_people('age_status_test_role_1',1,30,1,2)
		set_up_test_people('age_status_test_role_2',2,35,1,2)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '0',
											'age_status' : '2',
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
		set_up_test_people('age_status_test_role_1',1,30,1,2)
		set_up_test_people('age_status_test_role_2',2,35,1,2)
		set_up_test_people('age_status_test_find',2,37,1,2)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '0',
											'age_status' : '2',
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
		set_up_test_people('age_status_test_role_1',1,30,1,2)
		set_up_test_people('age_status_test_role_2',2,35,1,2)
		set_up_test_people('age_status_test_role_3',3,37,1,2)
		set_up_test_people('age_status_test_find',2,39,2,2)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '2',
											'age_status' : '2',
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
		Age_Status.objects.create(status='Third test age status')
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
											'age_status' : '3',
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
		set_up_test_people('trained_champion_test_',1,30,1,1,True)
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
											'age_status' : '1',
											'champions' : 'Trained Champions',
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
		set_up_test_people('trained_champion_test_',1,30,1,2,True)
		set_up_test_people('trained_champion_test_',1,27,1,1,True)
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
											'age_status' : '2',
											'champions' : 'Trained Champions',
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
		set_up_test_people('trained_test_find_',1,30,1,2,True)
		set_up_test_people('trained_not_found_',1,30,1,2,True)
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
											'champions' : 'Trained Champions',
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
		set_up_test_people('trained_test_role_1',1,30,1,1)
		set_up_test_people('trained_test_role_2',2,35,1,1,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '0',
											'age_status' : '0',
											'champions' : 'Trained Champions',
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
		set_up_test_people('trained_test_role_1',1,30,1,1)
		set_up_test_people('trained_test_role_2',2,35,1,1)
		set_up_test_people('trained_test_find',2,37,1,1,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
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
		set_up_test_people('trained_test_role_1',1,30,1,2)
		set_up_test_people('trained_test_role_2',2,35,1,2)
		set_up_test_people('trained_test_role_3',3,37,1,2)
		set_up_test_people('trained_test_find',2,39,2,2,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '2',
											'age_status' : '0',
											'champions' : 'Trained Champions',
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
											'champions' : 'Trained Champions',
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
		set_up_test_people('active_champion_test_',1,30,1,1,True,True)
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
											'age_status' : '1',
											'champions' : 'Active Champions',
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
		set_up_test_people('active_champion_test_',1,30,1,1,True,True)
		set_up_test_people('trained_champion_test_',1,17,1,1,True)
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
											'age_status' : '1',
											'champions' : 'Active Champions',
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
		set_up_test_people('active_champion_test_',1,30,1,2,True,True)
		set_up_test_people('active_champion_test_',1,27,1,1,True,True)
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
											'age_status' : '2',
											'champions' : 'Active Champions',
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
		set_up_test_people('active_test_find_',1,30,1,2,True,True)
		set_up_test_people('active_not_found_',1,30,1,2,True,True)
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
											'champions' : 'Active Champions',
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
		set_up_test_people('active_test_role_1',1,30,1,1)
		set_up_test_people('active_test_role_2',2,35,1,1,True,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : '',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '0',
											'age_status' : '0',
											'champions' : 'Active Champions',
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
		set_up_test_people('active_test_role_1',1,30,1,1)
		set_up_test_people('active_test_role_2',2,35,1,1)
		set_up_test_people('active_test_find',2,37,1,1,True,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
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
		set_up_test_people('active_test_role_1',1,30,1,2)
		set_up_test_people('active_test_role_2',2,35,1,2)
		set_up_test_people('active_test_role_3',3,37,1,2)
		set_up_test_people('active_test_find',2,39,2,2,True,True)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.post(
									reverse('listpeople'),
									data = { 
											'action' : 'search',
											'first_name' : 'find',
											'last_name' : '',
											'role_type' : '2',
											'ABSS_type' : '2',
											'age_status' : '0',
											'champions' : 'Active Champions',
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
											'champions' : 'Active Champions',
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
		response = self.client.get(reverse('role_type',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_ABSS_type_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('ABSS_type',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_age_status_successful_response_if_logged_in(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the people page
		response = self.client.get(reverse('age_status',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_role_type_search(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# create a new type
		test_role_type = Role_Type.objects.create(role_type_name='People Query Test')
		# create some extra people
		set_up_test_people('Role Type Query Test',test_role_type.pk,30,1,1)
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
		set_up_test_people('ABSS Type Query Test',1,30,test_ABSS_type.pk,1)
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
		set_up_test_people('Age Status Query Test',1,30,1,test_age_status.pk)
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
		# create a load of event types
		test_event_type_1 = Event_Type.objects.create(
														name = 'test_event_type_1',
														description = 'type desc',
														event_category = test_event_category)
		test_event_type_2 = Event_Type.objects.create(
														name = 'test_event_type_2',
														description = 'type desc',
														event_category = test_event_category)
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
														event_category = test_event_category)
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
											'event_type' : '6',
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
											'event_type' : '6',
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
											'event_type' : '1',
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

	def test_invalid_event(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an invalid event
		response = self.client.get(reverse('event',args=[9999]))
		# check that we got a valid response
		self.assertEqual(response.status_code, 200)
		# check that we got an error in the page
		self.assertContains(response,'ERROR')

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
		self.assertRedirects(response, '/profile/1')
		# get the record
		test_person = Person.objects.get(id=1)
		# check the record contents
		self.assertEqual(test_person.first_name,'Testfirst')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Testlast')
		self.assertEqual(test_person.default_role.role_type_name,'UNKNOWN')
		# check the record contents which have not been set yet
		self.assertEqual(test_person.email_address,'')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'')
		self.assertEqual(test_person.notes,'')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.addresses.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.english_is_second_language,False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.trained_champion,False)
		self.assertEqual(test_person.active_champion,False)

	def test_person_already_exists(self):
		# log the user in
		self.client.login(username='testuser', password='testword')
		# submit a post for a person who aready exists
		set_up_test_people('Person_',1,1)
		# submit the form
		response = self.client.post(
									reverse('addperson'),
									data = { 
												'first_name' : 'Person_0',
												'middle_names' : '',
												'last_name' : 'Person_0',
												'role_type' : '1'
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
		set_up_test_people('Person_',1,1)
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
		self.assertRedirects(response, '/profile/2')
		# get the record
		test_person = Person.objects.get(id=2)
		# check the record contents
		self.assertEqual(test_person.first_name,'Person_0')
		self.assertEqual(test_person.middle_names,'')
		self.assertEqual(test_person.last_name,'Person_0')
		self.assertEqual(test_person.default_role.role_type_name,'UNKNOWN')
		# check the record contents which have not been set yet
		self.assertEqual(test_person.email_address,'')
		self.assertEqual(test_person.date_of_birth,None)
		self.assertEqual(test_person.gender,'')
		self.assertEqual(test_person.notes,'')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.addresses.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.english_is_second_language,False)
		self.assertEqual(test_person.pregnant,False)
		self.assertEqual(test_person.due_date,None)
		self.assertEqual(test_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_person.families.all().exists(),False)
		self.assertEqual(test_person.savs_id,None)
		self.assertEqual(test_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_person.age_status.status,'Adult')
		self.assertEqual(test_person.trained_champion,False)
		self.assertEqual(test_person.active_champion,False)

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
		set_up_test_people('Person_',1,1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('profile',args=[1]),
									data = { 
											'first_name' : 'updated_first_name',
											'middle_names' : 'updated_middle_names',
											'last_name' : 'updated_last_name',
											'email_address' : 'updated_email_address@test.com',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'english_is_second_language' : True,
											'pregnant' : True,
											'due_date' : '01/01/2020',
											'role_type' : '2',
											'ethnicity' : '2',
											'ABSS_type' : '2',
											'age_status' : '2',
											'trained_champion' : True,
											'active_champion' : True
											}
									)
		# check the response
		self.assertEqual(response.status_code, 302)
		# get the record
		test_person = Person.objects.get(id=1)
		# check the record contents
		self.assertEqual(test_person.first_name,'updated_first_name')
		self.assertEqual(test_person.middle_names,'updated_middle_names')
		self.assertEqual(test_person.last_name,'updated_last_name')
		self.assertEqual(test_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_person.email_address,'updated_email_address@test.com')
		self.assertEqual(test_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		self.assertEqual(test_person.gender,'Male')
		self.assertEqual(test_person.notes,'test notes')
		self.assertEqual(test_person.relationships.all().exists(),False)
		self.assertEqual(test_person.children_centres.all().exists(),False)
		self.assertEqual(test_person.addresses.all().exists(),False)
		self.assertEqual(test_person.events.all().exists(),False)
		self.assertEqual(test_person.english_is_second_language,True)
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
												'event_type' : '1',
												'date' : '01/01/2019',
												'start_time' : '10:00',
												'end_time' : '11:00'
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/1')
		# get the record
		test_event = Event.objects.get(id=1)
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
		set_up_test_people('Test_exists_',1,1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[1]),
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
		set_up_test_people('Test_from_',1,1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[1]),
									data = { 
											'action' : 'addrelationshiptonewperson',
											'first_name' : 'new_first_name',
											'middle_names' : 'new_middle_names',
											'last_name' : 'new_last_name',
											'email_address' : 'new_email_address@test.com',
											'date_of_birth' : '01/01/2001',
											'gender' : 'Male',
											'role_type' : '2',
											'relationship_type' : '1',
											'ABSS_type' : '1',
											'age_status' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the newly created person record
		test_new_person = Person.objects.get(id=2)
		# check the record contents
		self.assertEqual(test_new_person.first_name,'new_first_name')
		self.assertEqual(test_new_person.middle_names,'new_middle_names')
		self.assertEqual(test_new_person.last_name,'new_last_name')
		self.assertEqual(test_new_person.default_role.role_type_name,'second_test_role_type')
		self.assertEqual(test_new_person.gender,'Male')
		self.assertEqual(test_new_person.date_of_birth.strftime('%d/%m/%Y'),'01/01/2001')
		# check the record contents which have not been set yet
		self.assertEqual(test_new_person.email_address,'')
		self.assertEqual(test_new_person.notes,'')
		self.assertEqual(test_new_person.relationships.all().exists(),True)
		self.assertEqual(test_new_person.children_centres.all().exists(),False)
		self.assertEqual(test_new_person.addresses.all().exists(),False)
		self.assertEqual(test_new_person.events.all().exists(),False)
		self.assertEqual(test_new_person.english_is_second_language,False)
		self.assertEqual(test_new_person.pregnant,False)
		self.assertEqual(test_new_person.due_date,None)
		self.assertEqual(test_new_person.ethnicity.description,'test_ethnicity')
		self.assertEqual(test_new_person.capture_type.capture_type_name,'test_capture_type')
		self.assertEqual(test_new_person.families.all().exists(),False)
		self.assertEqual(test_new_person.savs_id,None)
		self.assertEqual(test_new_person.ABSS_type.name,'test_ABSS_type')
		self.assertEqual(test_new_person.age_status.status,'Adult')
		# get the original person
		test_original_person = Person.objects.get(id=1)
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
		set_up_test_people('Test_from_',1,1)
		set_up_test_people('Test_to_',1,1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[1]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_2' : '1',
											}
									)
		# get the from person
		test_from_person = Person.objects.get(id=1)
		# and the to person
		test_to_person = Person.objects.get(id=2)
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
		set_up_test_people('Test_from_',1,1)
		set_up_test_people('Test_to_',1,1)
		# get the people
		test_from_person = Person.objects.get(id=1)
		# and the to person
		test_to_person = Person.objects.get(id=2)
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(id=1)
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(id=2)
			)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[1]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_2' : '3',
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
		set_up_test_people('Test_from_',1,1)
		set_up_test_people('Test_to_',1,1)
		# get the people
		test_from_person = Person.objects.get(id=1)
		# and the to person
		test_to_person = Person.objects.get(id=2)
		# create the relationships
		Relationship.objects.create(
										relationship_from=test_from_person,
										relationship_to=test_to_person,
										relationship_type=Relationship_Type.objects.get(id=1)
			)
		# and the other one
		Relationship.objects.create(
										relationship_from=test_to_person,
										relationship_to=test_from_person,
										relationship_type=Relationship_Type.objects.get(id=2)
			)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('add_relationship',args=[1]),
									data = { 
											'action' : 'editrelationships',
											'relationship_type_2' : '0',
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
												'event_type' : '1'
											}
									)
		# check that we got a redirect response
		self.assertRedirects(response, '/event_registration/1')
		# get the record
		test_event = Event.objects.get(id=1)
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
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get an event
		response = self.client.get(reverse('event_registration',args=[1]))
		# check the response
		self.assertEqual(response.status_code, 200)

	def test_event_registration_search_blank_search_error(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some people
		set_up_test_people('Found_name_',1,50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
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
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some people
		set_up_test_people('Found_name_',1,50)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
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
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some people
		set_up_test_people('Found_name_',1,17)
		set_up_test_people('Lost_name_',1,19)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
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
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some people
		set_up_test_people('Found_name_',1,17)
		set_up_test_people('Lost_name_',1,19)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
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
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		# create some people
		set_up_test_people('Registered_',1,3)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
									data = {
												'action' : 'addregistration',
												'search_keys' : '1,2,3',
												'registered_1' : 'on',
												'participated_1' : '',
												'role_type_1' : str(test_role_1.pk),
												'registered_2' : 'on',
												'participated_2' : '',
												'role_type_2' : str(test_role_2.pk),
												'registered_3' : 'on',
												'participated_3' : '',
												'role_type_3' : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(id=1)
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_participate_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		# create some people
		set_up_test_people('Registered_',1,3)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
									data = {
												'action' : 'addregistration',
												'search_keys' : '1,2,3',
												'registered_1' : '',
												'participated_1' : 'on',
												'role_type_1' : str(test_role_1.pk),
												'registered_2' : '',
												'participated_2' : 'on',
												'role_type_2' : str(test_role_2.pk),
												'registered_3' : '',
												'participated_3' : 'on',
												'role_type_3' : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(id=1)
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
		# check the values
		self.assertEqual(registration_1.registered,False)
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
		# check the values
		self.assertEqual(registration_2.registered,False)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
		# check the values
		self.assertEqual(registration_3.registered,False)
		self.assertEqual(registration_3.participated,True)
		self.assertEqual(registration_3.role_type,test_role_3)

	def test_event_registration_register_participate_people_multiple_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		# create some people
		set_up_test_people('Registered_',1,3)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
									data = {
												'action' : 'addregistration',
												'search_keys' : '1,2,3',
												'registered_1' : 'on',
												'participated_1' : 'on',
												'role_type_1' : str(test_role_1.pk),
												'registered_2' : 'on',
												'participated_2' : 'on',
												'role_type_2' : str(test_role_2.pk),
												'registered_3' : 'on',
												'participated_3' : 'on',
												'role_type_3' : str(test_role_3.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(id=1)
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.participated,True)
		self.assertEqual(registration_1.role_type,test_role_1)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,True)
		self.assertEqual(registration_2.role_type,test_role_2)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.participated,True)
		self.assertEqual(registration_3.role_type,test_role_3)


	def test_event_registration_register_change_roles(self):
		# create an event
		set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
		# create some role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		# create some people
		set_up_test_people('Registered_',1,3)
		# create some registrations
		Event_Registration.objects.create(
											event=Event.objects.get(id=1),
											person=Person.objects.get(id=1),
											role_type=test_role_1,
											registered=True,
											participated=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(id=1),
											person=Person.objects.get(id=2),
											role_type=test_role_3,
											registered=True,
											participated=False
											)
		Event_Registration.objects.create(
											event=Event.objects.get(id=1),
											person=Person.objects.get(id=3),
											role_type=test_role_3,
											registered=True,
											participated=False
											)
		# log the user in
		self.client.login(username='testuser', password='testword')
		# do a search
		response = self.client.post(
									reverse('event_registration',args=[1]),
									data = {
												'action' : 'editregistration',
												'registration_keys' : '1,2,3',
												'registered_1' : 'on',
												'participated_1' : '',
												'role_type_1' : str(test_role_2.pk),
												'registered_2' : 'on',
												'participated_2' : '',
												'role_type_2' : str(test_role_3.pk),
												'registered_3' : 'on',
												'participated_3' : '',
												'role_type_3' : str(test_role_1.pk),
											}
									)
		# check the response
		self.assertEqual(response.status_code, 200)
		# get the event
		event = Event.objects.get(id=1)
		# get the registration for the first person
		registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
		# check the values
		self.assertEqual(registration_1.registered,True)
		self.assertEqual(registration_1.participated,False)
		self.assertEqual(registration_1.role_type,test_role_2)
		# get the registration for the second person
		registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
		# check the values
		self.assertEqual(registration_2.registered,True)
		self.assertEqual(registration_2.participated,False)
		self.assertEqual(registration_2.role_type,test_role_3)
		# get the registration for the third person
		registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
		# check the values
		self.assertEqual(registration_3.registered,True)
		self.assertEqual(registration_3.participated,False)
		self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_register_change_registered_and_participated(self):
			# create an event
			set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
			# create some role types
			test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
			# create some people
			set_up_test_people('Registered_',1,3)
			# create some registrations
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=1),
												role_type=test_role_1,
												registered=False,
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=2),
												role_type=test_role_1,
												registered=False,
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=3),
												role_type=test_role_1,
												registered=False,
												participated=True
												)
			# log the user in
			self.client.login(username='testuser', password='testword')
			# do a search
			response = self.client.post(
										reverse('event_registration',args=[1]),
										data = {
													'action' : 'editregistration',
													'registration_keys' : '1,2,3',
													'registered_1' : 'on',
													'participated_1' : '',
													'role_type_1' : str(test_role_1.pk),
													'registered_2' : 'on',
													'participated_2' : '',
													'role_type_2' : str(test_role_1.pk),
													'registered_3' : 'on',
													'participated_3' : '',
													'role_type_3' : str(test_role_1.pk),
												}
										)
			# check the response
			self.assertEqual(response.status_code, 200)
			# get the event
			event = Event.objects.get(id=1)
			# get the registration for the first person
			registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
			# check the values
			self.assertEqual(registration_1.registered,True)
			self.assertEqual(registration_1.participated,False)
			self.assertEqual(registration_1.role_type,test_role_1)
			# get the registration for the second person
			registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
			# check the values
			self.assertEqual(registration_2.registered,True)
			self.assertEqual(registration_2.participated,False)
			self.assertEqual(registration_2.role_type,test_role_1)
			# get the registration for the third person
			registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
			# check the values
			self.assertEqual(registration_3.registered,True)
			self.assertEqual(registration_3.participated,False)
			self.assertEqual(registration_3.role_type,test_role_1)

	def test_event_registration_register_change_registered_and_participated_and_role(self):
			# create an event
			set_up_test_events('test_event_',Event_Type.objects.get(id=1),1)
			# create some role types
			test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
			test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
			test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
			# create some people
			set_up_test_people('Registered_',1,3)
			# create some registrations
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=1),
												role_type=test_role_1,
												registered=False,
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=2),
												role_type=test_role_2,
												registered=False,
												participated=True
												)
			Event_Registration.objects.create(
												event=Event.objects.get(id=1),
												person=Person.objects.get(id=3),
												role_type=test_role_3,
												registered=False,
												participated=True
												)
			# log the user in
			self.client.login(username='testuser', password='testword')
			# do a search
			response = self.client.post(
										reverse('event_registration',args=[1]),
										data = {
													'action' : 'editregistration',
													'registration_keys' : '1,2,3',
													'registered_1' : 'on',
													'participated_1' : '',
													'role_type_1' : str(test_role_2.pk),
													'registered_2' : 'on',
													'participated_2' : '',
													'role_type_2' : str(test_role_3.pk),
													'registered_3' : 'on',
													'participated_3' : '',
													'role_type_3' : str(test_role_1.pk),
												}
										)
			# check the response
			self.assertEqual(response.status_code, 200)
			# get the event
			event = Event.objects.get(id=1)
			# get the registration for the first person
			registration_1 = Event_Registration.objects.get(person=Person.objects.get(id=1),event=event)
			# check the values
			self.assertEqual(registration_1.registered,True)
			self.assertEqual(registration_1.participated,False)
			self.assertEqual(registration_1.role_type,test_role_2)
			# get the registration for the second person
			registration_2 = Event_Registration.objects.get(person=Person.objects.get(id=2),event=event)
			# check the values
			self.assertEqual(registration_2.registered,True)
			self.assertEqual(registration_2.participated,False)
			self.assertEqual(registration_2.role_type,test_role_3)
			# get the registration for the third person
			registration_3 = Event_Registration.objects.get(person=Person.objects.get(id=3),event=event)
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
		set_up_test_events('Event_',Event_Type.objects.get(id=1),1)
		# submit a post for a person who doesn't exist
		response = self.client.post(
									reverse('edit_event',args=[1]),
									data = { 
											'name' : 'updated_name',
											'description' : 'updated_description',
											'location' : 'updated_location',
											'date' : '05/05/2019',
											'start_time' : '13:00',
											'end_time' : '14:00',
											'event_type' : '1'
											}
									)
		# check the response
		self.assertEqual(response.status_code,302)
		# get the record
		test_event = Event.objects.get(id=1)
		# check the record contents
		self.assertEqual(test_event.name,'updated_name')
		self.assertEqual(test_event.description,'updated_description')
		self.assertEqual(test_event.location,'updated_location')
		self.assertEqual(test_event.date.strftime('%d/%m/%Y'),'05/05/2019')
		self.assertEqual(test_event.start_time.strftime('%H:%M'),'13:00')
		self.assertEqual(test_event.end_time.strftime('%H:%M'),'14:00')
