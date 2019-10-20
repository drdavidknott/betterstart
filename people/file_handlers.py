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
	def __init__(
					self,
					name,
					mandatory=False,
					corresponding_model=None,
					corresponding_field=None,
					corresponding_must_exist=False,
					corresponding_must_not_exist=False,
					):
		# set the attributes
		self.name = name
		self.mandatory = mandatory
		self.corresponding_model = corresponding_model
		self.corresponding_field = corresponding_field
		self.corresponding_must_exist = corresponding_must_exist
		self.corresponding_must_not_exist = corresponding_must_not_exist
		self.corresponding_record = None
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
		# check whether we have a corresponding record that should not exist
		if self.corresponding_must_not_exist and self.corresponding_exists():
			# set the error
			self.errors.append(
								' not created: ' + 
								str(self.corresponding_model.__name__) + ' ' +
								str(self.value)	+
								' already exists.')
		# check whether we have a corresponding record that should exist
		if self.corresponding_must_exist and not self.corresponding_exists():
			# set the error
			self.errors.append(
								' not created: ' + 
								str(self.corresponding_model.__name__) + ' ' +
								str(self.value)	+
								' does not exist.')

	def set_download_value(self, object):
		# set the value from the object
		self.value = getattr(object,self.name)

	def corresponding_exists(self):
		# define the query dict
		filter_dict = { self.corresponding_field : self.value }
		# attempt to get the record
		try:
			# try the read
			self.value = self.corresponding_model.objects.get(**filter_dict)
			# set the success flag
			exists = True
		# deal with the exception
		except (self.corresponding_model.DoesNotExist):
			# set the flag
			exists = False
		# return the result
		return exists

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

	def validate_upload_value(self,*args,**kwargs):
		# call the built in validator
		super(File_Datetime_Field, self).validate_upload_value(*args, **kwargs)
		# check whether we have a date
		if self.value:
			# check the value against the date
			try:
				self.value = datetime.datetime.strptime(self.value, datetime_format)
			# deal with the exception
			except ValueError:
				# set the result
				self.errors = str(value) + ' is invalid date or time'

	def convert_download_value(self):
		# check whether we have a value and that we haven't already converted
		if self.value:
			# set the converted value
			self.value = this_datetime.strftime(self.format)

class File_Boolean_Field(File_Field):
	# this class defines a field within a file of datetime format

	def validate_upload_value(self,*args,**kwargs):
		# call the built in validator
		super(File_Boolean_Field, self).validate_upload_value(*args, **kwargs)
		# set the value
		self.value = (self.value == 'True')

class File_Handler():
	# this class handles upload and download functions for a file, as well as validation
	def __init__(self,*args,**kwargs):
		# set default attributes
		self.results = []
		self.fields = []
		self.file_class = ''
		# check whether we have received a file class
		if 'file_class' in kwargs.keys():
			# set the file class
			self.file_class = kwargs['file_class']
		# and do the same for a field
		if 'field_name' in kwargs.keys():
			# get the simple load field
			field_name = kwargs['field_name']
			# create a file field objects
			file_field = File_Field(
									name=field_name,
									mandatory=True,
									corresponding_model=self.file_class,
									corresponding_field=field_name,
									corresponding_must_not_exist=True,
									)
			# set the field
			setattr(self,field_name,file_field)
			# and append the name to the fields list
			self.fields.append(field_name)
			# and set it to the label field
			self.label_field = field_name

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
					self.multi_field_corresponding_records_valid(record) and
					self.cross_field_valid(record)):
					# create the record
					self.create_record(record)
		# print(self.results)

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

	def multi_field_corresponding_records_valid(self,record):
		# placeholder function to be replaced in sub-classess
		return True

	def cross_field_valid(self,record):
		# placeholder function to be replaced in sub-classes
		return True

	def create_record(self,record):
		# build a dictionary which contains the fields
		field_dict = {}
		# go through the fields
		for field in self.fields:
			# get the object
			file_field = getattr(self,field)
			# set the value from the field
			field_dict[file_field.name] = file_field.value
		# create the record object
		new_record = self.file_class(**field_dict)
		# save the record
		new_record.save()
		# set a message
		self.add_record_results(record,[' created.'])

	def label(self,record):
		# placeholder function to be replaced in sub-classes
		return self.file_class.__name__ + ' ' + record[self.label_field]
	
class Event_Categories_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Event_Categories_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event_Category
		# set the file fields
		self.name = File_Field(
								name='name',
								mandatory=True,
								corresponding_model=Event_Category,
								corresponding_field='name',
								corresponding_must_not_exist=True)	
		self.description = File_Field(name='description',mandatory=True)
		# and a list of the fields
		self.fields = ['name','description']

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
		self.name = File_Field(
								name='name',
								mandatory=True,
								corresponding_model=Event_Type,
								corresponding_field='name',
								corresponding_must_not_exist=True
								)
		self.description = File_Field(name='description',mandatory=True)
		self.event_category = File_Field(
											name='event_category',
											mandatory=True,
											corresponding_model=Event_Category,
											corresponding_field='name',
											corresponding_must_exist=True)
		# and a list of the fields
		self.fields = ['name','description','event_category']

	def label(self,record):
		# return the label
		return 'Event Type ' + record['name']

class Wards_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Wards_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Ward
		# set the file fields
		self.ward_name = File_Field(
									name='ward_name',
									mandatory=True,
									corresponding_model=Ward,
									corresponding_field='ward_name',
									corresponding_must_not_exist=True
									)
		self.area = File_Field(
								name='area',
								mandatory=True,
								corresponding_model=Area,
								corresponding_field='area_name',
								corresponding_must_exist=True
								)
		# and a list of the fields
		self.fields = ['ward_name','area']

	def label(self,record):
		# return the label
		return 'Ward: ' + record['ward_name'] + ' (Area: ' + record['area'] + ')'

class Post_Codes_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Post_Codes_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Post_Code
		# set the file fields
		self.post_code = File_Field(
								name='post_code',
								mandatory=True,
								corresponding_model=Post_Code,
								corresponding_field='post_code',
								corresponding_must_not_exist=True
								)
		self.ward = File_Field(
								name='ward',
								mandatory=True,
								corresponding_model=Ward,
								corresponding_field='ward_name',
								corresponding_must_exist=True
								)
		# and a list of the fields
		self.fields = ['post_code','ward']

	def label(self,record):
		# return the label
		return 'Post code: ' + record['post_code'] + ' (Ward: ' + record['ward'] + ')'

class Streets_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Streets_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Street
		# set the file fields
		self.name = File_Field(
								name='name',
								mandatory=True,
								corresponding_model=Street,
								corresponding_field='name',
								corresponding_must_not_exist=True
								)
		self.post_code = File_Field(
								name='post_code',
								mandatory=True,
								corresponding_model=Post_Code,
								corresponding_field='post_code',
								corresponding_must_exist=True
								)
		# and a list of the fields
		self.fields = ['name','post_code']

	def label(self,record):
		# return the label
		return 'Street: ' + record['name'] + ' (Post Code: ' + record['post_code'] + ')'

class Role_Types_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Role_Types_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Role_Type
		# set the file fields
		self.role_type_name = File_Field(
								name='role_type_name',
								mandatory=True,
								corresponding_model=Role_Type,
								corresponding_field='role_type_name',
								corresponding_must_not_exist=True
								)
		self.use_for_events = File_Boolean_Field(name='use_for_events',mandatory=True)
		self.use_for_people = File_Boolean_Field(name='use_for_people',mandatory=True)
		self.trained = File_Boolean_Field(name='trained',mandatory=True)

		# and a list of the fields
		self.fields = ['role_type_name','use_for_events','use_for_people','trained']

	def label(self,record):
		# return the label
		return 'Role Type: ' + record['role_type_name']

class Relationship_Types_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Relationship_Types_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Relationship_Type
		# set the file fields
		self.relationship_type = File_Field(
											name='relationship_type',
											mandatory=True,
											corresponding_model=Relationship_Type,
											corresponding_field='relationship_type',
											corresponding_must_not_exist=True
											)
		self.relationship_counterpart = File_Field(name='relationship_counterpart',mandatory=True)

		# and a list of the fields
		self.fields = ['relationship_type','relationship_counterpart']

	def label(self,record):
		# return the label
		return 'Relationship type: ' + record['relationship_type']

