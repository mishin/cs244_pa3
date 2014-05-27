import re


try:
    f = open('output_formatted.txt', 'a')
    with open('output_raw.txt') as outputFile:
        for line in outputFile:
            print line
            match = re.search("real\t\dm(\d+.\d+)s", line)
            if match:
                f.write(match.group(1))
    f.close()
except EnvironmentError:
    print 'Error reading file'
