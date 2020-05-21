# Setup file, to execute the hole or a part of the prediction process
# Author: Youssef Hmamouche

import os, sys, glob, argparse

#==========================================================================#
# Generic funtion to
# Execute one script (python or R) on a file or multiple files in data_path,
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

#==========================================================================#
def pre_selection (data_path, script_name = ""):

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/pre_selection/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	graphs_path = "src/pre_selection/"

	if script_name == "":
		graph_names = [fn for fn in os.listdir(graphs_path)
              if any(fn.endswith(ext) for ext in ['.py', '.R'])]

		for script_name in graph_names:
			execute_script (data_path, output_directory, graphs_path + script_name)

	else:
		execute_script (data_path, output_directory,  script_name)


#==========================================================================#
def selection (data_path, script_name = ""):

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/selection/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	reduction_methods_path = "src/selection/"

	if script_name == "":
		reduction_methods = [fn for fn in os.listdir(reduction_methods_path)
              if any(fn.endswith(ext) for ext in ['.py', '.R'])]

		for script_name in reduction_methods:
			execute_script (data_path, output_directory, reduction_methods_path + script_name)

	else:
		execute_script (data_path, output_directory,  script_name)

#==========================================================================#
def prediction (data_path, script_name):

	if not os.path.exists(data_path):
		print ("Error: data path does not exist")
		exit (1)

	data_name = data_path.split ('/')[-1].split ('.')[0]
	output_directory = 'results/prediction/' + data_name + "/"

	if not os.path.exists (output_directory):
			os.makedirs (output_directory)

	selection_files_path = "results/selection/" + data_name + '/'

	script_name = script_name .split ('/')[-1]

	if script_name in ['var_shrinkage.py', 'auto_arima.R', 'auto_arima.py']:
		execute_script (data_path, output_directory, "src/prediction/" + script_name)

	elif script_name in ['lstm.py', 'vecm.R', 'vecm.py']:
		execute_script (selection_files_path, output_directory, "src/prediction/" + script_name)

	else:
		print ("Prediction script not found.")

#==========================================================================#
def pre_evaluation (data_path):

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

#==========================================================================#
def evaluation (data_path):

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

#==========================================================================#
if __name__ == '__main__':

	parser = argparse. ArgumentParser ()
	parser. add_argument ("data", help = "data path")
	parser. add_argument ("type", help = "task to perform", choices = ["pre_selection", "ps", "selection", "s", "prediction", "p", "pre_evaluation", "pe", "evaluation", "e"])
	parser. add_argument ("--script", "-s", help = "script path", default = "")
	args = parser.parse_args()

	# pre_selection step : computing the causality graphs
	if args.type in ['pre_selection','ps']  :
		pre_selection (args.data, args.script)

	# feature selection / dimension reduction
	elif args.type in ['selection', 's']:
		selection (args.data, args.script)

	# prediction
	elif args.type in ['prediction', 'p']:
		prediction (args.data, args.script)

	# pre_evaluation : compute rmse and mase
	elif args.type in ['pre_evaluation', 'pe']:
		pre_evaluation (args.data)

	# make evaluations: compare methods and models
	elif args.type in ['evaluation', 'e']:
		evaluation (args.data)

	else: print ("Error, unrecognized task name.")
