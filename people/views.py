from django.shortcuts import render, HttpResponse
from django.template import loader
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Address, Residence, Event, Event_Type, \
					Event_Category, Event_Registration
import os
import csv

def index(request):
	# get the template
	index_template = loader.get_template('people/index.html')
	# return the HttpResponse
	return HttpResponse(index_template.render(context=None, request=request))

def dataload(request):
	# get the template
	index_template = loader.get_template('people/dataload.html')
	# create a list of messages
	messages = []
	# get the directory
	directory = os.path.dirname(__file__)
	# load areas
	messages = messages + load_areas(directory)
	# load wards
	messages = messages + load_wards(directory)
	# load post codes and get the results as messages
	messages = messages + load_post_code(directory)
	# add the messages to the context
	context = {'messages' : messages}
	# return the HttpResponse
	return HttpResponse(index_template.render(context=context, request=request))

def load_areas(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	areas_file_name = os.path.join(directory, 'data/areas.csv')
	# open the areas file
	areas_file = open(areas_file_name,'r')
	# read it as a csv file
	areas = csv.DictReader(areas_file)
	# go through the csv file and process it
	for area in areas:
		# get the area name
		area_name = area['area']
		# check whether the area already exists
		try:
			area = Area.objects.get(area_name=area_name)
			# set the message to show that it exists
			messages.append('Area ' + area_name + ' already exists.')
		except (Area.DoesNotExist):
			# the area does not exist, so create it
			area = Area(area_name=area_name)
			# save the area
			area.save()
			# set the message
			messages.append('Area ' + area_name + ' created.')
	# return the messages
	return messages

def load_wards(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	wards_file_name = os.path.join(directory, 'data/wards.csv')
	# open the areas file
	wards_file = open(wards_file_name,'r')
	# read it as a csv file
	ward_rows = csv.DictReader(wards_file)
	# go through the csv file and process it
	for ward_row in ward_rows:
		# get the area name
		area_name = ward_row['area']
		# get the ward name
		ward_name = ward_row['ward']
		# check whether the area exists
		try:
			area = Area.objects.get(area_name=area_name)
			# now try to find the ward
			try:
				ward = Ward.objects.get(ward_name=ward_name)
				# set the message to show that it exists
				messages.append('Ward ' + ward_name + ' in area ' + area_name + ' already exists.')
			except (Ward.DoesNotExist):
				# create the ward
				ward = Ward(
							ward_name = ward_name,
							area = area
							)
				# save the ward
				ward.save()
				# and set the message
				messages.append('Ward ' + ward_name + ' in area ' + area_name + ' created.')
		except (Area.DoesNotExist):
			# the area does not exist, so set an error messaage
			messages.append('Area ' + area_name + ' does not exist, so ward ' + ward_name + ' not created.')
	# return the messages
	return messages

def load_post_code(directory):
	# set a blank messages lists
	messages = []
	# set the file name
	postcodes_file_name = os.path.join(directory, 'data/postcodes.csv')
	# open the post code file
	postcodes_file = open(postcodes_file_name,'r')
	# read it as a csv file
	postcode_rows = csv.DictReader(postcodes_file)
	# go through the csv file and process it
	for postcode_row in postcode_rows:
		# get the post code
		post_code_name = postcode_row['postcode']
		# and the ward
		ward_name = postcode_row['ward']
		# check whether the ward exists
		try:
			ward = Ward.objects.get(ward_name=ward_name)
			# now try to find the post code
			try:
				post_code = Post_Code.objects.get(post_code=post_code_name)
				# set the message to show that it exists
				messages.append('Post code ' + post_code_name + ' in ward ' + ward_name + ' already exists.')
			except (Post_Code.DoesNotExist):
				# create the ward
				post_code = Post_Code(
										post_code = post_code_name,
										ward = ward
									)
				# save the ward
				post_code.save()
				# and set the message
				messages.append('Post code ' + post_code_name + ' in ward ' + ward_name + ' created.')
		except (Ward.DoesNotExist):
			# the area does not exist, so set an error messaage
			messages.append('Ward ' + ward_name + ' does not exist, so post code ' + post_code_name + ' not created.')
	# return the messages
	return messages


