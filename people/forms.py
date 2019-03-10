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
