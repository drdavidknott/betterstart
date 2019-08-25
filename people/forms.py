# Define the forms that we will use in the volunteering appliction.

from django import forms
from django.contrib.auth.models import User
from people.models import Role_Type, Age_Status, ABSS_Type, Role_Type, Ethnicity, Relationship_Type, Event_Type, \
							Event_Category, Ward, Area
from django.contrib.auth import authenticate
import datetime

def role_type_choices(role_types):
	# set the choice field for role types
	role_type_list = []
	# go through the role types
	for role_type in role_types:
		# append a list of value and display value to the list
		role_type_list.append((role_type.pk, role_type.role_type_name))
	# return the list
	return role_type_list

def build_choices(choice_class,choice_field,default=False,default_label=''):
	# create a blank list
	choice_list = []
	# check whether we have a default
	if default:
		# add a default
		choice_list.append((0,default_label))
	# go through the choices, based on the supplied class
	for choice in choice_class.objects.all().order_by(choice_field):
		# append a list of value and display value to the list
		choice_list.append((choice.pk, getattr(choice,choice_field)))
	# return the list
	return choice_list

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
	age_status = forms.ChoiceField(
									label="Age status",
									widget=forms.Select(attrs={'class' : 'form-control'}))

	def __init__(self, *args, **kwargs):
		# over-ride the __init__ method to set the choices
		# call the built in constructor
		super(AddPersonForm, self).__init__(*args, **kwargs)
		# set the choice fields
		self.fields['age_status'].choices = build_choices(choice_class=Age_Status,choice_field='status')

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
									initial='',
									required=False,
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	email_address = forms.CharField(
									label="Email",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	home_phone = forms.CharField(
									label="Home phone number",
									max_length=50,
									required = False,
									widget=forms.NumberInput(attrs={'class' : 'form-control',}))
	mobile_phone = forms.CharField(
									label="Mobile phone number",
									max_length=50,
									required = False,
									widget=forms.NumberInput(attrs={'class' : 'form-control',}))
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
									label="Age status",
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
		self.fields['age_status'].choices = build_choices(choice_class=Age_Status,choice_field='status')
		self.fields['ABSS_type'].choices = build_choices(choice_class=ABSS_Type,choice_field='name')
		self.fields['ethnicity'].choices = build_choices(choice_class=Ethnicity,choice_field='description')
		# get the age status
		if self.is_bound:
			# we have an age status, so get the age status object
			age_status = Age_Status.objects.get(id=int(self['age_status'].value()))
			# get the role types via the age status
			self.fields['role_type'].choices = role_type_choices(
												age_status.role_types.filter(use_for_people=True).order_by('role_type_name'))
			# hide fields if they should not be shown by age status
			if not age_status.can_have_contact_details:
				# hide the contact fields
				self.fields['email_address'].widget = forms.HiddenInput()
				self.fields['home_phone'].widget = forms.HiddenInput()
				self.fields['mobile_phone'].widget = forms.HiddenInput()
			# and the champion fields
			if not age_status.can_be_parent_champion:
				# hide the parent champion fields
				self.fields['trained_champion'].widget = forms.HiddenInput()
				self.fields['active_champion'].widget = forms.HiddenInput()
			# and the pregnancy fields
			if not age_status.can_be_pregnant:
				# hide the parent champion fields
				self.fields['pregnant'].widget = forms.HiddenInput()
				self.fields['due_date'].widget = forms.HiddenInput()
		else:
			# get the full set of role types
			self.fields['role_type'].choices = role_type_choices(
												Role_Type.objects.filter(use_for_people=True).order_by('role_type_name'))
		# hide fields depending on age status

	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ProfileForm, self).is_valid()
		# now perform the additional checks
		# start by checking whether the active champion is set without the trained champion
		if self.cleaned_data['active_champion'] and not self.cleaned_data['trained_champion']:
			#set the error message
			self._errors['active_champion'] = "Only trained champions can be active champions."
			# set the validity flag
			valid = False
		# now check whether we have a child under four whose date of birth is more than four years ago
		# get the age status
		age_status = Age_Status.objects.get(id=self.cleaned_data['age_status'])
		# get today's date
		today = datetime.date.today()
		# now check the age
		if self.cleaned_data['date_of_birth'] != None and \
			self.cleaned_data['date_of_birth'] < today.replace(year=today.year-age_status.maximum_age):
			#set the error message
			self._errors['date_of_birth'] = "Must be less than " + str(age_status.maximum_age) + " years old."
			# set the validity flag
			valid = False
		# check whether the only error is due to a change in age status: if so, set the default
		if 'role_type' in self._errors.keys() and len(self._errors) == 1:
			# set the value to the default
			self.cleaned_data['role_type'] = str(age_status.default_role_type.pk)
			# reset the valid flag
			valid = True
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
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width'}))
	ABSS_type = forms.ChoiceField(
									label="ABSS",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width'}))
	age_status = forms.ChoiceField(
									label="Adult or Child",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width'}))
	champions = forms.ChoiceField(
									label="Champions",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(PersonSearchForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['role_type'].choices = [(0,'Any')] + \
											role_type_choices(Role_Type.objects.filter(use_for_people=True))
		self.fields['ABSS_type'].choices = build_choices(
															choice_class=ABSS_Type,
															choice_field='name',
															default=True,
															default_label='Any')
		self.fields['age_status'].choices = build_choices(
															choice_class=Age_Status,
															choice_field='status',
															default=True,
															default_label='Any')
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
	# Define the fields that we need in the form to capture the basics of the person's profile
	first_name = forms.CharField(
									label="First name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	middle_names = forms.CharField(
									label="Middle names",
									max_length=50,
									required=False,
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	age_status = forms.ChoiceField(
									label="Age status",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	relationship_type = forms.ChoiceField(
									label="Relationship",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the fields out of the parameters
		first_name = kwargs.pop('first_name')
		last_name = kwargs.pop('last_name')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['relationship_type'].choices = build_choices(choice_class=Relationship_Type,
																	choice_field='relationship_type')
		self.fields['relationship_type'].initial = Relationship_Type.objects.get(relationship_type='parent').pk
		self.fields['age_status'].choices = build_choices(choice_class=Age_Status,choice_field='status')
		self.fields['age_status'].initial = Age_Status.objects.get(status='Child under four').pk
		self.fields['first_name'].initial = first_name
		self.fields['last_name'].initial = last_name

class AddRelationshipToExistingPersonForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the person list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddRelationshipToExistingPersonForm, self).__init__(*args, **kwargs)
		# now go through the people and build fields
		for person in people:
			# set the field name
			field_name = 'relationship_type_' + str(person.pk)
			# create the field
			self.fields[field_name]= forms.ChoiceField(
										label="Relationship",
										widget=forms.Select(),
										choices=build_choices(choice_class=Relationship_Type,
																	choice_field='relationship_type',
																	default=True,
																	default_label='none')
										)

class EditExistingRelationshipsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the relationship types list out of the parameters
		relationships = kwargs.pop('relationships')
		# call the built in constructor
		super(EditExistingRelationshipsForm, self).__init__(*args, **kwargs)
		# now go through the people and build fields
		for person in relationships:
			# set the field name for the relationship type
			field_name = 'relationship_type_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.ChoiceField(
											label="Relationship",
											widget=forms.Select(),
											choices=build_choices(choice_class=Relationship_Type,
																	choice_field='relationship_type',
																	default=True,
																	default_label='none'),
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

class AddressToRelationshipsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the person list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddressToRelationshipsForm, self).__init__(*args, **kwargs)
		# now go through the people and build fields
		for person in people:
			# set the field name for applying the address
			field_name = 'apply_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Apply",
														required = False,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))

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
	location = forms.CharField(
									label="Location",
									max_length=50,
									required=False, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	ward = forms.ChoiceField(
									label="Ward",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(EventForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['event_type'].choices = build_choices(choice_class=Event_Type,choice_field='name')
		# and for the wards
		self.fields['ward'].choices = build_choices(choice_class=Ward,
													choice_field='ward_name',
													default=True,
													default_label='None')
		# and the initial choice for the ward
		self.fields['ward'].initial = 0
		# now go through the areas and build fields
		for area in Area.objects.filter(use_for_events=True).order_by('area_name'):
			# set the field name for the area
			field_name = 'area_' + str(area.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = area.area_name,
														required = False,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'})
														)
			# set the field name for participation

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
			# if this is a parent, make them a carer
			if person.default_role.role_type_name == 'Parent':
				# swith the role type id to carer
				role_type_id = Role_Type.objects.get(role_type_name='Carer').pk
			# check whether the role type exists
			elif not person.default_role.use_for_events:
				# set the role type to the default for the age status
				role_type_id = person.age_status.role_types.get(default_for_age_status=True)
			# otherwise set the id
			else:
				# set the id
				role_type_id = person.default_role.pk
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(),
														choices=role_type_choices(
																	person.age_status.role_types.filter(use_for_people=True).order_by('role_type_name')),
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
														widget=forms.Select(attrs={'class' : 'form-control'}),
														initial=registration.role_type.pk,
														choices=role_type_choices(
																	registration.person.age_status.role_types.filter(use_for_people=True).order_by('role_type_name')),
														)

class EventSearchForm(forms.Form):
	# Define the fields that we need in the form.
	name = forms.CharField(
									label="Event name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	event_category = forms.ChoiceField(
									label="Event Category",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width',}))
	event_type = forms.ChoiceField(
									label="Event Type",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width',}))
	ward = forms.ChoiceField(
									label="Ward",
									widget=forms.Select(attrs={'class' : 'form-control select-fixed-width',}))
	date_from = forms.DateField(
									label="From",
									required=False,
									widget=forms.DateInput(format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	date_to = forms.DateField(
									label="To",
									required=False,
									widget=forms.DateInput(format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(EventSearchForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['event_type'].choices = build_choices(choice_class=Event_Type,
															choice_field='name',
															default=True,
															default_label='Any')
		# set the choices
		self.fields['event_category'].choices = build_choices(choice_class=Event_Category,
																choice_field='name',
																default=True,
																default_label='Any')
		# set the wards
		self.fields['ward'].choices = build_choices(choice_class=Ward,
													choice_field='ward_name',
													default=True,
													default_label='Any')

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
			# and the notes names
			notes_name = 'notes_' + str(question.pk)
			# and the spacer name
			spacer_name = 'spacer_' + str(question.pk)
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
															widget=forms.Select(attrs={'class' : 'form-control'}),
															choices=option_list,
															initial=question.answer
															)
				# if the question has notes, also create a notes field
				if question.notes:
					# create the field
					self.fields[notes_name]= forms.CharField(
											label=question.notes_label,
											max_length=50,
											widget=forms.TextInput(attrs={'class' : 'form-control',}),
											required=False,
											initial=question.note
											)
				# otherwise create a spacer field
				else:
					self.fields[spacer_name]= forms.CharField(
											label='spacer',
											max_length=50,
											widget=forms.HiddenInput(attrs={'class' : 'form-control',}),
											initial='spacer'
											)
