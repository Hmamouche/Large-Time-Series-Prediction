from __future__ import print_function
import sys
from os import path
import pandas as pd

from jpype import *
import numpy as np


# Add JIDT jar library to the path
jarLocation = "infodynamics.jar"
# Start the JVM (add the "-Xmx" option with say 1024M if you get crashes due to not enough memory space)
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarLocation)

# Function that generates a transfer entropy matrix using the JDIT library
# The input data is the file name
def jdit_transfer_entropy (source, dest):

    calcClass = JPackage("infodynamics.measures.continuous.kernel").TransferEntropyCalculatorKernel
    calc = calcClass()
    # 2. Set any properties to non-default values:
    #calc.setProperty("k_HISTORY", "1")
    #calc.setProperty("l_HISTORY", "1")
    # 3. Initialise the calculator for (re-)use:
    calc.initialise()
    # 4. Supply the sample data:
    try:
        calc.setObservations(source, dest)
        # 5. Compute the estimate:
        result = calc.computeAverageLocalOfObservations()

    except (ValueError):
        result = 0

    return result
    
if __name__ == "__main__":
	print ("*")

