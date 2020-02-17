# a bunch of utilities to help manage page layouts etc.

from django.template import loader
from django.shortcuts import render, HttpResponse, redirect
import collections
import datetime

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
			page_list.append(
								Page(
									number = page,
									start = getattr(objects[start_index],attribute),
									end = getattr(objects[end_index],attribute),
									length = length,
									separator = separator
									)
							)
	# return the result
	return page_list

def make_banner(request, banner_text):
	# load the banner template
	banner_template = loader.get_template('people/banner.html')
	# set the context
	context = {"banner" : banner_text }
	# set the banner
	banner = HttpResponse(banner_template.render(context, request))
	# return the output
	return banner

# function to extract an id number from the end of an underscore delimited string
def extract_id(field_name):
	# build a list from the string
	name_elements = field_name.split('_')
	# now return the final element
	return name_elements[-1]

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
	# return the results
	return period_start, period_end


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

class Chart:
	# the class contains details of a chart
	def __init__(
					self,
					title,
					title_icon=False,
					title_url=False,
					fig='Not yet defined',
					labels = None,
					sizes = None,
					queryset=False,
					label_attr=False,
					size_attr=False,
					include_zeroes=False,
					):
		# set the attributes
		self.title = title
		self.title_icon = title_icon
		self.title_url = title_url
		self.fig = fig
		# convert the Nones to empty lists, due to python's treatment of default list parameters
		if labels is None:
			self.labels = []
		# and sizes
		if sizes is None:
			self.sizes = []
		# if we have a queryset, set the labels and sizes
		if queryset:
			# set the labels and sizes
			for record in queryset:
				# check whether we have a size
				if getattr(record,size_attr) or include_zeroes:
					# get the values
					size = getattr(record,size_attr)
					label = getattr(record,label_attr) + ' (' + str(size) + ')'
					# set the values
					self.labels.append(label)
					self.sizes.append(size)

