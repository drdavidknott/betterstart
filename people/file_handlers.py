# this module contains classes to handle the upload and download of files

# import necessary modules
import csv, datetime
# import models
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note

class File_Field():
	# this class defines a field witin a file
	def __init__(self, name, mandatory=False):
		# set the attributes
		self.name = name
		self.mandatory = mandatory
		self.default = ''
		self.errors = []
		self.converter = False

	def set_upload_value(self, record):
		# set the value to the default
		self.value = self.default
		# check whether we have a value in the record
		if self.name in record.keys():
		# set the value
			self.value = record[self.name]

	def validate_upload_value(self):
		# check whether we have a value for a mandatory field
		if self.mandatory and self.value == '':
			# set the error
			self.errors.append(' not created: mandatory field ' + self.name + ' not provided')

	def set_download_value(self, object):
		# set the value from the object
		self.value = getattr(object,self.name)

class File_Datetime_Field(File_Field):
	# this class defines a field within a file of datetime format
	# over-ride the built in __init__ method to add additional values
	def __init__(self, *args, **kwargs):
		# pull the datetime format out of the parameter
		datetime_format = kwargs.pop('datetime_format')
		# call the built in constructor
		super(File_Datetime_Field, self).__init__(*args, **kwargs)
		# and set the attributes
		self.datetime_format = datetime_format
		self.converter = True

	def set_upload_value(self, record):
		# set the value to the default
		self.value = self.default
		# check whether we have a value in the record
		if self.name in record.keys():
		# set the value
			self.value = record[self.name]

	def validate_upload_value(self):
		# call the built in validator
		super(File_Datetime_Field, self).validate_upload(*args, **kwargs)
		# check whether we have a date
		if self.value:
			# check the value against the date
			try:
				datetime.datetime.strptime(self.value, datetime_format)
				# pass the test
				pass
			# deal with the exception
			except ValueError:
				# set the result
				self.errors = str(value) + ' is invalid date or time'

	def convert_upload_value(self):
		# check whether we have a value
		if self.value:
			# set the converted value
			self.value = datetime.datetime.strptime(self.value,self.format)

	def convert_download_value(self):
		# check whether we have a value
		if self.value:
			# set the converted value
			self.value = this_datetime.strftime(self.format)

class File_Handler():
	# this class handles upload and download functions for a file, as well as validation
	def __init__(self):
		# set attributes
		self.results = []
		# create a list of class fields
		self.fields = []

	# process an uploaded file
	def handle_uploaded_file(self, file):
		# clear the results
		self.results = []
		# read the file as a csv file
		records = csv.DictReader(file)
		# check that we have the fields we were expecting
		if self.file_format_valid(records.fieldnames.copy()):
			# go through the records
			for record in records:
				# validate the record
				if (self.fields_valid(record) and 
					self.corresponding_records_valid(record) and
					self.cross_field_valid(record)):
					# create the record
					self.create_record(record)

	def file_format_valid(self, file_keys):
		# set the result to false
		success = False
		# sort them
		file_keys.sort()
		self.fields.sort()
		# now check that they match
		if file_keys != self.fields:
			# set the message to a failure message
			self.results.append('File cannot be loaded as it does not contain the right fields.')
			self.results.append('Expected ' + str(self.fields) + ' but got ' + str(file_keys) + '.')
		# otherwise, we got what we expected
		else:
			# set the success flag
			success = True
		# return the result
		return success

	def add_record_results(self,record,results):
		# add results if there are any
		if results:
			# go through the results
			for result in results:
				# set the result
				result = self.label(record) + result
				# and append the result
				self.results.append(result)

	def fields_valid(self,record):
		# set the result to True
		success = True
		# do field level validation
		for field in self.fields:
			# get the attr
			file_field = getattr(self,field)
			# now set the value 
			file_field.set_upload_value(record)
			# and check the value
			file_field.validate_upload_value()
			# if there are errors, append them to the file errors
			if file_field.errors: 
				# add the errors
				self.add_record_results(record,file_field.errors)
				# set the value
				success = False
		# return the result
		return success

	def corresponding_records_valid(self,record):
		# placeholder function to be replaced in sub-classess
		return True

	def cross_field_valid(self,record):
		# placeholder function to be replaced in sub-classes
		return True

	def create_record(self,record):
		# placeholder function to be replaced in sub-classes
		return True

	def label(self,record):
		# placeholder function to be replaced in sub-classes
		return ''
	
class Event_Categories_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Event_Categories_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event_Category
		# set the file fields
		self.name = File_Field(name='name',mandatory=True)	
		self.description = File_Field(name='description',mandatory=True)
		# and a list of the fields
		self.fields = ['name','description']

	def corresponding_records_valid(self,record):
		# set result to False
		result = False
		# get the event category name
		name = record['name']
		# check whether the event_category already exists
		try:
			event_category = Event_Category.objects.get(name=name)
			# set the message to show that it exists
			self.add_record_results(record,[' not created: event category already exists.'])
		# otherwise deal with the failure
		except (Event_Category.DoesNotExist):
			# set the flag
			result = True
		# return the result
		return result

	def create_record(self,record):
		# create the record
		event_category = Event_Category(
										name=record['name'],
										description=record['description']
										)
		# save the event_category
		event_category.save()
		# set a message
		self.add_record_results(record,[' created.'])

	def label(self,record):
		# return the label
		return 'Event Category ' + record['name']

class Event_Types_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Event_Types_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event_Type
		# set the file fields
		self.name = File_Field(name='name',mandatory=True)	
		self.description = File_Field(name='description',mandatory=True)
		self.event_category = File_Field(name='event_category',mandatory=True)
		# and a list of the fields
		self.fields = ['name','description','event_category']

	def corresponding_records_valid(self,record):
		# set result to True
		result = True
		# get the event category name
		name = record['name']
		# check whether the event_type already exists
		try:
			event_type = Event_Type.objects.get(name=name)
			# set the message to show that it exists
			self.add_record_results(record,[' not created: event type already exists.'])
			# and set the result
			result = False
		# otherwise deal with the failure
		except (Event_Type.DoesNotExist):
			# pass
			pass
		# check whether the event category exists
		try:
			event_category = Event_Category.objects.get(name=record['event_category'])
		# deal with the exception
		except (Event_Category.DoesNotExist):
			# set the message
			self.add_record_results(record,[' not created: event category ' + record['event_category'] + ' does not exist.'])
			# and set the result
			result = False
		# return the result
		return result

	def create_record(self,record):
		# create the record
		event_type = Event_Type(
								name = record['name'],
								description = record['description'],
								event_category = Event_Category.objects.get(name=record['event_category'])
								)
		# save the event_category
		event_type.save()
		# set a message
		self.add_record_results(record,[' created.'])

	def label(self,record):
		# return the label
		return 'Event Type ' + record['name']