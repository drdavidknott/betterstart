from django.db import models

# Family model: represents a family.
# Has a many to many relationship with Person
class Family(models.Model):
	description = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.description
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'families'

# Ethnicity model: represents the list of valid ethnicities.
# Has a one to many relationship with Person
class Ethnicity(models.Model):
	description = models.CharField(max_length=50)
	# define the function that will return the ethnicity name as the object reference
	def __str__(self):
		return self.description
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'ethnicities'

# Role_Type model: represents different types of role that a person can play, including staff, volunteer, parent, child ec.
# This is reference data.
class Role_Type(models.Model):
	role_type_name = models.CharField(max_length=50)
	use_for_events = models.BooleanField(default=False)
	use_for_people = models.BooleanField(default=False)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.role_type_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'role types'

# ABSS type model: represents different types of relationship that a person can have with ABSS
# This is reference data.
class ABSS_Type(models.Model):
	name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'ABSS types'

# Age status type model: represents the person's status dependent on age (adult or child)
# This is reference data.
class Age_Status(models.Model):
	status = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.status
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'Age statuses'

# Capture Type model: represents the way in which the person's details were captured
class Capture_Type(models.Model):
	capture_type_name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.capture_type_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'capture types'

# Children Centre model: represents Children Centres
# This is reference data.
class Children_Centre(models.Model):
	children_centre_name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.children_centre_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'children centres'

# Area model: represents valid areeas (which contain wards)
class Area(models.Model):
	area_name = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.area_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'areas'

# Wards model: represents valid wards (which contain post codes)
class Ward(models.Model):
	ward_name = models.CharField(max_length=50)
	area = models.ForeignKey(Area, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.ward_name + ' (' + self.area.area_name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'wards'

# Post Code model: represents valid post codes
class Post_Code(models.Model):
	post_code = models.CharField(max_length=10)
	ward = models.ForeignKey(Ward, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.post_code + ' (' + self.ward.ward_name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'post codes'

# Street model: represents valid streets aligned to post codes
class Street(models.Model):
	name = models.CharField(max_length=100)
	post_code = models.ForeignKey(Post_Code, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.name + ' (' + self.post_code.post_code + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'streets'

# Address model: represents addresses where people live
class Address(models.Model):
	house_name_or_number = models.CharField(max_length=50)
	street = models.CharField(max_length=50)
	town = models.CharField(max_length=50)
	post_code = models.ForeignKey(Post_Code, default=1, on_delete=models.SET_DEFAULT)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.house_name_or_number + ' ' + self.street + ', ' + self.town + ' ' + self.post_code.post_code
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'addresses'

# Event Type model: represents categories of event types.
# This is reference data
class Event_Category(models.Model):
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
class Event_Type(models.Model):
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
class Event(models.Model):
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=500)
	event_type = models.ForeignKey(Event_Type, default=1, on_delete=models.SET_DEFAULT)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	location = models.CharField(max_length=100)
	# define the function that will return the event name, date and time as the object reference
	def __str__(self):
		return self.name + ' at ' + str(self.start_time) + ' on '  + str(self.date) + \
				' (' + self.event_type.name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'events'

# Question model: represents questions
class Question(models.Model):
	question_text = models.CharField(max_length=150)
	# define the function that will return the question text as the object reference
	def __str__(self):
		return self.question_text
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'questions'

# Option model: represents the options which can be used to answer a question
class Option(models.Model):
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
class Person(models.Model):
	first_name = models.CharField(max_length=50)
	middle_names = models.CharField(max_length=50, default='', blank=True)
	last_name = models.CharField(max_length=50)
	email_address = models.CharField(max_length=50, default='', blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=25, default='', blank=True)
	notes = models.TextField(max_length=1000, default='', blank=True)
	relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False)
	default_role = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	children_centres = models.ManyToManyField(Children_Centre, through='CC_Registration')
	addresses = models.ManyToManyField(Address, through='Residence')
	events = models.ManyToManyField(Event, through='Event_Registration')
	answers = models.ManyToManyField(Option, through='Answer')
	english_is_second_language = models.BooleanField(default=False)
	pregnant = models.BooleanField(default=False)
	due_date = models.DateField(null=True, blank=True)
	ethnicity = models.ForeignKey(Ethnicity, default=1, on_delete=models.SET_DEFAULT)
	capture_type = models.ForeignKey(Capture_Type, default=1, on_delete=models.SET_DEFAULT)
	families = models.ManyToManyField(Family, blank=True)
	savs_id = models.IntegerField(blank=True, null=True)
	ABSS_type = models.ForeignKey(ABSS_Type, default=1, on_delete=models.SET_DEFAULT)
	age_status = models.ForeignKey(Age_Status, default=1, on_delete=models.SET_DEFAULT)
	trained_champion = models.BooleanField(default=False)
	active_champion = models.BooleanField(default=False)
	house_name_or_number = models.CharField(max_length=50, default='', blank=True)
	street = models.ForeignKey(Street, null=True, blank=True, on_delete=models.SET_NULL)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.first_name + ' ' + self.last_name
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'people'
	# and a function to return the full name
	def full_name(self):
		return self.first_name + ' ' + self.middle_names + ' ' + self.last_name

# Relationship_Type model: represents different types of relationship
# This is reference data.
class Relationship_Type(models.Model):
	relationship_type = models.CharField(max_length=50)
	relationship_counterpart = models.CharField(max_length=50)
	# define the function that will return the person name as the object reference
	def __str__(self):
		return self.relationship_type
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'relationship types'

# Relationship model: represents a relationship between two people.
# This is an intermediate model for a many to many relationship between two Person objects.
class Relationship(models.Model):
	relationship_from = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rel_from')
	relationship_to = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rel_to')
	relationship_type = models.ForeignKey(Relationship_Type, on_delete=models.CASCADE)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.relationship_from.first_name + ' ' + self.relationship_from.last_name + \
			' is the ' + self.relationship_type.relationship_type + ' of ' + \
				self.relationship_to.first_name + ' ' + self.relationship_to.last_name

# Role model: records that a person plays a particular type of role
# Records whether the person has been trained in the role, and whether the person is active in the role
class Role(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	role_type = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	trained = models.BooleanField()
	active = models.BooleanField()
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ': ' + self.role_type.role_type_name \
			+ ' (' + self.trained_status() + ' and ' + self.active_status() + ')'
	# define a function for returning active status as a string
	def active_status(self):
		if self.active:
			return 'active'
		else:
			return 'inactive'
	# define a function for returing trained status as a string
	def trained_status(self):
		if self.trained:
			return 'trained'
		else:
			return 'untrained'

# Role history model: records that a person has played a particular type of role
# Records whether the person has been trained in the role, and whether the person is active in the role
class Role_History(models.Model):
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
class CC_Registration(models.Model):
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

# Residence: records that a person is resident at an address.
class Residence(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	address = models.ForeignKey(Address, on_delete=models.CASCADE)
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ' lives at ' + \
				self.address.house_name_or_number + ' ' + self.address.street + ', ' + self.address.town + ' ' + \
				self.address.post_code.post_code + ' (' + self.address.post_code.ward.ward_name + ', ' + \
				self.address.post_code.ward.area.area_name + ')'
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'residences'

# Event Registration: records that a person registered for or participated in an event.
class Event_Registration(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)
	role_type = models.ForeignKey(Role_Type, on_delete=models.CASCADE)
	registered = models.BooleanField()
	participated = models.BooleanField()
	# define the function that will return a string showing the relationship as the object reference
	def __str__(self):
		return self.person.first_name + ' ' + self.person.last_name + ': ' + self.role_type.role_type_name \
			+ ' at ' + self.event.name + ' on ' + str(self.event.date) + \
			' (' + self.registered_status() + ' and ' + self.participated_status() + ')'
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
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'event registrations'

# Answer model: represents the answer to a question, using an option
class Answer(models.Model):
	option = models.ForeignKey(Option, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	# define the function that will return the option label as the object reference
	def __str__(self):
		return self.question.question_text + ': ' + self.option.option_label
	# set the name to be used in the admin console
	class Meta:
		verbose_name_plural = 'answers'