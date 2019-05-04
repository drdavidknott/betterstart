# a bunch of utilities to help manage page layouts etc.

from django.template import loader
from django.shortcuts import render, HttpResponse, redirect
import collections

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

def make_banner(request, banner_text):
	# load the banner template
	banner_template = loader.get_template('people/banner.html')
	# set the context
	context = {"banner" : banner_text }
	# set the banner
	banner = HttpResponse(banner_template.render(context, request))
	# return the output
	return banner

class Dashboard_Panel_Row():
	# this class contains the data and structure for a row
	def __init__(self, label, values, url=False, parameter=0):
		# set the attributes
		self.label = label
		self.values = values
		self.url = url
		self.parameter = parameter

	def has_data(self):
		# check whether any of the values contain data
		# set a flag
		has_data = False
		# go through the values
		for value in self.values:
			# check that it has a positive value
			if value:
				# set the flag
				has_data = True
		# return the value
		return has_data

class Dashboard_Panel:
	# this class contains the data and structure for a dashboard panel
	def __init__(
					self, 
					title,
					column_names,
					show_column_names=False,
					label_width=6,
					column_width=6,
					right_margin=0,
					rows=False,
					row_name=False, 
					row_values=False,
					row_url=False,
					row_parameter_name=False,
					totals=False,
					display_zeroes=False
					):
		# set the attributes
		self.title = title
		self.column_names = column_names
		self.show_column_names = show_column_names
		self.label_width = label_width
		self.column_width = column_width
		self.right_margin = right_margin
		self.totals = totals
		self.display_zeroes = display_zeroes
		# initialise the list of rows
		self.rows = []
		# if we have been passed a list of objects to load into rows, process them
		if rows:
			# call the function to populate the rows from a list of objects
			print(rows)
			self.load_rows_from_objects(
										rows=rows,
										row_name=row_name,
										row_values=row_values,
										row_url=row_url,
										row_parameter_name=row_parameter_name,
										totals = totals
										)

	def load_rows_from_objects(
								self,
								rows,
								row_name,
								row_values,
								row_url,
								row_parameter_name,
								totals
								):
	# this function will populate the panel from a list of objects, based on the name of the row field and the row
	# values fields
		# process the passed list of objects
		for row in rows:
			# get the row label using the passed row field name
			label = getattr(row, row_name)
			# get the parameter value using the passed paramter field nae
			if row_parameter_name:
				# get the parameter
				parameter = getattr(row, row_parameter_name)
			# otherwise set the parameter to zero
			else:
				# set the parameter to zero
				parameter = 0
			# set an empty list of values
			values = []
			# now build the list of values
			for row_value in row_values:
				# get the value
				value = getattr(row, row_value)
				# append the value
				values.append(value)
			# create a row object
			self.rows.append(Dashboard_Panel_Row(
													label = label,
													values = values,
													url = row_url,
													parameter = parameter
													))

	def get_totals(self):
		# return a list of totals for the panel
		# create a list of totals
		totals = []
		# create a dictionary of lists
		total_lists = collections.OrderedDict()
		# now go through the rows
		for row in self.rows:
			# now go through the values and build a list
			for index, value in enumerate(row.values):
				# check whether the dictionary entry exists
				if index not in total_lists:
					# initialise the list
					total_lists[index] = []
				# now add the item
				total_lists[index].append(value)
		# now build the actual totals
		for total_list in total_lists:
			# initalise the list for this total
			this_total = 0
			# go through the items
			for value in total_lists[total_list]:
				# add it to the total
				this_total += value
			# now append the total to the list
			totals.append(this_total)
		# return the list of totals
		return totals

class Dashboard_Column:
	# this class contains the data and sructure for a dashboard column
	def __init__(self, heading='', width=5, margins=1):
		# set the attributes
		self.heading = heading
		self.width = width
		self.margins = margins
		# and an empty list of panels
		self.panels = []

class Dashboard:
	# the class contains the data to be shown in the dashboard, as well as the dashboard structure
	def __init__(self, title = '', margin=1):
		# set the attributes
		self.title = title
		self.margin = margin
		# and an empty list of columns
		self.columns = []
