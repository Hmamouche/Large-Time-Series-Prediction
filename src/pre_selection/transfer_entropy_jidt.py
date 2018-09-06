from __future__ import print_function
from tools.csv_helper import *
import sys
import subprocess
from os import path
import pandas as pd

from jpype import *
import numpy as np


# Add JIDT jar library to the path
jarLocation = "src/pre_selection/infodynamics.jar"
# Start the JVM (add the "-Xmx" option with say 1024M if you get crashes due to not enough memory space)
startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarLocation)

# Function that generates a transfer entropy matrix using the JDIT library
# The input data is the file name
def jdit_transfer_entropy_matrix (fname):
    dataRaw = read_csv_and_metadata(fname)
    dataRaw = dataRaw.dropna(axis=1, how='all')
    data = dataRaw.values
    n_Features = len(data[0,:])
    te_matrix = np.ndarray(shape=(n_Features,n_Features))

    # 1. Construct the calculator:
    calcClass = JPackage("infodynamics.measures.continuous.kernel").TransferEntropyCalculatorKernel
    calc = calcClass()

    for i in range (0,n_Features):
        for j in range (0,n_Features):
            # if i == j:
            #   te_matrix[i,j] = 0
            #break;
            source = data[:,i]
            dest = data[:,j]

            # 2. Set any properties to non-default values:
            #calc.setProperty("k_HISTORY", "1")
            #calc.setProperty("l_HISTORY", "1")
            
            calc. setProperty("NORMALISE", "true")
            # 3. Initialise the calculator for (re-)use:
            calc.initialise(1, 0.5)
            # 4. Supply the sample data:
            calc.setObservations(source, dest)
            # 5. Compute the estimate:
            result = calc.computeAverageLocalOfObservations()
            if result <= 0:
                te_matrix[i,j] = 0
            #break
            te_matrix[i,j] = result

    out = pd.DataFrame(te_matrix, index=dataRaw.columns, columns=dataRaw.columns)
    out.meta_header = dataRaw.meta_header
    return out

if __name__ == "__main__":
    fname, output_directory = parse_selection_arguments(sys.argv)

    is_rolling = False
    if len(sys.argv) == 4:
        is_rolling = True

    out_fname = output_directory + "/" + path.basename(fname).split(".")[0] + '_te_jdit_graph.csv'
    df_out = jdit_transfer_entropy_matrix (fname)
    df_in = read_csv_and_metadata(fname)
    write_csv_with_metadata(df_out, out_fname, index=True)
