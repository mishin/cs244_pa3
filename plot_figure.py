import math
import csv
import numpy
import matplotlib as m
import os
if os.uname()[0] == "Darwin":
    m.use("MacOSX")
else:
    m.use("Agg")
import matplotlib.pyplot as plt
from argparse import ArgumentParser

# Parse arguments
parser = ArgumentParser(description="Takes nicely formatted data and makes a bar chart")
parser.add_argument('-f', '--file',
                    help="Input file for data, e.g.: -f output_formatted.txt",
                    dest="infile",
                    required=True,
                    default=None)
parser.add_argument('-o', '--out',
                    help="Save plot to output file, e.g.: --out plot.png",
                    dest="out",
                    required=True,
                    default=None)
args = parser.parse_args()

# bandwidth buckets
buckets = {}
buckets["56"] = []
buckets["256"] = []
buckets["512"] = []
buckets["1000"] = []
buckets["2000"] = []

# args:
#       bw - bandwidth (Kbps)
#       latency_small - response latency for smaller initcwnd
#       latency_large - response latency for larger initcwnd

def addToBucket(bw, latency_small, latency_large):
        improvement_abs = latency_small - latency_large
        improvement_perc = (improvement_abs / latency_small) * 100.0

        if bw <= 56:
                buckets["56"].append((improvement_abs, improvement_perc))
        elif bw <= 256:
                buckets["256"].append((improvement_abs, improvement_perc))
        elif bw <= 512:
                buckets["512"].append((improvement_abs, improvement_perc))
        elif bw <= 1000:
                buckets["1000"].append((improvement_abs, improvement_perc))
        elif bw <= 2000:
                buckets["2000"].append((improvement_abs, improvement_perc))
try:
        with open(args.infile) as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                        addToBucket(float(row[0]), float(row[1]), float(row[2]))
        improvement = []
        if buckets["56"]:
		improvement.append(numpy.mean(buckets["56"], 0))
	else:
		improvement.append((0,0))
        if buckets["256"]:
		improvement.append(numpy.mean(buckets["256"], 0))
	else:
		improvement.append((0,0))
        if buckets["512"]:
		improvement.append(numpy.mean(buckets["512"], 0))
	else:
		improvement.append((0,0))
        if buckets["1000"]:
		improvement.append(numpy.mean(buckets["1000"], 0))
	else:
		improvement.append((0,0))
        if buckets["2000"]:
		improvement.append(numpy.mean(buckets["2000"], 0))
	else:
		improvement.append((0,0))

	avg_improvement = []
        perc_improvement = []

	for a in improvement:
		avg_improvement.append(a[0])
		perc_improvement.append(a[1])

        N = 5
        ind = numpy.arange(N)  # the x locations for the groups
        width = 0.35       # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, avg_improvement, width, color='m')
        rects2 = ax.bar(ind+width, perc_improvement, width, color='b')

        # add some
        ax.set_ylabel('Improvement (ms)')
        ax.set_xlabel('Bandwidth (Kbps)')
        ax.set_xticks(ind+width)
        ax.set_xticklabels( ('56', '256', '512', '1000', '2000') )

        ax.legend( (rects1[0], rects2[0]), ('Absolute Improvement', 'Percentage Improvement') )
        plt.savefig(args.out)
except EnvironmentError:
        print 'Error reading file'
