# extensions to the django framework

# Mixin class which provides additional data access methods, mostly to handle exceptions
class DataAccessMixin ():
	@classmethod
	def try_to_get(cls,**kwargs):
		# try to get a record using get, and return false if unsuccessful
		try:
			# attempt to get the record
			result = cls.objects.get(**kwargs)
		# now deal with the exception
		except (cls.DoesNotExist):
			# set the result to false
			result = False
		# return the result
		return result
	@classmethod
	def try_to_get_just_one(cls,**kwargs):
		# try to get a record using get, and return false and a message if there is no record or multiple records
		# start by setting the result
		result = False
		# try to get the record
		try:
			# attempt to get the record
			result = cls.objects.get(**kwargs)
			# set the message
			message = 'matching ' + cls.__name__ + ' record exists'
		# now deal with non-existsnce
		except (cls.DoesNotExist):
			# set the message
			message = 'matching ' + cls.__name__ + ' record does not exist'
		# now deal with multiple records
		except (cls.MultipleObjectsReturned):
			# set the message
			message = 'multiple matching ' + cls.__name__ + ' records exist'
		# return the result
		return result, message
	@classmethod
	def search(cls,**kwargs):
		# conduct a search using optional parameters
		# declare the search dict
		search_dict = {}
		# set the list of non-search values
		not_for_search = ['','0','none',0,None]
		# now go through the kwargs
		for key, value in kwargs.items():
			# check the value
			if value not in not_for_search:
				# add the term to the search dict
				search_dict[key] = value
		# see whether we have any search terms
		if len(search_dict):
			# search using a filter
			results = cls.objects.filter(**search_dict)
		# otherwise get everything
		else:
			# get all
			results = cls.objects.all()
		# return the results
		return results
