import csv
import numpy
import matplotlib as m
import os
if os.uname()[0] == "Darwin":
    m.use("MacOSX")
else:
    m.use("Agg")
import matplotlib.pyplot as plt

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
        improvement_perc = improvement_abs / latency_small
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
        with open('sample_data.txt') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for row in reader:
                        addToBucket(float(row[0]), float(row[1]), float(row[2]))
        improvement = []
        improvement.append(numpy.mean(buckets["56"], 0))
        improvement.append(numpy.mean(buckets["256"], 0))
        improvement.append(numpy.mean(buckets["512"], 0))
        improvement.append(numpy.mean(buckets["1000"], 0))
        improvement.append(numpy.mean(buckets["2000"], 0))

        avg_improvement = list(a[0] for a in improvement)
        perc_improvement = list(a[1] for a in improvement)

        print avg_improvement
        print perc_improvement

        N = 5
        menMeans = (20, 35, 30, 35, 27)
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
        plt.savefig("test.png")
except EnvironmentError:
        print 'Error reading file'
