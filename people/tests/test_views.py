from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History
import datetime
from django.urls import reverse
from django.contrib.auth.models import User

def set_up_people_base_data():
	# set up base data needed to do tests for people
	# first the ethnicity
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')

def set_up_test_people(name_root,role_type,number):
	# set up the number of people asked for
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
											default_role = role_type,
											english_is_second_language = False,
											pregnant = False,
											due_date = None
											)
		# create a role history entry
		Role_History.objects.create(
									person = test_person,
									role_type = role_type
									)

def set_up_test_user():
	# create a test user
	test_user = User.objects.create_user(username='testuser', password='testword')
	# return the user
	return test_user

class PeopleViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# create a test user
		user = set_up_test_user()
		# create the Parent role
		parent_role = Role_Type.objects.create(role_type_name='Parent')
		# and the parent champion role
		parent_champion_role = Role_Type.objects.create(role_type_name='Parent Champion')
		# and four more test role types
		test_role_1 = Role_Type.objects.create(role_type_name='test role 1')
		test_role_2 = Role_Type.objects.create(role_type_name='test role 2')
		test_role_3 = Role_Type.objects.create(role_type_name='test role 3')
		test_role_4 = Role_Type.objects.create(role_type_name='test role 4')
		test_role_5 = Role_Type.objects.create(role_type_name='test role 5')
		# Create 50 of each type
		set_up_test_people('Parent_',parent_role,50)
		set_up_test_people('Parent_Champion_',parent_champion_role,50)
		set_up_test_people('Test_Role_1_',test_role_1,50)
		set_up_test_people('Test_Role_2_',test_role_2,50)
		# and 50 of each of the two test role types with different names
		set_up_test_people('Different_Name_',test_role_1,50)
		set_up_test_people('Another_Name_',test_role_2,50)
		# and more with the roles swapped over
		set_up_test_people('Different_Name_',test_role_2,50)
		set_up_test_people('Another_Name_',test_role_1,50)
		# and a short set to test a result set with less than a page
		set_up_test_people('Short_Set_',test_role_3,10)
		# create 25 ex-parent champions
		set_up_test_people('Ex_Parent_Champion_',parent_champion_role,50)
		# and a set that doesn't exactly fit two pagaes
		set_up_test_people('Pagination_',test_role_5,32)
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