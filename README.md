# Expérimentations-Thèse

Ce dossier contient les données utilisées et les résultats associés aux travaux de la thèse  qui sont présentés dans le mémoire. Les résultats incluent les graphes de caualités, les résultats de l'étape de sélection des variables et de la prédiction, et finalement les évaluations des prédictions.

# Structure:

## data: the used multivariate time series

## src 

	* tools: some function for reading and writing files and metadata

	* pre_selection: causality graphs computation with the granger causality and the transfert entropy

	* selection: feature selection methods

	* prediction: the implementations of the prediction models
	
	* pre_evaluation: scripts for gathering the prediction errors
	
	* evaluation: compute the forecast accuracy using MASE and RMSE measures.
	
		
## results 

	* pre_selection: causality matrix of each datasets
	* selection: feature selection (with all methods) for each target variable of each datasets.
	* prediction: the prediction associated to each file from src/selection/

      
# Installation

  * install dependencies for python
    ```bash
    pip install -r requirements.txt.
    ```
   * install dependencies for R
   Rscrip requirements.R
