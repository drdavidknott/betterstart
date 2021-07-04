# this module contains classes to handle the upload and download of files

# import necessary modules
import csv, datetime
# import models
from .models import Person, Relationship_Type, Relationship, Family, Ethnicity, Trained_Role, Role_Type, \
					Children_Centre, CC_Registration, Area, Ward, Post_Code, Event, Event_Type, \
					Event_Category, Event_Registration, Capture_Type, Question, Answer, Option, Role_History, \
					ABSS_Type, Age_Status, Street, Answer_Note, Activity, Activity_Type, Venue, Venue_Type, \
					Project, Membership, Membership_Type

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
					use_corresponding_for_download=False,
					include_in_create=True,
					include_in_update=True,
					set_download_from_object=True,
					corresponding_relationship_field=False,
					default='',
					max_length=False
					):
		# set the attributes
		self.name = name
		self.mandatory = mandatory
		self.corresponding_model = corresponding_model
		self.corresponding_must_exist = corresponding_must_exist
		self.corresponding_must_not_exist = corresponding_must_not_exist
		self.use_corresponding_for_download = use_corresponding_for_download
		self.include_in_create = include_in_create
		self.include_in_update = include_in_update
		self.set_download_from_object = set_download_from_object
		self.corresponding_record = None
		self.default = default
		self.max_length=max_length
		self.errors = []
		self.converter = False
		self.valid = False
		self.update = False
		# and set the corresponding  field if we have one
		if corresponding_field:
			# set the attribute
			self.corresponding_field = corresponding_field
		# else, set it to the field name
		else:
			# use the name
			self.corresponding_field = self.name
		# and set the corresponding relationship field if we have one
		if corresponding_relationship_field:
			# set the attribute
			self.corresponding_relationship_field = corresponding_relationship_field
		# else, set it to the field name
		else:
			# use the name
			self.corresponding_relationship_field = self.name

	def set_upload_value(self, record):
		# clear the errors
		self.errors = []
		# set the value to the default
		self.value = self.default
		# check whether we have a value in the record
		if self.name in record.keys():
		# set the value
			self.value = record[self.name]
			# if the value is blank, set the default
			if self.value == '':
				# set the default
				self.value = self.default

	def validate_upload_value(self):
		# check whether we have a value for a mandatory field
		if self.mandatory and self.value == '':
			self.errors.append(' not created: mandatory field ' + self.name + ' not provided')
		# check whether the field is greater than max_length
		if self.max_length and self.value and len(self.value) > self.max_length:
			self.errors.append(
								' not created: ' + 
								str(self.name) + ' ' + str(self.value) +
								' is longer than maximum length of ' + str(self.max_length))
		# if we have a corresponding record, attempt to get it
		if self.corresponding_model:
			self.corresponding_exists()
		# check whether we have a corresponding record that should not exist
		if self.value and self.corresponding_must_not_exist and self.exists:
			self.errors.append(
								' not created: ' + 
								str(self.corresponding_model.__name__) + ' ' +
								str(self.value)	+
								' already exists.')
		# check whether we have a corresponding record that should exist
		if self.value and self.corresponding_must_exist and not self.exists:
			self.errors.append(
								' not created: ' + 
								str(self.corresponding_model.__name__) + ' ' +
								str(self.value)	+
								' does not exist.')
		# set the validity flag
		self.valid = (not self.errors)

	def set_download_value(self, object):
		# check whether we should set this from the object
		if self.set_download_from_object:
			# see whether we get the value from this object or the corresponding object
			if self.use_corresponding_for_download:
				# get the object
				corresponding_object = getattr(object,self.corresponding_relationship_field)
				# check whether we have an object
				if corresponding_object:
					# now get the field from the corresponding object
					self.value = getattr(corresponding_object,self.corresponding_field)
				# otherwise set a blank value
				else:
					# set the default
					self.value = self.default
			# otherwise get it from the passed object
			else:
				# set the value from the object
				self.value = getattr(object,self.name)
		# otherwise set the default
		else:
			# set the default
			self.value = self.default

	def corresponding_exists(self):
		# check whether we have a value
		if self.value != '':
			# define the query dict
			filter_dict = { self.corresponding_field : self.value }
			# attempt to get the record
			try:
				self.value = self.corresponding_model.objects.get(**filter_dict)
				exists = True
			# deal with the exception
			except (self.corresponding_model.DoesNotExist):
				exists = False
		# otherwise set the values
		else:
			exists = False
			self.value = None
		# set the value
		self.exists = exists
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
		if self.value != '':
			# check the value against the date
			try:
				self.value = datetime.datetime.strptime(self.value, self.datetime_format)
			# deal with the exception
			except ValueError:
				# set the result
				self.errors.append(' not created: ' + str(self.name) + ' ' 
									+ str(self.value) + ' is invalid date or time.')
		# otherwise set the value to None
		else:
			# set the value
			self.value = None
		# set the validity flag
		self.valid = (not self.errors)

	def set_download_value(self,object):
		# call the built in validator
		super(File_Datetime_Field, self).set_download_value(object)
		# check whether we have a value
		if self.value:
			# set the converted value
			self.value = self.value.strftime(self.datetime_format)
		# otherwise set a blank
		else:
			# set a blank
			self.value = ''

class File_Delimited_List_Field(File_Field):
	# this class defines a field within a file which contains a list of delimited values
	# over-ride the built in __init__ method to add additional values
	def __init__(self, *args, **kwargs):
		# pull the delimiter out of the parameter
		delimiter = kwargs.pop('delimiter')
		# call the built in constructor
		super(File_Delimited_List_Field, self).__init__(*args, **kwargs)
		# and set the attributes
		self.delimiter = delimiter

	def validate_upload_value(self,*args,**kwargs):
		# call the built in validator
		super(File_Delimited_List_Field, self).validate_upload_value(*args, **kwargs)
		# check whether we have a value
		if self.value != '':
			# set the value
			self.value = self.value.split(self.delimiter)
		# otherwise create an exmpty list
		else:
			# set the value
			self.value = []
		# set the validity flag
		self.valid = (not self.errors)

	def set_download_value(self,object):
		# call the built in validator
		super(File_Delimited_List_Field, self).set_download_value(object)
		# create an empty string
		delimited_list = ''
		# go through the queryset
		for item in self.value.all():
			# check whether we need a delimiter
			if len(delimited_list):
				# add a delimiter
				delimited_list += self.delimiter
			# add the item to the list
			delimited_list += getattr(item,self.corresponding_field)
		# set the value to the delimited list
		self.value = delimited_list

class File_Boolean_Field(File_Field):
	# this class defines a field within a file of boolean format
	# over-ride the built in __init__ method to add additional values
	def __init__(self, *args, **kwargs):
		# call the built in constructor
		super(File_Boolean_Field, self).__init__(*args, **kwargs)
		# and set the attributes
		self.true_values = ['True','true','TRUE','yes','Yes','YES']

	def validate_upload_value(self,*args,**kwargs):
		# call the built in validator
		super(File_Boolean_Field, self).validate_upload_value(*args, **kwargs)
		# set the value
		self.value = (self.value in self.true_values)

class File_Integer_Field(File_Field):
	# this class defines a field within a file of integer format, with validation and conversion
	def validate_upload_value(self):
		# check whether we have an integer value
		try: 
			self.value = int(self.value)
			self.valid = True
		except ValueError:
			self.errors.append(' not created: integer field ' + self.name + ' ' + self.value + ' is not integer')
			self.valid = False

class File_Count_Field(File_Field):
	# this class defines a field within a file that contains a count 
	# over-ride the built in __init__ method to add additional values
	def __init__(self, *args, **kwargs):
		# pull the special fields out of the kwargs
		self.filter = kwargs.pop('filter')
		self.count_field = kwargs.pop('count_field')
		# call the built in constructor
		super(File_Count_Field, self).__init__(*args, **kwargs)

	def set_download_value(self, object):
		# get the queryset object
		queryset = getattr(object,self.count_field)
		# apply the filter if we have a filter, otherwise get all the objects
		if self.filter:
			queryset = queryset.filter(**self.filter)
		else:
			queryset = queryset.all()
		# set the value to the number of objects in the queryset
		self.value = queryset.count()

class File_Handler():
	# this class handles upload and download functions for a file, as well as validation
	def __init__(self,*args,**kwargs):
		# set default attributes
		self.results = []
		self.errors = []
		self.fields = []
		self.additional_download_fields = []
		self.file_class = ''
		self.upload = True
		self.update = False
		self.objects = None
		self.records_read = 0
		self.records_created = 0
		self.records_updated = 0
		self.records_with_errors = 0
		self.project_filter = {}
		# set the file class if we have received one
		if 'file_class' in kwargs.keys():
			self.file_class = kwargs['file_class']
		# add a field if we have received a field name
		if 'field_name' in kwargs.keys():
			field_name = kwargs['field_name']
			file_field = File_Field(
									name=field_name,
									mandatory=True,
									corresponding_model=self.file_class,
									corresponding_field=field_name,
									corresponding_must_not_exist=True,
									)
			setattr(self,field_name,file_field)
			self.fields.append(field_name)
			self.label_field = field_name
		# and the objects if we have received them
		if 'objects' in kwargs.keys():
			self.objects = kwargs['objects']
		# and the project if we have received one
		if 'project' in kwargs.keys():
			self.project = kwargs['project']

	# process an uploaded file
	def handle_uploaded_file(self, file):
		# clear the results
		self.results = []
		# check whhether we are allowed to upload this file
		if self.upload:
			# read the file as a csv file
			records = csv.DictReader(file)
			# check that we have the fields we were expecting
			if self.file_format_valid(records.fieldnames.copy()):
				# go through the records
				for record in records:
					# count the read
					self.records_read += 1
					# do the validation
					fields_valid = self.fields_valid(record)
					complex_valid = self.complex_validation_valid(record)
					# create the record if all is valid; increment counts in either case
					if (fields_valid and complex_valid):
						self.create_record(record)
						self.records_created += 1
					else:
						self.records_with_errors += 1
			# print(self.results)
		else:
			# set the message to say that upload is not allowed
			self.results.append('This file type cannot be uploaded.')

	# provide records for download
	def handle_download(self):
		# define empty records
		self.download_records = []
		# get the objects if we've not already been passed them, filtering by project if we have a project filter
		if not self.objects:
			self.objects = self.file_class.objects.all()
			if self.project_filter:
				self.objects = self.objects.filter(**self.project_filter)
		# go through the objects
		for this_object in self.objects:
			# set the fields
			self.set_download_fields(this_object)
			# now append the record
			self.download_records.append(self.get_download_record())
		# placeholder for now
		return

	# process an uploaded file
	def handle_update(self, file):
		# clear the results
		self.results = []
		# check whhether we are allowed to upload this file
		if self.update:
			# read the file as a csv file
			records = csv.DictReader(file)
			# check that we have the fields we were expecting
			if self.file_format_valid(records.fieldnames.copy()):
				# go through the records
				for record in records:
					# count the read
					self.records_read += 1
					# get the database entry to update
					self.get_existing_record(record)
					# do the validation
					if self.existing_record:
						fields_valid = self.fields_valid(record,update=True)
						update_valid = self.update_validation_valid(record)
						# update the record if all is valid; increment counts in either case
						if (fields_valid and update_valid):
							self.update_record(record)
							self.records_updated += 1
						else:
							self.records_with_errors += 1
					else:
						# process a new record
						fields_valid = self.fields_valid(record)
						complex_valid = self.complex_validation_valid(record)
						# create the record if all is valid; increment counts in either case
						if (fields_valid and complex_valid):
							self.create_record(record)
							self.records_created += 1
						else:
							self.records_with_errors += 1
			# print(self.results)
		else:
			# set the message to say that upload is not allowed
			self.results.append('This file type cannot be used for updates.')

	# set the download fields
	def set_download_fields(self,this_object):
		# go through the fields, getting and setting the value
		for field_name in self.fields + self.additional_download_fields:
			field = getattr(self,field_name)
			field.set_download_value(this_object)

	# build a download record
	def get_download_record(self):
		# set the empty list
		field_list = []
		# go through the fields, adding the values to the list
		for field_name in self.fields + self.additional_download_fields:
			field = getattr(self,field_name)
			field_list.append(field.value)
		# return the result
		return field_list

	def file_format_valid(self, file_keys):
		# set the result to false
		success = False
		# sort them
		file_keys.sort()
		self.fields.sort()
		# now check that they match
		if file_keys != self.fields:
			# set the message to a failure message
			self.add_file_errors([
									'File cannot be loaded as it does not contain the right fields.',
									'Expected ' + str(self.fields) + ' but got ' + str(file_keys) + '.'
									])
		# otherwise, we got what we expected
		else:
			# set the success flag
			success = True
		# return the result
		return success

	def add_record_results(self,record,results):
		# add results if there are any, adding the standard record label
		for result in results:
			result = self.label(record) + result
			self.results.append(result)

	def add_record_errors(self,record,errors):
		# add errors if there are any, adding the standard error label
		for error in errors:
			error = 'Record ' + str(self.records_read) + ': ' + self.label(record) + error
			self.errors.append(error)

	def add_file_errors(self,errors):
		# add errors if there are any
		for error in errors:
			self.errors.append(error)

	def fields_valid(self,record,update=False):
		# set the result to True
		success = True
		# attempt to validate the field, setting the value in the process
		for field in self.fields:
			file_field = getattr(self,field)
			file_field.set_upload_value(record)
			# validate the field if this is not an update or if we have a value
			if not update or file_field.value != '':
				file_field.validate_upload_value()
				file_field.update = True
			else:
				file_field.value = False
			# if there are errors, append them to the file errors
			if file_field.errors: 
				self.add_record_errors(record,file_field.errors)
				success = False
		# return the result
		return success

	def complex_validation_valid(self,record):
		# placeholder function to be replaced in sub-classess
		return True

	def update_validation_valid(self,record):
		# set the results
		valid = True
		# set values for complex validation
		for field_name in self.fields:
			file_field = getattr(self,field_name)
			if not file_field.value and file_field.include_in_update:
				value = getattr(self.existing_record,field_name)
				# convert dates to datetimes for validation
				if isinstance(value,datetime.date):
					value = datetime.datetime.combine(value, datetime.datetime.min.time())
				file_field.value = value
				file_field.exists = True
				file_field.valid = True
		# do the complex validation
		valid = self.complex_validation_valid(record,update=True)
		# return the result
		return valid

	def get_existing_record(self,record):
		# placeholder function to be replaced in sub-classess
		return True

	def create_record(self,record):
		# build a dictionary which contains the fields
		field_dict = {}
		# set the fields
		for field in self.fields:
			file_field = getattr(self,field)
			if file_field.include_in_create:
				field_dict[file_field.name] = file_field.value
		# create the record
		new_record = self.file_class(**field_dict)
		new_record.save()
		# record the creation
		self.add_record_results(record,[' created.'])
		# if we have a project, add the project
		if self.project:
			self.add_project(new_record)
		# return the created record
		return new_record

	def update_record(self,record):
		# set the fields
		for field in self.fields:
			file_field = getattr(self,field)
			if file_field.update and file_field.include_in_update:
				setattr(self.existing_record,field,file_field.value)
		# update the record
		self.existing_record.save()
		# record the creation
		self.add_record_results(record,[' updated.'])
		# return the created record
		return self.existing_record

	def add_project(self,record):
		# dummy function extended in sub-classes
		return

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
								corresponding_must_not_exist=True,
								max_length=50
								)	
		self.description = File_Field(name='description',mandatory=True,max_length=500)
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
								corresponding_must_not_exist=True,
								max_length=50
								)
		self.description = File_Field(name='description',mandatory=True,max_length=500)
		self.event_category = File_Field(
											name='event_category',
											mandatory=True,
											corresponding_model=Event_Category,
											corresponding_field='name',
											corresponding_must_exist=True
										)
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
									corresponding_must_not_exist=True,
									max_length=50
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
								corresponding_must_not_exist=True,
								max_length=10
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
								max_length=100
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

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether the option exists
		if self.post_code.valid:
			# try to get the street
			street = Street.try_to_get(
										name = self.name.value,
										post_code = self.post_code.value
										)
			# see if we got a street
			if street:
				# set the error
				self.add_record_errors(record,[' not created: street already exists.'])
				# and the flag
				valid = False
		# return the result
		return valid

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
								corresponding_must_not_exist=True,
								max_length=50
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
											corresponding_must_not_exist=True,
											max_length=50
											)
		self.relationship_counterpart = File_Field(
													name='relationship_counterpart',
													mandatory=True,
													max_length=50
													)

		# and a list of the fields
		self.fields = ['relationship_type','relationship_counterpart']

	def label(self,record):
		# return the label
		return 'Relationship type: ' + record['relationship_type']

class People_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(People_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Person
		# and the file attributes
		self.update = True
		self.existing_record = False
		# set the file fields
		self.first_name = File_Field(name='first_name',mandatory=True,max_length=50)
		self.last_name = File_Field(name='last_name',mandatory=True,max_length=50)
		self.other_names = File_Field(name='other_names',max_length=50)
		self.email_address = File_Field(name='email_address',max_length=50)
		self.home_phone = File_Field(name='home_phone',max_length=50)
		self.mobile_phone = File_Field(name='mobile_phone',max_length=50)
		self.date_of_birth = File_Datetime_Field(name='date_of_birth',datetime_format='%d/%m/%Y')
		self.gender = File_Field(name='gender',max_length=25)
		self.pregnant = File_Boolean_Field(name='pregnant')
		self.due_date = File_Datetime_Field(name='due_date',datetime_format='%d/%m/%Y')
		self.default_role = File_Field(
										name='default_role',
										mandatory=True,
										corresponding_model=Role_Type,
										corresponding_field='role_type_name',
										corresponding_must_exist=True,
										use_corresponding_for_download=True
										)
		self.ethnicity = File_Field(
									name='ethnicity',
									mandatory=True,
									corresponding_model=Ethnicity,
									corresponding_field='description',
									corresponding_must_exist=True,
									use_corresponding_for_download=True
									)
		
		self.age_status = File_Field(
									name='age_status',
									mandatory=True,
									corresponding_model=Age_Status,
									corresponding_field='status',
									corresponding_must_exist=True,
									use_corresponding_for_download=True
									)
		self.house_name_or_number = File_Field(name='house_name_or_number',max_length=50)
		self.street = File_Field(
									name='street',
									use_corresponding_for_download=True,
									corresponding_field='name',
									include_in_update=False,
									default=None
									)
		self.post_code = File_Field(
									name='post_code',
									corresponding_model=Post_Code,
									corresponding_field='post_code',
									corresponding_must_exist=True,
									include_in_create=False,
									include_in_update=False,
									set_download_from_object=False
									)
		self.ward = File_Field(
								name='ward',
								set_download_from_object=False,
								)
		self.notes = File_Field(name='notes')
		self.emergency_contact_details = File_Field(name='emergency_contact_details')
		self.membership_number = File_Integer_Field(name='membership_number')
		# set membership fields depending on whether we have a project
		if self.project:
			self.membership_type = File_Field(
										name='membership_type',
										mandatory=True,
										corresponding_model=Membership_Type,
										corresponding_field='name',
										corresponding_must_exist=True,
										include_in_create=False,
										include_in_update=False,
										set_download_from_object=False
										)
			self.date_joined = File_Datetime_Field(
										name='date_joined',
										datetime_format='%d/%m/%Y',
										include_in_create=False,
										include_in_update=False,
										set_download_from_object=False
										)
			self.date_left = File_Datetime_Field(
										name='date_left',
										datetime_format='%d/%m/%Y',
										include_in_create=False,
										include_in_update=False,
										set_download_from_object=False
										)
			membership_fields = [
									'membership_type',
									'date_joined',
									'date_left'
								]
		else:
			self.ABSS_type = File_Field(
										name='ABSS_type',
										mandatory=True,
										corresponding_model=ABSS_Type,
										corresponding_field='name',
										corresponding_must_exist=True,
										use_corresponding_for_download=True
										)
			self.ABSS_start_date = File_Datetime_Field(name='ABSS_start_date',datetime_format='%d/%m/%Y')
			self.ABSS_end_date = File_Datetime_Field(name='ABSS_end_date',datetime_format='%d/%m/%Y')
			membership_fields = [
									'ABSS_type',
									'ABSS_start_date',
									'ABSS_end_date'
								]
		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'other_names',
						'email_address',
						'home_phone',
						'mobile_phone',
						'date_of_birth',
						'gender',
						'pregnant',
						'due_date',
						'default_role',
						'ethnicity',
						'age_status',
						'house_name_or_number',
						'street',
						'post_code',
						'notes',
						'emergency_contact_details',
						'membership_number'
						]
		# add in the membership fields
		self.fields += membership_fields
		# and additional download fields
		self.additional_download_fields = [
											'ward',
											]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'projects' : self.project }

	def get_existing_record(self,record):
		# initialise variables
		self.existing_record = False
		person = False
		# set the fields
		first_name = record['first_name']
		last_name = record['last_name']
		# check the value against the date
		try:
			date_of_birth = datetime.datetime.strptime(record['date_of_birth'], self.date_of_birth.datetime_format)
		# deal with the exception
		except ValueError:
			date_of_birth = False
			self.add_record_errors(
									record,
									[' not updated: date of birth ' 
										+ str(record['date_of_birth']) + ' is invalid date or time.'])
		# set the validity flag
		self.valid = (not self.errors)
		# attempt to get the person record
		if first_name and last_name and date_of_birth:
			person, message, multiples  = Person.try_to_get_just_one(
																		first_name = first_name,
																		last_name = last_name,
																		date_of_birth = date_of_birth
																	)
			# if we have a set the attribute, otherwise raise an error
			if person:
				self.existing_record = person
			else:
				self.add_record_errors(
										record,
										[' not created: ' + message]
										)
		return

	def complex_validation_valid(self,record,update=False):
		# set the value
		valid = True
		# check whether the person exists
		if self.first_name.valid and self.last_name.valid and self.date_of_birth.valid and not update:
			if Person.search(
								first_name = self.first_name.value,
								last_name = self.last_name.value,
								date_of_birth = self.date_of_birth.value,
								project = self.project,
								include_people = 'all'
								).exists():
				self.add_record_errors(record,[' not created: person already exists.'])
				valid = False
		# check whether the role is valid for the age status
		if (self.age_status.exists 
			and self.default_role.exists 
			and not self.age_status.value.role_types.filter(pk=self.default_role.value.pk).exists()):
			self.add_record_errors(record,[' not created: role type is not valid for age status.'])
			valid = False
		# get today's date
		today = datetime.date.today()
		# check whether the age is correct
		if (self.date_of_birth.value
			and self.age_status.valid
			and self.date_of_birth.valid
			and self.date_of_birth.value.date() < today.replace(year=today.year-self.age_status.value.maximum_age)):
			self.add_record_errors(record,[' not created: too old for age status'])
			valid = False
		# now check whether we have a due date without a pregnancy flag
		if self.due_date.value and not self.pregnant.value:
			self.add_record_errors(record,[' not created: has due date but is not pregnant.'])
			valid = False
		# now check the other way around
		if not self.due_date.value and self.pregnant.value:
			self.add_record_errors(record,[' not created: has no due date but is pregnant.'])
			valid = False
		# check whether we have any address details
		if (self.post_code.value or self.street.value or self.house_name_or_number.value) and not update:
			# now check whether we have ALL address details
			if not (self.post_code.value and self.street.value and self.house_name_or_number.value):
				self.add_record_errors(record,[' not created: all of post code, street and name/number needed for address.'])
				valid = False
			# else check the details if the post code exists
			elif self.post_code.exists:
				street = Street.try_to_get(
											name = self.street.value,
											post_code = self.post_code.value
											)
				if not street:
					self.add_record_errors(record,[' not created: Street ' + self.street.value + ' does not exist.'])
					valid = False
				else:
					self.street.value = street
		# validate project dates if we have a project and ABSS dates if we don't
		if self.project:
			# check whether we have a left date without a joined date
			if self.date_left.value and not self.date_joined.value:
				self.add_record_errors(record,[' not created: date left is provided but not date joined.'])
				valid = False
			# check whether the end date is greater than the start date
			if (self.date_joined.value and self.date_left.value
				and self.date_joined.valid and self.date_left.valid
				and self.date_joined.value >= self.date_left.value): 
					self.add_record_errors(record,[' not created: date left is not greater than date joined.'])
					valid = False
		else:
			# check whether we have a left date without a joined date
			if self.ABSS_end_date.value and not self.ABSS_start_date.value:
				self.add_record_errors(record,[' not created: ABSS end date is provided but not ABSS start date.'])
				valid = False
			# check whether the end date is greater than the start date
			if (self.ABSS_start_date.value and self.ABSS_end_date.value
				and self.ABSS_start_date.valid and self.ABSS_end_date.valid
				and self.ABSS_start_date.value >= self.ABSS_end_date.value): 
					self.add_record_errors(record,[' not created: ABSS end date is not greater than ABSS start date.'])
					valid = False
		# return the result
		return valid
	
	def label(self,record):
		# return the label
		return record['first_name'] + ' ' + record['last_name']

	def set_download_fields(self,person):
		# call the built in field setter
		super(People_File_Handler, self).set_download_fields(person)
		# set the post code and ward if we have a street
		self.post_code.value = person.street.post_code.post_code if person.street else ''
		self.ward.value = person.street.post_code.ward.ward_name if person.street else ''
		# set the membership fields if we have a project
		if self.project:
			membership = Membership.objects.get(person=person,project=self.project)
			self.membership_type.value = membership.membership_type.name
			self.date_joined.value = membership.date_joined
			self.date_left.value = membership.date_left 

	def add_project(self,person):
		# create the membership
		membership = Membership(
								person=person,
								project=self.project,
								membership_type = self.membership_type.value,
								date_joined = self.date_joined.value,
								date_left = self.date_left.value
								)
		membership.save()
		return

	def create_record(self,record):
		# if we have a project, add an ABSS type field with a default value
		# TEMPORARY UNTIL ABSS TYPE REMOVED ENTIRELY
		if self.project:
			self.ABSS_type = File_Field(name='ABSS_type')
			self.ABSS_type.value = ABSS_Type.objects.get(default=True)
			self.fields.append('ABSS_type')
		# call the built in method
		person = super(People_File_Handler, self).create_record(record)

class Relationships_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Relationships_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Relationship
		# set the file fields
		self.from_first_name = File_Field(
											name='from_first_name',
											mandatory=True,
											corresponding_field='first_name',
											use_corresponding_for_download=True,
											corresponding_relationship_field='relationship_from'
											)
		self.from_last_name = File_Field(
											name='from_last_name',
											mandatory=True,
											corresponding_field='last_name',
											use_corresponding_for_download=True,
											corresponding_relationship_field='relationship_from'
											)
		self.from_age_status = File_Field(
											name='from_age_status',
											mandatory=True,
											corresponding_model=Age_Status,
											corresponding_field='status',
											corresponding_must_exist=True,
											set_download_from_object=False
											)
		self.to_first_name = File_Field(
										name='to_first_name',
										mandatory=True,
										corresponding_field='first_name',
										use_corresponding_for_download=True,
										corresponding_relationship_field='relationship_to'
										)
		self.to_last_name = File_Field(
										name='to_last_name',
										mandatory=True,
										corresponding_field='last_name',
										use_corresponding_for_download=True,
										corresponding_relationship_field='relationship_to'
										)
		self.to_age_status = File_Field(
										name='to_age_status',
										mandatory=True,
										corresponding_model=Age_Status,
										corresponding_field='status',
										corresponding_must_exist=True,
										set_download_from_object=False
										)
		self.relationship_type = File_Field(
											name='relationship_type',
											mandatory=True,
											corresponding_model=Relationship_Type,
											corresponding_field='relationship_type',
											corresponding_must_exist=True,
											use_corresponding_for_download=True
											)
		# and a list of the fields
		self.fields = [
						'from_first_name',
						'from_last_name',
						'from_age_status',
						'to_first_name',
						'to_last_name',
						'to_age_status',
						'relationship_type'
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 
									'relationship_from__projects' : self.project,
									'relationship_to__projects' : self.project
									}

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we had a valid from age status
		if self.from_age_status.exists:
			# check whether the from person exists
			person, message, multiples = Person.try_to_get_just_one(
																	first_name = self.from_first_name.value,
																	last_name = self.from_last_name.value,
																	age_status = self.from_age_status.value,
																	projects = self.project
																	)
			# if there was an error, add it
			if not person:
				# append the error message
				self.add_record_errors(record,[' not created: from ' + message])
				# and set the flag
				valid = False
		# check whether we had a valid to age status
		if self.to_age_status:
			# check whether the to person exists
			person, message, multiples  = Person.try_to_get_just_one(
																		first_name = self.to_first_name.value,
																		last_name = self.to_last_name.value,
																		age_status = self.to_age_status.value,
																		projects = self.project
																		)
			# if there was an error, add it
			if not person:
				# append the error message
				self.add_record_errors(record,[' not created: to ' + message])
				# and set the flag
				valid = False
		# return the result
		return valid

	def create_record(self,record):
		# get the records, starting with the person from
		person_from = Person.try_to_get(
												first_name = record['from_first_name'],
												last_name = record['from_last_name'],
												age_status__status = record['from_age_status'],
												projects = self.project
												)
		# and the person to
		person_to = Person.try_to_get(
										first_name = record['to_first_name'],
										last_name = record['to_last_name'],
										age_status__status = record['to_age_status'],
										projects = self.project
										)
		# and the relationship type
		relationship_type = Relationship_Type.objects.get(relationship_type = record['relationship_type'])
		# build the record using the edit relationship function
		Relationship.edit_relationship(
										person_from = person_from,
										person_to = person_to,
										relationship_type = relationship_type
										)
		# set a message
		self.add_record_errors(record,[' created.'])

	def set_download_fields(self,relationship):
		# call the built in field setter
		super(Relationships_File_Handler, self).set_download_fields(relationship)
		# set the special fields
		self.from_age_status.value = relationship.relationship_from.age_status.status
		self.to_age_status.value = relationship.relationship_to.age_status.status

	def label(self,record):
		# return the label
		return str(record['from_first_name']) + ' ' + str(record['from_last_name']) \
							+ ' is ' + str(record['relationship_type']) + ' of ' \
							+ str(record['to_first_name']) + ' ' + str(record['to_last_name'])

class Events_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Events_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event
		# set the file fields
		self.name = File_Field(name='name',mandatory=True,max_length=50)
		self.description = File_Field(name='description',mandatory=True,max_length=1500)
		self.event_type = File_Field(
									name='event_type',
									mandatory=True,
									corresponding_model=Event_Type,
									corresponding_field='name',
									corresponding_must_exist=True,
									use_corresponding_for_download=True
									)
		self.date = File_Datetime_Field(
										name='date',
										datetime_format='%d/%m/%Y',
										mandatory=True
										)
		self.start_time = File_Datetime_Field(
												name='start_time',
												datetime_format='%H:%M',
												mandatory=True
												)
		self.end_time = File_Datetime_Field(
											name='end_time',
											datetime_format='%H:%M',
											mandatory=True
											)
		self.location = File_Field(name='location',max_length=100)
		self.venue = File_Field(
									name='venue',
									corresponding_model=Venue,
									corresponding_field='name',
									corresponding_must_exist=True,
									use_corresponding_for_download=True
									)
		self.ward = File_Field(
								name='ward',
								corresponding_model=Ward,
								corresponding_field='ward_name',
								corresponding_must_exist=True,
								use_corresponding_for_download=True
								)
		self.areas = File_Delimited_List_Field(
												name='areas',
												delimiter=',',
												corresponding_field='area_name',
												include_in_create = False,
												corresponding_relationship_field='areas'
												)
		# and a list of the fields
		self.fields = [
						'name',
						'description',
						'event_type',
						'date',
						'start_time',
						'end_time',
						'location',
						'venue',
						'ward',
						'areas',
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'project' : self.project }

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# now attempt to get a matching event
		if self.name.valid and self.date.valid and Event.search(
																name = self.name.value,
																date = self.date.value,
																project = self.project
																).exists():
			# set the message to show that it exists
			self.add_record_errors(record,[' not created: event already exists.'])
			# and set the flag
			valid = False
		# now go through the areas
		for area_name in self.areas.value:
			# deal with the exception
			if not Area.try_to_get(area_name = area_name):
				# set the error
				self.add_record_errors(record,[' not created: area ' + area_name + ' does not exist.'])
				# and the flag
				valid = False
		# return the result
		return valid

	def create_record(self,record):
		# call the built in method
		event = super(Events_File_Handler, self).create_record(record)
		# and then create the areas, reporting with a message
		for area_name in self.areas.value:
			area = Area.objects.get(area_name = area_name)
			event.areas.add(area)
			self.add_record_results(record,[': area ' + area_name + ' created.'])
		# add the area which the ward is in, if it hasn't been created already
		if event.ward and event.ward.area.area_name not in self.areas.value:
			event.areas.add(event.ward.area)
			self.add_record_results(record,[': area ' + event.ward.area.area_name + ' created.'])

	def set_download_fields(self,event):
		# call the built in field setter
		super(Events_File_Handler, self).set_download_fields(event)

	def add_project(self,event):
		# add the project to the event
		event.project = self.project
		event.save()
		return

	def label(self,record):
		# return the label
		return record['name']

class Venues_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Venues_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Venue
		# set the file fields
		self.name = File_Field(
								name='name',
								mandatory=True,
								max_length=100,
								corresponding_model=Venue,
								corresponding_field='name',
								corresponding_must_not_exist=True,
								)
		self.venue_type = File_Field(
									name='venue_type',
									mandatory=True,
									corresponding_model=Venue_Type,
									corresponding_field='name',
									corresponding_must_exist=True,
									use_corresponding_for_download=True
									)
		self.building_name_or_number = File_Field(
													name='building_name_or_number',
													mandatory=True,
													max_length=50
													)
		self.street = File_Field(
									name='street',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_field='name',
									)
		self.post_code = File_Field(
									name='post_code',
									mandatory=True,
									corresponding_model=Post_Code,
									corresponding_field='post_code',
									corresponding_must_exist=True,
									include_in_create=False,
									set_download_from_object=False
									)
		self.contact_name = File_Field(name='contact_name',max_length=100)
		self.email_address = File_Field(name='email_address',max_length=50)
		self.phone = File_Field(name='phone',max_length=50)
		self.mobile_phone = File_Field(name='mobile_phone',max_length=50)
		self.website = File_Field(name='website',max_length=100)
		self.price = File_Field(name='price',max_length=100)
		self.facilities = File_Field(name='facilities',max_length=100)
		self.opening_hours = File_Field(name='opening_hours',max_length=100)
		self.notes = File_Field(name='notes',max_length=1500)

		# and a list of the fields
		self.fields = [
						'name',
						'venue_type',
						'building_name_or_number',
						'street',
						'post_code',
						'contact_name',
						'phone',
						'mobile_phone',
						'email_address',
						'website',
						'price',
						'facilities',
						'opening_hours',
						'notes',
						]

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we have all address details
		if (self.post_code.value and self.street.value and self.building_name_or_number.value):
			# check whether the combination of street and post code is valid
			if self.post_code.exists:
				street = Street.try_to_get(
											name = self.street.value,
											post_code = self.post_code.value
											)
				if not street:
					self.add_record_errors(record,[' not created: Street ' + self.street.value + ' does not exist.'])
					valid = False
				# otherwise set the street value
				else:
					self.street.value = street
		# return the result
		return valid

	def set_download_fields(self,venue):
		# call the built in field setter
		super(Venues_File_Handler, self).set_download_fields(venue)
		# set the post_code
		self.post_code.value = venue.street.post_code.post_code

	def label(self,record):
		# return the label
		return record['name']

class Venues_For_Events_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Venues_For_Events_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event
		# set the file fields
		self.event_name = File_Field(
									name='event_name',
									mandatory=True,
									corresponding_relationship_field='event',
									corresponding_field='name',
									use_corresponding_for_download=True,
									)
		self.event_date = File_Datetime_Field(
												name='event_date',
												datetime_format='%d/%m/%Y',
												mandatory=True,
												corresponding_field='date',
												corresponding_relationship_field='event',
												use_corresponding_for_download=True,
												)
		self.venue_name = File_Field(
										name='venue_name',
										mandatory=True,
										corresponding_model=Venue,
										corresponding_field='name',
										corresponding_must_exist=True,
										use_corresponding_for_download=True,
										)

		# and a list of the fields
		self.fields = [
						'event_name',
						'event_date',
						'venue_name'
						]

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether a matching event exists
		if self.event_date.valid:
			event, message, multiples  = Event.try_to_get_just_one(
																	name = self.event_name.value,
																	date = self.event_date.value,
																	project = self.project
																	)
			# deal with the exception if we couldn't find an event
			if not event:
				self.add_record_errors(record,[' not created: ' + message])
				valid = False
		# return the result
		return valid

	def create_record(self,record):
		# get the records
		event = Event.try_to_get(
									name = self.event_name.value,
									date = self.event_date.value,
									project = self.project
									)
		# update the event
		event.venue = self.venue_name.value
		event.save()
		# set a message
		self.add_record_results(record,[' updated.'])
		# return the updated record
		return event

	def label(self,record):
		# return the label
		return str(record['event_name']) + ' on ' + str(record['event_date']) + ' at ' + str(record['venue_name'])

class Registrations_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Registrations_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event_Registration
		# set the file fields
		self.first_name = File_Field(
										name='first_name',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_relationship_field='person'
										)
		self.last_name = File_Field(
									name='last_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='person'
									)
		self.age_status = File_Field(
									name='age_status',
									mandatory=True,
									corresponding_model=Age_Status,
									corresponding_field='status',
									corresponding_must_exist=True,
									set_download_from_object=False
									)
		self.event_name = File_Field(
									name='event_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='event',
									corresponding_field='name'
									)
		self.event_date = File_Datetime_Field(
												name='event_date',
												datetime_format='%d/%m/%Y',
												mandatory=True,
												corresponding_field='date',
												use_corresponding_for_download=True,
												corresponding_relationship_field='event'
												)
		self.registered = File_Boolean_Field(name='registered',mandatory=True)
		self.participated = File_Boolean_Field(name='participated',mandatory=True)
		self.apologies = File_Boolean_Field(name='apologies',mandatory=True)
		self.role_type = File_Field(
										name='role_type',
										mandatory=True,
										corresponding_model=Role_Type,
										corresponding_field='role_type_name',
										corresponding_must_exist=True,
										use_corresponding_for_download=True
										)

		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'age_status',
						'event_name',
						'event_date',
						'registered',
						'apologies',
						'participated',
						'role_type'
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = {
									'event__project' : self.project,
									'person__projects' : self.project
									}

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we have a valid age status
		if self.age_status.exists:
			# check whether the person exists
			person, message, multiples  = Person.try_to_get_just_one(
																	first_name = self.first_name.value,
																	last_name = self.last_name.value,
																	age_status = self.age_status.value,
																	projects = self.project
																	)
			# if there was an error, add it
			if not person:
				# append the error message
				self.add_record_errors(record,[' not created: ' + message])
				# and set the flag
				valid = False
		# check whether the role type is valid for the age status
		if (self.role_type.exists and self.age_status.exists 
				and self.role_type.value not in self.age_status.value.role_types.all()):
			# set the error
			self.add_record_errors(record,
									[' not created: ' + str(self.role_type.value.role_type_name) + 
										' is not valid for ' + str(self.age_status.value.status) + '.']
									)
			# and set the flag
			valid = False
		# check whether a matching event exists
		if self.event_date.valid:
			# try to get the event record
			event, message, multiples  = Event.try_to_get_just_one(
																	name = self.event_name.value,
																	date = self.event_date.value,
																	project = self.project
																	)
			# see what we got
			if not event:
				# append the error message
				self.add_record_errors(record,[' not created: ' + message])
				# and set the flag
				valid = False
		# check that one of registered or participated is set
		if not self.registered.value and not self.participated.value and not self.apologies.value:
			# set the error
			self.add_record_errors(record,[' not created: none of registered, apologies or participated is True.'])
			# and set the flag
			valid = False
		# return the result
		return valid

	def create_record(self,record):
		# get the records, starting with the person
		person = Person.try_to_get(
											first_name = self.first_name.value,
											last_name = self.last_name.value,
											age_status = self.age_status.value,
											projects = self.project
											)
		# and the event
		event = Event.try_to_get(
											name = self.event_name.value,
											date = self.event_date.value,
											project = self.project
											)
		# attempt to get the existing registration
		registration = Event_Registration.try_to_get(event=event,person=person)
		# deal with the failure
		if not registration:
			# create a record
			registration = Event_Registration(event=event,person=person,role_type=self.role_type.value)
		# set the values
		registration.registered = self.registered.value
		registration.apologies = self.apologies.value
		registration.participated = self.participated.value
		registration.role_type = self.role_type.value
		# save the record
		registration.save()
		# set a message
		self.add_record_results(record,[' created.'])
		# return the created record
		return registration

	def set_download_fields(self,registration):
		# call the built in field setter
		super(Registrations_File_Handler, self).set_download_fields(registration)
		# set the special fields
		self.age_status.value = registration.person.age_status.status

	def label(self,record):
		# return the label
		return str(record['first_name']) + ' ' + str(record['last_name']) \
							+ ' (' + str(record['age_status']) + ')' \
							+ ' at ' + str(record['event_name'])

class Events_And_Registrations_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Events_And_Registrations_File_Handler, self).__init__(*args, **kwargs)
		# set the flag to show that this file cannot be uploaded
		self.upload = False
		# set the class
		self.file_class = Event_Registration
		# set the file fields
		self.event_name = File_Field(
									name='event_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='event',
									corresponding_field='name'
									)
		self.event_date = File_Datetime_Field(
												name='event_date',
												datetime_format='%d/%m/%Y',
												corresponding_field='date',
												use_corresponding_for_download=True,
												corresponding_relationship_field='event'
												)
		self.event_description = File_Field(
											name='event_description',
											use_corresponding_for_download=True,
											corresponding_relationship_field='event',
											corresponding_field='description'
											)
		self.event_type = File_Field(
										name='event_type',
										set_download_from_object=False
										)
		self.event_start_time = File_Datetime_Field(
													name='start_time',
													datetime_format='%H:%M',
													use_corresponding_for_download=True,
													corresponding_relationship_field='event',
													corresponding_field='start_time'
													)
		self.event_end_time = File_Datetime_Field(
													name='end_time',
													datetime_format='%H:%M',
													use_corresponding_for_download=True,
													corresponding_relationship_field='event',
													corresponding_field='end_time'
													)
		self.event_location = File_Field(
											name='location',
											use_corresponding_for_download=True,
											corresponding_relationship_field='event',
											corresponding_field='location'
										)

		self.event_ward = File_Field(
										name='event_ward',
										set_download_from_object=False
										)
		self.event_areas = File_Field(
										name='areas',
										set_download_from_object=False
										)
		self.event_venue = File_Field(
										name='event_venue',
										set_download_from_object=False
										)
		self.first_name = File_Field(
										name='first_name',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_relationship_field='person'
										)
		self.last_name = File_Field(
									name='last_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='person'
									)
		self.age_status = File_Field(
									name='age_status',
									corresponding_model=Age_Status,
									corresponding_field='status',
									set_download_from_object=False
									)
		self.registered = File_Boolean_Field(name='registered',mandatory=True)
		self.participated = File_Boolean_Field(name='participated',mandatory=True)
		self.apologies = File_Boolean_Field(name='apologies',mandatory=True)
		self.role_type = File_Field(
										name='role_type',
										mandatory=True,
										corresponding_model=Role_Type,
										corresponding_field='role_type_name',
										corresponding_must_exist=True,
										use_corresponding_for_download=True
										)
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'event__project' : self.project }

		# and a list of the fields
		self.fields = [
						'event_name',
						'event_description',
						'event_type',
						'event_date',
						'event_start_time',
						'event_end_time',
						'event_location',
						'event_ward',
						'event_areas',
						'event_venue',
						'first_name',
						'last_name',
						'age_status',
						'registered',
						'apologies',
						'participated',
						'role_type'
						]

	def set_download_fields(self,registration):
		# call the built in field setter
		super(Events_And_Registrations_File_Handler, self).set_download_fields(registration)
		# set the special fields
		self.age_status.value = registration.person.age_status.status
		self.event_type.value = registration.event.event_type.name
		self.event_ward.value = registration.event.ward.ward_name if registration.event.ward else ''
		self.event_venue.value = registration.event.venue.name if registration.event.venue else ''
		# set the areas
		areas = ''
		for area in registration.event.areas.all():
			if len(areas):
				areas += ','
			areas += area.area_name
		self.event_areas.value = areas

class Questions_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Questions_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Question
		# set the file fields
		self.question_text = File_Field(
										name='question_text',
										mandatory=True,
										corresponding_model=Question,
										corresponding_must_not_exist=True,
										max_length=150
										)
		self.notes = File_Boolean_Field(name='notes',mandatory=True)
		self.notes_label = File_Field(name='notes_label',max_length=30)

		# and a list of the fields
		self.fields = ['question_text','notes','notes_label']

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we had a valid from age status
		if self.notes.value and not self.notes_label.value:
			# append the error message
			self.add_record_errors(record,[' not created: questions has notes but no notes label'])
			# and set the flag
			valid = False
		# return the result
		return valid

	def label(self,record):
		# return the label
		return 'Question: ' + record['question_text']

class Options_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Options_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Option
		# set the file fields
		self.question = File_Field(
										name='question',
										mandatory=True,
										corresponding_model=Question,
										corresponding_must_exist=True,
										corresponding_field='question_text',
										use_corresponding_for_download=True
										)
		self.option_label = File_Field(name='option_label',mandatory=True,max_length=50)
		# and a list of the fields
		self.fields = ['question','option_label']

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether the option exists
		if self.question.valid and self.option_label.valid:
			# try to get the option
			if Option.objects.filter(
										question = self.question.value,
										option_label = self.option_label.value
										).exists():
				# set the error
				self.add_record_errors(record,[' not created: option already exists.'])
				# and the flag
				valid = False
		# return the result
		return valid

	def label(self,record):
		# return the label
		return 'Option: ' + record['question'] + ' - ' + record['option_label']

class Answers_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Answers_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Answer
		self.update = True
		self.existing_record = False
		# set the file fields
		self.first_name = File_Field(
										name='first_name',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_relationship_field='person'
										)
		self.last_name = File_Field(
									name='last_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='person'
									)
		self.age_status = File_Field(
									name='age_status',
									mandatory=True,
									corresponding_model=Age_Status,
									corresponding_field='status',
									corresponding_must_exist=True,
									set_download_from_object=False
									)
		self.question = File_Field(
										name='question',
										mandatory=True,
										corresponding_model=Question,
										corresponding_must_exist=True,
										corresponding_field='question_text',
										use_corresponding_for_download=True
										)
		self.option = File_Field(
										name='option',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_field='option_label',
										corresponding_relationship_field='option'
										)
		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'age_status',
						'question',
						'option'
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'person__projects' : self.project }

	def complex_validation_valid(self,record,update=False):
		# set the value
		valid = True
		# check whether the option already exists
		if self.question.valid:
			# check whether the option is valid
			self.option.value, message, multiples  = Option.try_to_get_just_one(
																				question = self.question.value,
																				option_label = self.option.value
																				)
			if not self.option.value:
				self.add_record_errors(record,[' not created: ' + message])
				valid = False
				self.option.valid = False
		# check whether we have a valid age status
		if self.age_status.exists:
			# check whether the person exists
			person, message, multiples  = Person.try_to_get_just_one(
																		first_name = self.first_name.value,
																		last_name = self.last_name.value,
																		age_status = self.age_status.value,
																		projects = self.project
																		)
			if not person:
				self.add_record_errors(record,[' not created: ' + message])
				valid = False
			# otherwise, check whether we have a duplicate
			elif self.question.valid and self.option.valid:
				person = Person.try_to_get(
													first_name = self.first_name.value,
													last_name = self.last_name.value,
													age_status = self.age_status.value,
													projects = self.project
													)
				if not update and  Answer.objects.filter(
															person = person,
															question = self.question.value
														).exists():
					# set the error message
					self.add_record_errors(record,[' not created: answer already exists.'])
					# and the flag
					valid = False
		# return the result
		return valid

	def get_existing_record(self,record):
		# initialise variables
		self.existing_record = False
		person = False
		question = False
		answer = False
		# set the fields
		first_name = record['first_name']
		last_name = record['last_name']
		age_status = record['age_status']
		# attempt to get the person record
		person, message, multiples = Person.try_to_get_just_one(
																	first_name = first_name,
																	last_name = last_name,
																	age_status__status = age_status
																)
		# attempt to get the question record
		question_text = record['question']
		question, message, multiples = Question.try_to_get_just_one(
																	question_text = question_text
																)
		# attempt to get the answer
		if person and question:
			answer, message, multiples = Answer.try_to_get_just_one(
																		person = person,
																		question = question
																	)
		# if we have a set the attribute, otherwise raise an error
		if answer or multiples:
			self.existing_record = True
			self.person = person
		else:
			self.add_record_errors(
									record,
									[' not created: ' + message]
									)
		return

	def update_record(self,record):
		# clear the answers
		Answer.objects.filter(person=self.person,question=self.question.value).delete()
		# create the new answer
		answer = Answer(
						person = self.person,
						question = self.question.value,
						option = self.option.value
		)
		# save the record
		answer.save()
		self.existing_record = answer
		# record the creation
		self.add_record_results(record,[' updated.'])
		# return the created record
		return self.existing_record

	def create_record(self,record):
		# get the records, starting with the person
		person = Person.try_to_get(
											first_name = self.first_name.value,
											last_name = self.last_name.value,
											age_status = self.age_status.value,
											projects = self.project
											)
		# create the object
		answer = Answer(
						person = person,
						question = self.question.value,
						option = self.option.value
						)
		# save the record
		answer.save()
		# set a message
		self.add_record_results(record,[' created.'])
		# return the created record
		return answer

	def set_download_fields(self,answer):
		# call the built in field setter
		super(Answers_File_Handler, self).set_download_fields(answer)
		# set the special fields
		self.age_status.value = answer.person.age_status.status

	def label(self,record):
		# return the label
		return 'Answer: ' + str(record['first_name']) + ' ' + str(record['last_name']) \
							+ ' (' + str(record['age_status']) + ')' \
							+ ' - ' + record['question'] + ' - ' + record['option']

class Answer_Notes_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Answer_Notes_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Answer_Note
		# set the file fields
		self.first_name = File_Field(
										name='first_name',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_relationship_field='person'
										)
		self.last_name = File_Field(
									name='last_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='person'
									)
		self.age_status = File_Field(
									name='age_status',
									mandatory=True,
									corresponding_model=Age_Status,
									corresponding_field='status',
									corresponding_must_exist=True,
									set_download_from_object=False
									)
		self.question = File_Field(
										name='question',
										mandatory=True,
										corresponding_model=Question,
										corresponding_must_exist=True,
										corresponding_field='question_text',
										use_corresponding_for_download=True
										)
		self.notes = File_Field(
										name='notes',
										mandatory=True,
										max_length=500
										)
		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'age_status',
						'question',
						'notes'
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'person__projects' : self.project }

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we have a valid age status
		if self.age_status.valid:
			# check whether the person exists
			person, message, multiples  = Person.try_to_get_just_one(
																	first_name = self.first_name.value,
																	last_name = self.last_name.value,
																	age_status = self.age_status.value,
																	projects = self.project
																	)
			# if there was an error, add it
			if not person:
				# append the error message
				self.add_record_errors(record,[' not created: ' + message])
				# and set the flag
				valid = False
			# otherwise, do the other checks
			elif self.question.valid:
				# start by getting the person
				person = Person.try_to_get(
													first_name = self.first_name.value,
													last_name = self.last_name.value,
													age_status = self.age_status.value,
													projects = self.project
													)
				# chec whether we have at least one answer
				if not Answer.objects.filter(
												person = person,
												question = self.question.value
												).exists():
					# set the error message
					self.add_record_errors(record,['not created: person has not answered this question.'])
					# and the flag
					valid = False
				# now check whether notes already exist
				if Answer_Note.objects.filter(
												person = person,
												question = self.question.value
												).exists():
					# set the error message
					self.add_record_errors(record,[' not created: answer note already exists.'])
					# and the flag
					valid = False
		# return the result
		return valid

	def create_record(self,record):
		# get the records, starting with the person
		person = Person.try_to_get(
											first_name = self.first_name.value,
											last_name = self.last_name.value,
											age_status = self.age_status.value,
											projects = self.project
											)
		# create the object
		answer_note = Answer_Note(
									person = person,
									question = self.question.value,
									notes = self.notes.value
									)
		# save the record
		answer_note.save()
		# set a message
		self.add_record_results(record,[' created.'])
		# return the created record
		return answer_note

	def set_download_fields(self,answer):
		# call the built in field setter
		super(Answer_Notes_File_Handler, self).set_download_fields(answer)
		# set the special fields
		self.age_status.value = answer.person.age_status.status

	def label(self,record):
		# return the label
		return 'Answer Note: ' + str(record['first_name']) + ' ' + str(record['last_name']) \
							+ ' (' + str(record['age_status']) + ')' \
							+ ' - ' + record['question'] + ' - ' + record['notes']

class Activities_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Activities_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Activity
		# set the file fields
		self.first_name = File_Field(
										name='first_name',
										mandatory=True,
										use_corresponding_for_download=True,
										corresponding_relationship_field='person'
										)
		self.last_name = File_Field(
									name='last_name',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='person'
									)
		self.age_status = File_Field(
									name='age_status',
									mandatory=True,
									corresponding_model=Age_Status,
									corresponding_field='status',
									corresponding_must_exist=True,
									set_download_from_object=False
									)
		self.activity_type = File_Field(
										name='activity_type',
										mandatory=True,
										corresponding_model=Activity_Type,
										corresponding_must_exist=True,
										corresponding_field='name',
										use_corresponding_for_download=True
										)
		self.date = File_Datetime_Field(
										name='date',
										datetime_format='%d/%m/%Y',
										mandatory=True
										)
		self.hours = File_Field(name='hours',mandatory=True)
		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'age_status',
						'activity_type',
						'date',
						'hours',
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'person__projects' : self.project }

	def complex_validation_valid(self,record):
		# set the value
		valid = True
		# check whether we the person exists, if we have a valid age status
		if self.age_status.exists:
			# check whether the person exists
			person, message, multiples  = Person.try_to_get_just_one(
																		first_name = self.first_name.value,
																		last_name = self.last_name.value,
																		age_status = self.age_status.value,
																		projects = self.project
																		)
			# if there was an error, add it
			if not person:
				# append the error message
				self.add_record_errors(record,[' not created: ' + message])
				# and set the flag
				valid = False
		# return the result
		return valid

	def create_record(self,record):
		# get the records, starting with the person
		person = Person.try_to_get(
											first_name = self.first_name.value,
											last_name = self.last_name.value,
											age_status = self.age_status.value,
											projects = self.project
											)
		# attempt to get the existing activity
		activity = Activity.try_to_get(
										person=person,
										activity_type=self.activity_type.value,
										date=self.date.value
										)
		# deal with the failure
		if not activity:
			# create a record
			activity = Activity(
								person=person,
								activity_type=self.activity_type.value,
								date=self.date.value,
								hours=self.hours.value
								)
		# set the values
		activity.person = person
		activity_type = self.activity_type.value
		activity.date = self.date.value
		activity.hours = self.hours.value
		# save the record
		activity.save()
		# set a message
		self.add_record_results(record,[' created.'])
		# return the created record
		return activity

	def set_download_fields(self,activity):
		# call the built in field setter
		super(Activities_File_Handler, self).set_download_fields(activity)
		# set the special fields
		self.age_status.value = activity.person.age_status.status

	def add_project(self,activity):
		# add the project to the activity
		activity.project = self.project
		activity.save()
		return

	def label(self,record):
		# return the label
		return str(record['first_name']) + ' ' + str(record['last_name']) \
					+ ' (' + str(record['age_status']) + ')' \
					+ ', ' + str(record['activity_type']) + ' on ' + str(record['date'])

class Event_Summary_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(Event_Summary_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Event
		# set the flag to indicate that this file type is for downloads only
		self.upload = False
		# set the file fields
		self.name = File_Field(name='name')
		self.location = File_Field(name='location')
		self.venue = File_Field(
									name='venue',
									mandatory=True,
									use_corresponding_for_download=True,
									corresponding_relationship_field='venue',
									corresponding_field='name'
									)
		self.date = File_Datetime_Field(
										name='date',
										datetime_format='%d/%m/%Y',
										)
		self.registered = File_Count_Field(
											name='registered',
											count_field='event_registration_set',
											filter={ 'registered' : True }
											)
		self.apologies = File_Count_Field(
											name='apologies',
											count_field='event_registration_set',
											filter={ 'apologies' : True }
											)
		self.participated = File_Count_Field(
											name='registered',
											count_field='event_registration_set',
											filter={ 'participated' : True }
											)
		self.total = File_Count_Field(
											name='total',
											count_field='event_registration_set',
											filter=None
											)
		# and a list of the fields
		self.fields = [
						'name',
						'date',
						'location',
						'venue',
						'registered',
						'apologies',
						'participated',
						'total'
						]
		# set a project filter if we have a project
		if self.project:
			self.project_filter = { 'project' : self.project }

class People_Limited_Data_File_Handler(File_Handler):

	def __init__(self,*args,**kwargs):
		# call the built in constructor
		super(People_Limited_Data_File_Handler, self).__init__(*args, **kwargs)
		# set the class
		self.file_class = Person
		# set the flag to indicate that this file type is for downloads only
		self.upload = False
		# set the file fields
		self.first_name = File_Field(name='first_name')
		self.last_name = File_Field(name='last_name')
		self.other_names = File_Field(name='other_names')
		self.email_address = File_Field(name='email_address')
		self.home_phone = File_Field(name='home_phone')
		self.mobile_phone = File_Field(name='mobile_phone')
		self.address = File_Field(
								name='address',
								set_download_from_object=False,
								)
		self.ward = File_Field(
								name='ward',
								set_download_from_object=False,
								)
		# and a list of the fields
		self.fields = [
						'first_name',
						'last_name',
						'other_names',
						'email_address',
						'home_phone',
						'mobile_phone',
						'address',
						'ward',
						]
		# set a filtered set of objects if we have a project
		if self.project:
			self.objects = Person.search(projects=self.project,include_people='all')

	def set_download_fields(self,person):
		# call the built in field setter
		super(People_Limited_Data_File_Handler, self).set_download_fields(person)
		# set address and ward if we have a street
		if person.street:
			self.address.value = ' '.join([
											person.house_name_or_number,
											person.street.name,
											person.street.post_code.post_code,
											])
			self.ward.value = person.street.post_code.ward.ward_name

