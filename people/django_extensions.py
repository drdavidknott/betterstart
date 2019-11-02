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