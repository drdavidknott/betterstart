# this module contains classes to handle the processing of invitation steps

# import necessary modules
import datetime
from django import forms
from django.contrib.auth.models import User
from .models import Invitation, Invitation_Step, Invitation_Step_Type, \
							Person, Relationship, Relationship_Type, Street, Terms_And_Conditions
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Hidden, ButtonHolder, Field, HTML
from crispy_forms.bootstrap import FormActions
from django.urls import reverse

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
			self.form = self.form_class()
		else:
			# otherwise, check if the form is valid, do the updates for the step, and then update the step
			self.form = self.form_class(request.POST)
			if self.form.is_valid():
				self.handle_step_updates()
				self.mark_step_complete()

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




