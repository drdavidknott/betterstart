from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, Role_History
import datetime
from django.urls import reverse
from django.contrib.auth.models import User

def set_up_100_test_people():
# create two role types that our test people will belong to
	test_role_type_1 = Role_Type.objects.create(role_type_name='test_role_1')
	test_role_type_2 = Role_Type.objects.create(role_type_name='test_role_1')
	# and the ethnicity
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
	# create 50 people for role type 1
	for n in range(1,50):
		# create a person
		test_person = Person.objects.create(
											first_name = 'First_' + str(n),
											middle_names = 'Middle Names',
											last_name = 'Last',
											email_address = 'test@test.com',
											date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
											gender = 'Gender',
											notes = 'test notes',
											default_role = test_role_type_1,
											english_is_second_language = False,
											pregnant = False,
											due_date = None
											)
		# create a role history entry
		Role_History.objects.create(
									person = test_person,
									role_type = test_role_type_1
									)
	# create 50 people for role type 2
	for n in range(51,100):
		# create a person
		test_person = Person.objects.create(
											first_name = 'First_' + str(n),
											middle_names = 'Middle Names',
											last_name = 'Last',
											email_address = 'test@test.com',
											date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
											gender = 'Gender',
											notes = 'test notes',
											default_role = test_role_type_2,
											english_is_second_language = False,
											pregnant = False,
											due_date = None
											)
		# create a role history entry
		Role_History.objects.create(
									person = test_person,
									role_type = test_role_type_2
									)

def set_up_test_user():
	# create a test user
	test_user = User.objects.create_user(username='testuser', password='testword')
	# return the user
	return test_user

class PeopleViewTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# Create 100 people for the test
		set_up_100_test_people()

	def test_redirect_if_not_logged_in(self):
		# get the response
		response = self.client.get('/listpeople')
		# check the response
		self.assertRedirects(response, '/people/login?next=/listpeople')

	def test_empty_page_if_logged_in(self):
		# create a test user
		user = set_up_test_user()
		# log the user in
		self.client.login(username='testuser', password='testword')
		# attempt to get the events page
		response = self.client.get(reverse('listpeople'))
		# check the response
		self.assertEqual(response.status_code, 200)
		# the list of people passed in the context should be empty
		self.assertEqual(len(response.context['people']),0)
