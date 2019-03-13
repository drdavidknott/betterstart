from django.shortcuts import render, HttpResponse, redirect
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Address, Residence, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type
import os
import csv
from django.contrib.auth.decorators import login_required
from .forms import AddPersonForm, ProfileForm
from .utilities import get_page_list, make_banner
from django.contrib import messages
from django.urls import reverse

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
	context = {'messages' : messages}
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

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

def load_relationship_type(value):
	# create a label for use in messages
	relationship_type_label = 'Relationship type: ' + value
	# check whether the capture type already exists
	try:
		relationship_type = Relationship_Type.objects.get(relationship_type=value)
		# set the message to show that it exists
		message = relationship_type_label + ' not created: relationship type already exists.'
	except (Relationship_Type.DoesNotExist):
		# the capture type does not exist, so create it
		relationship_type = Relationship_Type(relationship_type=value)
		# save the relationship type
		relationship_type.save()
		# set the message
		message = relationship_type_label + ' created.'
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

def create_person(first_name,middle_names,last_name):
	# create a person
	person = Person(
					first_name = first_name,
					middle_names = middle_names,
					last_name = last_name
						)
	# save the record
	person.save()
	# and return the person
	return person

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
									'Another ' + first_name + ' ' + last_name + ' created.'
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
								first_name + ' ' + last_name + ' created.'
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
def person(request, person_id):
	# load the template
	person_template = loader.get_template('people/person.html')
	# set the context from the person based on person id
	context = {
				'person' : get_person(person_id)
				}
	# return the response
	return HttpResponse(person_template.render(context=context, request=request))

@login_required
def profile(request, person_id):
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
			messages.success(request, person.first_name + ' ' + person.last_name + ' profile updated.')
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
						'ethnicity' : person.ethnicity.pk
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



