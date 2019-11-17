# script to read a yaml template and build a yaml file, substituting environment variables

#import modules
import os

# set the file name
input_file = 'app_template.yaml'
output_file = 'app.yaml'
# open the files
input_file = open(input_file)
output_file = open(output_file,'w+')
# go through the file
for input_line in input_file:
	# check whether we have a tag
	if '${' in input_line:
		# split the string
		before_tag = input_line.split('${')[0]
		tag_with_trailer = input_line.split('${')[1]
		tag = tag_with_trailer.split('}')[0]
		after_tag = tag_with_trailer.split('}')[1]
		# get the environment variable to replace the tag
		value = os.getenv(tag, tag)
		# set the output line
		output_line = before_tag + value + after_tag
	# otherwise, we don't have a tage
	else:
		# set the output line
		output_line = input_line
	# write the line
	output_file.write(output_line)
# close the files
input_file.close()
output_file.close()