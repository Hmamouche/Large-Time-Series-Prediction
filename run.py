
# Setup file, to execute the hole or a part of the prediction process
# Author: Youssef Hmamouche

import os
import sys
import glob


def usage ():
	print ("Usage: python run.py arg0 arg1 arg2")
	print ("")
	print ("	arg0: operation type (-pre_selection, -selection, -prediction, -evaluation")
	print ("	arg1: data_path")
	print ("	arg2: script name (optional), if it is not given, all scripts of this step will be executed")
	print ("")
	print ("And to plot the results use: python run.py -plot arg")
	print ("	arg: is data path, for example data/us_diff.csv")
	
# Generic funtion to
# Execute one script on a file or multiple files in data_path, 
# and put results on output_directory
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
		print ("Current verstion accept just python and R files.")
		return

	try:
		os.system (query)
	except ValueError:
		print ("Error in executing the script " + script_path + " on " + data_path)

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
		execute_script (data_path, output_directory,  script_name)

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

		if script_name in ['var_shrinkage.py', 'auto_arima.R']:
			execute_script (data_path, output_directory, "src/prediction/" + script_name)

		elif script_name in ['lstm.py', 'vecm.R']:
			execute_script (selection_files_path, output_directory, "src/prediction/" + script_name)

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

def make_figures (data):

	if not os.path.exists ("plots/pdf"):
			os.makedirs ("plots/pdf")

	if not os.path.exists ("plots/csv"):
			os.makedirs ("plots/csv")

	try:
		os.system ("python plots/matrix-eval.py " + data)
	except (ValueError):
		print ("Error in generating reduction methods plots")

	try:
		os.system ("python plots/models-eval.py " + data)
	except (ValueError):
		print ("Error in generating reduction methods plots")

if __name__ == '__main__':

	if len (sys.argv) == 1:
		print ("Insufficient arguments, use -h for help")

	# help
	elif len (sys.argv) == 2 and sys.argv[1] == '-h':
		usage ()

	elif len (sys.argv) == 5 and sys.argv[1] == '-g':
		execute_script (sys.argv[2], sys.argv[3], sys.argv[4])

	elif len (sys.argv) == 5 and sys.argv[1] == '-mlf':
		for i in range (2, len (sys.argv)):
			# sys.argv[2]: script, sys.argv[3]: outout dir
			execute_script (sys.argv[i], sys.argv[3], sys.argv[2])

	# Generate plots for all datasets
	elif len (sys.argv) == 2 and sys.argv[1] in ['-pl', '-plot']:
		datasets = glob.glob ("data/*.csv")
		for data in datasets:
			make_figures (data)

	# Generate plots for one datasets passed as 3th argument
	elif len (sys.argv) == 3 and sys.argv[1] in ['-pl', '-plot']:
		data = sys.argv [2]
		data_path = "data/" + data.split ('/')[-1]

		if not os.path.exists (data_path):
			print ("Error, data does not exist.")
			exit (1)

		make_figures (data_path)


	# pre_selection step : computing the causality graphs
	elif sys.argv [1] in ['-pre_selection','-ps']  :
		pre_selection (sys.argv[1:])

	# the selection step
	elif sys.argv [1] in ['-selection', '-s']:
		selection (sys.argv[1:])

	# the prediction step
	elif sys.argv [1] in ['-prediction', '-p']:
		prediction (sys.argv[1:])

	# the evaluation steps

	elif sys.argv [1] in ['-pre_evaluation', '-pe']:
		pre_evaluation (sys.argv[1:])

	elif sys.argv [1] in ['-evaluation', '-e']:
		evaluation (sys.argv[1:])

	else:
		usage ()


	

	
	

