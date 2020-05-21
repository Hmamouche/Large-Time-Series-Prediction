import sys
from collections import defaultdict
import itertools
import pickle
import re

def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    symbols = defaultdict(list)
    for error in error_list:

        if "Error: Could not read file" in error:
            # get fname
            m = re.search("([^\s]*\.csv)", error)
            fname = m.group(1).split("/")[-1]
            fname = re.sub("VECM(-|_)", "", fname)
            fname = re.sub("rolling(-|_)", "", fname)
            prefix = "/".join(m.group(1).split("/")[:-1])
            print (prefix.replace("prediction","selection") + "/" + fname)

        continue
        m = re.search("([^\s]*\.csv)", error)
        fname = m.group(1).split("/")
        groups = ["Auto.Arima_","Univariate-Model_"]
        for g in groups:
            if "VECM" in fname[-1]:
                continue
            if g in fname[-1]:
                symbol = re.sub(g,"",fname[-1])
                symbol = re.sub("_%s.*"%(fname[-2]),"", symbol)
                symbols[g].append(symbol)
                print (error)
    for g in symbols:
        print(g,symbols[g])

        # if "VECM" not in fname[-1]:
        #     print fname[-2], fname[-1]

if __name__ == "__main__":
    main()
