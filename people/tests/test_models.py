from django.test import TestCase
from people.models import Person, Role_Type, Ethnicity, Capture_Type, Event, Event_Type, Event_Category, \
							Event_Registration
import datetime

def set_up_test_person():
    # create the role type that our test person will belong to
    test_role_type = Role_Type.objects.create(role_type_name='test_role')
    # and the ethnicity
    test_ethnicity = Ethnicity.objects.create(description='test_ethnicity')
    # and the capture type
    test_capture_type = Capture_Type.objects.create(capture_type_name='test_capture_type')
    # create the person
    test_person = Person.objects.create(
									    first_name = 'First',
										middle_names = 'Middle Names',
										last_name = 'Last',
										email_address = 'test@test.com',
										date_of_birth = datetime.datetime.strptime('2000-01-01','%Y-%m-%d'),
										gender = 'Gender',
										notes = 'test notes',
										default_role = test_role_type,
										english_is_second_language = False,
										pregnant = False,
										due_date = None
    									)
    # return the person
    return test_person
   
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
    	set_up_test_person()

    def setUp(self):
        pass

    def test_str_for_person(self):
        # test that the str method for person returns first name and last name separated by a space
        # get the person
        person = Person.objects.get(id=1)
        # check the str method
        self.assertEqual('First Last', str(person))

    def test_full_name_for_person(self):
        # test that the full name method for person returns first name, middle name and last names separated by spaces
        # get the person
        person = Person.objects.get(id=1)
        # check the str method
        self.assertEqual('First Middle Names Last', person.full_name())

class EventRegistrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # set up the standard test person
        test_person = set_up_test_person()
        # and the event
        test_event = set_up_test_event()
        # and get the role type
        test_role_type = Role_Type.objects.get(id=1)
        # create the event registration
        test_event_registration = Event_Registration.objects.create(
        															person = test_person,
        															event = test_event,
        															role_type = test_role_type,
        															registered = True,
        															participated = True)

    def setUp(self):
        pass

    def test_str_for_event_registration_registered_and_participated(self):
        # test that the str method for event registration returns the right string and details
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # check the str method
        self.assertEqual(
        	'First Last: test_role at Test event on 01/01/2019 (registered and participated)',
        	str(event_registration)
        				)

    def test_str_for_event_registration_registered_did_not_participate(self):
        # test that the str method for event registration returns the right string and details
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.participated = False
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual(
        	'First Last: test_role at Test event on 01/01/2019 (registered and did not participate)',
        	str(event_registration)
        				)

    def test_str_for_event_registration_did_not_register_did_not_participate(self):
        # test that the str method for event registration returns the right string and details
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.participated = False
        event_registration.registered = False
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual(
        	'First Last: test_role at Test event on 01/01/2019 (not registered and did not participate)',
        	str(event_registration)
        				)

    def test_str_for_event_registration_did_not_register_but_participated(self):
        # test that the str method for event registration returns the right string and details
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.registered = False
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual(
        	'First Last: test_role at Test event on 01/01/2019 (not registered and participated)',
        	str(event_registration)
        				)

    def test_registered_status_true_for_event_registration(self):
        # test that the registered status method for person returns the right string when registered = True
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.registered = True
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual('registered',event_registration.registered_status())

    def test_registered_status_false_for_event_registration(self):
        # test that the registered status method for person returns the right string when registered = False
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.registered = False
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual('not registered',event_registration.registered_status())

    def test_participated_status_true_for_event_registration(self):
        # test that the registered status method for person returns the right string when registered = True
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.participated = True
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual('participated',event_registration.participated_status())

    def test_participated_status_false_for_event_registration(self):
        # test that the registered status method for person returns the right string when registered = False
        # get the person
        event_registration = Event_Registration.objects.get(id=1)
        # update the object
        event_registration.participated = False
        # save the object
        event_registration.save()
        # check the str method
        self.assertEqual('did not participate',event_registration.participated_status())
