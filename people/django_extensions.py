# extensions to the django framework

# Mixin class which provides additional data access methods, mostly to handle exceptions
class DataAccessMixin ():
	@classmethod
	def try_to_get(cls,**kwargs):
		# try to get a record using get, and return false if unsuccessful
		try:
			result = cls.objects.get(**kwargs)
		except (cls.DoesNotExist):
			result = False
		# return the result
		return result
	@classmethod
	def try_to_get_just_one(cls,**kwargs):
		# try to get a record using get, and return false and a message if there is no record or multiple records
		# start by setting the result
		result = False
		# attempt success
		try:
			result = cls.objects.get(**kwargs)
			message = 'matching ' + cls.__name__ + ' record exists'
		# deal with non-existence
		except (cls.DoesNotExist):
			message = 'matching ' + cls.__name__ + ' record does not exist'
		# deal with multiple records
		except (cls.MultipleObjectsReturned):
			message = 'multiple matching ' + cls.__name__ + ' records exist'
		# return the result
		return result, message
	@classmethod
	def search(cls,**kwargs):
		# conduct a search using optional parameters
		# initialise variable, including a list of values not for search
		search_dict = {}
		not_for_search = ['','0','none',0,None]
		# build a list of search terms where the values do not match the not for search list
		for key, value in kwargs.items():
			if value not in not_for_search:
				search_dict[key] = value
		# filter if we have any remaining search terms, otherwise get everything
		if len(search_dict):
			results = cls.objects.filter(**search_dict)
		else:
			results = cls.objects.all()
		# return the results
		return results
