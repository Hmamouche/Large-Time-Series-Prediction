from __future__ import division
from fabric.api import *
import glob
import os
import re

# TODO: use compressed csv format for all of the intermediate files
# TODO: pandas should be ok with compressed filenames
# TODO: some changes required for R scripts to read compressed csv files

__RESULTS_DIRECTORY_PREFIX='results/'

def __run_R_method(args):
    """Runs R script with args,

    :args: list of args to run with R script

    """
    method = os.path.abspath(args[0])
    ts = os.path.abspath(args[1])
    outdir = os.path.abspath(args[2]) + '/'

    with settings(warn_only=True), lcd(os.path.dirname(method)):#, shell_env(R_COMPILE_PKGS='TRUE', R_ENABLE_JIT='3'):
        local("Rscript --vanilla " + " ".join([method, ts, outdir]))


def __run_Python_method(args):
    """Runs Python method with args

    :args: list of args to run with Python script

    """
    with shell_env(PYTHONPATH="$PYTHONPATH:src/"), settings(warn_only=True):
        local(' python ' + " ".join(args))


def __get_min_max_dates_from_files(files):
    dates = []
    for f in files:
        dates.append(os.path.getmtime(f))
    return min(dates), max(dates)


def __run_method(method, timeseries, method_prefix, timeseries_prefix=None):
    """Runs any method on a timeseries file

    :method: path to the method
    :timeseries: path to timeseries file
    :returns: None

    """

    # create output directory
    outdir = __RESULTS_DIRECTORY_PREFIX + method_prefix + timeseries.split("/")[-1].split(".")[0]
    if timeseries_prefix is not None:
        outdir = __RESULTS_DIRECTORY_PREFIX + method_prefix + timeseries_prefix
    local('mkdir -p ' + outdir)

    # guess interpreter type
    methodtype = method.split("/")[-1].split(".")[1]

    # Select runner to run script (R or Python)
    _run = __run_Python_method
    if methodtype == "R": _run = __run_R_method

    _run([method, timeseries, outdir])


def __run_methods(methods, timeseries, methods_prefix, timeseries_prefix=None):
    scripts = __select_methods(methods, methods_prefix)

    for method in scripts:
        __run_method(method, timeseries, '%s/'%(methods_prefix,), timeseries_prefix)


def __select_files(selected_files, directory, globing_expression):
    files = []
    if selected_files is None:
        files = glob.glob(directory + "/" + globing_expression)
    else:
        files = glob.glob(selected_files)

        # if this is not extended path, try glob in files_directory
        if len(files) == 0:
            files = glob.glob("%s/%s"%(directory, selected_files))

    files = [os.path.abspath(f) for f in files]
    return files


def __select_methods(selected_methods, methods_prefix):
    scripts = []
    if selected_methods is None:
        scripts = glob.glob("src/%s/*.py"%(methods_prefix,))
        scripts.extend(glob.glob("src/%s/*.R"%(methods_prefix,)))
    else:
        scripts = glob.glob(selected_methods)

        # if this is not extended path, try glob in methods_directory
        if len(scripts) == 0:
            scripts = glob.glob("src/%s/%s"%(methods_prefix, selected_methods))
    return scripts


# Targets
def update_requirements():
    local('gawk \'/^library/{test = gensub(/library\((.*)\).*/,"\\\\1","g"); A[test]=0}; BEGIN{printf("chooseCRANmirror()\\n");}END{for (k in A) printf("install.packages(\\\"%s\\\")\\n",k);}\' `find . -name "*.R"` > requirements.R')
    local('pipreqs --force .')


def get_uci_dataset():
    with lcd("src/tools/download_uci_ml/"):
        local("scrapy crawl uci")


def pre_selection(timeseries, methods=None):

    """Runs pre_selection methods found in src/pre_selection on a timeseries file

    :timeseries: path to timeseries file
    :methods: globing expresion in quotes for methods selection
    :returns: None

    """
    __run_methods(methods, timeseries, 'pre_selection')


def pre_selection_step2(timeseries, methods=None, selected_files = None):

    """Runs pre_selection methods found in src/pre_selection_step2 on a timeseries file
    It will write files to pre_selection folder (to simplify selection step)

    :timeseries: path to timeseries file
    :methods: globing expresion in quotes for methods selection
    :returns: None

    """
    # TODO: quick fix for pre_selection step
    timeseries_prefix = timeseries.split("/")[-1].split(".")[0]
    pre_selection_setp_directory = __RESULTS_DIRECTORY_PREFIX + 'pre_selection/' + timeseries_prefix

    methods = 'src/pre_selection_step2/*'

    files = __select_files(selected_files, pre_selection_setp_directory, "*_graph.csv")

    for fname in files:
        __run_methods(methods, fname, 'pre_selection', timeseries_prefix)

def selection(timeseries, methods=None):

    """Runs selection methods found in src/selection on a timeseries file

    :timeseries: path to timeseries file
    :methods: globing expresion in quotes for methods selection
    :returns: None

    """
    __run_methods(methods, timeseries, 'selection')



def prediction(timeseries, methods = None, selected_files=None, filter_by_mdate=True):
    ## TODO : manage the univariate model separately
    timeseries_prefix = timeseries.split("/")[-1].split(".")[0]
    selection_step_directory = __RESULTS_DIRECTORY_PREFIX + 'selection/' + timeseries_prefix

    files = __select_files(selected_files, selection_step_directory, "*.csv")

    # if filter_by_mdate:
    #     min_mdate_pfiles, max_mdate_pfiles = __get_min_max_dates_from_files(glob.glob(__RESULTS_DIRECTORY_PREFIX + 'prediction/' + timeseries_prefix + "/*.csv"))
    #     print (min_mdate_pfiles, max_mdate_pfiles)
    #     files = [f for f in files if os.path.getmtime(f) > min_mdate_pfiles ]
    #     print (files)
    methods_prefix = 'prediction'
    scripts = __select_methods(methods, methods_prefix)

    univariate_model_regex = re.compile(".*(arima|ar|naive|shrinkage).*")
    for method in scripts:

        if univariate_model_regex.match(method):
            __run_method(method, timeseries, '%s/'%(methods_prefix,), timeseries_prefix)
        else:
            # if the resulting argv is > 50 kb, split it (until a fix is done in *.R prediction)
            f_in = " ".join(files)
            f_in_batches = []
            max_argv_size = 50000

            # this is supposed to be temporary fix, so we do just a rough estimate over the number of splits
            if len(f_in) == 0:
                print("Error: No input files")
                continue
            parts = len(files) // ((len(f_in) + max_argv_size - 1)  // max_argv_size)
            chunks = [files[i:i + parts] for i in range(0, len(files), parts)]
            for chunk in chunks:
                f_in = " ".join(chunk)
                __run_method(method, f_in, '%s/'%(methods_prefix,), timeseries_prefix)

def pre_evaluation(timeseries, methods=None):
    __run_methods(methods, timeseries, 'pre_evaluation')

def evaluation(timeseries, methods=None):
    __run_methods(methods, timeseries, 'evaluation')

def all_steps(timeseries):
    pre_selection(timeseries)
    pre_selection_step2(timeseries)
    selection(timeseries)
    prediction(timeseries)
    pre_evaluation(timeseries)
    evaluation(timeseries)

def check_step_csv_files(step_directory):
    files = glob.glob(step_directory + "/*.csv")
    for f in files:
        __run_Python_method(["src/tools/csv_helper.py", f])
