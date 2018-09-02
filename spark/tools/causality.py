from __future__ import print_function
import sys
from os import path
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

from jpype import *
import numpy as np

def granger_causality (source, dest, maxlag = 1):

    data = np.vstack ((source, dest)).T
    try:
        model = grangercausalitytests (data, maxlag, verbose = 0)
        p_value = model[maxlag][0]['params_ftest'][1]
    except (ValueError):
        print (ValueError)
        p_value = 1

    return p_value

if __name__ == "__main__":
    x = [1,2,3,3,3,3,5,7,8,9]
    y = [1,2,3,3,3,7,8,8,8,0]
    p_value = granger_causality (x, y, 1)
    print (p_value)
