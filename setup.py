
# Setup file, to execute the hole or a part of the prediction process
# Author: Youssef Hmamouche

import os
import sys
import glob


def usage ():
	print ("Usage: setup.py arg0 arg1 arg2 arg3")
	print ("arg0: operation type (pre_selection, selection, prediction, evaluation)")
	print ("arg1: data_path")
	print ("arg2: output_directory")
	print ("arg3: script name (optional), if it is not given, all scripts will be executed")

def execute_script (data_path, output_directory, script_path):

	script_name = script_path.split ('/')[-1]

	if not os.path.exists(script_path):
		print ("Error: the script does not exist!")
		exit (1)

	if script_name.endswith('.py'):
		query = "python " + script_path + " " + data_path + " " + output_directory

	elif script_name.endswith('.R'):
		query = "Rscript " + script_path  + " " + data_path + " " + output_directory

	else:
		return

	print (query)
	os.system (query)

def execute_pred_script (files_path, output_directory, script_path):

	script_name = script_path.split ('/')[-1]

	if not os.path.exists(script_path):
		print ("Error: the script does not exist!")
		exit (1)

	if script_name.endswith('.py'):
		query = "python " + script_path + " " + files_path + " " + output_directory

	elif script_name.endswith('.R'):
		query = "Rscript " + script_path  + " " + files_path + " " + output_directory

	else:
		return

	#print (query)
	os.system (query)



def pre_selection (argv):

	data_path = argv [1]

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/pre_selection/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)


	graphs_path = "src/pre_selection/"

	if len (argv) == 2:

		
		graph_names = [fn for fn in os.listdir(graphs_path)
              if any(fn.endswith(ext) for ext in ['.py', '.R'])]

		for script_name in graph_names:
			execute_script (data_path, output_directory, graphs_path + script_name)


	elif len (argv) == 3:
		script_name = argv [2]
		execute_script (data_path, output_directory, graphs_path + script_name)

	else:
		usage ()

def selection (argv):

	data_path = argv [1]

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/selection/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	reduction_methods_path = "src/selection/"

	if len (argv) == 2:
		
		reduction_methods = [fn for fn in os.listdir(reduction_methods_path)
              if any(fn.endswith(ext) for ext in ['.py', '.R'])]

		for script_name in reduction_methods:
			execute_script (data_path, output_directory, reduction_methods_path + script_name)

	elif len (argv) == 3:
		script_name = argv [2]
		execute_script (data_path, output_directory,  script_name)

	else:
		usage ()

def prediction (argv):

	data_path = argv [1]

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/prediction/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	#selection_files = glob.glob ("results/selection/" + data_name  + "/*.csv*")
	selection_files_path = "results/selection/" + data_name + '/'

	if len (argv) == 3:
		script_name = argv [2]
		script_name = script_name .split ('/')[-1]

		if script_name in ['var_shrinkage.py', 'Autp_arima.R']:
			execute_script (data_path, output_directory, "src/prediction/" + script_name)

		elif script_name in ['Lstm.py', 'vecm.R']:
			execute_pred_script (selection_files_path, output_directory, "src/prediction/" + script_name)

	else:
		usage ()


def pre_evaluation (argv):

	data_path = argv [1]
	data_name = data_path.split ('/')[-1].split ('.')[0]

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)


	output_directory = "results/pre_evaluation/" + data_name + '/'
	os.system ("rm -r " +  output_directory)
	os.makedirs (output_directory)

	script = "src/pre_evaluation/pre_evaluation.py"

	query = "python " + script + ' ' + data_path + ' ' + output_directory
	os. system (query)

def evaluation (argv):

	data_path = argv [1]
	data_name = data_path.split ('/')[-1].split ('.')[0]

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)


	output_directory = "results/evaluation/" + data_name + '/'
	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	scripts = glob.glob ("src/evaluation/*.py")

	for script in scripts:

		query = "python " + script + ' ' + data_path + ' ' + output_directory
		os. system (query)


if __name__ == '__main__':

	if len (sys.argv) == 1:
		print ("Insufficient arguments, add -h for help")

	elif len (sys.argv) == 2 and sys.argv[1] == '-h':
		usage ()

	elif sys.argv [1] in ['-pre_selection','-ps']  :
		pre_selection (sys.argv[1:])

	elif sys.argv [1] in ['-selection', '-s']:
		selection (sys.argv[1:])

	elif sys.argv [1] in ['-prediction', '-p']:
		prediction (sys.argv[1:])

	elif sys.argv [1] in ['-pre_evaluation', '-pe']:
		pre_evaluation (sys.argv[1:])

	elif sys.argv [1] in ['-evaluation', '-e']:
		evaluation (sys.argv[1:])

	else:
		usage ()


	

	
	

