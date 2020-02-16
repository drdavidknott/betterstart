import collections
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note, Site, Activity_Type, Activity, \
					Dashboard_Panel_Spec, Dashboard_Panel_Column_Spec, Dashboard_Panel_Column_Inclusion, \
					Filter_Spec, Dashboard_Column_Spec, Dashboard_Panel_Inclusion, Dashboard_Spec, \
					Dashboard_Column_Inclusion
import datetime

def class_from_str(class_str):
	# this function takes the name of a class in a string and returns the class, if it exists
	return globals()[class_str] if class_str in globals() else False

class Dashboard_Panel:
	# this class contains the data and structure for a dashboard panel
	def __init__(
					self, 
					title='',
					column_names=False,
					title_url=False,
					title_icon=False,
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
					display_zeroes=False,
					spec_name=False,
					spec=False,
					):
		# if we got a spec name or value, set the values from the spec, otherwise use parameters
		if spec or spec_name:
			# set the values
			self.spec = spec
			self.spec_name = spec_name
			# build the values
			self.build_panel_from_spec()
		# otherwise use the parameters as supplied
		else:
			self.title = title
			self.title_url = title_url
			self.title_icon = title_icon
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
				self.load_rows_from_objects(
											rows=rows,
											row_name=row_name,
											row_values=row_values,
											row_url=row_url,
											row_parameter_name=row_parameter_name,
											totals = totals
											)

	def build_panel_from_spec(self):
		# if we've been passed a spec name, try to get the corresponding spec record
		if self.spec_name:
			self.spec = Dashboard_Panel_Spec.try_to_get(name=self.spec_name)
		# if we have no record, set the errors and return
		if not self.spec:
			self.set_panel_error('SPEC DOES NOT EXIST')
			return
		# set the panel level variables
		self.title = self.spec.title
		self.title_url = self.spec.title_url
		self.title_icon = self.spec.title_icon
		self.show_column_names = self.spec.show_column_names
		self.label_width = self.spec.label_width
		self.column_width = self.spec.column_width
		self.right_margin = self.spec.right_margin
		self.totals = self.spec.totals
		self.display_zeroes = self.spec.display_zeroes
		self.row_url = self.spec.row_url
		self.row_parameter_name = self.spec.row_parameter_name
		# try to set the model for the panel
		self.model = class_from_str(self.spec.model)
		# if that didn't work, set panel level errors and return
		if not self.model:
			self.set_panel_error('MODEL DOES NOT EXIST')
			return
		# now build the rows
		self.build_rows_from_spec()

	def build_rows_from_spec(self):
		# get the columns
		columns = self.spec.dashboard_panel_column_inclusion_set.order_by('order')
		# initialise variables
		rows = []
		row_values = []
		self.column_names = []
		self.rows = []
		# build the row value and column titles
		for column in columns:
			row_values.append(column.dashboard_panel_column_spec.name)
			self.column_names.append(column.dashboard_panel_column_spec.title)
		# get the queryset
		panel_queryset = self.get_panel_queryset()
		# go through the rows, based on the model for the panel
		for row in panel_queryset:
			# for each row, go through each column
			for column in columns:
				# get the queryset
				count_queryset = getattr(row,column.dashboard_panel_column_spec.count_field).all()
				# apply filters
				count_queryset = self.apply_filters(count_queryset,column.dashboard_panel_column_spec.filters.all())
				# add the count field to the row object
				setattr(
						row,
						column.dashboard_panel_column_spec.name,
						count_queryset.count()
						)
			# append the row to the list
			rows.append(row)
		# call the function to populate the rows from a list of objects
		self.load_rows_from_objects(
									rows=rows,
									row_name=self.spec.row_name_field,
									row_values=row_values,
									row_url=self.row_url,
									row_parameter_name=self.row_parameter_name,
									totals = self.totals
									)

	def get_panel_queryset(self):
		# get the queryset used to populate the panel
		panel_queryset = self.model.objects.all()
		# order it if it needs ordering
		if self.spec.sort_field:
			panel_queryset = panel_queryset.order_by(self.spec.sort_field)
		# and filter it if it needs filtering
		panel_queryset = self.apply_filters(panel_queryset,self.spec.filters.all())
		# return the results
		return panel_queryset

	def apply_filters(self,queryset,filters):
		# set an empty dict
		filter_dict = {}
		# apply filters to a queryset and return the result
		for filter in filters:
			# set the value depending on the type
			if filter.filter_type == 'boolean':
				filter_dict[filter.term] = filter.boolean_value
			elif filter.filter_type == 'string':
				filter_dict[filter.term] = filter.string_value
			elif filter.filter_type == 'period':
				filter_dict = self.add_period_filters(filter, filter_dict)
			# apply the filter
			queryset = queryset.filter(**filter_dict)
		# return the result
		return queryset

	def add_period_filters(self,filter,filter_dict):
		# get the start and end of the period, based on the type of period
		period_start, period_end = self.get_period_dates(filter.period)
		# set the terms based on the supplied term
		start_term = filter.term + '__gte'
		end_term = filter.term + '__lte'
		# add the start filter
		filter_dict[start_term] = period_start
		filter_dict[end_term] = period_end
		# return the results
		return filter_dict

	def get_period_dates(self,period):
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

	def set_panel_error(self, error='ERROR'):
		# set up the panel to show that we have failed to load it
		self.title = error
		# initialise variables to help display the error
		self.rows = []
		self.totals = False
		# create a single row object
		self.rows.append(Dashboard_Panel_Row(
												label = error,
												values = [error],
												url = False,
												parameter = 0
												))

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
	def __init__(
					self,
					title = '',
					margin=1,
					spec = False,
					spec_name = False
					):
		# set the attributes
		self.title = title
		self.margin = margin
		self.spec = spec
		self.spec_name = spec_name
		# and an empty list of columns
		self.columns = []
		# build from spec if we have a spec
		if self.spec or self.spec_name:
			self.build_dashboard_from_spec()

	# function to build the dashboard contents from a spec defined in the database
	def build_dashboard_from_spec(self):
		# if we have a name, attempt to get the object
		if self.spec_name:
			self.spec = Dashboard_Spec.try_to_get(name=self.spec_name)
		# if we don't have a spec, build errors
		if not self.spec:
			set_dashboard_error('NO DASHBOARD SPEC')
			return

	def set_dashboard_error(self, error='ERROR'):
		# create a panel row to show the error
		error_row = Dashboard_Panel_Row(
										label=error,
										values=[error]
										)
		# and a panel, with the row appended
		error_panel = Dashboard_Panel(
										title = error,
										title_icon = 'glyphicon-warning-sign',
										label_width = 6,
										column_width = 5,
										right_margin = 1,
										)
		error_panel.rows.append(error_row)
		# and a column with the row appended
		error_column = Dashboard_Column(width=4)
		error_column.panels.append(error_panel)
		# and, finally, append the column
		self.columns.append(error_column)