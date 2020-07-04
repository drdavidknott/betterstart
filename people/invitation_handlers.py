# this module contains classes to handle the processing of invitation steps

# import necessary modules
import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Invitation, Invitation_Step, Invitation_Step_Type, \
							Person, Relationship, Relationship_Type, Street, Terms_And_Conditions, \
							Ethnicity, Age_Status, Question, Answer, Option, Answer_Note, Site
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Hidden, ButtonHolder, Field, HTML
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from .utilities import build_choices, replace_if_value
from jsignature.forms import JSignatureField
import json

class IntroductionForm(forms.Form):
	# this form has no fields: it simply presents the introduction
	# over-ride the __init__ method
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(IntroductionForm, self).__init__(*args, **kwargs)
		# build the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(	
									Submit('submit', 'Start')
									)

class TermsAndConditionsForm(forms.Form):
	# Define the fields that we need in the form.
	accept_conditions = forms.BooleanField(
											label = "I have read and accept the terms and conditions shown above",
											required = True,
											widget=forms.CheckboxInput()
											)
	# over-ride the __init__ method to set the choices
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(TermsAndConditionsForm, self).__init__(*args, **kwargs)
		# build the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									'accept_conditions',	
									Submit('submit', 'Accept')
									)

class PersonalDetailsForm(forms.Form):
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
	last_name = forms.CharField(
									label="Last name",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	email_address = forms.CharField(
									label="Email",
									max_length=50,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	home_phone = forms.CharField(
									label="Home phone number",
									max_length=50,
									required = False,
									widget=forms.TextInput(attrs={'class' : 'form-control',}))
	mobile_phone = forms.CharField(
									label="Mobile phone number",
									max_length=50,
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
	gender = forms.ChoiceField(
									label="Gender",
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
	def __init__(self, *args, **kwargs):
		# pull out the person if we have been passed one
		person = kwargs.pop('person') if 'person' in kwargs.keys() else False
		# call the built in constructor
		super(PersonalDetailsForm, self).__init__(*args, **kwargs)
		# set the initial values for names if we have a person
		if person:
			self.fields['first_name'].initial = person.first_name
			self.fields['last_name'].initial = person.last_name
		# define the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('first_name',css_class='form-group col-md-6 mbt-0'),	
										Column('last_name',css_class='form-group col-md-6 mbt-0'),
										),
									Row(
										Column('date_of_birth',css_class='form-group col-md-6 mbt-0'),	
										Column('gender',css_class='form-group col-md-6 mbt-0'),
										),
									Row(
										Column('pregnant',css_class='form-group col-md-4 mbt-0'),
										Column('due_date',css_class='form-group col-md-8 mbt-0'),	
										),
									Row(
										Column('email_address',css_class='form-group col-md-4 mbt-0'),
										Column('home_phone',css_class='form-group col-md-4 mbt-0'),	
										Column('mobile_phone',css_class='form-group col-md-4 mbt-0'),
										),
									Row(
										Column('emergency_contact_details',css_class='form-group col-md-12 mbt-0'),
										),
									Row(
										Column(Submit('action', 'Enter'),css_class='col-md-12 mb-0')
										),
									)

	# override the validation to provide additional checks	
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(PersonalDetailsForm, self).is_valid()
		# check the date of birth
		today = datetime.date.today()
		date_of_birth = self.cleaned_data['date_of_birth']
		if (date_of_birth != None) and (date_of_birth > today):
			self.add_error('date_of_birth','Must not be in the future.')
			valid = False
		# return the result
		return valid

class AddressForm(forms.Form):
	# Define the fields that we need in the form to capture initial venue details and search for address
	house_name_or_number = forms.CharField(
									label="House name or no.",
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
	# over-ride the __init__ method to define the form layout
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(AddressForm, self).__init__(*args, **kwargs)
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
		# define the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('house_name_or_number',css_class='form-group col-md-2 mbt-0'),
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
										Column(Submit('action', 'Enter'),css_class='col-md-12 mb-0')
										),
									)
	# override the validation to provide additional checks	
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(AddressForm, self).is_valid()
		# set the return value if the built in validation function fails
		if valid == False:
			return valid
		# always invalidate for a search, also checking whether have either post code or street name
		if self.data['action'] == 'Search':
			valid = False
			if not self.cleaned_data['post_code'] and not self.cleaned_data['street_name'] :
				self.add_error('street_name','Either post code or street name must be entered.')
		# and check whether we have a street if we have been asked to do a create
		if self.data['action'] == 'Enter' and not self.cleaned_data['street']:
			self.add_error('street','Street must be selected.')
			valid = False
		# return the result
		return valid

	# over-ride cleaning to handle street field
	def clean(self):
		# custom clean method to remove key errors on street search
		# call the built in method
		cleaned_data = super(AddressForm, self).clean()
    	# remove the error and add the street back into the cleaned data
		if 'street' in self.errors:
			del self._errors['street']
			cleaned_data['street'] = self.data['street']
		# return the results
		return cleaned_data

class ChildrenForm(forms.Form):

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(ChildrenForm, self).__init__(*args, **kwargs)
		# set the choice fields
		gender_choices = (
							('','--------'),
							('Male' , 'Male'),
							('Female' , 'Female'),
							)
		relationship_types = Relationship_Type.objects.filter(use_for_invitations=True)
		relationship_type_choices = build_choices(
													choice_queryset=relationship_types,
													choice_field='relationship_type',
													default=True,
													default_value='',
													default_label='--------',
													)
		# build six sets of fields
		for i in range(6):
			str_i = str(i)
			self.fields['first_name_' + str_i] = forms.CharField(
															label="First name",
															max_length=50,
															required=False,
															widget=forms.TextInput(attrs={'class' : 'form-control',}))
			self.fields['last_name_' + str_i] = forms.CharField(
															label="Last name",
															max_length=50,
															required=False,
															widget=forms.TextInput(attrs={'class' : 'form-control',}))
			self.fields['date_of_birth_' + str_i] = forms.DateField(
															label="Date of birth",
															required=False,
															widget=forms.DateInput(	
																	format='%d/%m/%Y',
																	attrs={
																		'class' : 'form-control default-date-of-birth',
																		'autocomplete' : 'off',
																		}
																					),
						        							input_formats=('%d/%m/%Y',))
			self.fields['gender_' + str_i] = forms.ChoiceField(
																label="Gender",
																choices=gender_choices,
																required=False,
																widget=forms.Select(attrs={'class' : 'form-control'}))
			self.fields['relationship_type_' + str_i] = forms.ChoiceField(
																label="Your relationship",
																choices=relationship_type_choices,
																required=False,
																widget=forms.Select(attrs={'class' : 'form-control'}))
		# build the crispy form
		self.helper = FormHelper()
		rows = []
		for i in range(6):
			str_i = str(i)
			row = Row(
						Column('first_name_' + str_i,css_class='form-group col-md-3 mbt-0'),
						Column('last_name_' + str_i,css_class='form-group col-md-3 mbt-0'),
						Column('date_of_birth_' + str_i,css_class='form-group col-md-2 mbt-0'),
						Column('gender_' + str_i,css_class='form-group col-md-2 mbt-0'),
						Column('relationship_type_' + str_i,css_class='form-group col-md-2 mbt-0'),
						)
			rows.append(row)
		row = Row(
					Column(Submit('action', 'Enter'),css_class='col-md-12 mb-0')
					)
		rows.append(row)
		self.helper.layout = Layout(*rows)

	# override the validation to provide additional checks	
	def is_valid(self):
		# the validation function
		# start by calling the built in validation function
		valid = super(ChildrenForm, self).is_valid()
		# set the return value if the built in validation function fails
		if valid == False:
			return valid
		# go through the field
		for i in range(6):
			first_name = self.cleaned_data['first_name_' + str(i)] \
				if 'first_name_' + str(i) in self.cleaned_data else False
			last_name = self.cleaned_data['last_name_' + str(i)] \
				if 'last_name_' + str(i) in self.cleaned_data else False
			date_of_birth = self.cleaned_data['date_of_birth_' + str(i)] \
				if 'date_of_birth_' + str(i) in self.cleaned_data else False
			gender = self.cleaned_data['gender_' + str(i)] \
				if 'gender_' + str(i) in self.cleaned_data else False
			relationship_type = self.cleaned_data['relationship_type_' + str(i)] \
				if 'relationship_type_' + str(i) in self.cleaned_data else False
			# check that if we have any fields, we have all fields
			if (first_name or last_name or date_of_birth or gender or relationship_type) and \
				not (first_name and last_name and date_of_birth and gender and relationship_type) :
				self.add_error('first_name_' + str(i),'All fields must be entered')
				valid = False
			# check that children are not too old
			child_over_four = Age_Status.objects.get(status='Child over four')
			maximum_age = child_over_four.maximum_age
			today = datetime.date.today()
			if (date_of_birth != None) and (date_of_birth < today.replace(year=today.year-maximum_age)):
				self.add_error('date_of_birth_' + str(i),'Must be less than ' + str(maximum_age) + ' years old.')
				valid = False
			if (date_of_birth != None) and (date_of_birth > today):
				self.add_error('date_of_birth_' + str(i),'Must not be in the future.')
				valid = False
		# return the result
		return valid

class QuestionsForm(forms.Form):
	# over-ride the built in __init__ method so that we can add fields dynamically
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(QuestionsForm, self).__init__(*args, **kwargs)
		# build the crispy form
		self.helper = FormHelper()
		rows = []
		# now through the questions to be used for invitaions and build fields
		for question in Question.objects.filter(use_for_invitations=True):
			field_name = 'question_' + str(question.pk)
			notes_name = 'notes_' + str(question.pk)
			option_list = []
			# set the non-answer
			option_list.append((0,'No answer'))
			# now build the options
			for option in question.option_set.all():
				option_list.append((option.pk,option.option_label))
			# create the field
			self.fields[field_name]= forms.ChoiceField(
														label=question.question_text,
														widget=forms.Select(attrs={'class' : 'form-control'}),
														choices=option_list,
														required=False
														)
			# if the question has notes, also create a notes field
			if question.notes:
				self.fields[notes_name]= forms.CharField(
										label=question.notes_label,
										max_length=50,
										widget=forms.TextInput(attrs={'class' : 'form-control',}),
										required=False,
										)
			# build the crispy row
			if question.notes:
				row = Row(
						Column(field_name,css_class='form-group col-md-6 mbt-0'),
						Column(notes_name,css_class='form-group col-md-6 mbt-0'),
						)
			else:
				row = Row(
						Column(field_name,css_class='form-group col-md-6 mbt-0'),
						)
			rows.append(row)
		# build the crispy layout
		row = Row(
					Column(Submit('action', 'Enter'),css_class='col-md-12 mb-0')
					)
		rows.append(row)
		self.helper.layout = Layout(*rows)

class SignatureForm(forms.Form):
	signature = JSignatureField()

class Invitation_Handler():
	template = 'people/invitation.html'

	def __init__(self,invitation,invitation_step_type):
		# set defaults
		self.invitation = invitation
		self.invitation_step_type = invitation_step_type
		self.step_complete = False
		self.display_text = False
		self.default_date = datetime.date.today().strftime('%d/%m/%Y')
		self.signature = False
		self.step_data = ''
		# set the default date of birth based on site level offset
		site = Site.objects.all().first()
		dob_offset = site.dob_offset if site else 0
		today = datetime.date.today()
		self.default_date_of_birth = today.replace(year=today.year-dob_offset).strftime('%d/%m/%Y')
	
	def handle_request(self,request=False):
		# initialise variables
		# if we didn't get a post, set a blank form
		if not request or request.method != 'POST':
			self.form = self.initialise_form()
		else:
			# otherwise, check if the form is valid, do the updates for the step, and then update the step
			self.form = self.initialise_form_from_post(request.POST)
			# print(request.POST['signature'])
			if self.form.is_valid():
				self.handle_step_updates()
				self.mark_step_complete()

	def initialise_form(self):
		return self.form_class()

	def initialise_form_from_post(self,post):
		return self.form_class(post)

	def handle_step_updates(self):
		# placeholder for handler specific updates
		pass

	def mark_step_complete(self):
		# mark the step as complete in this object and in the database
		Invitation_Step.objects.create(
										invitation=self.invitation,
										invitation_step_type=self.invitation_step_type,
										step_data = self.step_data
										)
		self.step_complete = True

class Terms_And_Conditions_Invitation_Handler(Invitation_Handler):
	form_class = TermsAndConditionsForm

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(Terms_And_Conditions_Invitation_Handler, self).__init__(*args, **kwargs)
		# get the terms and conditions text and set it as display text
		self.display_text = self.invitation_step_type.terms_and_conditions.notes

	def handle_step_updates(self):
		# set the data
		self.step_data = self.invitation_step_type.terms_and_conditions.name + ' accepted'

class Introduction_Invitation_Handler(Invitation_Handler):
	form_class = IntroductionForm

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(Introduction_Invitation_Handler, self).__init__(*args, **kwargs)
		# get the introduction text from the site and set it as display text
		site = Site.objects.all().first()
		self.display_text = site.invitation_introduction if site else ''

	def handle_step_updates(self):
		# set the data
		self.step_data = 'Introduction acknowledged'

class Personal_Details_Invitation_Handler(Invitation_Handler):
	form_class = PersonalDetailsForm

	def initialise_form(self):
		return self.form_class(person=self.invitation.person)

	def handle_step_updates(self):
		# get records to use in the update
		person = self.invitation.person
		# update the record
		person.first_name = self.form.cleaned_data['first_name']
		person.last_name = self.form.cleaned_data['last_name']
		person.email_address = replace_if_value(person.email_address,self.form.cleaned_data['email_address'])
		person.home_phone = replace_if_value(person.home_phone,self.form.cleaned_data['home_phone'])
		person.mobile_phone = replace_if_value(person.mobile_phone,self.form.cleaned_data['mobile_phone'])
		person.emergency_contact_details = replace_if_value(
																person.emergency_contact_details,
																self.form.cleaned_data['emergency_contact_details']
																)
		person.date_of_birth = replace_if_value(person.date_of_birth,self.form.cleaned_data['date_of_birth'])
		person.gender = replace_if_value(person.gender,self.form.cleaned_data['gender'])
		person.pregnant = replace_if_value(person.pregnant,self.form.cleaned_data['pregnant'])
		person.due_date = replace_if_value(person.due_date,self.form.cleaned_data['due_date'])
		person.save()
		# update the data for recording and display
		data_dict = {
						'First Name' : self.form.cleaned_data['first_name'],
						'Last Name' : self.form.cleaned_data['last_name'],
						'Email Address' : self.form.cleaned_data['email_address'],
						'Home Phone' : self.form.cleaned_data['home_phone'],
						'Mobile Phone' : self.form.cleaned_data['mobile_phone'],
						'Emergency Contact Details' : self.form.cleaned_data['emergency_contact_details'],
						'Date of Birth' : str(self.form.cleaned_data['date_of_birth']),
						'Gender' : self.form.cleaned_data['gender'],
						'Pregnant' : str(self.form.cleaned_data['pregnant']),
						'Due Data': str(self.form.cleaned_data['due_date']),
					}
		self.step_data = json.dumps(data_dict)

class Address_Invitation_Handler(Invitation_Handler):
	form_class = AddressForm

	def handle_step_updates(self):
		# get records to use in the update
		person = self.invitation.person
		street = Street.objects.get(pk=self.form.cleaned_data['street'])
		# update the record
		person.house_name_or_number = self.form.cleaned_data['house_name_or_number']
		person.street = street
		person.save()
		# update the data for recording and display
		self.step_data = person.house_name_or_number + ' ' + person.street.name + ' ' + person.street.post_code.post_code

class Children_Invitation_Handler(Invitation_Handler):
	form_class = ChildrenForm

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(Children_Invitation_Handler, self).__init__(*args, **kwargs)
		# set the default date of birth for the form, based on maximum age for Child under four
		child_under_four = Age_Status.objects.get(status='Child under four')
		today = datetime.date.today()
		self.default_date_of_birth = today.replace(year=today.year-child_under_four.maximum_age).strftime('%d/%m/%Y')

	def handle_step_updates(self):
		# get records and set values to use in the update
		person = self.invitation.person
		child_over_four = Age_Status.objects.get(status='Child over four')
		child_under_four = Age_Status.objects.get(status='Child under four')
		today = datetime.date.today()
		data_dict = {}
		rows = []
		# go through the fields
		for i in range(6):
			# check that we have the data to create the record
			if self.form.cleaned_data['first_name_' + str(i)] != '':
				# figure out the age
				date_of_birth = self.form.cleaned_data['date_of_birth_' + str(i)]
				if date_of_birth < today.replace(year=today.year-child_under_four.maximum_age):
					age_status = child_over_four
				else:
					age_status = child_under_four
				# create the person
				child = Person.objects.create(
												first_name = self.form.cleaned_data['first_name_' + str(i)],
												last_name = self.form.cleaned_data['last_name_' + str(i)],
												date_of_birth = date_of_birth,
												age_status = age_status,
												default_role = age_status.default_role_type,
												gender = self.form.cleaned_data['gender_' + str(i)]
												)
				# and the relationship
				relationship_type = Relationship_Type.objects.get(
										pk=self.form.cleaned_data['relationship_type_' + str(i)])
				Relationship.create_relationship(
													person_from=person,
													person_to=child,
													relationship_type_from=relationship_type
													)
				# append the data to the row
				rows.append(
							[
								self.form.cleaned_data['first_name_' + str(i)],
								self.form.cleaned_data['last_name_' + str(i)],
								str(date_of_birth),
								str(age_status),
								self.form.cleaned_data['gender_' + str(i)],
								str(relationship_type)
							]
							)
		# if data has been entered, store it as json in the step data
		if rows:
			data_dict['headers'] = (
									'First Name',
									'Last Name',
									'Date of Birth',
									'Age Status',
									'Gender',
									'Relationship'
									)
			data_dict['rows'] = rows
			self.step_data = json.dumps(data_dict)
		else:
			self.step_data = ''

class Questions_Invitation_Handler(Invitation_Handler):
	form_class = QuestionsForm

	def handle_step_updates(self):
		# initialise the variables
		data_dict = {}
		rows = []
		# get the questions and set the values we need for each question
		for question in Question.objects.filter(use_for_invitations=True):
			field_name = 'question_' + str(question.pk)
			notes_name = 'notes_' + str(question.pk)
			option_id = self.form.cleaned_data[field_name]
			notes = self.form.cleaned_data[notes_name] if question.notes else False
			person = self.invitation.person
			# if we have a value, create or update the answer
			if option_id != '0':
				option = Option.try_to_get(pk=int(option_id))
				answer = Answer.try_to_get(
											person=person,
											question=question
											)
				if answer:
					answer.option = option
				else:
					answer = Answer(
									person=person,
									question=question,
									option=option)
				answer.save()
				# if we have notes, update those too
				if notes:
					answer_note = Answer_Note.try_to_get(
														person=person,
														question=question
														)
					if answer_note:
						answer_note.notes = notes
					else:
						answer_note = Answer_Note(
													person=person,
													question=question,
													notes=notes)
					answer_note.save()
				# append the data to the row
				rows.append(
							[
								str(question),
								option.option_label,
								notes if notes else 'No notes'
							]
							)
		# if data has been entered, store it as json in the step data
		if rows:
			data_dict['headers'] = (
										'Question',
										'Answer',
										'Notes',
									)
			data_dict['rows'] = rows
			self.step_data = json.dumps(data_dict)
		else:
			self.step_data = ''

class Signature_Invitation_Handler(Invitation_Handler):
	form_class = SignatureForm

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(Signature_Invitation_Handler, self).__init__(*args, **kwargs)
		# set the signature flag
		self.signature = True

	def handle_step_updates(self):
		# add the signature to the invitation
		self.signature = self.form.cleaned_data['signature']

	def mark_step_complete(self):
		# mark the step as complete in this object and in the database
		# as this is a signature step, include the signature
		Invitation_Step.objects.create(
										invitation=self.invitation,
										invitation_step_type=self.invitation_step_type,
										signature = self.signature,
										step_data='signed',
										)
		self.step_complete = True

	