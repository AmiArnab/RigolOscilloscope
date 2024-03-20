#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import scipy.stats

wstart = 3
wstop = -1

myfile = "waveform.csv"

srow = []
i = 0

with open(myfile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        srow = []
        srow.append(np.array(row[wstart:wstop]).astype(np.float))
        i = i+1
        if i > 5:
            break
        
print(len(srow))

plt.plot(srow[0], linewidth=1)    

plt.locator_params(axis='y', nbins=10)
title = "Single Trace Plot"
plt.xlabel('Sample Number')
plt.ylabel('Amplitude')
plt.title(title)
plt.savefig("Traceplot.png",dpi=300,bbox_inches='tight')

plt.show()