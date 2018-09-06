import sys
import pandas as pd
from tools.global_measures import GLOBAL_MEASURES
import pickle

class transform_into_excel(object):

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def write(self, timeseries_prefix):
        # Write excel
        # TODO: write error list to separate spreadsheet
        writer = pd.ExcelWriter(
            "%s/%s.xlsx" % (self.out_dir, timeseries_prefix,))
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    val.to_excel(writer, sheet_name="%s_%s_%s" %
                                 (target_name, horizon, predict_model))
        writer.close()


def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_excel(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
