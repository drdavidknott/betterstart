from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration, ABSS_Type, Age_Status
import datetime

def set_up_test_people():
	# create the role type that our test person will belong to
	test_role_type = Role_Type.objects.create(role_type_name='test_role')
	# and the ethnicity
	test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
	# and another ethnicity
	test_ethnicity = Ethnicity.objects.create(description='Prefer not to say')
	# and the capture type
	test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
	# create a test ABSS type
	test_ABSS_type = ABSS_Type.objects.create(name='test_ABSS_type')
	# and another type
	test_ABSS_type = ABSS_Type.objects.create(name='ABSS beneficiary')
	# create a test age status
	test_age_status = Age_Status.objects.create(status='Adult')
	# create the person
	test_person = Person.objects.create(
										first_name = 'First',
										middle_names = 'Middle Names',
										last_name = 'Last',
										other_names = 'Nick',
										email_address = 'test@test.com',
										date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
										gender = 'Gender',
										notes = 'test notes',
										default_role = test_role_type,
										pregnant = False,
										due_date = None,
										capture_type = test_capture_type,
										ABSS_type = test_ABSS_type,
										age_status = test_age_status,
										ethnicity = test_ethnicity
										)
	# create the person
	test_person = Person.objects.create(
										first_name = 'Another',
										middle_names = 'Middle Names',
										last_name = 'Person',
										other_names = 'Nnames',
										email_address = 'test@test.com',
										date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
										gender = 'Gender',
										notes = 'test notes',
										default_role = test_role_type,
										pregnant = False,
										due_date = None,
										capture_type = test_capture_type,
										ABSS_type = test_ABSS_type,
										age_status = test_age_status,
										ethnicity = test_ethnicity
										)
   
def set_up_test_event():
	# create an event category
	test_event_category = Event_Category.objects.create(name='test_event_category',description='category desc')
	# create an event type
	test_event_type = Event_Type.objects.create(
												name = 'test_event_type',
												description = 'type desc',
												event_category = test_event_category)
	# create the event
	test_event = Event.objects.create(
										name = 'Test event',
										description = 'Test event description',
										event_type = test_event_type,
										date = datetime.datetime.strptime('2019-01-01','%Y-%m-%d'),
										start_time = datetime.datetime.strptime('10:00','%H:%M'),
										end_time = datetime.datetime.strptime('11:00','%H:%M'),
										location = 'Test location'
									)
	# return the event
	return test_event

class PersonModelTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# call the function to set up standard test data
		set_up_test_people()

	def setUp(self):
		pass

	def test_str_for_person(self):
		# test that the str method for person returns all names, including other_names and prior names
		# get the person
		person = Person.objects.get(first_name='First')
		# check the str method
		self.assertEqual('First Last, also known as Nick', str(person))

	def test_full_name_for_person(self):
		# test that the full name method for person returns first name, middle name and last names separated by spaces
		# get the person
		person = Person.objects.get(first_name='First')
		# check the str method
		self.assertEqual('First Last', person.full_name())

	def test_names_search_first(self):
		# test that the search on each type of name works
		# start with first name
		results = Person.search(names='First')
		# check that we only got one result
		self.assertEqual(results.count(),1)
		# check that we got a result
		self.assertEqual(results.first().first_name,'First')

	def test_names_search_last(self):
		# test that the search on each type of name works
		# start with first name
		results = Person.search(names='Last')
		# check that we only got one result
		self.assertEqual(results.count(),1)
		# check that we got a result
		self.assertEqual(results.first().first_name,'First')

	def test_names_search_nick(self):
		# test that the search on each type of name works
		# start with first name
		results = Person.search(names='Nick')
		# check that we only got one result
		self.assertEqual(results.count(),1)
		# check that we got a result
		self.assertEqual(results.first().first_name,'First')

	def test_try_to_get_success(self):
		# get the person
		person = Person.objects.get(first_name='First')
		# test whether the try to get function works
		self.assertEqual(Person.try_to_get(first_name='First'),person)

	def test_try_to_get_failure(self):
		# test whether the try to get function works
		self.assertEqual(Person.try_to_get(first_name='Nonexistent'),False)

	def test_try_to_get_just_one_success(self):
		# get the person
		person = Person.objects.get(first_name='First')
		# test whether the try to get function works
		result, message = Person.try_to_get_just_one(first_name='First')
		# check that we got the right results
		self.assertEqual(result,person)
		self.assertEqual(message,'matching Person record exists')

	def test_try_to_get_just_one_failure_none(self):
		# test whether the try to get function works
		result, message = Person.try_to_get_just_one(first_name='Nonexistent')
		# check that we got the right results
		self.assertFalse(result)
		self.assertEqual(message,'matching Person record does not exist')

	def test_try_to_get_just_one_failure_multiple(self):
		# test whether the try to get function works
		result, message = Person.try_to_get_just_one(other_names__icontains='N')
		# check that we got the right results
		self.assertFalse(result)
		self.assertEqual(message,'multiple matching Person records exist')


class EventRegistrationTest(TestCase):
	@classmethod
	def setUpTestData(cls):
		# set up the standard test person
		set_up_test_people()
		# get the person 
		test_person = Person.objects.get(first_name='First')
		# and the event
		test_event = set_up_test_event()
		# and get the role type
		test_role_type = Role_Type.objects.get(role_type_name='test_role')
		# create the event registration
		test_event_registration = Event_Registration.objects.create(
																	person = test_person,
																	event = test_event,
																	role_type = test_role_type,
																	registered = True,
																	participated = True,
																	apologies = True)

	def setUp(self):
		pass

	def test_str_for_event_registration_registered_and_participated_and_apologies(self):
		# test that the str method for event registration returns the right string and details
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# check the str method
		self.assertEqual(
			'First Last: test_role at Test event on Jan 01 2019 (registered, participated, apologies sent)',
			str(event_registration)
						)

	def test_str_for_event_registration_registered_did_not_participate_and_apologies(self):
		# test that the str method for event registration returns the right string and details
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.participated = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual(
			'First Last: test_role at Test event on Jan 01 2019 (registered, apologies sent)',
			str(event_registration)
						)

	def test_str_for_event_registration_did_not_register_did_not_participate_and_apologies(self):
		# test that the str method for event registration returns the right string and details
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.participated = False
		event_registration.registered = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual(
			'First Last: test_role at Test event on Jan 01 2019 (apologies sent)',
			str(event_registration)
						)

	def test_str_for_event_registration_did_not_register_but_participated_and_apologies(self):
		# test that the str method for event registration returns the right string and details
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.registered = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual(
			'First Last: test_role at Test event on Jan 01 2019 (participated, apologies sent)',
			str(event_registration)
						)

	def test_str_for_event_registration_registered_and_participated_no_apologies(self):
		# test that the str method for event registration returns the right string and details
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.apologies = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual(
			'First Last: test_role at Test event on Jan 01 2019 (registered, participated)',
			str(event_registration)
						)

	def test_registered_status_true_for_event_registration(self):
		# test that the registered status method for person returns the right string when registered = True
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.registered = True
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual('registered',event_registration.registered_status())

	def test_registered_status_false_for_event_registration(self):
		# test that the registered status method for person returns the right string when registered = False
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.registered = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual('not registered',event_registration.registered_status())

	def test_participated_status_true_for_event_registration(self):
		# test that the registered status method for person returns the right string when registered = True
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.participated = True
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual('participated',event_registration.participated_status())

	def test_participated_status_false_for_event_registration(self):
		# test that the registered status method for person returns the right string when registered = False
		# get the person
		event_registration = Event_Registration.objects.get(person=Person.objects.get(first_name='First'))
		# update the object
		event_registration.participated = False
		# save the object
		event_registration.save()
		# check the str method
		self.assertEqual('did not participate',event_registration.participated_status())
