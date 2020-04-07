
This repository contain an implementation of a framework for large time series prediction. The approach includes computing the  graphs of dependencies between time series, feature selection, then prediction using different algorithms.
Examples on real datasets are provided.

# Requirements

  * R >= 3.6
  * Python >= 3.6
  * Installing dependencies
    ```bash
      Rscript requirements.R
      pip install -r requirements.txt
    ```
  * Remarque: there are some issues when installing rJava, and Biocomb package, try to install them manually, else, you don't have to
  	use the src/selection/fcbf.R script (for the FCBF method).


# Execution

## Run all the process on a given dataset "dataname"
```bash
	python run.py -pre_selection data/dataname
	python run.py -selection data/dataname
	python run.py -prediction data/dataname
	python run.py -pre_evaluation data/dataname
	python run.py -evaluation data/dataname

```
## Running just some steps of the process
```bash
  python run.py -h
```
