# Define the forms that we will use in the volunteering appliction.

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import datetime

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
	middle_names = forms.CharField(
									label="Middle Name",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Surname",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		role_types = kwargs.pop('role_types')
		# call the built in constructor
		super(AddPersonForm, self).__init__(*args, **kwargs)
		# set the choice field for role types
		role_type_list = []
		# set an initial value
		initial = 1
		# go through the role types
		for role_type in role_types:
			# append a list of value and display value to the list
			role_type_list.append((role_type.pk, role_type.role_type_name))
			# also see whether we have the UNKKNOWN role type
			if role_type.role_type_name == 'UNKNOWN':
				# set the initial value
				initial = role_type.pk
		# set the choices
		self.fields['role_type'].choices = role_type_list
		# set the initial value
		self.fields['role_type'].initial = initial

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
									widget=forms.DateInput(attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
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
									widget=forms.DateInput(attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}))
	
	def __init__(self, *args, **kwargs):
		# over-ride the __init__ method to set the choices
		# pull the choices fields out of the parameters
		ethnicities = kwargs.pop('ethnicities')
		role_types = kwargs.pop('role_types')
		# call the built in constructor
		super(ProfileForm, self).__init__(*args, **kwargs)
		# set the choice field for ethnicities
		ethnicity_list = []
		# go through the ethnicities
		for ethnicity in ethnicities:
			# append a list of value and display value to the list
			ethnicity_list.append((ethnicity.pk, ethnicity.description))
		# set the choices
		self.fields['ethnicity'].choices = ethnicity_list
		# set the choice field for role types
		role_type_list = []
		# go through the role types
		for role_type in role_types:
			# append a list of value and display value to the list
			role_type_list.append((role_type.pk, role_type.role_type_name))
		# set the choices
		self.fields['role_type'].choices = role_type_list

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
									widget=forms.DateInput(attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}))
	gender = forms.ChoiceField(
									label="Gender",
									choices=gender_choices,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	relationship_type = forms.ChoiceField(
									label="Relationship",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		role_types = kwargs.pop('role_types')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choice field for ethnicities
		relationship_type_list = []
		# go through the ethnicities
		for relationship_type in relationship_types:
			# append a list of value and display value to the list
			relationship_type_list.append((relationship_type.pk, relationship_type.relationship_type))
		# set the choices
		self.fields['relationship_type'].choices = relationship_type_list
		# set the choice field for role types
		role_type_list = []
		# go through the role types
		for role_type in role_types:
			# append a list of value and display value to the list
			role_type_list.append((role_type.pk, role_type.role_type_name))
		# set the choices
		self.fields['role_type'].choices = role_type_list


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
	# Define the fields that we need in the form to capture the address
	house_name_or_number = forms.CharField(
									label="House name or number",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	street = forms.CharField(
									label="Street",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))

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

class AddEventForm(forms.Form):
	# Define the fields that we need in the form to capture the event
	name = forms.CharField(
									label="Name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	description = forms.CharField(
									label="Description",
									max_length=1000,
									widget=forms.Textarea(attrs={'class' : 'form-control', 'cols' : 100, 'rows' : 6}))
	event_type = forms.ChoiceField(
									label="Event Type",
									widget=forms.Select())
	date = forms.DateField(
									label="Date",
									widget=forms.DateInput(attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}))
	start_time = forms.TimeField(
									label="Start Time",
									widget=forms.TimeInput(attrs={'class' : 'form-control',}))
	end_time = forms.TimeField(
									label="Start Time",
									widget=forms.TimeInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		event_types = kwargs.pop('event_types')
		# call the built in constructor
		super(AddEventForm, self).__init__(*args, **kwargs)
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
		# pull the role types list out of the parameters
		role_types = kwargs.pop('role_types')
		# pull the people list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddRegistrationForm, self).__init__(*args, **kwargs)
		# set the choice field for role types
		role_type_list = []
		# go through the role types to build the options
		for role_type in role_types:
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
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(),
														choices=role_type_list,
														initial=person.default_role.pk
														)

class EditRegistrationForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the role types list out of the parameters
		role_types = kwargs.pop('role_types')
		# pull the registrations list out of the parameter
		registrations = kwargs.pop('registrations')
		# call the built in constructor
		super(EditRegistrationForm, self).__init__(*args, **kwargs)
		# set the choice field for role types
		role_type_list = []
		# go through the role types to build the options
		for role_type in role_types:
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
