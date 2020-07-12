from django.db import models
from .django_extensions import DataAccessMixin
from .utilities import extract_id, add_description
from datetime import datetime, date, timedelta
from django.db.models import Sum
from .utilities import get_period_dates
import collections
import random, string
from django.contrib.auth.models import User
from django.utils import timezone
import pygal
import calendar
from dateutil.relativedelta import relativedelta
from inspect import ismethod
from jsignature.fields import JSignatureField
from jsignature.utils import draw_signature
import json
import base64
from PIL import Image
from io import BytesIO
from django.urls import reverse, resolve

# function to derive a class from a string
def class_from_str(class_str):
	# this function takes the name of a class in a string and returns the class, if it exists
	return globals()[class_str] if class_str in globals() else False

# function to derive a class from a set string: i.e. a django relationship manager ending in _set
def class_name_from_set_str(set_str):
	# format the str
	class_str = set_str.replace('_set','')
	class_name = '_'.join([word.capitalize() for word in class_str.split('_')])
	# return the class if it is valid
	return class_name

# function to check whether a model contains a field
def has_field(model,field_name):
	# this function takes a model Class and the name of a field, and uses the _meta API to check whether the 
	# field exists on the model, returning True if it does and False if it doesn't
	try:
		model._meta.get_field(field_name)
		return True
	except models.FieldDoesNotExist:
		return False

# Family model: represents a family.
# Has a many to many relationship with Person
class Family(DataAccessMixin,models.Model):
	description = models.CharField(max_length=50)
	# define the function that will return the family description as the object reference
	def __str__(self):
		return self.description
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'families'

# Ethnicity model: represents the list of valid ethnicities.
# Has a one to many relationship with Person
class Ethnicity(DataAccessMixin,models.Model):
	description = models.CharField(max_length=50)
	# define the function that will return the ethnicity name as the object reference
	def __str__(self):
		return self.description
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'ethnicities'

# Role_Type model: represents different types of role that a person can play, including staff, volunteer, parent, child ec.
# This is reference data.
class Role_Type(DataAccessMixin,models.Model):
	role_type_name = models.CharField(max_length=50)
	use_for_events = models.BooleanField(default=False)
	use_for_people = models.BooleanField(default=False)
	trained = models.BooleanField(default=False)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.role_type_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'role types'

# Relationship_Type model: represents different types of relationship
# This is reference data.
class Relationship_Type(DataAccessMixin,models.Model):
	relationship_type = models.CharField(max_length=50)
	relationship_counterpart = models.CharField(max_length=50)
	use_for_invitations  = models.BooleanField(default=False)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.relationship_type
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'relationship types'

# ABSS type model: represents different types of relationship that a person can have with ABSS
# This is reference data.
class ABSS_Type(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	membership_number_required = models.BooleanField(default=False)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'ABSS types'

# Age status type model: represents the person's status dependent on age (adult or child)
# This is reference data.
class Age_Status(DataAccessMixin,models.Model):
	status = models.CharField(max_length=50)
	role_types = models.ManyToManyField(Role_Type)
	relationship_types = models.ManyToManyField(Relationship_Type)
	default_role_type = models.ForeignKey(Role_Type,
											blank=True,
											null=True,
											on_delete=models.SET_NULL,
											related_name='age_status_default')
	default_role_type_only = models.BooleanField(default=False)
	can_be_parent_champion = models.BooleanField(default=False)
	can_be_pregnant = models.BooleanField(default=False)
	can_have_contact_details = models.BooleanField(default=False)
	maximum_age = models.IntegerField(default=999)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.status
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'Age statuses'

# Capture Type model: represents the way in which the person's details were captured
class Capture_Type(DataAccessMixin,models.Model):
	capture_type_name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.capture_type_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'capture types'

# Children Centre model: represents Children Centres
# This is reference data.
class Children_Centre(DataAccessMixin,models.Model):
	children_centre_name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.children_centre_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'children centres'

# Area model: represents valid areeas (which contain wards)
class Area(DataAccessMixin,models.Model):
	area_name = models.CharField(max_length=50)
	use_for_events = models.BooleanField(default=False)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.area_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'areas'

# Wards model: represents valid wards (which contain post codes)
class Ward(DataAccessMixin,models.Model):
	ward_name = models.CharField(max_length=50)
	area = models.ForeignKey(Area, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.ward_name + ' (' + self.area.area_name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'wards'

# Post Code model: represents valid post codes
class Post_Code(DataAccessMixin,models.Model):
	post_code = models.CharField(max_length=10)
	ward = models.ForeignKey(Ward, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.post_code + ' (' + self.ward.ward_name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'post codes'
		ordering = ('post_code',)

# Street model: represents valid streets aligned to post codes
class Street(DataAccessMixin,models.Model):
	name = models.CharField(max_length=100)
	post_code = models.ForeignKey(Post_Code, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.name + ' (' + self.post_code.post_code + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'streets'

# Venue Type model: represents the list of types of venues.
# Has a one to many relationship with Venue
class Venue_Type(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	# define the function that will return the venue type name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'venue types'

# Venue model: represents the list of venues in which events can take place.
# Has a many to one relationship with venue type.
# Has a one to many relationship with venue.
class Venue(DataAccessMixin,models.Model):
	name = models.CharField(max_length=100)
	venue_type = models.ForeignKey(Venue_Type, on_delete=models.CASCADE)
	building_name_or_number = models.CharField(max_length=50)
	street = models.ForeignKey(Street, blank=True, null=True, on_delete=models.SET_NULL)
	contact_name = models.CharField(max_length=100, default='', null=True)
	phone = models.CharField(max_length=50, default='', null=True)
	mobile_phone = models.CharField(max_length=50, default='', null=True)
	email_address = models.CharField(max_length=50, default='', null=True)
	website = models.CharField(max_length=100, default='', null=True)
	price = models.CharField(max_length=100, default='', null=True)
	facilities = models.CharField(max_length=100, default='', null=True)
	opening_hours = models.CharField(max_length=100, default='', null=True)
	notes = models.TextField(max_length=1500, default='', blank=True)

	# define the function that will return the venue name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'venues'

# Event Type model: represents categories of event types.
# This is reference data
class Event_Category(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=500)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'event categories'

# Event Type model: represents types of events.
# Types of events are further grouped into categories.
# This is reference data
class Event_Type(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=500)
	event_category = models.ForeignKey(Event_Category, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the event name and the owning category as the object reference
	def __str__(self):
		return self.name + ' (' + str(self.event_category.name) + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'event types'

# Event model: represents events which people register for and attend
class Event(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=1500)
	event_type = models.ForeignKey(Event_Type, default=1, on_delete=models.SET_DEFAULT)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	location = models.CharField(max_length=100)
	ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.SET_NULL)
	areas = models.ManyToManyField(Area)
	venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL)
	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name + ' on '  + self.date.strftime('%b %d %Y') + \
				' (' + self.event_type.name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'events'
		ordering = ['-date']
	# define a function to return the areas as a comma separated string
	def get_areas(self):
		# set the string to blank
		areas = ''
		# go through the areas
		for area in self.areas.all():
			# if the string already has a value, add a comma
			if areas:
				# add a comma
				areas += ', '
			# and add the name
			areas += area.area_name
		# return the result
		return areas
	# define a function to return the duration as a timedelta object
	def duration(self):
		# define the empty timedelta
		duration = timedelta()
		# check that we have both a start time and end time
		if self.start_time and self.end_time:
			# set the duration
			duration = (
						datetime.combine(date.min, self.end_time) 
						- datetime.combine(date.min, self.start_time)
						)
		# and return the results
		return duration
	# define a function to return a string containing the month and year of the event
	def month_and_year(self):
		return self.date.strftime('%Y %m %B')
	# define a set of functions to return counts based on registration, participation and apologies
	def registered_count(self):
		return self.event_registration_set.filter(registered=True).count()
	def apologies_count(self):
		return self.event_registration_set.filter(apologies=True).count()
	def participated_count(self):
		return self.event_registration_set.filter(participated=True).count()
	# define a function to return the total number of hours participated for this event
	def participation_hours(self):
		participation = self.event_registration_set.filter(participated=True).count()
		participation_seconds = self.duration().seconds * participation
		participation_hours = participation_seconds / 3600 
		return participation_hours

# Question model: represents questions
class Question(DataAccessMixin,models.Model):
	question_text = models.CharField(max_length=150)
	notes = models.BooleanField(default=False)
	notes_label = models.CharField(max_length=30, default='Notes')
	use_for_invitations = models.BooleanField(default=False)
	order = models.IntegerField(default=0)
	# define the function that will return the question text as the object reference
	def __str__(self):
		return self.question_text
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'questions'
		ordering = ('order',)

# Option model: represents the options which can be used to answer a question
class Option(DataAccessMixin,models.Model):
	option_label = models.CharField(max_length=50)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	keyword = models.CharField(max_length=50, default='', blank=True)
	# define the function that will return the option label as the object reference
	def __str__(self):
		return self.question.question_text + ' ' + self.option_label
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'options'

# Person model: represents a participant in the Betterstart scheme.
# A person may be an adult or a child.
class Person(DataAccessMixin,models.Model):
	first_name = models.CharField(max_length=50)
	middle_names = models.CharField(max_length=50, default='', blank=True)
	last_name = models.CharField(max_length=50)
	other_names = models.CharField(max_length=50, default='', blank=True)
	prior_names = models.CharField(max_length=50, default='', blank=True)
	email_address = models.CharField(max_length=50, default='', blank=True)
	home_phone = models.CharField(max_length=50, default='', blank=True)
	mobile_phone = models.CharField(max_length=50, default='', blank=True)
	emergency_contact_details = models.TextField(max_length=1000, default='', blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=25, default='', blank=True)
	notes = models.TextField(max_length=1000, default='', blank=True)
	relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False)
	default_role = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	trained_roles = models.ManyToManyField(Role_Type, through='Trained_Role', related_name='trained_people')
	children_centres = models.ManyToManyField(Children_Centre, through='CC_Registration')
	events = models.ManyToManyField(Event, through='Event_Registration')
	answers = models.ManyToManyField(Option, through='Answer')
	pregnant = models.BooleanField(default=False)
	due_date = models.DateField(null=True, blank=True)
	ethnicity = models.ForeignKey(Ethnicity, default=1, on_delete=models.SET_DEFAULT)
	capture_type = models.ForeignKey(Capture_Type, blank=True, null=True, on_delete=models.SET_NULL)
	families = models.ManyToManyField(Family, blank=True)
	savs_id = models.IntegerField(blank=True, null=True)
	ABSS_type = models.ForeignKey(ABSS_Type, default=1, on_delete=models.SET_DEFAULT)
	ABSS_start_date = models.DateField(null=True, blank=True, default=None)
	ABSS_end_date = models.DateField(null=True, blank=True, default=None)
	age_status = models.ForeignKey(Age_Status, default=1, on_delete=models.SET_DEFAULT)
	trained_champion = models.BooleanField(default=False)
	active_champion = models.BooleanField(default=False)
	house_name_or_number = models.CharField(max_length=50, default='', blank=True)
	street = models.ForeignKey(Street, null=True, blank=True, on_delete=models.SET_NULL)
	datetime_created = models.DateTimeField(auto_now_add=True)
	datetime_updated = models.DateTimeField(auto_now=True)
	membership_number = models.IntegerField(default=0)

	# define the function that will return the person name as the object reference
	def __str__(self):
		# set the name
		name = self.first_name + ' ' + self.last_name
		# set the nicknames
		if self.other_names:
			# add the nicknames
			name += ', also known as ' + self.other_names
		# return the name
		return name

	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'people'
		ordering = ('last_name','first_name')
	# and a function to return the full name
	def full_name(self):
		return self.first_name + ' ' + self.last_name
	# and a function to return an age description
	def age_description(self):
		# create a description
		desc = self.age_status.status
		# check whether we have a date of birth
		if self.date_of_birth:
			# add the date of brith
			desc += ', born on ' + self.date_of_birth.strftime('%b %d %Y')
		# return the value
		return desc

	# and a function to return a description of membership in the project
	def project_description(self):
		# create a description
		desc = self.ABSS_type.name
		# and add the joining date
		if self.ABSS_start_date:
			# add to the description
			desc += ', joined project on ' + self.ABSS_start_date.strftime('%b %d %Y')
		# and the add the leaving date
		if self.ABSS_end_date:
			# add to the description
			desc += ', left project on ' + self.ABSS_end_date.strftime('%b %d %Y')
		# return the value
		return desc

	# and a function to return a pregnancy description
	def pregnancy_description(self):
		# create a description
		desc = 'Not pregnant'
		# check whether person is pregnant
		if self.pregnant:
			# set the description
			desc = 'Pregnant (or partner is pregnant)'
			# and add to the description
			if self.due_date:
				# add the due date
				desc += ', due on ' + self.due_date.strftime('%b %d %Y')
		# return the value
		return desc

	# and a set of stats funcions, starting with registrations
	def registered_count(self):
		return self.event_registration_set.filter(registered=True).count()
	# count the apologies
	def apologies_count(self):
		return self.event_registration_set.filter(apologies=True).count()
	# and the participations
	def participated_count(self):
		return self.event_registration_set.filter(participated=True).count()

	# and the hours participated
	def participated_time(self):
		# set the total seconds
		seconds = 0
		# get the events
		for event_registration in self.event_registration_set.filter(participated=True):
			# add the hours
			seconds += event_registration.event.duration().seconds
		# get the hours
		hours = seconds // 3600
		# now get the minutes
		minutes = (seconds - (hours * 3600)) // 60
		# build the string
		time_desc = ''
		# set the hours
		if hours:
			# add the hours
			time_desc += str(hours) + ' hours'
			# and extend the string if there are minutes
			if minutes:
				# add the and
				time_desc += ' and '
		# set the minutes
		if minutes:
			# add the minutes
			time_desc += str(minutes) + ' minutes'
		# and set a negative description
		if not hours and not minutes:
			# set the description
			time_desc = 'no participation'
		# return the result
		return time_desc

	# and the hours per activity type
	def activity_types_with_hours(self):
		# get the activity types
		activity_types = Activity_Type.objects.all().order_by('name')
		# run through the types
		for activity_type in activity_types:
			# set the hours
			activity_type.hours = 0
			# get the hours per activity type
			for activity in Activity.objects.filter(
													person=self,
													activity_type=activity_type):
				# add the hours
				activity_type.hours += activity.hours
		# return the results
		return activity_types

	# and the total activity hours
	def activity_hours(self):
		# set the hours to zero
		hours = 0
		# go through the activities
		for activity in self.activity_set.all():
			# add the hours
			hours += activity.hours
		# set the string
		if hours:
			# build a description
			hours_desc = str(hours) + ' hours'
		# otherwise set the string to the negative value
		else:
			# set the string
			hours_desc = ' no activities'
		# return the string
		return hours_desc

	# and an indication of whether there is an open invitation
	def has_open_invitation(self):
		return Invitation.try_to_get(person=self,datetime_completed__isnull=True)

	# and an indication of whether there is an unvalidated invitation
	def has_unvalidated_invitation(self):
		return Invitation.objects.filter(person=self,datetime_completed__isnull=False,validated=False).exists()

	# and the current age in years
	def age_in_years(self):
		if self.date_of_birth:
			age_in_years = relativedelta(datetime.today(), self.date_of_birth).years
		else:
			age_in_years = 'Unknown'
		return str(age_in_years)

	# and the first participation date
	def first_participation_date(self):
		# initialise variables
		first_participation_date = None
		# try to get the date
		if self.event_registration_set.all().exists():
			first_participation = self.event_registration_set.latest('event__date')
			first_participation_date = first_participation.event.date
		# return the date
		return first_participation_date

	# and a class method to get a person by names and age status
	@classmethod
	def check_person_by_name_and_age_status(cls,first_name,last_name,age_status):
		# set a blank error
		error = ''
		# check whether the from person exists
		try:
			# attempt to get the record
			person_from = cls.objects.get(
											first_name = first_name,
											last_name = last_name,
											age_status = age_status
											)
		# deal with the record not existing
		except (cls.DoesNotExist):
			# set the error
			error = ' does not exist.'
		# deal with more than one match
		except (cls.MultipleObjectsReturned):
			# set the error
			error = ' duplicate with name and age status.'
		# return the errors
		return error

	# supplement the mixin search function
	@classmethod
	def search(cls,*args,**kwargs):
		# initialise variables
		trained_role = 'none'
		include_people = 'in_project'
		names = False
		keywords = False

		# get values from the search request if we have them
		if 'trained_role' in kwargs.keys():
			trained_role = kwargs.pop('trained_role')
		if 'include_people' in kwargs.keys():
			include_people = kwargs.pop('include_people')
		if 'names' in kwargs.keys():
			names = kwargs.pop('names')
		if 'keywords' in kwargs.keys():
			keywords = kwargs.pop('keywords')

		# call the mixin method
		results = super().search(**kwargs)

		# if we have a trained role, filter by the trained role
		if trained_role != 'none':
			role_type = Role_Type.objects.get(pk=int(extract_id(trained_role)))
			results = results.filter(trained_roles=role_type)
			# filter further if we want active only
			if 'active' in trained_role:
				for person in results:
					if not person.trained_role_set.filter(role_type=role_type,active=True).exists():
						results = results.exclude(pk=person.pk)

		# filter further depending on whether we want people in the project, or those who have left
		if include_people == 'in_project' or include_people == '':
			results = results.exclude(ABSS_end_date__isnull=False)
		elif include_people == 'left_project':
			results = results.exclude(ABSS_end_date__isnull=True)

		# if we have names in the search terms, split on spaces and attempt to find matches in the name fields
		# and the membership number field
		if names:
			name_list = names.split(' ')
			for name in name_list:
				# see whether this is a name or a number
				if all(map(str.isdigit,name)):
					# we have a number, so search on membership number
					results = results.filter(membership_number=int(name))
				else:
					# we have a name, so search on name
					results = results.filter(first_name__icontains=name) \
								| results.filter(last_name__icontains=name) \
								| results.filter(other_names__icontains=name) \
								| results.filter(email_address__icontains=name)

		# if we have any terms in keywords, call the function to search by keywords
		if keywords:
			results = Person.search_by_keywords(keywords,results)

		# order the results by name
		results = results.order_by('last_name','first_name')

		# return the results
		return results

	# supplement the mixin search function further with a keyword search
	@classmethod
	def search_by_keywords(cls,keywords,results):

		# initialise variables
		filter_dict = {}

		# create a dictionary of search terms and filters: each search term identifies a dictionary
		# that will be used to build the filter
		keyword_filters = {
						'pregnant' : { 'pregnant' : True },
						'in project' : { 'ABSS_end_date__isnull' : True },
						'left project' : { 'ABSS_end_date__isnull' : False }
						}

		# build more keyword filters from reference data
		for role_type in Role_Type.objects.filter(trained=False):
			keyword_filters[role_type.role_type_name] = \
					{ 'default_role__role_type_name' : role_type.role_type_name }

		for role_type in Role_Type.objects.filter(trained=True):
			keyword_filters[role_type.role_type_name] = \
					{ 'trained_role__role_type__role_type_name' : role_type.role_type_name }

		for ward in Ward.objects.all():
			keyword_filters[ward.ward_name] = \
					{ 'street__post_code__ward__ward_name' : ward.ward_name }

		for age_status in Age_Status.objects.all():
			keyword_filters[age_status.status] = \
					{ 'age_status__status' : age_status.status }

		for ABSS_type in ABSS_Type.objects.all():
			keyword_filters[ABSS_type.name] = \
					{ 'ABSS_type__name' : ABSS_type.name }

		for ethnicity in Ethnicity.objects.all():
			keyword_filters[ethnicity.description] = \
					{ 'ethnicity__description' : ethnicity.description }

		for option in Option.objects.exclude(keyword=''):
			keyword_filters[option.keyword] = \
					{ 'answer__option__keyword' : option.keyword }

		# split the keywords, then go through the search terms looking for matches, converting keywords to 
		# lower case to avoid case sensitivity
		for keyword in keyword_filters.keys():
			if keyword.lower() in keywords.lower():
				# go through the terms in the dictionary, adding them to the filter
				for keyword_filter in keyword_filters[keyword].keys():
					filter_dict[keyword_filter] = keyword_filters[keyword][keyword_filter]

		# if we have a filter dictionary, filter, otherwise return an empty queryset
		if filter_dict:
			results = results.filter(**filter_dict)
		else:
			results = Person.objects.none()

		# return the results
		return results

	# class method to get the next membership number
	@classmethod
	def get_next_membership_number(cls,*args,**kwargs):
		# if we have any people get the latest number, otherwise set it to 0
		if Person.objects.all().exists():
			last_number = Person.objects.all().order_by('membership_number').last().membership_number
		else:
			last_number = 0
		# return an incremented version of the number
		return last_number + 1

# Relationship model: represents a relationship between two people.
# This is an intermediate model for a many to many relationship between two Person objects.
class Relationship(DataAccessMixin,models.Model):
	relationship_from = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rel_from')
	relationship_to = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rel_to')
	relationship_type = models.ForeignKey(Relationship_Type, on_delete=models.CASCADE)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.relationship_from.first_name + ' ' + self.relationship_from.last_name + \
			' is the ' + self.relationship_type.relationship_type + ' of ' + \
				self.relationship_to.first_name + ' ' + self.relationship_to.last_name
	def short_desc(self):
		return self.relationship_type.relationship_type + ' of ' + \
			self.relationship_to.first_name + ' ' + self.relationship_to.last_name
	# define the class method to create both sides of a relationship
	@classmethod
	def create_relationship(cls, person_from, person_to, relationship_type_from):
		# create a symmetrical relationship between two people
		# create a flag
		success = False
		# check whether the relationship already exists
		try:
			# do the database call
			relationship = cls.objects.get(relationship_from=person_from,relationship_to=person_to)
		# handle the exception
		except Relationship.DoesNotExist:
			# start by getting the other half of the relationship
			relationship_type_to = Relationship_Type.objects.get(
													relationship_type=relationship_type_from.relationship_counterpart)
			# now create the from part of the relationship
			relationship_from = cls(
									relationship_from = person_from,
									relationship_to = person_to,
									relationship_type = relationship_type_from)
			# now save it
			relationship_from.save()
			# now create the to part of the relationship
			relationship_to = cls(
									relationship_from = person_to,
									relationship_to = person_from,
									relationship_type = relationship_type_to)
			# now save it
			relationship_to.save()
			# set the flag
			success = True
		# that's it!
		return success
	# define the class method to edit both sides of a relationship
	@classmethod
	def edit_relationship(cls, person_from, person_to, relationship_type):
		# edit a relationship: this includes deletion of existing relationships and creation of new relationships
		# if we have been passed a relationship type id of zero of False, we just do the deletion
		# set a flag
		success = False
		# see whether we have an existing relationship
		try:
			# attempt to get the from record
			relationship_from = cls.objects.get(
												relationship_from=person_from,
												relationship_to=person_to
												)
			# attempt to get the to record
			relationship_to = cls.objects.get(
												relationship_from=person_to,
												relationship_to=person_from
												)
			# check whether the relationship has changed
			if (relationship_from.relationship_type != relationship_type):
				# delete the existing relationships
				relationship_from.delete()
				relationship_to.delete()
			# if nothing has changed, we are done, so we can return success
			else:
				# set the flag
				success = True
				# return success
		# deal with the failure to find a record
		except (cls.DoesNotExist):
			# nothing to do
			pass
		# if we have a valid realtionship type, create the relationship
		if relationship_type:
			# try to create the relationship
			if cls.create_relationship(
										person_from = person_from,
										person_to = person_to,
										relationship_type_from = relationship_type
										):
				# set the success flag
				success = True
		# return the result
		return success

# Trained Role model: records that a person is trained to play a particular type of role
# Records whether the person has been trained in the role, and whether the person is active in the role
class Trained_Role(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role_type = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	active = models.BooleanField(default=False)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ': ' + self.role_type.role_type_name \
			+ ' (' + self.active_status() + ')'
	# define a function for returning active status as a string
	def active_status(self):
		if self.active:
			return 'active'
		else:
			return 'inactive'
	# and a function to return a status description
	def status_description(self):
		# create a description
		desc = 'Trained'
		# check whether the role is active
		if self.active:
			# add to the description
			desc += ' and active'
		# return the value
		return desc
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'trained roles'

# Role history model: records that a person has played a particular type of role
# Records whether the person has been trained in the role, and whether the person is active in the role
class Role_History(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role_type = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	started = models.DateTimeField(auto_now_add=True)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ': ' + self.role_type.role_type_name \
			+ ' from ' + str(self.started.date())
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'role histories'

# CC Registration model: records that a person is registered at a Children Centre
class CC_Registration(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	children_centre = models.ForeignKey(Children_Centre, on_delete=models.CASCADE)
	registration_date = models.DateField()
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ' registered at ' + \
				self.children_centre.children_centre_name + ' on ' + str(self.registration_date)
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'children centre registrations'

# Event Registration: records that a person registered for or participated in an event.
class Event_Registration(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	role_type = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	registered = models.BooleanField()
	participated = models.BooleanField()
	apologies = models.BooleanField(default=False)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ': ' + self.role_type.role_type_name \
			+ ' at ' + self.event.name + ' on ' + self.event.date.strftime('%b %d %Y') + \
			' (' + self.description() + ')'
	# define a function for returning active status as a string
	def registered_status(self):
		if self.registered:
			return 'registered'
		else:
			return 'not registered'
	# define a function for returing trained status as a string
	def participated_status(self):
		if self.participated:
			return 'participated'
		else:
			return 'did not participate'
	# define a function to return a description
	def description(self):
		# set a blank result
		desc = ''
		# add registered
		desc = add_description(desc=desc,value=self.registered,text='registered')
		# and participated
		desc = add_description(desc=desc,value=self.participated,text='participated')
		# and apologies
		desc = add_description(desc=desc,value=self.apologies,text='apologies sent')
		# now return the result
		return desc
	# define a function to return the duration of the event in hours
	def hours(self):
		# return an exact number of hours
		return self.event.duration().seconds / 3600

	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'event registrations'

# Answer model: represents the answer to a question, using an option
class Answer(DataAccessMixin,models.Model):
	option = models.ForeignKey(Option, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	# define the function that will return the option label as the object reference
	def __str__(self):
		return self.question.question_text + ': ' + self.option.option_label
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'answers'

# Answer note model: adds supplementary notes to a question
class Answer_Note(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	notes = models.TextField(max_length=500, default='', blank=True)
	# define the function that will return the option label as the object reference
	def __str__(self):
		return self.question.notes_label + ': ' + self.notes
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'answer notes'

# Activity Type model: represents types of activity
class Activity_Type(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	# define the function that will return the name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'activity types'

# Activity model: represents an activity
class Activity(DataAccessMixin,models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	activity_type = models.ForeignKey(Activity_Type, on_delete=models.CASCADE)
	date = models.DateField()
	hours = models.IntegerField()
	# define the function that will return the name as the object reference
	def __str__(self):
		return self.activity_type.name + \
				' for ' + str(self.hours) + \
				' hours on ' + self.date.strftime('%b %d %Y')
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'activities'

# Filter_Spec model: used to define filter terms for a dashboard model
class Filter_Spec(DataAccessMixin,models.Model):
	term = models.CharField(max_length=50)
	filter_type = models.CharField(
									max_length=50,
									choices = [
												('string','string'),
												('boolean','boolean'),
												('period','period'),
												('object','object')
												],
									default='',
									blank=True
									)
	string_value = models.CharField(max_length=50, default='', blank=True)
	boolean_value = models.BooleanField(default=False)
	period = models.CharField(
								max_length=50,
								choices = [
											('','no period'),
											('this_month','this month'),
											('last_month','last_month'),
											('this_project_year','this project year'),
											('last_project_year','last project year'),
											('this_calendar_year','this calendar year'),
											('last_calendar_year','last_calendar_year'),
											('rolling_quarter','rolling_quarter')
											],
								default='',
								blank=True
								)
	exclusion = models.BooleanField(default=False)
	# define the function that will return a description of the filter
	def __str__(self):
		# build the description depending on the type of filter
		if self.filter_type == 'boolean':
			filter_str = self.term + ' = '  + str(self.boolean_value)
		elif self.filter_type == 'period':
			filter_str = self.term + ' within ' + self.period
		elif self.filter_type == 'object':
			filter_str = self.term + ' = object'
		else: 
			filter_str = self.term + ' = '  + self.string_value
		# add exlcusion text if this is an exclusion
		if self.exclusion:
			filter_str = filter_str + ' (exclusion)'
		#return the value
		return filter_str
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'filter specs'
		ordering = ['term']

# Panel model: used to define a dashboard panel
class Chart(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	chart_type = models.CharField(
									max_length=50,
									choices = [
												('pie','Pie Chart'),
												('bar','Bar Chart'),
												('month_bar','Bar Chart by Month'),
												('stacked_bar','Stacked Bar Chart'),
												],
									default='',
									blank=True
									)
	title = models.CharField(max_length=50)
	model = models.CharField(max_length=50)
	label_field = models.CharField(max_length=50, blank=True)
	sort_field = models.CharField(max_length=50, blank=True)
	count_field = models.CharField(max_length=50, blank=True)
	date_field = models.CharField(max_length=50, blank=True)
	sum_field = models.CharField(max_length=50, blank=True)
	group_by_field = models.CharField(max_length=50, blank=True)
	super_filters = models.ManyToManyField(Filter_Spec, blank=True, related_name='owning_charts')
	filters = models.ManyToManyField(Filter_Spec, blank=True)
	months = models.IntegerField(choices=[(i, i) for i in range(0, 13)], blank=True, default=0)
	query_type = models.CharField(
							max_length=50,
							choices = [
										('query from one','query from one'),
										('query from many','query from many'),
										],
							default='query from one',
							blank=True
							)
	many_model = models.CharField(max_length=50, blank=True)
	stack_model = models.CharField(max_length=50, blank=True)
	stack_label_field = models.CharField(max_length=50, blank=True)
	stack_filter_term = models.CharField(max_length=50, blank=True)
	x_label_rotation = models.IntegerField(default=0)

	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'charts'
		ordering = ['name']

	# over ride the init to add an errors field
	def __init__(self, *args, **kwargs):
		super(Chart, self).__init__(*args, **kwargs)
		self.errors = []

	# add an error to the list
	def add_error(self,error):
		self.errors.append('ERROR: ' + error)

	# build and return a set of rows
	def get_chart(self,start_date,end_date):
		# add the dates
		self.start_date = start_date
		self.end_date = end_date
		# check validity
		if not self.is_valid():
			return False
		# get the chart based on the chart type
		if self.chart_type == 'pie':
			chart = self.get_pie_chart()
		elif self.chart_type == 'bar':
			chart = self.get_bar_chart()
		elif self.chart_type == 'month_bar':
			chart = self.get_month_bar_chart()
		elif self.chart_type == 'stacked_bar':
			chart = self.get_stacked_bar_chart()
		# return the results, or False if we have errors
		return chart.render_data_uri() if not self.errors else False

	# check whether the chart is valid
	def is_valid(self):
		# if we have a count field, figure out the model
		count_model_name = class_name_from_set_str(self.count_field) if self.count_field else False
		# check whether the models are valid classes
		for this_model in (self.model, self.many_model, self.stack_model, count_model_name):
			if this_model:
				model = class_from_str(this_model)
				if not model:
					self.add_error(this_model + ' is not a valid model')
					return False
		# get the main model and the count model
		model = class_from_str(self.model)
		count_model = class_from_str(count_model_name) if count_model_name else False
		# check the attributes
		for attribute in (self.sort_field, self.label_field, self.count_field, self.group_by_field):
			if attribute and not hasattr(model,attribute):
				self.add_error(attribute + ' is not a valid attribute')
				return False
		# what we do with sum field depends on whether we are grouping or navigating a relationship
		if self.sum_field:
			if count_model:
				if not hasattr(count_model,self.sum_field):
					self.add_error(self.sum_field + ' is not a valid attribute')
					return False
			elif not hasattr(model,self.sum_field):
				self.add_error(self.sum_field + ' is not a valid attribute')
				return False
		# check that we have the fields necessary fro a pie or bar chart
		if self.query_type == 'query from one' and self.chart_type in ('pie','bar'):
			if not self.label_field:
				self.add_error('Label not provided')
				return False
			if not self.count_field and not self.sum_field and not self.group_by_field:
				self.add_error('Count or sum or group by not provided')
				return False
		# we made it this far, so it must be valid
		return True

	def get_bar_chart(self):
		# initialise variables
		x_labels = []
		data_values = []
		# get the data, breaking out if we get errors
		data = self.get_data()
		if self.errors:
			return False
		# build the chart
		bar_chart = pygal.Bar(show_legend=False,x_label_rotation=self.x_label_rotation)
		bar_chart.x_labels = data.keys()
		bar_chart.add('', data.values())
		# return the chart
		return bar_chart

	def get_pie_chart(self):
		# create the chart
		pie_chart = pygal.Pie()
		# get the data, breaking out if we get errors
		data = self.get_data()
		if self.errors:
			return False
		# build the pie wedges
		for key in data.keys():
			pie_chart.add(key,data[key])
		# return the chart
		return pie_chart

	def get_month_bar_chart(self):
		# initialise variables
		x_labels = []
		data_values = []
		today = datetime.today()
		this_year = today.year
		this_month = today.month
		model = class_from_str(self.model)
		# build an array of months
		months = []
		start_month = (today - relativedelta(months=self.months)).month
		for month in range(0,self.months):
			this_month = (start_month + month)%12 + 1
			months.append(this_month)
		# go through months, building labels and data
		for month in months:
			x_labels.append(calendar.month_name[month])
			# set the right year, based on current month
			if month > this_month:
				query_year = this_year - 1
			else:
				query_year = this_year
			# set the filter
			filter_dict = {
							self.date_field + '__month' : month,
							self.date_field + '__year' : query_year
							}
			# get the queryset, apply further filters and add to the chart
			queryset = model.objects.filter(**filter_dict)
			queryset, valid = self.apply_filters(queryset,self.super_filters.all())
			data_values.append(self.get_value(queryset))
		# build the chart
		bar_chart = pygal.Bar(show_legend=False,x_label_rotation=self.x_label_rotation)
		bar_chart.x_labels = x_labels
		bar_chart.add('', data_values)
		# return the chart
		return bar_chart

	def get_data(self):
		# build and return a dictionary of data
		data = {}
		# get the data from the database, filtering and sorting as required
		model = class_from_str(self.model)
		records, valid = self.apply_filters(model.objects.all(),self.super_filters.all())
		if not valid:
			return False
		# sort the records if we have a sort field
		if self.sort_field:
			records = records.order_by(self.sort_field)
		# go through the data
		for record in records:
			# get the label, converting methods to values if necessary, and converting the label to a string
			label = getattr(record,self.label_field)
			if ismethod(label):
				label = label()
			label = str(label)
			# get the data and calculate the value
			if self.group_by_field:
				data[label] = self.add_group_by_value(record,data,label)
			else:
				queryset = self.get_queryset(record)
				if not self.errors:
					value = self.get_value(queryset)
					data[label] = value
		# return the result
		return data

	def add_group_by_value(self,record,data,label):
		# return the value to add to the dictionary
		# start by figuring out whether we are adding or counting
		if self.sum_field:
			sum_attr = getattr(record,self.sum_field)
			if ismethod(sum_attr):
				value = sum_attr()
		else:
			value = 1
		# add the value to the dictionary entry if it exists
		if label in data.keys():
			value = data[label] + value
		# return the value
		return value

	def get_stacked_bar_chart(self):
		# initialise variables
		x_labels = []
		data_values = []
		# initialise a list for each stack_record
		stack_model = class_from_str(self.stack_model)
		stack_records = stack_model.objects.all().order_by(self.stack_label_field)
		for stack_record in stack_records:
			stack_record.values = []
		# get the data
		model = class_from_str(self.model)
		records, valid = self.apply_filters(model.objects.all(),self.super_filters.all())
		# create the chart
		bar_chart = pygal.StackedBar(x_label_rotation=self.x_label_rotation)
		# build up the data for the chart
		for record in records:
			# get the label, converting methods to values if necessary
			label = getattr(record,self.label_field)
			if ismethod(label):
				label = label()
			x_labels.append(label)
			# get the queryset
			queryset = self.get_queryset(record)
			# go through the stack entries and set the values based on a filter of the queryset
			for stack_record in stack_records:
				filter_dict = { self.stack_filter_term : stack_record }
				try:
					count = queryset.filter(**filter_dict).count()
					stack_record.values.append(count)
				except:
					self.add_error('Invalid stack filter')
					return False
		# build the chart
		bar_chart.x_labels = x_labels
		for stack_record in stack_records:
			if not all([ value == 0 for value in stack_record.values ]):
				bar_chart.add(getattr(stack_record,self.stack_label_field),stack_record.values)
		# return the chart
		return bar_chart

	def get_queryset(self,record):
		# get the queryset used to populate the chart
		if self.query_type == 'query from one':
			queryset = getattr(record,self.count_field).all()
		else:
			many_model = class_from_str(self.many_model)
			queryset = many_model.objects.all()
		# filter it if it needs filtering
		queryset, valid = self.apply_filters(queryset,self.filters.all(),master_object=record)
		# deduplicate the results if they are valid
		if valid:
			queryset = queryset.distinct()
		# return the results
		return queryset

	def apply_filters(self,queryset,filters,master_object=False):
		# initialise the variables
		filter_dict = {}
		exclusion_dict = {}
		valid = True
		# apply filters to a queryset and return the result
		for filter in filters:
			if not filter.exclusion:
				if filter.filter_type == 'boolean':
					filter_dict[filter.term] = filter.boolean_value
				elif filter.filter_type == 'string':
					filter_dict[filter.term] = filter.string_value
				elif filter.filter_type == 'period':
					filter_dict = self.add_period_filters(filter, filter_dict)
				elif filter.filter_type == 'object':
					filter_dict[filter.term] = master_object
			else:
				if filter.filter_type == 'boolean':
					exclusion_dict[filter.term] = filter.boolean_value
				elif filter.filter_type == 'string':
					exclusion_dict[filter.term] = filter.string_value
				elif filter.filter_type == 'period':
					exclusion_dict = self.add_period_filters(filter, filter_dict)
				elif filter.filter_type == 'object':
					exclusion_dict[filter.term] = master_object
		# try to apply the filters
		if filter_dict:
			try:
				queryset = queryset.filter(**filter_dict)
			except:
				queryset = False
				valid = False
				self.add_error('Invalid filter')
		# try to apply the exclusions
		if exclusion_dict:
			try:
				queryset = queryset.exclude(**exclusion_dict)
			except:
				queryset = False
				valid = False
				self.add_error('Invalid filter')
		# return the result
		return queryset, valid

	def add_period_filters(self,filter,filter_dict):
		# get the start and end of the period, based on the type of period
		# if we have a start date or end date on the panel, over-ride the filter
		if self.start_date or self.end_date:
			period_start = self.start_date if self.start_date else False
			period_end = self.end_date if self.end_date else False
		else:
			period_start, period_end = get_period_dates(filter.period)
		# set the terms based on the supplied term
		start_term = filter.term + '__gte'
		end_term = filter.term + '__lte'
		# add the filters if we have values
		if period_start:
			filter_dict[start_term] = period_start
		if period_end:
			filter_dict[end_term] = period_end
		# return the results
		return filter_dict

	def get_value(self,queryset):
		# initialise variables
		value = 0
		# return a value depending on whether we are doing a count or a sum
		if self.sum_field:
			# if the sum_field is a method, iterate through, applying the method, else use aggregation
			test_record = queryset.first()
			if test_record:
				sum_attr = getattr(test_record,self.sum_field)
				if ismethod(sum_attr):
					for record in queryset:
						sum_attr = getattr(record,self.sum_field)
						value += sum_attr()
				else:
					value = queryset.aggregate(sum_value=Sum(self.sum_field))['sum_value']
		else:
			value = queryset.count()
		# return the value
		return value

# Dashboard_Column model: used to define a dashboard column
class Panel_Column(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	title = models.CharField(max_length=50, default='', blank=True)
	query_type = models.CharField(
							max_length=50,
							choices = [
										('query from one','query from one'),
										('query from many','query from many'),
										],
							default='query from one',
							blank=True
							)
	count_field = models.CharField(max_length=50, default='', blank=True)
	count_model = models.CharField(max_length=50, default='', blank=True)
	filters = models.ManyToManyField(Filter_Spec, blank=True)
	apply_sub_filters = models.BooleanField(default=True)
	# define the function that will return the name
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'panel columns'
		ordering = ['name']

# Panel model: used to define a dashboard panel
class Panel(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	title = models.CharField(max_length=50)
	title_url = models.CharField(max_length=50, default='', blank=True)
	title_icon = models.CharField(max_length=50, default='', blank=True)
	show_column_names = models.BooleanField(default=False)
	label_width = models.IntegerField(default=6)
	column_width = models.IntegerField(default=6)
	right_margin = models.IntegerField(default=0)
	row_url = models.CharField(max_length=50, default='', blank=True)
	row_parameter_name = models.CharField(max_length=50, default='', blank=True)
	row_parameter_prefix = models.CharField(max_length=50, default='', blank=True)
	row_name_field = models.CharField(max_length=50, default='', blank=True)
	sort_field = models.CharField(max_length=50, default='', blank=True)
	totals = models.BooleanField(default=False)
	display_zeroes = models.BooleanField(default=False)
	model = models.CharField(max_length=50,default='',blank=True)
	filters = models.ManyToManyField(Filter_Spec, blank=True)
	sub_filters = models.ManyToManyField(Filter_Spec, blank=True, related_name='owning_panels')
	columns = models.ManyToManyField(Panel_Column, through='Panel_Column_In_Panel')
	prebuilt_panel = models.CharField(
										max_length=50,
										choices = [
													('Parent_Exceptions_Panel','Parent Exceptions'),
													('Age_Status_Exceptions_Panel','Age Status Exceptions')
													],
										default='',
										blank=True
										)
	chart = models.ForeignKey(Chart, blank=True, null=True, on_delete=models.SET_NULL)

	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'panels'
		ordering = ['name']

	# build and return a set of rows
	def get_rows(self):
		self.build()
		return self.rows

	# build a chart
	def get_chart(self):
		# set dates if they have been set for the panel
		start_date = self.start_date if hasattr(self,'start_date') else False
		end_date = self.end_date if hasattr(self,'end_date') else False
		return self.chart.get_chart(start_date=start_date,end_date=end_date)

	# return a set of column names
	def get_column_names(self):
		# initialise the variables
		columns = self.panel_column_in_panel_set.order_by('order')
		self.column_names = []
		# get and return the column names
		for column in columns:
			self.column_names.append(column.panel_column.title)
		return self.column_names

	# build the contents of the panel from the database
	def build(self):
		# build from a prebuilt panel if we have, otherwise check validity and build from data if valid
		if self.chart:
			pass
		elif self.prebuilt_panel:
			self.build_from_prebuilt_panel()
		elif self.is_valid():
			self.model = class_from_str(self.model)
			self.build_rows()

	# check whether the panel is valid
	def is_valid(self):
		# check whether the model is a valid class
		model = class_from_str(self.model)
		if not model:
			self.set_panel_error('MODEL DOES NOT EXIST')
			return False
		# get one record, so that we can test attributes
		test_object = model.objects.first()
		# check the sort field
		if self.sort_field and not has_field(model,self.sort_field):
			self.set_panel_error('SORT FIELD DOES NOT EXIST')
			return False
		# check the name field
		if not hasattr(test_object,self.row_name_field):
			self.set_panel_error('ROW NAME FIELD DOES NOT EXIST')
			return False
		# check the parameter field
		if self.row_parameter_name and not hasattr(test_object,self.row_parameter_name):
			self.set_panel_error('ROW PARAMETER FIELD DOES NOT EXIST')
			return False
		# go through the columns
		for column in self.panel_column_in_panel_set.order_by('order'):
			# check the count field
			if column.panel_column.query_type == 'query from one':
				if not hasattr(test_object,column.panel_column.count_field):
					self.set_panel_error('COUNT FIELD DOES NOT EXIST')
					return False
			else:
				# check the count model
				if not class_from_str(column.panel_column.count_model):
					self.set_panel_error('COUNT MODEL DOES NOT EXIST')
					return False
		# we made it this far, so it must be valid
		return True

	def build_from_prebuilt_panel(self):
		# define a dictionary of functions for prebuilt panels
		prebuilt_panels = {
							'Parent_Exceptions_Panel' : self.build_parent_exceptions,
							'Age_Status_Exceptions_Panel' : self.build_age_status_exceptions
							}
		# check that the prebuilt model is in the dictionary
		if self.prebuilt_panel in prebuilt_panels:
			# build using the function
			prebuilt_function = prebuilt_panels[self.prebuilt_panel]
			prebuilt_function()
		# otherwise set the error
		else:
			self.set_panel_error('PREBUILT DOES NOT EXIST')

	def build_age_status_exceptions(self):
		# initialise the variables
		age_statuses = []
		today = date.today()
		self.rows = []
		# now go through the age statuses and get the exceptions
		for age_status in Age_Status.objects.all():
			age_exceptions = age_status.person_set.filter(
									date_of_birth__lt=today.replace(year=today.year-age_status.maximum_age),
									ABSS_end_date__isnull=True)
			# add the exception count to the list if we got any
			if age_exceptions.count() > 0:
				# create a row and append it to the list of rows
				dashboard_panel_row = Dashboard_Panel_Row(
															label=age_status.status,
															values=[age_exceptions.count()],
															url='age_exceptions',
															parameter=age_status.pk)
				self.rows.append(dashboard_panel_row)

	def build_parent_exceptions(self):
		# initialise the variables
		parents_with_no_children, parents_with_no_children_under_four = self.get_parents_without_children()
		parents_with_overdue_children = self.get_parents_with_overdue_children()
		self.rows=[]
		# build the the rows
		self.rows.append(
							Dashboard_Panel_Row(
												label = 'Parents with no children',
												values = [len(parents_with_no_children)],
												url = 'parents_with_no_children',
												parameter = 1
												)
						)
		self.rows.append(
							Dashboard_Panel_Row(
												label = 'Parents with no children under four',
												values = [len(parents_with_no_children_under_four)],
												url = 'parents_without_children_under_four',
												parameter = 1
												)
						)
		self.rows.append(
							Dashboard_Panel_Row(
												label = 'Parents with overdue children',
												values = [len(parents_with_overdue_children)],
												url = 'parents_with_overdue_children',
												parameter = 1
												)
						)

	def get_parents_without_children(self):
		# create an empty list
		parents_with_no_children = []
		parents_with_no_children_under_four = []
		# get today's date
		today = date.today()
		# get the date four years ago
		today_four_years_ago = today.replace(year=today.year-4)
		# attempt to get parents with no children
		parents = Person.search(default_role__role_type_name__contains='Parent')
		# exclude those with pregnancy dates in the future
		parents = parents.exclude(pregnant=True, due_date__gte=today)
		# order the list
		parents = parents.order_by('last_name','first_name')
		# now exclude those where we can find a child relationship
		for parent in parents:
			# attempt to get parent relationships
			parent_relationships = parent.rel_from.filter(relationship_type__relationship_type='parent')
			# if we didn't get a parent relationship, add the parent to the no children list
			if not parent_relationships:
				# append to the no children list
				parents_with_no_children.append(parent)
			# otherwise check how old the children are
			else:
				# set a flag
				child_under_four = False
				# go through the relationships
				for relationship in parent_relationships:
					# check whether the child has a date of birth
					if relationship.relationship_to.date_of_birth != None:
						# and whether the date is less than four years ago
						if relationship.relationship_to.date_of_birth >= today_four_years_ago:
							# set the flag
							child_under_four = True
				# see whether we got a child
				if not child_under_four:
					# add the parent to the list
					parents_with_no_children_under_four.append(parent)
		# return the results
		return parents_with_no_children, parents_with_no_children_under_four

	def get_parents_with_overdue_children(self):
		# return a list of parents with a pregnancy flag and a due date before today
		return Person.search(
								pregnant=True,
								due_date__lt=date.today()
								)

	# function to build the row in the panel
	def build_rows(self):
		# get the columns
		columns = self.panel_column_in_panel_set.order_by('order')
		# initialise variables
		self.row_values = []
		self.rows = []
		# build the row value and column titles
		for column in columns:
			self.row_values.append(column.panel_column.name)
		# get the queryset
		panel_queryset = self.get_panel_queryset()
		# go through the rows, based on the model for the panel if we got a valid result
		if panel_queryset:
			for row in panel_queryset:
				self.add_row(row,columns)

	# function to build an individual row
	def add_row(self,row,columns):
		# initialise variables
		parameter = ''
		values = []
		# try to get the field attribute
		label = getattr(row, self.row_name_field)
		# build the parameter if we have a parameter name
		if self.row_parameter_name:
			parameter = getattr(row, self.row_parameter_name)
			parameter = self.row_parameter_prefix + str(parameter)
		# go through the columns
		for column in columns:
			# get the queryset depending on the type of query
			if column.panel_column.query_type == 'query from one':
				count_queryset = getattr(row,column.panel_column.count_field).all()
			else:
				# try to get the model type, then get all the object for the model
				count_model = class_from_str(column.panel_column.count_model)
				count_queryset = count_model.objects.all()
			# apply filters
			count_queryset, valid_filters = self.apply_filters(
																queryset=count_queryset,
																filters=column.panel_column.filters.all(),
																master_object=row
																)
			# if we need to apply sub filters, apply those too
			if column.panel_column.apply_sub_filters:
				count_queryset, valid_filters = self.apply_filters(
																queryset=count_queryset,
																filters=self.sub_filters.all(),
																master_object=row
																)
			# if it was valid, append the value, else append an error
			if valid_filters:
				values.append(count_queryset.count())
			else:
				values.append('ERROR')
		# build the row and append it to the list of rows
		dashboard_panel_row = Dashboard_Panel_Row(
													label=label,
													values=values,
													url=self.row_url,
													parameter=parameter)
		# append the results
		self.rows.append(dashboard_panel_row)

	def get_panel_queryset(self):
		# get the queryset used to populate the panel
		panel_queryset = self.model.objects.all()
		# filter it if it needs filtering
		panel_queryset, valid_filters = self.apply_filters(panel_queryset,self.filters.all())
		# deal with the error if we got an error
		if not valid_filters:
			self.set_panel_error('INVALID PANEL FILTERS')
		# and try to order it if it needs ordering
		if valid_filters and self.sort_field:
				panel_queryset = panel_queryset.order_by(self.sort_field)
		# deduplicate the results if we have them
		if valid_filters:
			panel_queryset = panel_queryset.distinct()
		# return the results
		return panel_queryset

	def apply_filters(self,queryset,filters,master_object=False):
		# initialise the variables
		filter_dict = {}
		exclusion_dict = {}
		valid = True
		# apply filters to a queryset and return the result
		for filter in filters:
			if not filter.exclusion:
				if filter.filter_type == 'boolean':
					filter_dict[filter.term] = filter.boolean_value
				elif filter.filter_type == 'string':
					filter_dict[filter.term] = filter.string_value
				elif filter.filter_type == 'period':
					filter_dict = self.add_period_filters(filter, filter_dict)
				elif filter.filter_type == 'object':
					filter_dict[filter.term] = master_object
			else:
				if filter.filter_type == 'boolean':
					exclusion_dict[filter.term] = filter.boolean_value
				elif filter.filter_type == 'string':
					exclusion_dict[filter.term] = filter.string_value
				elif filter.filter_type == 'period':
					exclusion_dict = self.add_period_filters(filter, filter_dict)
				elif filter.filter_type == 'object':
					exclusion_dict[filter.term] = master_object
		# try to apply the filters
		if filter_dict:
			try:
				queryset = queryset.filter(**filter_dict)
			except:
				queryset = False
				valid = False
		# try to apply the exclusions
		if exclusion_dict:
			try:
				queryset = queryset.exclude(**exclusion_dict)
			except:
				queryset = False
				valid = False
		# return the result
		return queryset, valid

	def add_period_filters(self,filter,filter_dict):
		# get the start and end of the period, based on the type of period
		# if we have a start date or end date on the panel, over-ride the filter
		if self.start_date or self.end_date:
			period_start = self.start_date if self.start_date else False
			period_end = self.end_date if self.end_date else False
		else:
			period_start, period_end = get_period_dates(filter.period)
		# set the terms based on the supplied term
		start_term = filter.term + '__gte'
		end_term = filter.term + '__lte'
		# add the filters if we have values
		if period_start:
			filter_dict[start_term] = period_start
		if period_end:
			filter_dict[end_term] = period_end
		# return the results
		return filter_dict

	def set_panel_error(self, error='ERROR'):
		# set up the panel to show that we have failed to load it
		self.title = error
		# initialise variables to help display the error
		self.rows = []
		self.totals = False
		# create a single row object
		self.rows.append(Dashboard_Panel_Row(
												label = error,
												values = [error],
												url = False,
												parameter = 0
												))

	def get_totals(self):
		# return a list of totals for the panel
		# create a list of totals
		totals = []
		# create a dictionary of lists
		total_lists = collections.OrderedDict()
		# now go through the rows
		for row in self.rows:
			# now go through the values and build a list
			for index, value in enumerate(row.values):
				# check whether the dictionary entry exists
				if index not in total_lists:
					# initialise the list
					total_lists[index] = []
				# now add the item
				total_lists[index].append(value)
		# now build the actual totals
		for total_list in total_lists:
			# initalise the list for this total
			this_total = 0
			# go through the items
			for value in total_lists[total_list]:
				# add it to the total
				this_total += value
			# now append the total to the list
			totals.append(this_total)
		# return the list of totals
		return totals

# Dashboard_Column model: used to define a dashboard column
class Panel_Column_In_Panel(DataAccessMixin,models.Model):
	order = models.IntegerField(default=0)
	panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
	panel_column = models.ForeignKey(Panel_Column, on_delete=models.CASCADE)
	# define the function that will return the name
	def __str__(self):
		return self.panel_column.name + ' in ' + self.panel.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'panel columns in panels'
		ordering = ('panel__name','order')

# Column model: used to define a dashboard column
class Column(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	heading = models.CharField(max_length=50, default='', blank=True)
	width = models.IntegerField(default=4)
	margins = models.IntegerField(default=1)
	panels = models.ManyToManyField(Panel, through='Panel_In_Column')
	# define the function that will return the name
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'columns'
		ordering = ['name']

	def get_panels(self):
		# get the through models in order and return a list of panels
		panels = []
		# go through the panels
		for panel_in_column in self.panel_in_column_set.all().order_by('order'):
			panels.append(panel_in_column.panel)
			# if we have dates, add them
			panel_in_column.panel.start_date = self.start_date if self.start_date else False
			panel_in_column.panel.end_date = self.end_date if self.end_date else False
		# return the results
		return panels

# Panel_In_Column model: used to define the inclusion of a panel within a column
class Panel_In_Column(DataAccessMixin,models.Model):
	order = models.IntegerField(default=0)
	panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
	column = models.ForeignKey(Column, on_delete=models.CASCADE)
	# define the function that will return the name
	def __str__(self):
		return self.panel.name + ' in ' + self.column.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'panels in columns'

# Dashboard model: used to define a dashboard
class Dashboard(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	title = models.CharField(max_length=50)
	margin = models.IntegerField(default=1)
	columns = models.ManyToManyField(Column, through='Column_In_Dashboard')
	live = models.BooleanField(default=False)
	date_controlled = models.BooleanField(default=False)
	period = models.CharField(
								max_length=50,
								choices = [
											('','no period'),
											('this_month','this month'),
											('last_month','last_month'),
											('this_project_year','this project year'),
											('last_project_year','last project year'),
											('this_calendar_year','this calendar year'),
											('last_calendar_year','last_calendar_year'),
											('rolling_quarter','rolling_quarter')
											],
								default='',
								blank=True
								)
	# define the function that will return the name
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'dashboards'
		ordering = ['name']

	def get_columns(self):
		# get the through models in order and return a list of columns
		columns = []
		# go through the columns
		for column_in_dashboard in self.column_in_dashboard_set.all().order_by('order'):
			columns.append(column_in_dashboard.column)
			# if we have dates, add them
			column_in_dashboard.column.start_date = self.start_date if self.start_date else False
			column_in_dashboard.column.end_date = self.end_date if self.end_date else False
		# return the results
		return columns

	def get_dates(self):
		# get the start and end of the default period for the dashboard, based on the type of period
		if self.period:
			start_date, end_date = get_period_dates(self.period)
		else:
			start_date, end_date = False, False
		# return the results
		return start_date, end_date

# Column_In_Dashboard model: used to define the inclusion of a column within a dashboard
class Column_In_Dashboard(DataAccessMixin,models.Model):
	order = models.IntegerField(default=0)
	dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
	column = models.ForeignKey(Column, on_delete=models.CASCADE)
	# define the function that will return the name
	def __str__(self):
		return self.column.name + ' in ' + self.dashboard.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'columns in dashboards'

class Dashboard_Panel_Row():
	# this class contains the data and structure for a row
	def __init__(self, label, values, url=False, parameter=0):
		# set the attributes
		self.label = label
		self.values = values
		self.url = url
		self.parameter = parameter

	def has_data(self):
		# check whether any of the values contain data
		has_data = False
		# go through the values and set the flag if we have a value
		for value in self.values:
			if value:
				has_data = True
		# return the value
		return has_data

# Site model: provides configuration for the site
class Site(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	navbar_background = models.CharField(max_length=50, blank=True)
	navbar_text = models.CharField(max_length=50, blank=True, null=True, default=None)
	messages = models.BooleanField(default=False)
	dob_offset = models.IntegerField(default=0)
	dashboard = models.ForeignKey(Dashboard, null=True, blank=True, on_delete=models.SET_NULL)
	otp_required = models.BooleanField(default=False)
	otp_practice = models.BooleanField(default=False)
	invitations_active = models.BooleanField(default=False)
	invitation_introduction = models.TextField(max_length=25000, default='', blank=True)
	password_reset_allowed = models.BooleanField(default=False)
	password_reset_email_from = models.CharField(max_length=100, default='', blank=True)
	password_reset_email_cc = models.CharField(max_length=100, default='', blank=True)
	password_reset_email_title = models.CharField(max_length=100, default='', blank=True)
	password_reset_email_text = models.TextField(max_length=1000, default='', blank=True)
	password_reset_timeout = models.IntegerField(default=15)
	# define the function that will return the SITE name as the object reference
	def __str__(self):
		return self.name

# Profile model: keeps track of additional information about the user
class Profile(DataAccessMixin,models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	successful_logins = models.IntegerField(default=0)
	unsuccessful_logins = models.IntegerField(default=0)
	successful_otp_logins = models.IntegerField(default=0)
	unsuccessful_otp_logins = models.IntegerField(default=0)
	requested_resets = models.IntegerField(default=0)
	successful_resets = models.IntegerField(default=0)
	reset_code = models.CharField(max_length=16,default='',null=True,blank=True)
	reset_timeout = models.DateTimeField(null=True, blank=True)

	# define the function that will return the SITE name as the object reference
	def __str__(self):
		return self.user.username

	# class method to generate a code
	@classmethod
	def generate_reset_code(cls,*args,**kwargs):
		# return an randomly generated 16 character string of letters and digits
		return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

	# class method to generate a code
	@classmethod
	def generate_reset_timeout(cls,*args,**kwargs):
		# get the site and the timeout value
		site = Site.objects.first()
		site_reset_timeout = site.password_reset_timeout if site else False
		# generate the value
		reset_timeout = timezone.now() + timedelta(minutes=site_reset_timeout) if site_reset_timeout else None
		# return the result
		return reset_timeout

# Terms_And_Conditions model: used to store terms and conditions, bounded by dates
class Terms_And_Conditions(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	notes = models.TextField(max_length=25000, default='', blank=True)
	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'terms and conditions'

# Invitation_Step_Type model: contains the steps to be followed for an invitation
class Invitation_Step_Type(DataAccessMixin,models.Model):
	name_choices = [
					('introduction','Introduction'),
					('terms_and_conditions','Terms and Conditions'),
					('personal_details','Personal Details'),
					('address','Address'),
					('children','Children'),
					('questions','Questions'),
					('signature','Signature'),
					]
	name = models.CharField(max_length=50, choices=name_choices)
	display_name = models.CharField(max_length=50, default='')
	order = models.IntegerField(default=0)
	active = models.BooleanField(default=True)
	terms_and_conditions = models.ForeignKey(Terms_And_Conditions, null=True, blank=True, on_delete=models.CASCADE)
	data_type = models.CharField(
									max_length=50,
									choices=[
										('string', 'string'),
										('table', 'table'),
										('fields', 'fields'),
										('signature', 'signature'),
									],
									default='',
									blank=True
								)
	special_category_text = models.TextField(max_length=1000, default='', blank=True)
	# define the function that will return the SITE name as the object reference
	def __str__(self):
		return self.display_name

	class Meta:
		verbose_name_plural = 'invitation step types'
		ordering = ('order',)

# Invitation model: contains the code to access an invitation, and links to the steps
class Invitation(DataAccessMixin,models.Model):
	code = models.CharField(max_length=16)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	datetime_created = models.DateTimeField(auto_now_add=True)
	datetime_completed = models.DateTimeField(null=True, blank=True)
	notes = models.TextField(max_length=1000, default='', blank=True)
	invitation_steps = models.ManyToManyField(Invitation_Step_Type, through='Invitation_Step')
	validated = models.BooleanField(default=False)
	invalid  = models.BooleanField(default=False)
	# define the function that will return the string for the object
	def __str__(self):
		completed = 'completed' if self.datetime_completed is not None else 'not completed'
		return self.person.full_name() + ' invited with code ' + self.code + ' (' + completed + ')'
 
	class Meta:
		verbose_name_plural = 'invitations'

	# class method to generate a code
	@classmethod
	def generate_code(cls,*args,**kwargs):
		# return an randomly generated 16 character string of letters and digits
		return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

	# method to get incomplete steps
	def incomplete_steps(self):
		# get steps which are active and which do not exist for this invitation
		incomplete_steps = Invitation_Step_Type.objects.filter(active=True).exclude(invitation=self)
		# if we have no questions, exclude the question step
		if not Question.objects.filter(use_for_invitations=True).exists():
			incomplete_steps = incomplete_steps.exclude(name='questions')
		# return the result
		return incomplete_steps

	# method to get complete steps
	def complete_steps(self):
		return Invitation_Step_Type.objects.filter(invitation=self)

	# method to display the signature
	def get_signature(self):
		# initialise variables
		signature_image = False
		# if we have a signature, build a base64 string
		if self.signature:
			signature_image = draw_signature(self.signature)
		# return the results
		return signature_image

# Invitation_Step model: contains the steps that have been followed 
class Invitation_Step(DataAccessMixin,models.Model):
	invitation = models.ForeignKey(Invitation, on_delete=models.CASCADE)
	invitation_step_type = models.ForeignKey(Invitation_Step_Type, on_delete=models.CASCADE)
	datetime_created = models.DateTimeField(auto_now_add=True)
	step_data = models.TextField(max_length=1500, default='', blank=True)
	signature = JSignatureField(blank=True, null=True)
	special_category_accepted = models.BooleanField(null=True)

	# define the function that will return the SITE name as the object reference
	def __str__(self):
		return self.invitation_step_type.display_name + ' for ' + \
		self.invitation.person.full_name() + ' on ' \
		+ self.datetime_created.strftime('%b %d %Y')

	class Meta:
		verbose_name_plural = 'invitation steps'
		ordering = (['invitation_step_type__order'])

	# return data for display
	def get_display_data(self):
		# initialise variables
		step_data = 'No data'
		data_type = self.invitation_step_type.data_type
		# get the data depending on the type
		if self.step_data:
			if data_type == 'string':
				step_data = self.step_data
			elif data_type == 'table' or data_type == 'fields':
				step_data = json.loads(self.step_data)
			elif data_type == 'signature':
				step_data = reverse('display_signature',args=[self.pk])
		# return the results
		return step_data

	# method to display the signature
	def get_signature(self):
		# initialise variables
		signature_image = False
		# if we have a signature, build a base64 string
		if self.signature:
			signature_image = draw_signature(self.signature)
		# return the results
		return signature_image