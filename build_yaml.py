# script to read a yaml template and build a yaml file, substituting environment variables
# set the file name
input_file = 'template.yaml'
output_file = 'app.yaml'
# open the files
file = open(input_file)
file = open(output_file)
# go through the file
for input_line in input_file:
	# check whether we have a tag
	if '${' in input_line:
		# split the 