'''
Utility analysis functions (e.g. distance between columns, overlap)
'''
from __future__ import division
import os
import json
from itertools import combinations
from collections import OrderedDict  # Get unique elements of list while preserving order
from time import time
import numpy as np
import pandas as pd
import scipy.stats as stats
import math
from decimal import Decimal
import random

from dive.data.access import get_data

import logging
logger = logging.getLogger(__name__)

def get_bin_decimals(v, max_sample=10000, default=3):
    v = v.astype(float)
    if len(v) <= max_sample:
        sample = v
    else:
        sample = random.sample(v, max_sample)
    num_decimals = [ (Decimal.from_float(e).as_tuple().exponent * -1) for e in sample]
    max_decimals = max(num_decimals)
    return min(max_decimals, 3)

###
# Get bin specifier (e.g. bin edges) given a numeric vector
###
DEFAULT_BINS = 10
MAX_BINS = 20
def get_bin_edges(v, procedural=True, procedure='freedman', num_bins=10, num_decimals=2):
    '''
    Given a quantitative vector, either:
    1) Automatically bin according to Freedman
    2) Procedurally bin according to some procedure
    3) Create num_bins uniform bins

    Returns the edges of each bin
    '''
    min_v = min(v)
    max_v = max(v)
    n = len(v)
    v = v.astype(float)

    # Procedural binning
    if procedural:
        if procedure == 'freedman':
            IQR = np.subtract(*np.percentile(v, [75, 25]))
            bin_width = 2 * IQR * n**(-1/3)
            num_bins = (max_v - min_v) / bin_width
        elif procedure == 'square_root':
            num_bins = math.sqrt(n)
        elif procedure == 'doane':
            skewness = abs(stats.skew(v))
            sigma_g1 = math.sqrt((6*(n-2)) / ((n+1) * (n+3)))
            num_bins = 1 + math.log(n, 2) + math.log((1 + (skewness / sigma_g1)), 2)
        elif procedure == 'rice':
            num_bins = 2 * n**(-1/3)
        elif procedure == 'sturges':
            num_bins = math.ceil(math.log(n, 2) + 1)

        num_bins = math.floor(num_bins)
        num_bins = min(num_bins, MAX_BINS)
        if not num_bins:
            num_bins = DEFAULT_BINS

    rounding_string = '%.' + str(num_decimals) + 'f'
    edges = np.linspace(min_v, max_v, num_bins+1)
    rounded_edges = []
    if num_decimals == 0:
        for i in range(len(edges)):
            rounded_edges.append(int(float(rounding_string % edges[i])))
    else:
        for i in range(len(edges)):
            rounded_edges.append(float(rounding_string % edges[i]))
    rounded_edges[-1] += 0.0001 * max_v
    return rounded_edges
