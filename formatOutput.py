try:
	with open('output_raw.txt') as outputFile:
		for line in outputFile:
			print line
except EnvironmentError:
        print 'Error reading file'
