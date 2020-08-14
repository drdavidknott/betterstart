# Define the forms that we will use in the volunteering appliction.

from django import forms
from django.contrib.auth.models import User
from people.models import Role_Type, Age_Status, ABSS_Type, Role_Type, Ethnicity, Relationship_Type, Event_Type, \
							Event_Category, Ward, Area, Activity_Type, Venue_Type, Venue, Street, Site, Profile
from django.contrib.auth import authenticate
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Hidden, ButtonHolder, Field
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from .utilities import build_choices
from zxcvbn_password.fields import PasswordField, PasswordConfirmationField
from django.contrib.auth.hashers import check_password

def role_type_choices(role_types):
	# set the choice field for role types
	role_type_list = []
	# go through the role types
	for role_type in role_types:
		# append a list of value and display value to the list
		role_type_list.append((role_type.pk, role_type.role_type_name))
	# return the list
	return role_type_list

def check_relationship_types(relationship_types,to_person):
	# take a copy of the queryset
	valid_relationship_types = relationship_types
	# this person checks whether relationship types in a queryset are valid for the person
	for relationship_type in relationship_types:
		# check whether the relationship type is valid for the to person
		if not to_person.age_status.relationship_types.filter(
														relationship_counterpart=relationship_type.relationship_type
														):
			# remove the relationship type from the queryset
			valid_relationship_types = valid_relationship_types.exclude(pk=relationship_type.pk)
	# return the results
	return valid_relationship_types

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
	token = forms.CharField(
										label="Token",
										max_length=30,
										required=False,
										widget=forms.TextInput(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(LoginForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout, depending on whether the site required otp or not
		site = Site.objects.all().first()
		if site and (site.otp_required or site.otp_practice):
			self.helper.layout = Layout(
										Row(
											Column('email_address',css_class='form-group col-xs-12 mbt-0'),	
											),
										Row(
											Column('password',css_class='form-group col-xs-12 mbt-0'),	
											),
										Row(
											Column('token',css_class='form-group col-xs-12 mbt-0'),	
											),
										Row(
											Column(Submit('submit', 'Login'),css_class='col-xs-12 mb-0')
											)
										)
		else:
			self.helper.layout = Layout(
										Row(
											Column('email_address',css_class='form-group col-xs-12 mbt-0'),	
											),
										Row(
											Column('password',css_class='form-group col-xs-12 mbt-0'),	
											),
										Row(
											Column(Submit('submit', 'Login'),css_class='col-xs-12 mb-0')
											)
										)

class ChangePasswordForm(forms.Form):
	# Define the fields that we need in the form.
	old_password = forms.CharField(
										label="Password",
										max_length=30,
										widget=forms.PasswordInput(attrs={'class' : 'form-control'}))
	new_password = PasswordField()
	new_password_confirmation = PasswordConfirmationField(confirm_with='new_password',)
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the user out of the parameters
		self.user = kwargs.pop('user') if 'user' in kwargs.keys() else False
		# call the built in constructor
		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		self.helper.attrs['autocomplete'] = 'off'
		# and define the layout, depending on whether the site required otp or not
		self.helper.layout = Layout(
									Row(
										Column('old_password',css_class='form-group col-xs-12 mbt-0'),	
										),
									Row(
										Column(
												'new_password',
												css_class='form-group col-xs-12 mbt-0',
												autocomplete='off',
												),	
										),
									Row(
										Column('new_password_confirmation',css_class='form-group col-xs-12 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Submit'),css_class='col-xs-12 mb-0')
										)
									)

	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ChangePasswordForm, self).is_valid()
		# now perform the additional checks
		# check that the old password is correct
		if not check_password(
								password=self.cleaned_data['old_password'],
								encoded=self.user.password
								):
			self.add_error('old_password','Password is not correct.')
			valid = False
		# check that the password and the confirmation match
		if valid:
			if self.cleaned_data['new_password'] != self.cleaned_data['new_password_confirmation']:
				self.add_error('new_password_confirmation','Passwords do not match.')
				valid = False
		# return the result
		return valid

class ForgotPasswordForm(forms.Form):
	# Define the fields that we need in the form.
	email_address = forms.EmailField(
										label="Email address",
										max_length=100,
										widget=forms.EmailInput(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(ForgotPasswordForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout, depending on whether the site required otp or not
		self.helper.layout = Layout(
									Row(
										Column('email_address',css_class='form-group col-xs-12 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Submit'),css_class='col-xs-12 mb-0')
										)
									)

class ResetForgottenPasswordForm(forms.Form):
	# Define the fields that we need in the form.
	email_address = forms.EmailField(
										label="Email address",
										max_length=100,
										widget=forms.EmailInput(attrs={'class' : 'form-control'}))
	new_password = PasswordField()
	new_password_confirmation = PasswordConfirmationField(confirm_with='new_password',)
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the user out of the parameters
		self.reset_code = kwargs.pop('reset_code')
		# call the built in constructor
		super(ResetForgottenPasswordForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		self.helper.attrs['autocomplete'] = 'off'
		# and define the layout, depending on whether the site required otp or not
		self.helper.layout = Layout(
									Row(
										Column('email_address',css_class='form-group col-xs-12 mbt-0'),	
										),
									Row(
										Column(
												'new_password',
												css_class='form-group col-xs-12 mbt-0',
												autocomplete='off',
												),	
										),
									Row(
										Column('new_password_confirmation',css_class='form-group col-xs-12 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Submit'),css_class='col-xs-12 mb-0')
										)
									)

	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ResetForgottenPasswordForm, self).is_valid()
		# now perform the additional checks
		# check that the email address is correct
		email_address = self.cleaned_data['email_address']
		profile = Profile.try_to_get(
										user__username=email_address,
										reset_code=self.reset_code
										)
		if not profile:
			self.add_error('email_address','Incorrect email address.')
			valid = False
		# check that the password and the confirmation match
		if valid:
			if self.cleaned_data['new_password'] != self.cleaned_data['new_password_confirmation']:
				self.add_error('new_password_confirmation','Passwords do not match.')
				valid = False
		# return the result
		return valid

class UploadDataForm(forms.Form):
	# Define the choices for file type
	file_type_choices = (
							('Event Categories','Event Categories'),
							('Event Types','Event Types'),
							('Areas','Areas'),
							('Wards','Wards'),
							('Post Codes','Post Codes'),
							('Streets','Streets'),
							('Age Statuses','Age Statuses'),
							('Ethnicities','Ethnicities'),
							('ABSS Types','ABSS Types'),
							('Relationship Types','Relationship Types'),
							('Role Types','Role Types'),
							('People','People'),
							('Events','Events'),
							('Relationships','Relationships'),
							('Registrations','Registrations'),
							('Questions','Questions'),
							('Options','Options'),
							('Answers','Answers'),
							('Answer Notes','Answer Notes'),
							('Activity Types','Activity Types'),
							('Activities','Activities'),
							('Venue Types','Venue Types'),
							('Venues','Venues'),
							('Venues for Events','Venues for Events'),
						)
	# Define the fields that we need in the form.
	file_type = forms.ChoiceField(
									label="File Type",
									widget=forms.Select(attrs={'class' : 'form-control'}),
									choices=file_type_choices)
	file = forms.FileField(
									label="Data File")

class DownloadDataForm(forms.Form):
	# Define the choices for file type
	file_type_choices = (
							('People','People'),
							('Events','Events'),
							('Event Summary','Event Summary'),
							('Relationships','Relationships'),
							('Registrations','Registrations'),
							('Questions','Questions'),
							('Options','Options'),
							('Answers','Answers'),
							('Answer Notes','Answer Notes'),
							('Activities','Activities'),
							('Venues','Venues')
						)
	# Define the fields that we need in the form.
	file_type = forms.ChoiceField(
									label="File Type",
									widget=forms.Select(attrs={'class' : 'form-control'}),
									choices=file_type_choices)
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(DownloadDataForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('file_type',css_class='form-group col-md-12 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Download'),css_class='col-md-12 mb-0')
										)
									)

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
					('Prefer Not To Say', 'Prefer Not To Say')
					)
	# and the choices for trained roles
	trained_role_choices = (
							('none','Not trained'),
							('trained' , 'Trained'),
							('active' , 'Trained and active'),
							)
	# and the choices for 
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
	other_names = forms.CharField(
									label="Other names",
									max_length=50,
									initial='',
									required=False,
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
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	mobile_phone = forms.CharField(
									label="Mobile phone number",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	emergency_contact_details = forms.CharField(
									label="Emergency contact details",
									required=False,
									max_length=1500,
									widget=forms.Textarea(attrs={'class' : 'form-control','rows' : 4})
									)
	date_of_birth = forms.DateField(
									label="Date of birth",
									required=False,
									widget=forms.DateInput(	
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control default-date-of-birth',
																	'autocomplete' : 'off',
																	}),
        							input_formats=('%d/%m/%Y',))
	ABSS_type = forms.ChoiceField(
									label="ABSS type",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ABSS_start_date = forms.DateField(
									label="ABSS start date",
									required=False,
									widget=forms.DateInput(
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	ABSS_end_date = forms.DateField(
									label="ABSS end date",
									required=False,
									widget=forms.DateInput(
																format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off',
																	}),
									input_formats=('%d/%m/%Y',))
	membership_number = forms.CharField(
									label="Membership number",
									max_length=10,
									widget=forms.NumberInput(attrs={'class' : 'form-control',}))
	age_status = forms.ChoiceField(
									label="Age status",
									widget=forms.Select(attrs={'class' : 'form-control'}))
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
	pregnant = forms.BooleanField(
									label = "Pregnant (or partner is pregnant)",
									required = False)
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
	notes = forms.CharField(
								label="Notes",
								required=False,
								max_length=1500,
								widget=forms.Textarea(attrs={'class' : 'form-control','rows' : 4})
								)
	def __init__(self, *args, **kwargs):
		# over-ride the __init__ method to set the choices
		# pop out the extra parameters if we have them
		user = kwargs.pop('user') if 'user' in kwargs.keys() else False
		person = kwargs.pop('person') if 'person' in kwargs.keys() else False
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
			# and the pregnancy fields
			if not age_status.can_be_pregnant:
				# hide the pregnancy fields
				self.fields['pregnant'].widget = forms.HiddenInput()
				self.fields['due_date'].widget = forms.HiddenInput()
			# and the role type
			if age_status.default_role_type_only:
				# hide the role type field
				self.fields['role_type'].widget = forms.HiddenInput()
		else:
			# get the full set of role types
			self.fields['role_type'].choices = role_type_choices(
												Role_Type.objects.filter(use_for_people=True).order_by('role_type_name'))
		# get the trained roles and set up fields and rows for them
		trained_rows = []
		for trained_role in age_status.role_types.filter(trained=True):
			# create a field to capture whether the person is trained in a specific role
			role_field_name = 'trained_role_' + str(trained_role.pk)
			self.fields[role_field_name]= forms.ChoiceField(
														label=trained_role.role_type_name,
														widget=forms.Select(attrs={'class' : 'form-control'}),
														choices=self.trained_role_choices,
														required=False
														)
			# and an accompanying field to capture the date on which they were trained
			date_field_name = 'trained_date_' + str(trained_role.pk)
			self.fields[date_field_name] = forms.DateField(
														label="Date trained",
														required=False,
														widget=forms.DateInput(	
																				format='%d/%m/%Y',
																				attrs={
																					'class' : 'form-control datepicker',
																					'autocomplete' : 'off',
																					}),
														input_formats=('%d/%m/%Y',))
			# append the row
			row = Row(
						Column(role_field_name,css_class='form-group col-md-3 mb-0'),
						Column(date_field_name,css_class='form-group col-md-3 mb-0'),
						Column(css_class='form-group col-md-6 mb-0'),
						css_class='form-row'	
						)
			trained_rows.append(row)
		# build the crispy form
		rows = []
		rows.append(
					Row(
						Column('first_name',css_class='form-group col-md-4 mb-0'),
						Column('last_name',css_class='form-group col-md-4 mb-0'),
						Column('other_names',css_class='form-group col-md-4 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(
						Column('email_address',css_class='form-group col-md-4 mb-0'),
						Column('home_phone',css_class='form-group col-md-4 mb-0'),
						Column('mobile_phone',css_class='form-group col-md-4 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(		
						Column('emergency_contact_details',css_class='form-group col-md-12 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(
						Column('ABSS_type',css_class='form-group col-md-3 mb-0'),
						Column('ABSS_start_date',css_class='form-group col-md-3 mb-0'),
						Column('ABSS_end_date',css_class='form-group col-md-3 mb-0'),
						Column('membership_number',css_class='form-group col-md-3 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(
						Column('age_status',css_class='form-group col-md-3 mb-0'),
						Column('date_of_birth',css_class='form-group col-md-3 mb-0'),
						Column('ethnicity',css_class='form-group col-md-3 mb-0'),
						Column('gender',css_class='form-group col-md-3 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(
						Column('pregnant',css_class='form-group col-md-3 mb-0'),
						Column('due_date',css_class='form-group col-md-9 mb-0'),
						css_class='form-row'	
						)
					)
		rows.append(
					Row(
						Column('role_type',css_class='form-group col-md-3 mb-0'),
						css_class='form-row'	
						)
					)
		rows += trained_rows
		# build and append the button row
		site = Site.objects.all().first()
		if user.is_superuser and site and site.invitations_active and not person.has_open_invitation():
			button_row = Row(
								Column(
										Submit('action', 'Submit'),
										Submit('action', 'Generate Invitation'),
										css_class='col-md-12 mb-0 form-group',
										),
								css_class='form-row'
							)				
		else:
			button_row = Row(Column(Submit('action', 'Submit'),css_class='col-md-12 mb-0'))
		rows.append(button_row)	
		# build the rows into a crispy layout
		self.helper = FormHelper()
		self.helper.layout = Layout(*rows)

	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ProfileForm, self).is_valid()
		# now perform the additional checks
		# get the age status
		age_status = Age_Status.objects.get(id=self.cleaned_data['age_status'])
		# check whether the only error is due to a change in age status: if so, set the default
		if 'role_type' in self._errors.keys():
			# set a relevant error message
			self._errors['role_type'] = ['Select a valid role for this age status.']
			# set the value to the default
			self.cleaned_data['role_type'] = str(age_status.default_role_type.pk)
			# check whether this is the only error and if only defaults are allowed
			if len(self._errors) == 1 and age_status.default_role_type_only:
				# set the valid flag
				valid = True
			# otherwise set the default on the page
			else:
				# set the value, remembering that self.data is immutable unless we copy it
				form_data_copy = self.data.copy()
				# set the value
				form_data_copy['role_type'] = str(age_status.default_role_type.pk)
				# replace with the copy
				self.data = form_data_copy
		# get the role type to determine whether it must be trained
		role_type = Role_Type.objects.get(pk=self.cleaned_data['role_type'])
		# if the role type requires training, check that the person is trained
		if role_type.trained:
			if self.cleaned_data['trained_role_' + str(role_type.pk)] not in ['trained','active']:
				self._errors['role_type'] = ['Must be trained to perform this role.']
				valid = False
		# if we have a valid date of birth, check whether it is allowed by age status
		if 'date_of_birth' in self.cleaned_data:
			today = datetime.date.today()
			if self.cleaned_data['date_of_birth'] != None and \
				self.cleaned_data['date_of_birth'] < today.replace(year=today.year-age_status.maximum_age):
				self._errors['date_of_birth'] = ["Must be less than " + str(age_status.maximum_age) + " years old."]
				valid = False
		# if we have valid ABSS dates, check that they are valid in relation to each other
		if 'ABSS_start_date' in self.cleaned_data and 'ABSS_end_date' in self.cleaned_data:
			# check that we don't have an ABSS end date without a start date
			if self.cleaned_data['ABSS_end_date'] != None and self.cleaned_data['ABSS_start_date'] == None:
				self._errors['ABSS_end_date'] = ['ABSS end date can only be entered if ABSS start date is entered.']
				valid = False
			# check that we don't have an ABSS end date before the start date
			if (self.cleaned_data['ABSS_end_date'] != None and self.cleaned_data['ABSS_start_date'] != None 
					and self.cleaned_data['ABSS_end_date'] <= self.cleaned_data['ABSS_start_date'] ):
				self._errors['ABSS_end_date'] = ['ABSS end date must be after ABSS start date.']
				valid = False
		# return the result
		return valid

class PersonSearchForm(forms.Form):
	# Define the choices for who should be included in the search
	include_people_choices = (
								('in_project','In project'),
								('all' , 'All'),
								('left_project' , 'Left project'),
								)
	# Define the fields that we need in the form.
	names = forms.CharField(
									label="Names, membership number or email address",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	keywords = forms.CharField(
									label="Keywords",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	role_type = forms.ChoiceField(
									label="Role",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ABSS_type = forms.ChoiceField(
									label="ABSS",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	age_status = forms.ChoiceField(
									label="Age status",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	trained_role = forms.ChoiceField(
									label="Trained role",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ward = forms.ChoiceField(
									label="Ward",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	include_people = forms.ChoiceField(
									label="Include people",
									choices=include_people_choices,
									initial='in_project',
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	action = forms.CharField(
									initial='action',
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	page = forms.CharField(
									initial='1',
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull additional paramterts out of kwargs if provided
		user = kwargs.pop('user') if 'user' in kwargs.keys() else False
		download = kwargs.pop('download') if 'download' in kwargs.keys() else False
		# call the built in constructor
		super(PersonSearchForm, self).__init__(*args, **kwargs)
		# build the crispy form
		self.helper = FormHelper()
		self.helper.form_action = reverse('listpeople')
		# define the row containing buttons, depending on whether the user is allowed to download or not
		if not download:
			button_row = FormActions(
										Submit('action', 'Search'),
									)
		else:
			if user and user.is_superuser:
				button_row = FormActions(
											Submit('action', 'Search'),
											Submit('action', 'Download'),
											Submit('action', 'Download Full Data')
										)
			else:
				button_row = FormActions(
											Submit('action', 'Search'),
											Submit('action', 'Download'),
										)
		# define the layout
		self.helper.layout = Layout(
									Row(
										Column('names',css_class='form-group col-md-6 mbt-0'),
										Column('keywords',css_class='form-group col-md-6 mbt-0'),
										),
									Row(
										Column('role_type',css_class='form-group col-md-2 mbt-0'),
										Column('age_status',css_class='form-group col-md-2 mbt-0'),
										Column('trained_role',css_class='form-group col-md-2 mbt-0'),
										Column('ward',css_class='form-group col-md-2 mbt-0'),
										Column('ABSS_type',css_class='form-group col-md-2 mbt-0'),
										Column('include_people',css_class='form-group col-md-2 mbt-0'),
										),
									Hidden('page','1'),
									button_row,
									)
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
		self.fields['ward'].choices = build_choices(
															choice_class=Ward,
															choice_field='ward_name',
															default=True,
															default_label='Any')
		# build the choices for the trained roles, starting with a default entry, then adding trained and active
		# options for each of the trained roles
		trained_role_choices = [('none','N/A')]
		for trained_role in Role_Type.objects.filter(trained=True):
			trained_role_choices.append(('trained_'+str(trained_role.pk),'Trained ' + trained_role.role_type_name))
			trained_role_choices.append(('active_'+str(trained_role.pk),'Active ' + trained_role.role_type_name))
		self.fields['trained_role'].choices = trained_role_choices

class PersonNameSearchForm(forms.Form):
	# Define the choices for who should be included in the search
	include_people_choices = (
								('in_project','In project'),
								('all' , 'All'),
								('left_project' , 'Left project'),
								)
	# Define the fields that we need in the form.
	names = forms.CharField(
							label="Names or membership number",
							max_length=50,
							widget=forms.TextInput(attrs={'class' : 'form-control',}))
	include_people = forms.ChoiceField(
									label="Include people",
									choices=include_people_choices,
									initial='in_project',
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(PersonNameSearchForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('names',css_class='form-group col-md-8 mbt-0'),
										Column('include_people',css_class='form-group col-md-4 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Search'),css_class='col-md-12 mb-0')),
									Hidden('action','search'),
									)

class PersonRelationshipSearchForm(forms.Form):
	# Define the fields that we need in the form.
	first_name = forms.CharField(
									label="First Name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last Name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(PersonRelationshipSearchForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('first_name',css_class='form-group col-md-6 mbt-0'),	
										Column('last_name',css_class='form-group col-md-6 mbt-0'),	
										),
									Row(
										Column(Submit('submit', 'Search'),css_class='col-md-12 mb-0')),
									Hidden('action','search'),
									)

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
									label="is this person's",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull the fields out of the parameters
		first_name = kwargs.pop('first_name')
		last_name = kwargs.pop('last_name')
		person = kwargs.pop('person')
		# call the built in constructor
		super(AddRelationshipForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['relationship_type'].choices = build_choices(
													choice_queryset=person.age_status.relationship_types.all(),
													choice_field='relationship_type'
													)
		self.fields['relationship_type'].initial = Relationship_Type.objects.get(relationship_type='parent').pk
		self.fields['age_status'].choices = build_choices(choice_class=Age_Status,choice_field='status')
		self.fields['age_status'].initial = Age_Status.objects.get(status='Child under four').pk
		self.fields['first_name'].initial = first_name
		self.fields['last_name'].initial = last_name
		# and the label for the relationship field
		self.fields['relationship_type'].label = person.full_name() + " is this person's"
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('first_name',css_class='form-group col-md-3 mbt-0'),	
										Column('last_name',css_class='form-group col-md-3 mbt-0'),
										Column('age_status',css_class='form-group col-md-3 mbt-0'),
										Column('relationship_type',css_class='form-group col-md-3 mbt-0'),		
										),
									Row(
										Column(
												Submit('submit', 'Create and Add Relationship'),
												css_class='col-md-12 mb-0'
												)
										),
									Hidden('action','addrelationshiptonewperson'),
									)

class AddRelationshipToExistingPersonForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the person list out of the parameter
		people = kwargs.pop('people')
		from_person = kwargs.pop('from_person')
		# call the built in constructor
		super(AddRelationshipToExistingPersonForm, self).__init__(*args, **kwargs)
		# now go through the people and build fields
		for person in people:
			# set the field name
			field_name = 'relationship_type_' + str(person.pk)
			# get the relationship types for the from person
			relationship_types = from_person.age_status.relationship_types.all()
			# now check that they are valid for the to person
			relationship_types = check_relationship_types(relationship_types,person)
			# create the field
			self.fields[field_name]= forms.ChoiceField(
										label="Relationship",
										widget=forms.Select(),
										choices=build_choices(
											choice_queryset=relationship_types,
											choice_field='relationship_type',
											default=True,
											default_label='none')
										)

class EditExistingRelationshipsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# pull the relationship types list and person out of the parameters
		relationships = kwargs.pop('relationships')
		from_person = kwargs.pop('from_person')
		# call the built in constructor
		super(EditExistingRelationshipsForm, self).__init__(*args, **kwargs)
		# now go through the people and build fields
		for person in relationships:
			# set the field name for the relationship type
			field_name = 'relationship_type_' + str(person.pk)
			# get the relationship types for the from person
			relationship_types = from_person.age_status.relationship_types.all()
			# now check that they are valid for the to person
			relationship_types = check_relationship_types(relationship_types,person)
			# create the field
			self.fields[field_name] = forms.ChoiceField(
											label="Relationship",
											widget=forms.Select(),
											choices=build_choices(
												choice_queryset=relationship_types,
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
	# over-ride the __init__ method to define the form layout
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(AddressSearchForm, self).__init__(*args, **kwargs)
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('house_name_or_number',css_class='form-group col-md-4 mbt-0'),
										Column('street',css_class='form-group col-md-4 mbt-0'),
										Column('post_code',css_class='form-group col-md-4 mbt-0'),	
										),
									Hidden('action','search'),
									Hidden('page','1'),
									Row(
										Column(Submit('submit', 'Search'),css_class='col-md-12 mb-0'))
									)	
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

class VenueForm(forms.Form):
	# Define the fields that we need in the form to capture initial venue details and search for address
	name = forms.CharField(
							label="Name",
							max_length=100,
							widget=forms.TextInput(attrs={'class' : 'form-control',}))
	venue_type = forms.ChoiceField(
									label="Venue type",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	building_name_or_number = forms.CharField(
									label="Building name or no.",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	street_name = forms.CharField(
									label="Street Name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	post_code = forms.CharField(
									label="Post Code",
									max_length=10,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	street = forms.ChoiceField(
									label="Street",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	contact_name = forms.CharField(
									label="Contact Name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	phone = forms.CharField(
									label="Phone",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	mobile_phone = forms.CharField(
									label="Mobile",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	email_address = forms.CharField(
									label="Email",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	website = forms.CharField(
									label="Website",
									max_length=100,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	price = forms.CharField(
									label="Price",
									max_length=100,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	facilities = forms.CharField(
									label="Facilities",
									max_length=100,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	opening_hours = forms.CharField(
									label="Opening Hours",
									max_length=100,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	notes = forms.CharField(
									label="Notes",
									required=False,
									max_length=1500,
									widget=forms.Textarea(attrs={'class' : 'form-control','rows' : 4})
									)
	# over-ride the __init__ method to define the form layout
	def __init__(self, *args, **kwargs):
		# pull the venue id out of the parameters
		self.venue_id = int(kwargs.pop('venue_id')) if 'venue_id' in kwargs.keys() else False
		# call the built in constructor
		super(VenueForm, self).__init__(*args, **kwargs)
		# build choices
		self.fields['venue_type'].choices = build_choices(choice_class=Venue_Type,choice_field='name')
		# if this is a submission, attempt to build a list of streets and set the choices
		if self.is_bound and (self.data['street_name'] or self.data['post_code']):
			streets = Street.search(
									name__icontains=self.data['street_name'],
									post_code__post_code__icontains=self.data['post_code']
									).order_by('name')
			# build the choices if we got results, set a default if we didn't
			if streets:
				choices = []
				for street in streets:
					choices.append((street.pk,street.name + ' (' + street.post_code.post_code + ')'))
				self.fields['street'].choices = choices
			else:
				self.fields['street'].choices = [('','No streets found')]
		# otherwise set the choices to the current street if we already have a venue and no street name or post code
		elif self.venue_id:
			venue = Venue.objects.get(pk=self.venue_id)
			self.fields['street'].choices = \
				[(venue.street.pk,venue.street.name + ' (' + venue.street.post_code.post_code + ')')]
		# define the crispy form
		submit_text = 'Update' if self.venue_id else 'Create'
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('name',css_class='form-group col-md-6 mbt-0'),
										Column('venue_type',css_class='form-group col-md-6 mbt-0'),	
										),
									Row(
										Column('building_name_or_number',css_class='form-group col-md-2 mbt-0'),
										Column('street_name',css_class='form-group col-md-2 mbt-0'),
										Column('post_code',css_class='form-group col-md-2 mbt-0'),
										Column('street',css_class='form-group col-md-5 mbt-0'),
										Column(FormActions(ButtonHolder(
																		Submit(
																				'action',
																				'Search',
																				),
																		css_class='form-group col-md-1 mb-0',
																		)
															)
												),
										),
									Row(
										Column('contact_name',css_class='form-group col-md-4 mbt-0'),
										Column('phone',css_class='form-group col-md-2 mbt-0'),
										Column('mobile_phone',css_class='form-group col-md-2 mbt-0'),	
										Column('email_address',css_class='form-group col-md-2 mbt-0'),
										Column('website',css_class='form-group col-md-2 mbt-0'),	
										),
									Row(
										Column('price',css_class='form-group col-md-4 mbt-0'),
										Column('facilities',css_class='form-group col-md-4 mbt-0'),
										Column('opening_hours',css_class='form-group col-md-4 mbt-0'),	
										),
									Row(
										Column('notes',css_class='form-group col-md-12 mbt-0'),	
										),
									Hidden('page','1'),
									Row(
										Column(Submit('action', submit_text),css_class='col-md-12 mb-0')
										),
									)
	# override the validation to provide additional checks	
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(VenueForm, self).is_valid()
		# set the return value if the built in validation function fails
		if valid == False:
			return valid
		# now perform the additional checks
		# start by checking whether we have either a post code or a street
		if self.data['action'] == 'Search' \
			and not self.cleaned_data['post_code'] \
			and not self.cleaned_data['street_name'] :
			self.add_error('street_name','Either post code or street name must be entered.')
			valid = False
		# and check whether we have a street if we have been asked to do a create
		if self.data['action'] in ('Create','Update') and not self.cleaned_data['street']:
			self.add_error('street','Street must be selected.')
			valid = False
		# and check whether we already have a venue with this name
		venue = Venue.try_to_get(name=self.cleaned_data['name'])
		if venue and (not self.venue_id or (self.venue_id and venue.pk != self.venue_id)):
			self.add_error('name','Venue with this name already exists.')
			valid = False
		# return the result
		return valid
	# over-ride cleaning to handle street field
	def clean(self):
		# custom clean method to remove key errors on street search
		# call the built in method
		cleaned_data = super(VenueForm, self).clean()
    	# remove the error and add the street back into the cleaned data
		if 'street' in self.errors:
			del self._errors['street']
			cleaned_data['street'] = self.data['street']
		# return the results
		return cleaned_data

class VenueSearchForm(forms.Form):
	# Define the fields that we need in the form.
	name = forms.CharField(
									label="Name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	venue_type = forms.ChoiceField(
									label="Venue type",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	ward = forms.ChoiceField(
									label="Ward",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	area = forms.ChoiceField(
									label="Area",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control'}))
	action = forms.CharField(
									initial='action',
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	page = forms.CharField(
									initial='1',
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(VenueSearchForm, self).__init__(*args, **kwargs)
		# build the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('name',css_class='form-group col-md-3 mbt-0'),
										Column('venue_type',css_class='form-group col-md-3 mbt-0'),
										Column('ward',css_class='form-group col-md-3 mbt-0'),
										Column('area',css_class='form-group col-md-3 mbt-0'),
										),
									Hidden('action','search'),
									Hidden('page','1'),
									Row(
										Column(Submit('submit', 'Search'),css_class='col-md-12 mb-0'))
									)
		# set the choices
		self.fields['venue_type'].choices = build_choices(
															choice_class=Venue_Type,
															choice_field='name',
															default=True,
															default_label='Any')
		self.fields['area'].choices = build_choices(
															choice_class=Area,
															choice_field='area_name',
															default=True,
															default_label='Any')
		self.fields['ward'].choices = build_choices(
															choice_class=Ward,
															choice_field='ward_name',
															default=True,
															default_label='Any')

class EventForm(forms.Form):
	# Define the fields that we need in the form to capture the event
	name = forms.CharField(
									label="Name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	description = forms.CharField(
									label="Description",
									max_length=7500,
									widget=forms.Textarea(attrs={'class' : 'form-control', 'cols' : 100, 'rows' : 6}))
	event_type = forms.ChoiceField(
									label="Event Type",
									widget=forms.Select())
	date = forms.DateField(
									label="Date",
									widget=forms.DateInput(		format='%d/%m/%Y',
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
									label="Location (free format)",
									max_length=50,
									required=False, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	ward = forms.ChoiceField(
									label="Ward in which event takes place",
									widget=forms.Select())
	venue = forms.ChoiceField(
									label="Venue",
									widget=forms.Select())
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(EventForm, self).__init__(*args, **kwargs)
		# build the choices
		self.fields['event_type'].choices = build_choices(choice_class=Event_Type,choice_field='name')
		self.fields['ward'].choices = build_choices(choice_class=Ward,
													choice_field='ward_name',
													default=True,
													default_label='None')
		self.fields['ward'].initial = 0
		self.fields['venue'].choices = build_choices(choice_class=Venue,
													choice_field='name',
													default=True,
													default_label='None')
		self.fields['venue'].initial = 0
		# build the area selector
		area_columns = []
		for area in Area.objects.filter(use_for_events=True).order_by('area_name'):
			field_name = 'area_' + str(area.pk)
			self.fields[field_name] = forms.BooleanField(
														label = area.area_name,
														required = False
														)
			area_columns.append(Column(field_name,css_class='form-group col-md-4 mb-0'))
		# build the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('name',css_class='form-group col-md-6 mb-0'),
										Column('event_type',css_class='form-group col-md-6 mb-0'),
										css_class='form-row'	
										),
									Row(
										Column('description',css_class='form-group col-md-12 mb-0'),
										css_class='form-row'	
										),
									Row(
										Column('date',css_class='form-group col-md-4 mb-0'),
										Column('start_time',css_class='form-group col-md-4 mb-0'),
										Column('end_time',css_class='form-group col-md-4 mb-0'),
										css_class='form-row'	
										),
									Row(
										Column('venue',css_class='form-group col-md-4 mb-0'),
										Column('location',css_class='form-group col-md-4 mb-0'),
										Column('ward',css_class='form-group col-md-4 mb-0'),
										css_class='form-row'	
										),
									Row(
										*area_columns,
										css_class='form-row'
										),
									Hidden('action','search'),
									Hidden('page','1'),
									Row(Column(Submit('submit', 'Submit'),css_class='col-md-12 mb-0'))
									)

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
			# set the field name for apologies
			field_name = 'apologies_' + str(person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Apologies",
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
			# get the list of roles available
			role_types = person.age_status.role_types.filter(use_for_events=True).order_by('role_type_name')
			# go through the role types and exclude any where the role requires training and the person is not trained
			for role_type in role_types:
				if role_type.trained and not person.trained_role_set.filter(role_type=role_type).exists():
					role_types = role_types.exclude(pk=role_type.pk)
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(),
														choices=role_type_choices(role_types),
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
			# set the field name for apologies
			field_name = 'apologies_' + str(registration.person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Apologies",
														required = False,
														initial = registration.apologies,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
			# set the field name for participation
			field_name = 'participated_' + str(registration.person.pk)
			# create the field
			self.fields[field_name] = forms.BooleanField(
														label = "Participated",
														required = False,
														initial = registration.participated,
														widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
			# get the the person, then build the list of roles available for the person
			person = registration.person
			role_types = person.age_status.role_types.filter(use_for_events=True).order_by('role_type_name')
			# go through the role types and exclude any where the role requires training and the person is not trained
			for role_type in role_types:
				if role_type.trained and not person.trained_role_set.filter(role_type=role_type).exists():
					role_types = role_types.exclude(pk=role_type.pk)
			# build the field
			field_name = 'role_type_' + str(registration.person.pk)
			self.fields[field_name]= forms.ChoiceField(
														label="Role",
														widget=forms.Select(attrs={'class' : 'form-control'}),
														initial=registration.role_type.pk,
														choices=role_type_choices(role_types),
														)

class AddPersonAndRegistrationForm(forms.Form):
	# Define the fields that we need in the form to capture the basics of the person's profile
	first_name = forms.CharField(
									label="First name",
									max_length=50, 
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	age_status = forms.ChoiceField(
									label="Age status",
									widget=forms.Select(attrs={'class' : 'form-control'}))
	role_type = forms.ChoiceField(
									label="Role",
									widget=forms.Select())
	registered = forms.BooleanField(
									label = "Registered",
									required = False,)
									# widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	apologies = forms.BooleanField(
									label = "Apologies",
									required = False,)
									#widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	participated = forms.BooleanField(
										label = "Participated",
										required = False,)
										#widget=forms.CheckboxInput(attrs={'class' : 'form-control'}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# initialise first name and last name
		first_name = ''
		last_name = ''
		# pull the fields out of the parameters if we got them
		if 'first_name' in kwargs.keys():
			first_name = kwargs.pop('first_name')
			last_name = kwargs.pop('last_name')
		# call the built in constructor
		super(AddPersonAndRegistrationForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['role_type'].choices = build_choices(
															choice_class=Role_Type,
															choice_field='role_type_name'
															)
		self.fields['age_status'].choices = build_choices(
															choice_class=Age_Status,
															choice_field='status'
															)
		# set the initial values if we have been passed them
		if first_name:
			self.fields['first_name'].initial = first_name
			self.fields['last_name'].initial = last_name
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('first_name',css_class='form-group col-md-3 mbt-0'),	
										Column('last_name',css_class='form-group col-md-3 mbt-0'),
										Column('age_status',css_class='form-group col-md-3 mbt-0'),
										Column('role_type',css_class='form-group col-md-3 mbt-0'),		
										),
									Row(
										Column('participated',css_class='form-group col-md-3 mbt-0'),	
										Column('apologies',css_class='form-group col-md-3 mbt-0'),
										Column('registered',css_class='form-group col-md-3 mbt-0'),		
										),
									Row(
										Column(
												Submit('submit', 'Create and Add Registration'),
												css_class='col-md-12 mb-0'
												)
										),
									Hidden('action','addpersonandregistration'),
									)
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(AddPersonAndRegistrationForm, self).is_valid()
		# now perform the additional checks
		# get the age status
		age_status = Age_Status.objects.get(id=self.cleaned_data['age_status'])
		# check whether the role type is valid for the age status
		if not age_status.role_types.filter(id=self.cleaned_data['role_type']).exists():
			# set the error and invalidate the form
			self.add_error(None,'Role type is not valid for age status')
			valid = False
		# check whether any registration field has been set
		if (not self.cleaned_data['participated'] 
			and not self.cleaned_data['apologies']
			and not self.cleaned_data['registered']):
			# set the error and invalidate the form
			self.add_error(None,'At least one of registered, apologies or participated must be selected.')
			valid = False
		# return the result
		return valid

class EventSearchForm(forms.Form):
	# Define the fields that we need in the form.
	name = forms.CharField(
									label="Name",
									max_length=50,
									required=False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	event_category = forms.ChoiceField(
									label="Category",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control',}))
	event_type = forms.ChoiceField(
									label="Type",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control',}))
	venue = forms.ChoiceField(
									label="Venue",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control',}))
	ward = forms.ChoiceField(
									label="Ward",
									required=False,
									widget=forms.Select(attrs={'class' : 'form-control',}))
	date_from = forms.DateField(
									label="From",
									required=False,
									widget=forms.DateInput(format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=['%d/%m/%Y'])
	date_to = forms.DateField(
									label="To",
									required=False,
									widget=forms.DateInput(format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=['%d/%m/%Y'])
	action = forms.CharField(
									initial='action',
									widget=forms.HiddenInput(attrs={'class' : 'form-control',}))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# initialise variables
		user = False
		# pull the user out of the parameters if provided
		if 'user' in kwargs.keys():
			user = kwargs.pop('user')
		# call the built in constructor
		super(EventSearchForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['event_type'].choices = build_choices(
															choice_class=Event_Type,
															choice_field='name',
															default=True,
															default_label='Any'
															)
		self.fields['event_category'].choices = build_choices(
																choice_class=Event_Category,
																choice_field='name',
																default=True,
																default_label='Any'
																)
		self.fields['ward'].choices = build_choices(
													choice_class=Ward,
													choice_field='ward_name',
													default=True,
													default_label='Any'
													)
		self.fields['venue'].choices = build_choices(
													choice_class=Venue,
													choice_field='name',
													default=True,
													default_label='Any'
													)
		# build the crispy form
		self.helper = FormHelper()
		self.helper.form_action = reverse('events')
		# define the row containing buttons, depending on whether the user is allowed to download or not
		if user and user.is_superuser:
			button_row = FormActions(
										Submit('action', 'Search'),
										Submit('action', 'Download Events'),
										Submit('action', 'Download Registrations'),
									)
		else:
			button_row = FormActions(
										Submit('action', 'Search')
									)
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('name',css_class='form-group col-md-12 mbt-0'),
										),
									Row(
										Column('event_category',css_class='form-group col-md-2 mbt-0'),	
										Column('event_type',css_class='form-group col-md-2 mbt-0'),
										Column('venue',css_class='form-group col-md-2 mbt-0'),
										Column('ward',css_class='form-group col-md-2 mbt-0'),
										Column('date_from',css_class='form-group col-md-2 mbt-0'),
										Column('date_to',css_class='form-group col-md-2 mbt-0'),
										),
									Hidden('page','1'),
									button_row,
									)

class ActivityForm(forms.Form):
	# Define the fields that we need in the form.
	activity_type = forms.ChoiceField(
										label="Activity",
										widget=forms.Select(attrs={'class' : 'form-control',}))
	date = forms.DateField(
							label="Date",
							widget=forms.DateInput(
													format='%d/%m/%Y',
													attrs={
														'class' : 'form-control datepicker',
														'autocomplete' : 'off'
														}
													),
							input_formats=['%d/%m/%Y']
							)
	hours = forms.IntegerField(
								label="Hours",
								min_value=0,
								max_value=24
								)
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(ActivityForm, self).__init__(*args, **kwargs)
		# set the choices
		self.fields['activity_type'].choices = build_choices(choice_class=Activity_Type,
															choice_field='name')
		# define the crispy form helper
		self.helper = FormHelper()
		# and define the layout
		self.helper.layout = Layout(
									Row(
										Column('activity_type',css_class='form-group col-xs-6 mbt-0'),
										Column('date',css_class='form-group col-xs-4 mbt-0'),	
										Column('hours',css_class='form-group col-xs-2 mbt-0'),
										),
									Row(
										Column(Submit('submit', 'Submit'),css_class='col-xs-12 mb-0')
										),
									)

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

class DashboardDatesForm(forms.Form):
	# Define the fields that we need in the form to capture the event
	start_date = forms.DateField(
									label="From",
									widget=forms.DateInput(		format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	end_date = forms.DateField(
									label="To",
									widget=forms.DateInput(		format='%d/%m/%Y',
																attrs={
																	'class' : 'form-control datepicker',
																	'autocomplete' : 'off'
																	}),
									input_formats=('%d/%m/%Y',))
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# pull additional paramterts out of kwargs if provided
		start_date = kwargs.pop('start_date') if 'start_date' in kwargs.keys() else False
		end_date = kwargs.pop('end_date') if 'end_date' in kwargs.keys() else False
		# call the built in constructor
		super(DashboardDatesForm, self).__init__(*args, **kwargs)
		# build the initial values
		if start_date:
			self.fields['start_date'].initial = start_date
		if end_date:
			self.fields['end_date'].initial = end_date
		# build the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('start_date',css_class='form-group col-md-2 mb-0'),
										Column('end_date',css_class='form-group col-md-2 mb-0'),
										Column(Submit('submit', 'Submit'),css_class='col-md-2 mb-0')
										)
									)