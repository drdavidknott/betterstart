from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Address, Residence, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type
import os
import csv
from django.contrib.auth.decorators import login_required
from .forms import AddPersonForm, ProfileForm, RelationshipSearchForm, AddRelationshipForm, \
					AddRelationshipToExistingPersonForm, EditExistingRelationshipsForm, \
					AddAddressForm, AddressSearchForm, AddEventForm
from .utilities import get_page_list, make_banner
from django.contrib import messages
from django.urls import reverse
import datetime

def index(request):
	# get the template
	index_template = loader.get_template('people/index.html')
	# return the HttpResponse
	return HttpResponse(index_template.render(context=None, request=request))

@login_required
def dataload(request):
	# get the template
	index_template = loader.get_template('people/dataload.html')
	# create a list of messages
	messages = []
	# get the directory
	directory = os.path.dirname(__file__)
	# load simple reference data
	messages = messages + load_reference_data(directory)
	# load relationship types
	messages = messages + load_relationship_types(directory)
	# load event categories
	messages = messages + load_event_categories(directory)
	# load event types
	messages = messages + load_event_types(directory)
	# load areas
	messages = messages + load_areas(directory)
	# load wards
	messages = messages + load_wards(directory)
	# load post codes and get the results as messages
	messages = messages + load_post_code(directory)
	# add the messages to the context
	context = {'load_messages' : messages}
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

# DATA LOAD FUNCTIONS
# A set of functions which read csv files and use them to load data

def load_event_categories(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	event_categories_file_name = os.path.join(directory, 'data/event_categories.csv')
	# open the event_categories file
	event_categories_file = open(event_categories_file_name,'r')
	# read it as a csv file
	event_categories = csv.DictReader(event_categories_file)
	# go through the csv file and process it
	for event_category_record in event_categories:
		# get the event category name
		name = event_category_record['name']
		# create a label for use in messages
		event_category_label = 'Event Category: ' + name
		# check whether the event_category already exists
		try:
			event_category = Event_Category.objects.get(name=name)
			# set the message to show that it exists
			messages.append(event_category_label + ' not created: event_category already exists.')
		except (Event_Category.DoesNotExist):
			# the event_category does not exist, so create it
			event_category = Event_Category(
											name=name,
											description=event_category_record['description']
											)
			# save the event_category
			event_category.save()
			# set the message
			messages.append(event_category_label + ' created.')
	# return the messages
	return messages

def load_event_types(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	event_types_file_name = os.path.join(directory, 'data/event_types.csv')
	# open the areas file
	event_types_file = open(event_types_file_name,'r')
	# read it as a csv file
	event_type_rows = csv.DictReader(event_types_file)
	# go through the csv file and process it
	for event_type_row in event_type_rows:
		# get the category name
		event_category_name = event_type_row['event_category']
		# get the event_type name
		event_type_name = event_type_row['name']
		# create a label for use in messages
		event_type_label = 'Event type: ' + event_type_name + ' (Category: ' + event_category_name + ')'
		# check whether the area exists
		try:
			event_category = Event_Category.objects.get(name=event_category_name)
			# now try to find the event_type
			try:
				event_type = Event_Type.objects.get(name=event_type_name)
				# set the message to show that it exists
				messages.append(event_type_label + ' not created: event type already exists.')
			except (Event_Type.DoesNotExist):
				# create the event_type
				event_type = Event_Type(
										name = event_type_name,
										description = event_type_row['description'],
										event_category = event_category
							)
				# save the event_type
				event_type.save()
				# and set the message
				messages.append(event_type_label + ' created.')
		except (Event_Category.DoesNotExist):
			# the area does not exist, so set an error message
			messages.append(event_type_label + ' not created: event category does not exist.')
	# return the messages
	return messages

def load_areas(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	areas_file_name = os.path.join(directory, 'data/areas.csv')
	# open the areas file
	areas_file = open(areas_file_name,'r')
	# read it as a csv file
	areas = csv.DictReader(areas_file)
	# go through the csv file and process it
	for area in areas:
		# get the area name
		area_name = area['area']
		# create a label for use in messages
		area_label = 'Area: ' + area_name
		# check whether the area already exists
		try:
			area = Area.objects.get(area_name=area_name)
			# set the message to show that it exists
			messages.append(area_label + ' not created: area already exists.')
		except (Area.DoesNotExist):
			# the area does not exist, so create it
			area = Area(area_name=area_name)
			# save the area
			area.save()
			# set the message
			messages.append(area_label + ' created.')
	# return the messages
	return messages

def load_wards(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	wards_file_name = os.path.join(directory, 'data/wards.csv')
	# open the areas file
	wards_file = open(wards_file_name,'r')
	# read it as a csv file
	ward_rows = csv.DictReader(wards_file)
	# go through the csv file and process it
	for ward_row in ward_rows:
		# get the area name
		area_name = ward_row['area']
		# get the ward name
		ward_name = ward_row['ward']
		# create a label for use in messages
		ward_label = 'Ward: ' + ward_name + ' (Area: ' + area_name + ')'
		# check whether the area exists
		try:
			area = Area.objects.get(area_name=area_name)
			# now try to find the ward
			try:
				ward = Ward.objects.get(ward_name=ward_name)
				# set the message to show that it exists
				messages.append(ward_label + ' not created: ward already exists.')
			except (Ward.DoesNotExist):
				# create the ward
				ward = Ward(
							ward_name = ward_name,
							area = area
							)
				# save the ward
				ward.save()
				# and set the message
				messages.append(ward_label + ' created.')
		except (Area.DoesNotExist):
			# the area does not exist, so set an error message
			messages.append(ward_label + ' not created: area does not exist.')
	# return the messages
	return messages

def load_post_code(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	postcodes_file_name = os.path.join(directory, 'data/postcodes.csv')
	# open the post code file
	postcodes_file = open(postcodes_file_name,'r')
	# read it as a csv file
	postcode_rows = csv.DictReader(postcodes_file)
	# go through the csv file and process it
	for postcode_row in postcode_rows:
		# get the post code
		post_code_name = postcode_row['postcode']
		# and the ward
		ward_name = postcode_row['ward']
		# create a label for use in messages
		post_code_label = 'Post code: ' + post_code_name + ' (Ward: ' + ward_name + ')'
		# check whether the ward exists
		try:
			ward = Ward.objects.get(ward_name=ward_name)
			# now try to find the post code
			try:
				post_code = Post_Code.objects.get(post_code=post_code_name)
				# set the message to show that it exists
				messages.append(post_code_label + ' not created: postcode already exists.')
			except (Post_Code.DoesNotExist):
				# create the ward
				post_code = Post_Code(
										post_code = post_code_name,
										ward = ward
									)
				# save the ward
				post_code.save()
				# and set the message
				messages.append(post_code_label + ' created.')
		except (Ward.DoesNotExist):
			# the area does not exist, so set an error messaage
			messages.append(post_code_label + ' not created: ward does not exist.')
	# return the messages
	return messages

def load_reference_data(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	data_file_name = os.path.join(directory, 'data/reference_data.csv')
	# open the areas file
	data_file = open(data_file_name,'r')
	# read it as a csv file
	records = csv.DictReader(data_file)
	# go through the csv file and process it
	for record in records:
		# get the data type
		data_type = record['data_type']
		# get the value
		value = record['value']
		# try to create the record, starting with capture type
		if data_type == 'capture_type':
			messages.append(load_capture_type(value))
		# now ethnicity
		elif data_type == 'ethnicity':
			messages.append(load_ethnicity(value))
		# then relationship type
		elif data_type == 'relationship_type':
			messages.append(load_relationship_type(value))
		# then children centres
		elif data_type == 'children_centre':
			messages.append(load_children_centre(value))
		# and finally role type
		elif data_type == 'role_type':
			messages.append(load_role_type(value))
		# and deal with any unknown type
		else:
			# set an error message
			messages = messages + 'Data type: ' + data_type + ' is not recognised.'
	# return the messages
	return messages

def load_capture_type(value):
	# create a label for use in messages
	capture_type_label = 'Capture type: ' + value
	# check whether the capture type already exists
	try:
		capture_type = Capture_Type.objects.get(capture_type_name=value)
		# set the message to show that it exists
		message = capture_type_label + ' not created: capture type already exists.'
	except (Capture_Type.DoesNotExist):
		# the capture type does not exist, so create it
		capture_type = Capture_Type(capture_type_name=value)
		# save the capture type
		capture_type.save()
		# set the message
		message = capture_type_label + ' created.'
	# return the messages
	return message

def load_ethnicity(value):
	# create a label for use in messages
	ethnicity_label = 'Ethnicity: ' + value
	# check whether the capture type already exists
	try:
		ethnicity = Ethnicity.objects.get(description=value)
		# set the message to show that it exists
		message = ethnicity_label + ' not created: ethnicity already exists.'
	except (Ethnicity.DoesNotExist):
		# the capture type does not exist, so create it
		ethnicity = Ethnicity(description=value)
		# save the ethnicity
		ethnicity.save()
		# set the message
		message = ethnicity_label + ' created.'
	# return the messages
	return message

def load_role_type(value):
	# create a label for use in messages
	role_type_label = 'Role type: ' + value
	# check whether the capture type already exists
	try:
		role_type = Role_Type.objects.get(role_type_name=value)
		# set the message to show that it exists
		message = role_type_label + ' not created: role type already exists.'
	except (Role_Type.DoesNotExist):
		# the capture type does not exist, so create it
		role_type = Role_Type(role_type_name=value)
		# save the role type
		role_type.save()
		# set the message
		message = role_type_label + ' created.'
	# return the messages
	return message

def load_children_centre(value):
	# create a label for use in messages
	children_centre_label = 'Children centre: ' + value
	# check whether the capture type already exists
	try:
		children_centre = Children_Centre.objects.get(children_centre_name=value)
		# set the message to show that it exists
		message = children_centre_label + ' not created: children centre already exists.'
	except (Children_Centre.DoesNotExist):
		# the capture type does not exist, so create it
		children_centre = Children_Centre(children_centre_name=value)
		# save the children centre
		children_centre.save()
		# set the message
		message = children_centre_label + ' created.'
	# return the messages
	return message

def load_relationship_types(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	relationship_types_file_name = os.path.join(directory, 'data/relationship_types.csv')
	# open the relationship types file
	relationship_types_file = open(relationship_types_file_name,'r')
	# read it as a csv file
	relationship_type_records = csv.DictReader(relationship_types_file)
	# go through the csv file and process it
	for relationship_type_record in relationship_type_records:
		# get the values
		relationship_type = relationship_type_record['relationship_type']
		relationship_counterpart = relationship_type_record['relationship_counterpart']
		# create a label for use in messages
		relationship_type_label = 'Relationship type: ' + relationship_type
		# check whether the relationship type already exists
		try:
			this_relationship_type = Relationship_Type.objects.get(relationship_type=relationship_type)
			# set the message to show that it exists
			message = relationship_type_label + ' not created: relationship type already exists.'
		# handle the exception (which is what we expect)
		except (Relationship_Type.DoesNotExist):
			# the relationship type does not exist, so create it
			this_relationship_type = Relationship_Type(
														relationship_type=relationship_type,
														relationship_counterpart=relationship_counterpart
														)
			# save the relationship type
			this_relationship_type.save()
			# set the message
			message = relationship_type_label + ' created.'
		# append the message
		messages.append(message)
	# return the messages
	return messages

# DATA ACCESS FUNCTIONS
# A set of functions which carry out simple and complex data access, filtering and updates.
# These functions are kept as simple as possible.

def get_person(person_id):
	# try to get a person using the person id
	try:
		# do the database call
		person = Person.objects.get(pk=person_id)
	# handle the exception
	except Person.DoesNotExist:
		# set the person to false
		person = False
	# return the result
	return person

def get_relationships_to(person):
	# this function gets all the Person objects via the relationship_to relationship from Perso
	# it returns a list of people with realtionship type added
	# create an empty list
	relationships_to = []
	# get the relationships using the foreign key
	relationships = Relationship.objects.filter(relationship_from=person.pk)
	# now go through the list and get the person
	for relationship in relationships:
		# get the person
		person = Person.objects.get(pk=relationship.relationship_to.pk)
		# add the relationship type to the person object
		person.relationship_type = relationship.relationship_type.relationship_type
		# and the key
		person.relationship_type_pk = relationship.relationship_type.pk
		# append the person to the list
		relationships_to.append(person)
	# return the relationships
	return relationships_to

def get_people():
	# get a list of people
	people = Person.objects.order_by('last_name', 'first_name')
	# return the list of people
	return people

def get_people_by_name(first_name,last_name):
	# try to get people with the matching name
	people = Person.objects.filter(first_name=first_name,last_name=last_name)
	# return the people
	return people

def get_people_by_names(first_name,last_name):
	# get all people
	people = Person.objects.all()
	# check whether we have a first name
	if first_name:
		# filter by the name
		people = people.filter(first_name__contains=first_name)
	# check whether we have a last name
	if last_name:
		# filter by the name
		people = people.filter(last_name__contains=last_name)
	# return the list of people
	return people

def get_address(address_id):
	# try to get a address using the address id
	try:
		# do the database call
		address = Address.objects.get(pk=address_id)
	# handle the exception
	except Address.DoesNotExist:
		# set the address to false
		address = False
	# return the result
	return address

def get_addresses_by_number_or_street(house_name_or_number,street):
	# try to get addresses with the matching properties
	addresses = Address.objects.filter(
										house_name_or_number__contains=house_name_or_number,
										street__contains=street)
	# return the people
	return addresses

def get_post_code_by_code(code):
	# try to get a post code using the code
	try:
		# do the database call
		post_code = Post_Code.objects.get(post_code=code)
	# handle the exception
	except Post_Code.DoesNotExist:
		# set the post code to false
		post_code = False
	# return the result
	return post_code

def get_residence(person, address):
	# try to get a residence
	try:
		# do the database query
		residence = Residence.objects.get(
											person=person,
											address=address
											)
	# handle the exception
	except Residence.DoesNotExist:
		# set a false value
		residence = False
	# return the value
	return residence

def get_ethnicity(ethnicity_id):
	# try to get ethnicity
	try:
		ethnicity = Ethnicity.objects.get(pk=ethnicity_id)
	# handle the exception
	except Ethnicity.DoesNotExist:
		# set a false value
		ethnicity = false
	# return the ethnicity
	return ethnicity

def get_relationship_type(relationship_type_id):
	# try to get relationship type
	try:
		relationship_type = Relationship_Type.objects.get(pk=relationship_type_id)
	# handle the exception
	except Relationship_Type.DoesNotExist:
		# set a false value
		relationship_type = False
	# return the relationship_type
	return relationship_type

def get_relationship_type_by_type(relationship_type):
	# try to get relationship type using the name of the relationship type
	try:
		relationship_type = Relationship_Type.objects.get(relationship_type=relationship_type)
	# handle the exception
	except Relationship_Type.DoesNotExist:
		# set a false value
		relationship_type = false
	# return the relationship type
	return relationship_type

def get_event(event_id):
	# try to get an event using the event id
	try:
		# do the database call
		event = Event.objects.get(pk=event_id)
	# handle the exception
	except Event.DoesNotExist:
		# set the address to false
		event = False
	# return the result
	return event

def get_events():
	# get a list of events
	events = Event.objects.order_by('date', 'start_time')
	# return the list of people
	return events

def get_event_type(event_type_id):
	# try to get event type
	try:
		event_type = Event_Type.objects.get(pk=event_type_id)
	# handle the exception
	except Event_Type.DoesNotExist:
		# set a false value
		event_type = False
	# return the event type
	return event_type

def get_event_types():
	# return a list of all the event type objects
	return Event_Type.objects.all()

def get_ethnicities():
	# return a list of all the ethnicity objects
	return Ethnicity.objects.all()

def get_ethnicity_list():
	# return a list containing all of the ethnicity descriptions
	ethnicity_list = []
	# get the ethnicities
	ethnicities = Ethnicity.objects.all()
	# go through them all
	for ethnicity in ethnicities:
		# append to the list
		ethnicity_list.append(ethnicity.description)
	# return the list
	return ethnicity_list

def get_relationship_types():
	# return a list of all the relationship type objects
	return Relationship_Type.objects.all()

def get_relationship(person_from, person_to):
	# try to get a relationship
	try:
		# do the database query
		relationship = Relationship.objects.get(
												relationship_from=person_from.pk,
												relationship_to=person_to.pk
												)
	# handle the exception
	except Relationship.DoesNotExist:
		# set a false value
		relationship = False
	# return the value
	return relationship

def get_relationship_from_and_to(person_from, person_to):
	# get both sides of a relationship
	# start with the from side
	relationship_from = get_relationship(person_from, person_to)
	# and the to side
	relationship_to = get_relationship(person_to, person_from)
	# return the results
	return relationship_from, relationship_to

def create_person(first_name,middle_names,last_name,date_of_birth=None,gender='',ethnicity=1):
	# create a person
	person = Person(
					first_name = first_name,
					middle_names = middle_names,
					last_name = last_name,
					date_of_birth = date_of_birth,
					gender = gender,
					ethnicity = get_ethnicity(ethnicity)
						)
	# save the record
	person.save()
	# and return the person
	return person

def create_address(house_name_or_number,street,town,post_code):
	# create an address
	address = Address(
					house_name_or_number = house_name_or_number,
					street = street,
					town = town,
					post_code = post_code
						)
	# save the record
	address.save()
	# and return the address
	return address

def create_residence(person, address):
	# create a residence
	residence = Residence(
					person = person,
					address = address
							)
	# save the residence
	residence.save()
	# return the residence
	return residence

def create_relationship(person_from, person_to, relationship_type_from):
	# create a symmetrical relationship between two people
	# create a flag
	success = False
	# check whether the relationship already exists
	try:
		# do the database call
		relationship = Relationship.objects.get(relationship_from=person_from,
												relationship_to=person_to)
	# handle the exception
	except Relationship.DoesNotExist:
		# start by getting the other half of the relationship
		relationship_type_to = get_relationship_type_by_type(relationship_type_from.relationship_counterpart)
		# now create the from part of the relationship
		relationship_from = Relationship(
										relationship_from = person_from,
										relationship_to = person_to,
										relationship_type = relationship_type_from)
		# now save it
		relationship_from.save()
		# now create the to part of the relationship
		relationship_to = Relationship(
										relationship_from = person_to,
										relationship_to = person_from,
										relationship_type = relationship_type_to)
		# now save it
		relationship_to.save()
		# set the flag
		success = True
	# that's it!
	return success

def create_event(name, description, date, start_time, end_time, event_type):
	# create an event
	event = Event(
					name = name,
					description = description,
					date = date,
					start_time = start_time,
					end_time = end_time,
					event_type = event_type
						)
	# save the record
	event.save()
	# and return the event
	return event

# BUILD FUNCTIONS
# These are slightly more sophisticated creation functions which do additional work such as looking up values and 
# setting messsages.

def edit_relationship(request, person_from, person_to, relationship_type_id):
	# edit a relationship: this includes deletion of existing relationships and creation of new relationships
	# if we have been passed a relationship type id of zero of False, we just do the deletion
	# set a flag
	success = False
	# check whether we either have a valid relationship type or a zero
	if relationship_type_id:
		# get the relationship type
		relationship_type_from = get_relationship_type(relationship_type_id)
		# if we didn't get one, set an error message and crash out
		if not relationship_type_from:
			# set the messages
			messages.error(request, 'Relationship type ' + str(relationship_type_id) + ' does not exist.')
			# crash out
			return success
	# see whether we have an existing relationship
	relationship_from, relationship_to = get_relationship_from_and_to(person_from, person_to)
	# if there is an existing relationship, check whether it is different from the one we have been passed
	if relationship_from:
		# check whether the relationship has changed
		if (relationship_from.relationship_type.pk != relationship_type_id):
			# delete the existing relationships
			relationship_from.delete()
			relationship_to.delete()
			# set a message
			messages.success(request,'Relationship between ' + person_from.name() + ' and ' 
								+ person_to.name() + ' deleted.')
		# if nothing has changed, we are done, so we can return success
		else:
			# set the flag
			success = True
			# return the value
			return success
	# if we have a valid realtionship type, create the relationship
	if relationship_type_id:
		# try to create the relationship
		if create_relationship(
							 person_from = person_from,
							 person_to = person_to,
							 relationship_type_from = relationship_type_from
							):
			# set the success message
			messages.success(request,
				'Relationship created: ' + str(person_from) + 
				' is the ' + relationship_type_from.relationship_type + ' of ' + str(person_to))
			# and the other success message
			messages.success(request,
				'Relationship created: ' + str(person_to) + 
				' is the ' + relationship_type_from.relationship_counterpart + ' of ' + str(person_from))
			# set the success flag
			success = True
		# otherwise set the failure message
		else:
			# set the message
			messages.error(request, 'Relationship could not be created.')
	# return the result
	return success

def build_residence(request, person, address):
	# attempt to create a new residence record, checking first that the residence does not exist
	residence = get_residence(person,address)
	# check whether we got a residence or not
	if not residence:
		# create the residence
		residence = create_residence(person,address)
		# set the success message
		messages.success(request,'New residence (' + str(residence) + ') created.')
	# otherwise set a warning message
	else:
		# set the warning that the residence already exists
		messages.error(request,'Residence (' + str(residence) + ') already exists.')
	# return the residence
	return residence

def remove_residence(request, person, address):
	# attempt to remove a residence record, checking first that the residence exists
	residence = get_residence(person,address)
	# check whether we got the residence or not
	if residence:
		# preserve the name
		residence_name = str(residence)
		# delete the residence
		residence.delete()
		# set the success message
		messages.success(request,'Residence (' + residence_name + ') deleted.')
	# otherwise set a warning message
	else:
		# set the warning that the residence already exists
		messages.error(request,'Residence does not exist.')
	# return with no parameters
	return

def build_event(request, name, description, date, start_time, end_time, event_type_id):
	# get the event type
	event_type = get_event_type(event_type_id)
	# if we got an event type, create the event
	if event_type:
		# create the event
		event = create_event(
								name = name,
								description = description,
								date = date,
								start_time = start_time,
								end_time = end_time,
								event_type = event_type
							)
		# set a message
		messages.success(request, 'New event (' + str(event) + ') created.')
	# otherwise set a message
	else:
		# set the failed creation message
		messages.error(request, 'Event (' + name + ') could not be created: event type does not exist.')
	# return the event
	return event

def remove_residence(request, person, address):
	# attempt to remove a residence record, checking first that the residence exists
	residence = get_residence(person,address)
	# check whether we got the residence or not
	if residence:
		# preserve the name
		residence_name = str(residence)
		# delete the residence
		residence.delete()
		# set the success message
		messages.success(request,'Residence (' + residence_name + ') deleted.')
	# otherwise set a warning message
	else:
		# set the warning that the residence already exists
		messages.error(request,'Residence does not exist.')
	# return with no parameters
	return

# UTILITY FUNCTIONS
# A set of functions which perform basic utility tasks such as string handling and list editing

# function to extract an id number from the end of an underscore delimited string
def extract_id(field_name):
	# build a list from the string
	name_elements = field_name.split('_')
	# now return the final element
	return name_elements[-1]

def remove_existing_relationships(person_from, people):
	# this function takes a person and a list of people, and returns a list of only those people who do
	# not have an existing relationship
	# create an empty list
	people_without_existing_relationships = []
	# now got through the list
	for person_to in people:
		# check that we haven't got the person themselves
		if person_to != person_from:
			# try to get a relationship
			try:
				# do the database query
				relationship = Relationship.objects.get(
														relationship_from=person_from.pk,
														relationship_to=person_to.pk
														)
			# handle the exception
			except Relationship.DoesNotExist:
				# add the person to the list
				people_without_existing_relationships.append(person_to)
	# return the list
	return people_without_existing_relationships

def remove_existing_addresses(person, addresses):
	# this function takes a person and a list of addresses, and returns a list of only those addresses where
	# the person does not have an existing residence
	# create an empty list
	addresses_without_existing_residences = []
	# now got through the list
	for address in addresses:
		# attempt to get the residence
		if not get_residence(person,address):
			# add the address to the list
			addresses_without_existing_residences.append(address)
	# return the list
	return addresses_without_existing_residences

# VIEW FUNCTIONS
# A set of functions which implement the functionality of the site and serve pages.

@login_required
def people(request):
	# get the list of people
	people = get_people()
	# get the template
	people_template = loader.get_template('people/people.html')
	# set the context
	context = {
				'people' : people
				}
	# return the HttpResponse
	return HttpResponse(people_template.render(context=context, request=request))

@login_required
def addperson(request):
	# create a blank list of matching people
	matching_people = []
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		addpersonform = AddPersonForm(request.POST)
		# check whether the form is valid
		if addpersonform.is_valid():
			# get the names
			first_name = addpersonform.cleaned_data['first_name']
			middle_names = addpersonform.cleaned_data['middle_names']
			last_name = addpersonform.cleaned_data['last_name']
			# see whether this is a confirmation action
			# get the action from the request
			action = request.POST.get('action','')
			# see if there is an action
			if action == 'CONFIRM':
				# create the person
				person = create_person(first_name,middle_names,last_name)
				# set a success message
				messages.success(request,
									'Another ' + str(person) + ' created.'
 									)
				# go to the profile of the person
				return redirect('/person/' + str(person.pk))
		# otherwise see whether the person matches an existing person by name
		matching_people = get_people_by_name(first_name,last_name)
		# if there aren't any matching people, also create the person
		if not matching_people:
			# create the person
			person = create_person(first_name,middle_names,last_name)
			# set a success message
			messages.success(request,
								str(person) + ' created.'
 								)
			# go to the profile of the person
			return redirect('/person/' + str(person.pk))
	# otherwise create a fresh form
	else:
		# create the fresh form
		addpersonform = AddPersonForm()
	# get the template
	addperson_template = loader.get_template('people/addperson.html')
	# set the context
	context = {
				'addpersonform' : addpersonform,
				'matching_people' : matching_people
				}
	# return the HttpResponse
	return HttpResponse(addperson_template.render(context=context, request=request))

@login_required
def person(request, person_id=0):
	# load the template
	person_template = loader.get_template('people/person.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get the relationships for the person
	relationships_to = get_relationships_to(person)
	# set the context from the person based on person id
	context = {
				'person' : person,
				'relationships_to' : relationships_to,
				'addresses' : person.addresses.all()
				}
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def profile(request, person_id=0):
	# try to get the person
	person = get_person(person_id)
	# if there isn't a person, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# check whether this is a post
	if request.method == 'POST':
		# create a form
		profileform = ProfileForm(request.POST, ethnicities=get_ethnicities())
		# check whether the entry is valid
		if profileform.is_valid():
			# update the person record
			person.first_name = profileform.cleaned_data['first_name']
			person.middle_names = profileform.cleaned_data['middle_names']
			person.last_name = profileform.cleaned_data['last_name']
			person.email_address = profileform.cleaned_data['email_address']
			person.date_of_birth = profileform.cleaned_data['date_of_birth']
			person.gender = profileform.cleaned_data['gender']
			person.english_is_second_language = profileform.cleaned_data['english_is_second_language']
			# attempt to get the ethnicity
			ethnicity = get_ethnicity(profileform.cleaned_data['ethnicity'])
			# set the value for the person
			if ethnicity:
				# set the value
				person.ethnicity = ethnicity
			# otherwise crash out to a banner
			else:
				# set the banner
				return make_banner(request, 'Ethnicity does not exist.')
			# save the record
			person.save()
			# set a success message
			messages.success(request, str(person) + ' profile updated.')
			# send the user back to the main person page
			return redirect('/person/' + str(person.pk))
	else:
		# there is a person, so build a dictionary of initial values we want to set
		profile_dict = {
						'first_name' : person.first_name,
						'middle_names' : person.middle_names,
						'last_name' : person.last_name,
						'email_address' : person.email_address,
						'date_of_birth' : person.date_of_birth,
						'ethnicity' : person.ethnicity.pk,
						'gender' : person.gender,
						'english_is_second_language' : person.english_is_second_language
						}
		# create the form
		profileform = ProfileForm(profile_dict, ethnicities=get_ethnicities())
	# load the template
	profile_template = loader.get_template('people/profile.html')
	# set the context
	context = {
				'profileform' : profileform,
				'person' : person,
				}
	# return the response
	return HttpResponse(profile_template.render(context, request))

@login_required
def add_relationship(request,person_id=0):
	# this is one of the most complex views on the site, which allows the user to search for people and to 
	# add relationships to both existing and new people
	# initalise the forms which we might not need
	addrelationshipform = ''
	addrelationshiptoexistingpersonform = ''
	editexistingrelationshipsform = ''
	# load the template
	person_template = loader.get_template('people/add_relationship.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# get existing relationships
	relationships_to = get_relationships_to(person)
	# get relationship types
	relationship_types = get_relationship_types()
	# set the search results
	search_results = []
	# set a blank search_error
	search_error = ''
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		relationshipsearchform = RelationshipSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			relationshipsearchform.is_valid()
			# get the names
			first_name = relationshipsearchform.cleaned_data['first_name']
			last_name = relationshipsearchform.cleaned_data['last_name']
			# if neither name is blank, do the search
			if first_name or last_name:
				# conduct a search
				people = get_people_by_names(first_name,last_name)
				# remove the people who already have a relationship
				search_results = remove_existing_relationships(person, people)
				# if there are search results, create a form to create relationships from the search results
				if search_results:
					# create the form
					addrelationshiptoexistingpersonform = AddRelationshipToExistingPersonForm(
															request.POST,
															relationship_types=relationship_types,
															people=search_results
															)
					# go through the search results and add a field name to the object
					for result in search_results:
						# add the field
						result.field_name = 'relationship_type_' + str(result.pk)
				# create a form to add the relationship
				addrelationshipform = AddRelationshipForm(request.POST,relationship_types=relationship_types)
			# otherwise we have a blank form
			else:
				# set the message
				search_error = 'First name or last name must be entered.'
		# check whether we have been asked to edit relationships
		# note that we get this action for editing existing relationships and creating new relationships
		elif request.POST['action'] == 'editrelationships':
			# go through the post
			for field_name, field_value in request.POST.items():
				# check whether this is a relevant field
				if field_name.startswith('relationship_type'):
					# try to find a person using the id at the end of the field name
					person_to = get_person(int(extract_id(field_name)))
					# if we got a person, edit the relationship
					if person_to:
						# edit the relationship
						edit_relationship(request, person, person_to, int(field_value))
		# check whether we have been asked to add a relationship to a new person
		elif request.POST['action'] == 'addrelationshiptonewperson':
			# create the form
			addrelationshipform = AddRelationshipForm(request.POST,relationship_types=relationship_types)
			# check whether the form is valid
			if addrelationshipform.is_valid():
				# we now need to create the person
				person_to = create_person(
											first_name = addrelationshipform.cleaned_data['first_name'],
											middle_names = addrelationshipform.cleaned_data['middle_names'],
											last_name = addrelationshipform.cleaned_data['last_name'],
											date_of_birth = addrelationshipform.cleaned_data['date_of_birth'],
											gender = addrelationshipform.cleaned_data['gender']
											)
				# set a message to say that we have create a new person
				messages.success(request, str(person) + ' created.')
				# now create the relationship
				edit_relationship(request,person, person_to, addrelationshipform.cleaned_data['relationship_type'])
				# clear the add relationship form so that it doesn't display
				addrelationshipform = ''
	# otherwise we didn't get a post
	else:
		# create a blank form
		relationshipsearchform = RelationshipSearchForm()
	# update the existing relationships: there may be new ones
	relationships_to = get_relationships_to(person)
	# if there are existing relationships, create an edit form
	if relationships_to:
		# build the form
		editexistingrelationshipsform = EditExistingRelationshipsForm(
																		relationships=relationships_to,
																		relationship_types=get_relationship_types())
		# and go through the relationships, adding the name of the select field and the hidden field
		for relationship_to in relationships_to:
			# set the values
			relationship_to.select_name = 'relationship_type_' + str(relationship_to.pk)
			relationship_to.hidden_name = 'original_relationship_type_' + str(relationship_to.pk)
	# set the context from the person based on person id
	context = {
				'relationshipsearchform' : relationshipsearchform,
				'addrelationshipform' : addrelationshipform,
				'addrelationshiptoexistingpersonform' : addrelationshiptoexistingpersonform,
				'editexistingrelationshipsform' : editexistingrelationshipsform,
				'search_results' : search_results,
				'search_error' : search_error,
				'person' : person,
				'relationships_to' : relationships_to
				}
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def add_address(request,person_id=0):
	# this view is used to add an address to a person, either by performing a search and adding an address which 
	# has been found, or by adding a new address
	# load the template
	person_template = loader.get_template('people/add_address.html')
	# get the person
	person = get_person(person_id)
	# if the person doesn't exist, crash to a banner
	if not person:
		return make_banner(request, 'Person does not exist.')
	# initialise blank forms in case we don't need them (but need to pass them in the context)
	addaddressform = ''
	# get existing addresses
	addresses = person.addresses.all()
	# set the search results
	search_results = []
	# set a blank search_error
	search_error = ''
	# check whether this is a post
	if request.method == 'POST':
		# create a search form
		addresssearchform = AddressSearchForm(request.POST)
		# check what type of submission we got
		if request.POST['action'] == 'search':
			# validate the form
			addresssearchform.is_valid()
			# get the house name or number and street name
			house_name_or_number = addresssearchform.cleaned_data['house_name_or_number']
			street = addresssearchform.cleaned_data['street']
			# if neither field is blank, do the search
			if house_name_or_number or street:
				# conduct a search
				search_addresses = get_addresses_by_number_or_street(house_name_or_number,street)
				# remove the people who already have a relationship
				search_results = remove_existing_addresses(person, search_addresses)
				# if there are search results, create a form to create relationships from the search results
				addaddressform = AddAddressForm(request.POST)
			# otherwise we have a blank form
			else:
				# set the message
				search_error = 'Street name or house name or number must be entered.'
		# check whether we have been asked to add a relationship to a new person
		elif request.POST['action'] == 'addnewaddress':
			# create the form
			addaddressform = AddAddressForm(request.POST)
			# check whether the form is valid
			if addaddressform.is_valid():
				# attempt to get the post code
				post_code = get_post_code_by_code(addaddressform.cleaned_data['post_code'])
				# check whether that was successful
				if post_code:
					# create the address
					address = create_address(
											house_name_or_number = addaddressform.cleaned_data['house_name_or_number'],
											street = addaddressform.cleaned_data['street'],
											town = addaddressform.cleaned_data['town'],
											post_code = post_code
											)
					# set the message
					messages.success(request, 'Address ' + str(address) + ' created.')
					# create a residence
					residence = build_residence(
												request,
												person = person,
												address = address
												)
					# clear the add address form so that it doesn't display
					addaddressform = ''
				# otherwise deal with an invalid post code
				else:
					# set the error message
					addaddressform.add_error('post_code','Invalid post code.')
		# check whether we have been asked to add an existing address
		elif request.POST['action'] == 'addexistingaddress':
			# get the address
			address = get_address(int(request.POST['address_id']))
			# if we got an address, build the residence
			if address:
				# build the residence
				residence = build_residence(
											request,
											person = person,
											address = address
											)
			# otherwise set an error message
			else:
				# set the message
				messages.error('Address does not exist.')
		# check whether we have been asked to remove an existing address
		elif request.POST['action'] == 'removeaddress':
			# get the address
			address = get_address(int(request.POST['address_id']))
			# if we got an address, build the residence
			if address:
				# build the residence
				residence = remove_residence(
											request,
											person = person,
											address = address
											)
			# otherwise set an error message
			else:
				# set the message
				messages.error('Address does not exist.')
	# otherwise we didn't get a post
	else:
		# create a blank form
		addresssearchform = AddressSearchForm()
	# get the addresses: there may be new ones
	addresses = person.addresses.all()
	# set the context from the person based on person id
	context = {
				'addresssearchform' : addresssearchform,
				'addaddressform' : addaddressform,
				'addresses' : addresses,
				'search_results' : search_results,
				'search_error' : search_error,
				'person' : person,
				}
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def addevent(request):
	# get the event types
	event_types = get_event_types()
	# see whether we got a post or not
	if request.method == 'POST':
		# create a form from the POST to retain data and trigger validation
		addeventform = AddEventForm(request.POST, event_types=event_types)
		# check whether the form is valid
		if addeventform.is_valid():
			# create the event
			event = build_event(
								request,
								name = addeventform.cleaned_data['name'],
								description = addeventform.cleaned_data['description'],
								date = addeventform.cleaned_data['date'],
								start_time = addeventform.cleaned_data['start_time'],
								end_time = addeventform.cleaned_data['end_time'],
								event_type_id = addeventform.cleaned_data['event_type']
								)
			# if we were successful, clear the form
			if event:
				# create a fresh form
				addeventform = AddEventForm(event_types=event_types)
	# otherwise create a fresh form
	else:
		# create the fresh form
		addeventform = AddEventForm(event_types=event_types)
	# get the template
	addevent_template = loader.get_template('people/addevent.html')
	# set the context
	context = {
				'addeventform' : addeventform,
				}
	# return the HttpResponse
	return HttpResponse(addevent_template.render(context=context, request=request))

@login_required
def events(request):
	# get the list of events
	events = get_events()
	# get the template
	events_template = loader.get_template('people/events.html')
	# set the context
	context = {
				'events' : events
				}
	# return the HttpResponse
	return HttpResponse(events_template.render(context=context, request=request))