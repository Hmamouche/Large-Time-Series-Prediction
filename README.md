# Thesis Experiments

This foalder contains the used data, the models and methods implementations,  and the results associated with the work of the thesis. The results include the  graphs of dependenceis between time series, the results of the feature selection, the predictions using different prediction models, and finally the prediction accuracy evaluations.

# Structure:

## data: the used multivariate time series

## src: methdods and models implementations

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
    pip install -r requirements.txt.
    ```
   * install dependencies for R
   ```bash
    Rscript requirements.R
   ```
# To reproduce the results
```bash
	fab pre_selection:data/"dataname"
	fab selection:data/"dataname"
	fab predition:data/"dataname"
	fab pre_evaluation:data/"dataname"
	fab evaluation:data/"dataname"
```


