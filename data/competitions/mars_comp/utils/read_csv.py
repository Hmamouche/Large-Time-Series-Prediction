"""
Extract subsystem command counts per hour
"""
import os
import pandas as pd

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

def write_csv_with_metadata(df, filename, **kwargs):
    
    # if not set in kwargs, use defaults for this project
    if 'index' not in kwargs: kwargs['index'] = False
    if 'delimiter' not in kwargs or 'sep' not in kwargs: kwargs['sep'] = ';'
    
    with open(filename, "w") as file_in:
        for k in df.meta_header:
            file_in.write("# %s; " % (k,) + ';'.join(df.meta_header[k])+"\n")
        df.to_csv(file_in, **kwargs)



