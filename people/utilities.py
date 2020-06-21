# a bunch of utilities to help manage page layouts etc.

from django.template import loader
from django.shortcuts import render, HttpResponse, redirect
import collections
import datetime
from dateutil.relativedelta import relativedelta
import operator

def get_page_list(objects, page_length):
	# take a list of objects and a page length, and build a list of pages
	object_number = len(objects)
	# see if we have more than one page
	if object_number <= page_length:
		# we only have one page, so make the list false
		page_list = False
	# otherwise we need to iterate through the list
	else:
		# create an empty list
		page_list = [1]
		# and a page number
		page_number = 1
		# iterate through the list
		while (object_number > page_length):
			# increase the page number
			page_number += 1
			# append to the list
			page_list.append(page_number)
			# decrease the object number
			object_number -= page_length
	# return the result
	return page_list

def build_page_list(objects, page_length, attribute, length=False, separator='to'):
	# take a list of objects and a page length, and build a list of pages
	object_number = len(objects)
	# see if we have more than one page
	if object_number <= page_length:
		# we only have one page, so make the list false
		page_list = False
	# otherwise we need to iterate through the list
	else:
		# create an empty pagelist
		page_list = []
		# create an empty list of pages
		pages = [1]
		# and a page number
		page_number = 1
		# iterate through the list
		while (object_number > page_length):
			# increase the page number
			page_number += 1
			# append to the list
			pages.append(page_number)
			# decrease the object number
			object_number -= page_length
		# now go through the list and build page objects
		for page in pages:
			# set the values
			start_index = (25 * (page - 1))
			# and the end index
			end_index = ((25 * page) - 1)
			# check whether the end index is greater than the length
			if end_index > (len(objects) -1):
				# set the end index
				end_index = (len(objects) - 1)
			# create a page object in a new list
			attribute_getter = operator.attrgetter(attribute)
			page_list.append(
								Page(
									number = page,
									start = attribute_getter(objects[start_index]),
									end = attribute_getter(objects[end_index]),
									length = length,
									separator = separator
									)
							)
	# return the result
	return page_list

def make_banner(request, banner_text, public=False):
	# load the banner template
	if public:
		banner_template = loader.get_template('people/public_banner.html')
	else:
		banner_template = loader.get_template('people/banner.html')
	# set the context
	context = {"banner" : banner_text }
	# set the banner
	banner = HttpResponse(banner_template.render(context, request))
	# return the output
	return banner

# function to extract an id number from the end of an underscore delimited string
def extract_id(field_name):
	# build a list from the string if it contains underscore, else just take the string
	if '_' in field_name:
		name_elements = field_name.split('_')
		extracted_id = name_elements[-1]
	else:
		extracted_id = field_name
	# now return the results
	return extracted_id

# function to take a string, a value, a descriptor and delimiter, and build a description
def add_description(value,text,delimiter=', ',desc=''):
	# check the value
	if value:
		# check whether there is already a value in the description
		if desc:
			# add the delimiter
			desc += delimiter
		# and add the text
		desc += text
	# return the desc
	return desc

# function to take a string defining a period and return the start and end dates
def get_period_dates(period):
	# initialise the variables
	period_start = False
	period_end = False
	today = datetime.date.today()
	# build a set of useful dates
	this_month_start = today.replace(day=1)
	last_month_end = this_month_start - datetime.timedelta(days=1)
	last_month_start = last_month_end.replace(day=1)
	this_project_year_start = today.replace(day=1,month=4)
	rolling_quarter_start = (today - relativedelta(months=3))
	# check if we have jumped into the future
	if this_project_year_start > today:
		this_project_year_start = this_project_year_start.replace(year=this_project_year_start.year-1)
	last_project_year_end = this_project_year_start - datetime.timedelta(days=1)
	last_project_year_start = this_project_year_start.replace(year=this_project_year_start.year-1)
	this_calendar_year_start = today.replace(day=1,month=1)
	last_calendar_year_start = today.replace(day=1,month=1,year=this_calendar_year_start.year-1)
	last_calendar_year_end = this_calendar_year_start - datetime.timedelta(days=1)
	# set the dates dependent on the period type we are looking for
	if period == 'this_month':
		period_start = this_month_start
	elif period == 'last_month':
		period_start = last_month_start
		period_end = last_month_end
	elif period == 'this_project_year':
		period_start = this_project_year_start
	elif period == 'last_project_year':
		period_start = last_project_year_start
		period_end = last_project_year_end
	elif period == 'this_calendar_year':
		period_start = this_calendar_year_start
	elif period == 'last_calendar_year':
		period_start = last_calendar_year_start
		period_end = last_calendar_year_end
	elif period == 'rolling_quarter':
		period_start = rolling_quarter_start
		period_end = today
	# return the results
	return period_start, period_end

def build_choices(
					choice_field='',
					choice_queryset=False,
					choice_class=False,
					default=False,
					default_value=0,
					default_label=''
					):
	# create a blank list
	choice_list = []
	# set the default if we have one
	if default:
		choice_list.append((default_value,default_label))
	# build the choices from a query set, or from all objects in a class
	if choice_queryset:
		choices = choice_queryset.order_by(choice_field)
	else:
		choices = choice_class.objects.all().order_by(choice_field)
	# build the list for use in the form
	for choice in choices:
		choice_list.append((choice.pk, getattr(choice,choice_field)))
	# return the list
	return choice_list

def replace_if_value(old_value,new_value):
	# replaces the old value with the new value, if there is data in the new value
	return new_value if new_value not in ('',False,None,0) else old_value

class Page:
	# the class contains details of a page
	def __init__(self,number,start,end,separator= 'to',length=False):
		# set the attributes
		self.number = number
		self.separator = separator
		# if we have a length, limit the length of the start and end string
		if length:
			# set the start and end
			self.start = str(start)[:length]
			self.end = str(end)[:length]
		# otherwise, just take the start and end
		else:
			# set the start and end
			self.start = start
			self.end = end
	# return the page description as a string
	def __str__(self):
		# return the page description
		return str(self.start) + ' ' + str(self.separator) + ' ' + str(self.end)

