import sys
import base64
import hashlib
from os import path
from functools import partial

import pandas as pd

def parse_selection_arguments(argv):
    """Parse cmdline arguments for selection method script

    :args: TODO
    :returns: TODO

    """
    if len(argv) < 3:
        print('Error: wrong number of params')
        exit(0)

    fname = argv[1]
    output_directory = argv[2]+"/"

    if not path.isdir(output_directory):
        print("Error: output directory does not exist")
        exit()
    if not path.isfile(fname):
        print("Error: input CSV file does not exist")
        exit()
    return fname, output_directory

def get_filename_from_method(fname, predicted_column, method_name, prefix="", postfix=".csv"):
    fname_part = fname.split('/')
    fname_part = fname_part[-1].split(".")[0]
    name = method_name.split("(")
    hasher = hashlib.sha1(method_name.encode('utf-8'))
    hfname = base64.urlsafe_b64encode(hasher.digest()[0:200]).decode('utf-8')
    return prefix + "_".join([fname_part, predicted_column, name[0], hfname]) + postfix

def pretty_print_method_name(method):
    mname = str(method).replace("\n", " ")
    if hasattr(method, "__pretty_print_extra_str"):
        mname = mname.replace("(", "_" + method.__pretty_print_extra_str + "(")
    return ' '.join(mname.split())

def partial_with_pretty_method_name(fun, **kwargs):
    partialfun = partial(fun, **kwargs)
    partialfun.__pretty_print_extra_str = "_".join([str(k)+"_"+str(v) for k, v in partialfun.keywords.items()])
    def __iner(*args, **kwargs):
        out = partialfun(*args, **kwargs)
        out.__pretty_print_extra_str = partialfun.__pretty_print_extra_str
        return out
    return __iner

def read_metadata_from_csv_file(filename):
    def __parse_metadata(line):
        record = line[1:]
        values = record.split(';')
        return values[0].strip(), [v.strip().replace('"',"") for v in values[1:]]

    metadata = {}
    with open(filename) as file_in:
        for line in file_in:
            if line[:1] == '#':
                key, values = __parse_metadata(line)
                metadata[key] = values
            else:
                return metadata

def read_csv_and_metadata(filename, **kwargs):
    pd.DataFrame._metadata = ["meta_header"]

    # if not set in kwargs, use defaults for this project
    if 'comment' not in kwargs:
        kwargs['comment'] = '#'
    if 'delimiter' not in kwargs or 'sep' not in kwargs:
        kwargs['delimiter'] = ';'
    if 'engine' not in kwargs:
        kwargs['engine'] = 'c'

    matrix = pd.read_csv(filename, **kwargs)
    matrix._metadata = ["meta_header"]
    matrix.meta_header = read_metadata_from_csv_file(filename)
    return matrix

def exclude_column_generator(df):
    for c in df.meta_header['predict']:
        yield c, df[df.columns.difference([c,])]

def write_csv_with_metadata(df, filename, **kwargs):

    # if not set in kwargs, use defaults for this project
    if 'index' not in kwargs: kwargs['index'] = False
    if 'delimiter' not in kwargs or 'sep' not in kwargs: kwargs['sep'] = ';'

    with open(filename, "w") as file_in:
        for k in df.meta_header:
            file_in.write("# %s; " % (k,) + ';'.join(df.meta_header[k])+"\n")
        df.to_csv(file_in, **kwargs)

def test():
    input_data = read_csv_and_metadata(sys.argv[1])
    print(input_data.size)

if __name__ == "__main__":
    test()
