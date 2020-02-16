from django.db import models
from .django_extensions import DataAccessMixin
from .utilities import extract_id, add_description
from datetime import datetime, date, timedelta
from django.db.models import Sum

# Site model: provides configuration for the site
class Site(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	navbar_background = models.CharField(max_length=50, blank=True)
	navbar_text = models.CharField(max_length=50, blank=True, null=True, default=None)
	messages = models.BooleanField(default=False)
	dob_offset = models.IntegerField(default=0)
	# define the function that will return the SITE name as the object reference
	def __str__(self):
		return self.name

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
	description = models.TextField(max_length=500)
	event_type = models.ForeignKey(Event_Type, default=1, on_delete=models.SET_DEFAULT)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	location = models.CharField(max_length=100)
	ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.SET_NULL)
	areas = models.ManyToManyField(Area)
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

# Question model: represents questions
class Question(DataAccessMixin,models.Model):
	question_text = models.CharField(max_length=150)
	notes = models.BooleanField(default=False)
	notes_label = models.CharField(max_length=30, default='Notes')
	# define the function that will return the question text as the object reference
	def __str__(self):
		return self.question_text
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'questions'

# Option model: represents the options which can be used to answer a question
class Option(DataAccessMixin,models.Model):
	option_label = models.CharField(max_length=50)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
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
	# and a set of stats funcions
	def registered_count(self):
		# return the count of events the person has registered for
		return self.event_registration_set.filter(registered=True).count()
	# count the apologies
	def apologies_count(self):
		# return the count of events the person has apologised for
		return self.event_registration_set.filter(apologies=True).count()
	# and the participations
	def participated_count(self):
		# return the count of events the person has participated in
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
		# set a blank trained role
		trained_role = 'none'
		# and a blank in_project
		include_people = 'in_project'
		# and blank names
		names = False
		# check whether we have a trained role in the search request
		if 'trained_role' in kwargs.keys():
			# pull the trained role out of the kwargs
			trained_role = kwargs.pop('trained_role')
		# check whether we have a trained role in the search request
		if 'include_people' in kwargs.keys():
			# pull the include all out of the kwargs
			include_people = kwargs.pop('include_people')
		# check whether we have names in the search request
		if 'names' in kwargs.keys():
			# pull the include all out of the kwargs
			names = kwargs.pop('names')
		# call the mixin method
		results = super().search(**kwargs)
		# if we have a trained role, filter by the trained role
		if trained_role != 'none':
			# get the role type
			role_type = Role_Type.objects.get(pk=int(extract_id(trained_role)))
			# do the filter
			results = results.filter(trained_roles=role_type)
			# and check whether we want active only
			if 'active' in trained_role:
				# got through the people
				for person in results:
					# attempt to get the active record
					if not person.trained_role_set.filter(role_type=role_type,active=True).exists():
						# exclude the person
						results = results.exclude(pk=person.pk)
		# if we should only include people in the project exclude those who have left
		if include_people == 'in_project' or include_people == '':
			# do the filter
			results = results.exclude(ABSS_end_date__isnull=False)
		# otherwise check whether we only want people in the project
		elif include_people == 'left_project':
			# do the filter
			results = results.exclude(ABSS_end_date__isnull=True)
		# check to see whether we have names
		if names:
			# start by splitting on spaces
			name_list = names.split(' ')
			# go through the names
			for name in name_list:
				# attempt to find the name in the various name fields
				results = results.filter(first_name__icontains=name) \
							| results.filter(last_name__icontains=name) \
							| results.filter(other_names__icontains=name)
		# order the results by name
		results = results.order_by('last_name','first_name')
		# return the results
		return results

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
												('period','period')
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
											('last_calendar_year','last_calendar_year')
											],
								default='',
								blank=True
								)
	# define the function that will return a description of the filter
	def __str__(self):
		# build the description depending on the type of filter
		if self.filter_type == 'boolean':
			filter_str = self.term + ' = '  + str(self.boolean_value)
		elif self.filter_type == 'period':
			filter_str = self.term + ' within ' + self.period
		else: 
			filter_str = self.term + ' = '  + self.string_value
		#return the value
		return filter_str
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'filter specs'
		ordering = ['term']

# Dashboard_Column model: used to define a dashboard column
class Dashboard_Panel_Column_Spec(DataAccessMixin,models.Model):
	name = models.CharField(max_length=50)
	title = models.CharField(max_length=50, default='', blank=True)
	count_field = models.CharField(max_length=50)
	filters = models.ManyToManyField(Filter_Spec, blank=True)
	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'dashboard panel column specs'
		ordering = ['title']

# Dashboard_Panel_Spec model: used to define a dashboard panel
class Dashboard_Panel_Spec(DataAccessMixin,models.Model):
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
	row_name_field = models.CharField(max_length=50)
	sort_field = models.CharField(max_length=50, default='', blank=True)
	totals = models.BooleanField(default=False)
	display_zeroes = models.BooleanField(default=False)
	model = models.CharField(max_length=50)
	filters = models.ManyToManyField(Filter_Spec, blank=True)
	columns = models.ManyToManyField(Dashboard_Panel_Column_Spec, through='Dashboard_Panel_Column_Inclusion')
	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'dashboard panel specs'
		ordering = ['name']

# Dashboard_Column model: used to define a dashboard column
class Dashboard_Panel_Column_Inclusion(DataAccessMixin,models.Model):
	order = models.IntegerField(default=0)
	dashboard_panel_spec = models.ForeignKey(Dashboard_Panel_Spec, on_delete=models.CASCADE)
	dashboard_panel_column_spec = models.ForeignKey(Dashboard_Panel_Column_Spec, on_delete=models.CASCADE)
	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.dashboard_panel_column_spec.name + ' in ' + self.dashboard_panel_spec.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'dashboard panel column inclusions'


