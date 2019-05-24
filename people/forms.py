# Define the forms that we will use in the volunteering appliction.

from django import forms
from django.contrib.auth.models import User
from people.models import Role_Type, Age_Status, ABSS_Type, Role_Type, Ethnicity, Relationship_Type
from django.contrib.auth import authenticate
import datetime

def relationship_type_choices(relationship_types):
	# set the choice field for relationship types
	relationship_type_list = []
	# go through the relationship types
	for relationship_type in relationship_types:
		# append a list of value and display value to the list
		relationship_type_list.append((relationship_type.pk, relationship_type.relationship_type))
	# return the list
	return relationship_type_list

def age_status_choices(age_statuses):
	# set the choice field for age statuses
	age_status_list = []
	# go through the age statuses
	for age_status in age_statuses:
		# append a list of value and display value to the list
		age_status_list.append((age_status.pk, age_status.status))
	# return the list
	return age_status_list

def ABSS_type_choices(ABSS_types):
	# set the choice field for ABSS types
	ABSS_type_list = []
	# go through the ABSS types
	for ABSS_type in ABSS_types:
		# append a list of value and display value to the list
		ABSS_type_list.append((ABSS_type.pk, ABSS_type.name))
	# return the choices
	return ABSS_type_list

def role_type_choices(role_types):
	# set the choice field for role types
	role_type_list = []
	# go through the role types
	for role_type in role_types:
		# append a list of value and display value to the list
		role_type_list.append((role_type.pk, role_type.role_type_name))
	# return the list
	return role_type_list

def ethnicity_choices(ethnicities):
	# set the choice field for ethnicities
	ethnicity_list = []
	# go through the ethnicities
	for ethnicity in ethnicities:
		# append a list of value and display value to the list
		ethnicity_list.append((ethnicity.pk, ethnicity.description))
	# return the list
	return ethnicity_list

class LoginForm(forms.Form):
	# Define the fields that we need in the form.
	email_address = forms.EmailField(
										label="Email address",
										max_length=100,
										widget=forms.EmailInput(attrs={'class' : 'form-control'}))
	password = forms.CharField(
										label="Password",
										max_length=30,
										widget=forms.PasswordInput(attrs={'class' : 'form-control'}))

class AddPersonForm(forms.Form):
	# Define the fields that we need in the form.
	first_name = forms.CharField(
									label="First name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Surname",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))

class ProfileForm(forms.Form):
	# Define the choices for gender
	gender_choices = (
					('Not specified','Not specified'),
					('Male' , 'Male'),
					('Female' , 'Female'),
					)
	# Define the fields that we need in the form to capture the basics of the person's profile
	first_name = forms.CharField(
									label="First name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	middle_names = forms.CharField(
									label="Middle names",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	email_address = forms.CharField(
									label="Email",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	date_of_birth = forms.DateField(
									label="Date of birth",
									required=False,
									widget=forms.DateInput(	
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
        							input_formats=('%d/%m/%Y',))
	ABSS_type = forms.ChoiceField(
									label="ABSS Type",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	age_status = forms.ChoiceField(
									label="Adult or Child",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	trained_champion = forms.BooleanField(
									label = "Trained Parent Champion",
									required = False,
									widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	active_champion = forms.BooleanField(
									label = "Active Parent Champion",
									required = False,
									widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	ethnicity = forms.ChoiceField(
									label="Ethnicity",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	gender = forms.ChoiceField(
									label="Gender",
									required=False,
									choices=gender_choices,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	english_is_second_language = forms.BooleanField(
									label = "English is a second language",
									required = False,
									widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	pregnant = forms.BooleanField(
									label = "Pregnant (or partner is pregnant)",
									required = False,
									widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	due_date = forms.DateField(
									label="Pregnancy due date",
									required=False,
									widget=forms.DateInput(
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	
	def __init__(self, *args, **kwargs):
		# over-ride the __init__ method to set the choices
		# call the built in constructor
		super(ProfileForm, self).__init__(*args, **kwargs)
		# set the choice fields
		self.fields['age_status'].choices = age_status_choices(Age_Status.objects.all())
		self.fields['role_type'].choices = role_type_choices(Role_Type.objects.filter(use_for_people=True))
		self.fields['ABSS_type'].choices = ABSS_type_choices(ABSS_Type.objects.all())
		self.fields['ethnicity'].choices = ethnicity_choices(Ethnicity.objects.all())
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ProfileForm, self).is_valid()
		# set the return value if the built in validation function fails
		if valid == False:
			return valid
		# now perform the additional checks
		# start by checking whether the active champion is set without the trained champion
		if self.cleaned_data['active_champion'] and not self.cleaned_data['trained_champion']:
			#set the error message
			self._errors['active_champion'] = "Only trained champions can be active champions."
			# set the validity flag
			valid = False
		# return the result
		return valid

class PersonSearchForm(forms.Form):
	# Define the fields that we need in the form.
	first_name = forms.CharField(
									label="First name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Surname",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ABSS_type = forms.ChoiceField(
									label="ABSS",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	age_status = forms.ChoiceField(
									label="Adult or Child",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	champions = forms.ChoiceField(
									label="Parent Champions",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(PersonSearchForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['role_type'].choices = [(0,'Any')] + \
											role_type_choices(Role_Type.objects.filter(use_for_people=True))
		self.fields['ABSS_type'].choices = [(0,'Any')] + ABSS_type_choices(ABSS_Type.objects.all())
		self.fields['age_status'].choices = [(0,'Any')] + age_status_choices(Age_Status.objects.all())
		self.fields['champions'].choices = [(0,'N/A'),('trained','Trained Champions'),('active','Active Champions')]

class PersonNameSearchForm(forms.Form):
	# Define the fields that we need in the form.
	first_name = forms.CharField(
									label="First name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Surname",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))

class AddRelationshipForm(forms.Form):
	# Define the choices for gender
	gender_choices = (
					('Not specified','Not specified'),
					('Male' , 'Male'),
					('Female' , 'Female'),
					)
	# Define the fields that we need in the form to capture the basics of the person's profile
	first_name = forms.CharField(
									label="First name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	middle_names = forms.CharField(
									label="Middle names",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	date_of_birth = forms.DateField(
									label="Date of birth",
									widget=forms.DateInput(
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	gender = forms.ChoiceField(
									label="Gender",
									choices=gender_choices,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ABSS_type = forms.ChoiceField(
									label="ABSS",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	age_status = forms.ChoiceField(
									label="Adult or Child",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	relationship_type = forms.ChoiceField(
									label="Relationship",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices fields out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		role_types = kwargs.pop('role_types')
		ABSS_types = kwargs.pop('ABSS_types')
		age_statuses = kwargs.pop('age_statuses')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['relationship_type'].choices = relationship_type_choices(relationship_types)
		self.fields['age_status'].choices = age_status_choices(age_statuses)
		self.fields['role_type'].choices = role_type_choices(role_types)
		self.fields['ABSS_type'].choices = ABSS_type_choices(ABSS_types)

class AddRelationshipToExistingPersonForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the relationship types list out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		# pull the person list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddRelationshipToExistingPersonForm, self).__init__(*args, **kwargs)
		# set the choice field for relationship types
		relationship_type_list = []
		# add an initial option
		relationship_type_list.append((0,'none'))
		# go through the relationship types to build the options
		for relationship_type in relationship_types:
			# append a list of value and display value to the list
			relationship_type_list.append((relationship_type.pk, relationship_type.relationship_type))
		# now go through the people and build fields
		for person in people:
			# set the field name
			field_name = 'relationship_type_' + str(person.pk)
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Relationship",
														widget=forms.Select(),
														choices=relationship_type_list,
														)

class EditExistingRelationshipsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the relationship types list out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		# pull the relationship list out of the parameters
		relationships = kwargs.pop('relationships')
		# call the built in constructor
		super(EditExistingRelationshipsForm, self).__init__(*args, **kwargs)
		# set the choice field for relationship types
		relationship_type_list = []
		# add an initial option
		relationship_type_list.append((0,'none'))
		# go through the relationship types to build the options
		for relationship_type in relationship_types:
			# append a list of value and display value to the list
			relationship_type_list.append((relationship_type.pk, relationship_type.relationship_type))
		# now go through the people and build fields
		for person in relationships:
			# set the field name for the relationship type
			field_name = 'relationship_type_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.ChoiceField(
														label="Relationship",
														widget=forms.Select(),
														choices=relationship_type_list,
														initial=person.relationship_type_pk
														)

class AddressSearchForm(forms.Form):
	# Define the fields that we need in the form to search for the address
	house_name_or_number = forms.CharField(
									label="House name or number",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	street = forms.CharField(
									label="Street",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	post_code = forms.CharField(
									label="Post Code",
									max_length=10,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(AddressSearchForm, self).is_valid()
		# set the return value if the built in validation function fails
		if valid == False:
			return valid
		# now perform the additional checks
		# start by checking whether we have either a post code or a street
		if not self.cleaned_data['post_code'] and not self.cleaned_data['street']:
			#set the error message
			self.add_error(None,'Either post code or street must be entered.')
			# set the validity flag
			valid = False
		# return the result
		return valid

class UpdateAddressForm(forms.Form):
	# Define the fields that we need in the form to update the address
	street_id = forms.CharField(
									label="Street",
									max_length=50,
									widget=forms.HiddenInput())
	house_name_or_number = forms.CharField(
											label="House Name or Number",
											max_length=50,
											widget=forms.HiddenInput())

class AddAddressForm(forms.Form):
	# Define the fields that we need in the form to capture the address
	house_name_or_number = forms.CharField(
									label="House name or number",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	street = forms.CharField(
									label="Street",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	town = forms.CharField(
									label="Town",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	post_code = forms.CharField(
									label="Post code",
									max_length=10,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))

class EventForm(forms.Form):
	# Define the fields that we need in the form to capture the event
	name = forms.CharField(
									label="Name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	description = forms.CharField(
									label="Description",
									max_length=1000,
									widget=forms.Textarea(attrs={'class' : 'form-control', 'cols' : 100, 'rows' : 6}))
	location = forms.CharField(
									label="Location",
									max_length=50,
									required=False, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	event_type = forms.ChoiceField(
									label="Event Type",
									widget=forms.Select())
	date = forms.DateField(
									label="Date",
									widget=forms.DateInput(																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	start_time = forms.TimeField(
									label="Start Time",
									widget=forms.TimeInput(attrs={'class' : 'form-control',}))
	end_time = forms.TimeField(
									label="End Time",
									widget=forms.TimeInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		event_types = kwargs.pop('event_types')
		# call the built in constructor
		super(EventForm, self).__init__(*args, **kwargs)
		# set the choice field for event types
		event_type_list = []
		# go through the event types
		for event_type in event_types:
			# append a list of value and display value to the list
			event_type_list.append((event_type.pk, event_type.name))
		# set the choices
		self.fields['event_type'].choices = event_type_list

class AddRegistrationForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the people list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddRegistrationForm, self).__init__(*args, **kwargs)
		# set the choice field for role types
		role_type_list = []
		# go through the role types to build the options
		for role_type in Role_Type.objects.filter(use_for_events=True):
			# append a list of value and display value to the list
			role_type_list.append((role_type.pk, role_type.role_type_name))
		# now go through the people and build fields
		for person in people:
			# set the field name for registration
			field_name = 'registered_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Registered",
														required = False,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
			# set the field name for participation
			field_name = 'participated_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Participated",
														required = False,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
			# set the field name for role
			field_name = 'role_type_' + str(person.pk)
			# TODO: change the approach below to an alternate relationship
			# if this is a parent, make them a carer
			if person.default_role.role_type_name == 'Parent':
				# swith the role type id to carer
				role_type_id = Role_Type.objects.get(role_type_name='Carer').pk
			# check whether the role type exists
			elif not person.default_role.use_for_events:
				# set the role type to UNKNOWN
				role_type_id = Role_Type.objects.get(role_type_name='UNKNOWN').pk
			# otherwise set the id
			else:
				# set the id
				role_type_id = person.default_role.pk
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(),
														choices=role_type_list,
														initial=role_type_id
														)

class EditRegistrationForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the registrations list out of the parameter
		registrations = kwargs.pop('registrations')
		# call the built in constructor
		super(EditRegistrationForm, self).__init__(*args, **kwargs)
		# set the choice field for role types
		role_type_list = []
		# go through the role types to build the options
		for role_type in Role_Type.objects.filter(use_for_events=True):
			# append a list of value and display value to the list
			role_type_list.append((role_type.pk, role_type.role_type_name))
		# now go through the registrations and build fields
		for registration in registrations:
			# set the field name for registration
			field_name = 'registered_' + str(registration.person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Registered",
														required = False,
														initial = registration.registered,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'})
														)
			# set the field name for participation
			field_name = 'participated_' + str(registration.person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Participated",
														required = False,
														initial = registration.participated,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
			# set the field name for role
			field_name = 'role_type_' + str(registration.person.pk)
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(),
														initial=registration.role_type.pk,
														choices=role_type_list,
														)

class EventSearchForm(forms.Form):
	# Define the fields that we need in the form.
	name = forms.CharField(
									label="Event name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	event_type = forms.ChoiceField(
									label="Event Type",
									widget=forms.Select())
	date_from = forms.DateField(
									label="From",
									required=False,
									widget=forms.DateInput(																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	date_to = forms.DateField(
									label="To",
									required=False,
									widget=forms.DateInput(																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		event_types = kwargs.pop('event_types')
		# call the built in constructor
		super(EventSearchForm, self).__init__(*args, **kwargs)
		# set the choice field for event types
		event_type_list = []
		# add the default choice
		event_type_list.append((0,'Any'))
		# go through the event types
		for event_type in event_types:
			# append a list of value and display value to the list
			event_type_list.append((event_type.pk, event_type.name))
		# set the choices
		self.fields['event_type'].choices = event_type_list

class AnswerQuestionsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the questions out of the parameters
		questions = kwargs.pop('questions')
		# call the built in constructor
		super(AnswerQuestionsForm, self).__init__(*args, **kwargs)
		# now through the questions and build fields
		for question in questions:
			# set the field name
			field_name = 'question_' + str(question.pk)
			# set an empty option list
			option_list = []
			# set the non-answer
			option_list.append((0,'No answer'))
			# now build the options
			for option in question.options:
				# set the value
				option_list.append((option.pk,option.option_label))
				# create the field
				self.fields[field_name]= forms.ChoiceField(
															label=question.question_text,
															widget=forms.Select(),
															choices=option_list,
															initial=question.answer
															)
