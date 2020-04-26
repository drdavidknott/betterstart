# this module contains classes to handle the processing of invitation steps

# import necessary modules
import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Invitation, Invitation_Step, Invitation_Step_Type, \
							Person, Relationship, Relationship_Type, Street, Terms_And_Conditions, \
							Ethnicity, Age_Status, Question, Answer, Option, Answer_Note
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Hidden, ButtonHolder, Field, HTML
from crispy_forms.bootstrap import FormActions
from django.urls import reverse
from .utilities import build_choices, replace_if_value

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
	ethnicity = forms.ChoiceField(
									label="Ethnicity",
									widget=forms.Select(attrs={'class' : 'form-control'}))
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
		# over-ride the __init__ method to set the choices
		# call the built in constructor
		super(PersonalDetailsForm, self).__init__(*args, **kwargs)
		# set the choice fields
		self.fields['ethnicity'].choices = build_choices(choice_class=Ethnicity,choice_field='description')
		# define the crispy form
		self.helper = FormHelper()
		self.helper.layout = Layout(
									Row(
										Column('date_of_birth',css_class='form-group col-md-4 mbt-0'),
										Column('ethnicity',css_class='form-group col-md-4 mbt-0'),	
										Column('gender',css_class='form-group col-md-4 mbt-0'),
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
		# over-ride the __init__ method to set the choices
		# call the built in constructor
		super(ChildrenForm, self).__init__(*args, **kwargs)
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
		# build the crispy form
		self.helper = FormHelper()
		rows = []
		for i in range(6):
			str_i = str(i)
			row = Row(
						Column('first_name_' + str_i,css_class='form-group col-md-4 mbt-0'),
						Column('last_name_' + str_i,css_class='form-group col-md-4 mbt-0'),
						Column('date_of_birth_' + str_i,css_class='form-group col-md-4 mbt-0')
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
			# check that if we have any fields, we have all fields
			if (first_name or last_name or date_of_birth) and \
				not (first_name and last_name and date_of_birth) :
				self.add_error('first_name_' + str(i),'All fields must be entered')
				valid = False
			# check that children are not too old
			child_over_four = Age_Status.objects.get(status='Child over four')
			maximum_age = child_over_four.maximum_age
			today = datetime.date.today()
			if (date_of_birth != None) and (date_of_birth < today.replace(year=today.year-maximum_age)):
				self.add_error('date_of_birth_' + str(i),'Must be less than ' + str(maximum_age) + ' years old.')
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

class Invitation_Handler():
	template = 'people/invitation.html'

	def __init__(self,invitation,invitation_step_type):
		self.invitation = invitation
		self.invitation_step_type = invitation_step_type
		self.step_complete = False
		self.display_text = False
	
	def handle_request(self,request=False):
		# initialise variables
		# if we didn't get a post, set a blank form
		if not request or request.method != 'POST':
			self.form = self.initialise_form()
		else:
			# otherwise, check if the form is valid, do the updates for the step, and then update the step
			self.form = self.initialise_form_from_post(request.POST)
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
										invitation_step_type=self.invitation_step_type
										)
		self.step_complete = True

class Terms_And_Conditions_Invitation_Handler(Invitation_Handler):
	form_class = TermsAndConditionsForm

	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(Terms_And_Conditions_Invitation_Handler, self).__init__(*args, **kwargs)
		# get the terms and conditions text and set it as display text
		terms_and_conditions = Terms_And_Conditions.objects.get(
																start_date__lte=datetime.date.today(),
																end_date__isnull=True
																)
		self.display_text = terms_and_conditions.notes

class Personal_Details_Invitation_Handler(Invitation_Handler):
	form_class = PersonalDetailsForm

	def handle_step_updates(self):
		# get records to use in the update
		person = self.invitation.person
		ethnicity = Ethnicity.try_to_get(pk=self.form.cleaned_data['ethnicity'])
		# update the record
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
		person.ethnicity = ethnicity
		person.save()

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

class Children_Invitation_Handler(Invitation_Handler):
	form_class = ChildrenForm

	def handle_step_updates(self):
		# get records and set values to use in the update
		person = self.invitation.person
		child_over_four = Age_Status.objects.get(status='Child over four')
		child_under_four = Age_Status.objects.get(status='Child over four')
		carer_relationship = Relationship_Type.objects.get(relationship_type__iexact='Other carer')
		today = datetime.date.today()
		# go through the fields
		for i in range(6):
			# get the form data
			first_name = self.form.cleaned_data['first_name_' + str(i)] \
				if 'first_name_' + str(i) in self.form.cleaned_data else False
			last_name = self.form.cleaned_data['last_name_' + str(i)] \
				if 'last_name_' + str(i) in self.form.cleaned_data else False
			date_of_birth = self.form.cleaned_data['date_of_birth_' + str(i)] \
				if 'date_of_birth_' + str(i) in self.form.cleaned_data else False
			# if we have an entry, create the record
			if first_name:
				# figure out the age
				if date_of_birth < today.replace(year=today.year-child_under_four.maximum_age):
					age_status = child_over_four
				else:
					age_status = child_under_four
				# create the person
				child = Person.objects.create(
												first_name = first_name,
												last_name = last_name,
												date_of_birth = date_of_birth,
												age_status = age_status,
												default_role = age_status.default_role_type
												)
				# and the relationship
				Relationship.create_relationship(
													person_from=person,
													person_to=child,
													relationship_type_from=carer_relationship
													)

class Questions_Invitation_Handler(Invitation_Handler):
	form_class = QuestionsForm

	def handle_step_updates(self):
		# get the questions and set the values we need for each question
		for question in Question.objects.filter(use_for_invitations=True):
			field_name = 'question_' + str(question.pk)
			notes_name = 'notes_' + str(question.pk)
			option_id = self.form.cleaned_data[field_name]
			notes = self.form.cleaned_data[notes_name]
			person = self.invitation.person
			# if we have a value, create or update the answer
			if option_id != '0':
				option = Option.try_to_get(pk=int(option_id))
				print(option_id)
				print(option)
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



	