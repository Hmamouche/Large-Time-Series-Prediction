# A Process for Large Time Series Prediction

This repository contains process for large time series prediction, and an experiments analysis. It contains the used data, the models and methods implementations including the proposed algorithms,  and the obtained results. The results include the  graphs of dependencies between time series, the results of the feature selection, the predictions using different prediction models, and finally the prediction accuracy evaluations.

# Structure:

## data: the used multivariate time series

## src: methods and models implementations

	* tools: some function for reading and writing files and metadata

	* pre_selection: causality graphs computation with the granger causality and the transfert entropy

	* selection: feature selection methods

	* prediction: the implementations of the prediction models
	
	* pre_evaluation: scripts for gathering the prediction errors
	
	* evaluation: compute the forecast accuracy using MASE and RMSE measures.
	
		
## results

	* pre_selection: causality matrix of each datasets

	* selection: feature selection (with all methods) for each target variable of each datasets.

	* prediction: the predictions associated to each file in results/selection/dataset/

      
# Installation

  * install dependencies for python
    ```bash
    sudo pip install -r requirements.txt.
    ```
   * install dependencies for R
   ```bash
    sudo Rscript requirements.R
   ```
  
  * Remarque: there are some issues when installing rJava, and Biocomb package, try to install them manually, else, you don't have to 
  	use the src/selection/fcbf.R script (for the FCBF method).

 
# To reproduce the results

## To execute the hole process for a given dataset "dataname"
```bash
	python run.py -pre_selection data/dataname
	python run.py -selection data/dataname
	python run.py -prediction data/dataname
	python run.py -pre_evaluation data/dataname
	python run.py -evaluation data/dataname

```
## To execute just some steps of the process
```bash
python run.py -h 
```


