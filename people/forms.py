# Define the forms that we will use in the volunteering appliction.

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import datetime

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
	
	def __init__(self, *args, **kwargs):
		# over-ride the __init__ method to set the choices
		# pull the choices field out of the parameters
		ethnicities = kwargs.pop('ethnicities')
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

class RelationshipSearchForm(forms.Form):
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
	relationship_type = forms.ChoiceField(
									label="Relationship",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the choices field out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choice field for ethnicities
		relationship_type_list = []
		# go through the ethnicities
		for relationship_type in relationship_types:
			# append a list of value and display value to the list
			relationship_type_list.append((relationship_type.pk, relationship_type.relationship_type))
			# if we have the child relationship type, set initial
			if relationship_type.relationship_type == 'child':
				# set the value
				self.fields['relationship_type'].initial = relationship_type.pk
		# set the choices
		self.fields['relationship_type'].choices = relationship_type_list


class AddRelationshipToExistingPersonForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the relationship types list out of the parameters
		relationship_types = kwargs.pop('relationship_types')
		# pull the person list out of the parameter
		people = kwargs.pop('people')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choice field for relationship types
		relationship_type_list = []
		# add an initial option
		relation.append(0,'none')
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
														choices=relationship_type_list
														)