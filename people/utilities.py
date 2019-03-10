# a bunch of utilities to help manage page layouts etc.

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