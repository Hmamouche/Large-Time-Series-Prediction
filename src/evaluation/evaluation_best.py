import sys
import pandas as pd
sys.path.append ("src")
from tools.global_measures import GLOBAL_MEASURES
import pickle

from collections import defaultdict

class transform_into_best_excel(object):

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_best_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def write(self, timeseries_prefix):
        target_min = defaultdict(lambda : defaultdict(list))
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    val['horizon'] = horizon
                    target_min[horizon][target_name].append(val)

                target_min[horizon][target_name] = pd.concat(target_min[horizon][target_name], ignore_index=True)

        # Write excel
        writer = pd.ExcelWriter(
            "%s/%s_best.xlsx" % (self.out_dir, timeseries_prefix,))

        target_avg = {}
        for horizon in target_min:
            ret = {}
            for target_name in target_min[horizon]:
                ret[target_name] = target_min[horizon][target_name].iloc[target_min[horizon][target_name]['rmse'].idxmin(axis=0)][['rmse', 'group', 'predict', 'method']]
                if target_name not in target_avg.keys():
                    target_avg[target_name] = target_min[horizon][target_name]
                else:
                    target_avg[target_name]['rmse'] += target_min[horizon][target_name]['rmse']

            pd.DataFrame.from_dict(ret).to_excel(writer, sheet_name=str(horizon))

        writer.close()

        ret = {}
        avg_count = len(target_min)
        for target_name in target_avg:
            ret[target_name] = target_avg[target_name].iloc[target_avg[target_name]['rmse'].idxmin(axis=0)][['rmse', 'group', 'predict', 'method']]
            # print target_name, ret[target_name]['rmse']
            ret[target_name]['rmse'] /= avg_count
            # print target_name, ret[target_name]['rmse']

        # print target_avg

        # Write excel
        writer = pd.ExcelWriter(
            "%s/%s_best_avg.xlsx" % (self.out_dir, timeseries_prefix,))

        pd.DataFrame.from_dict(ret).to_excel(writer)

        writer.close()


def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_best_excel(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
