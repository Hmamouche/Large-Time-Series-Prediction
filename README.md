# Expérimentations-Thèse

Ce dossier contient les données utilisées et les résultats associés aux travaux de la thèse  qui sont présentés dans le mémoire. Les résultats incluent les graphes de caualités, les résultats de l'étape de sélection des variables et de la prédiction, et finalement les évaluations des prédictions.

# Structure:

data: the used multivariate time series
	|_____ dataset1
	|_____ dataset2
	|_____ dataset3

src 	____________ tools: some function for reading and writing files and metadata
     	|
      	|___________ pre_selection: causality graphs computation with the granger causality and the transfert entropy
	|
	|___________  selection: feature selection methods
    	|
      	|___________  prediction: the prediction models
	|
	|___________  pre_evaluation: scripts for gathering the prediction errors
	|
	|___________  evaluation: compute the forecast accuracy using MASE and RMSE measures.
	
		
results 	___________   pre_selection: causality matrix of each datasets
		|		     			|_____ dataset1
		|		     			|_____ dataset2
		|		     			|_____ dataset3			
     	   	|
      		|___________  selection: feature selection (with all methods) for each target variable of each datasets.
		|					|_____ dataset1
		|		     			|_____ dataset2
		|		     			|_____ dataset3
      		|
      		|___________  prediction: the prediction associated to each file from src/selection/
							|_____ dataset1
				     			|_____ dataset2
				     			|_____ dataset3
      
# Installation

  * install dependencies for python
    ```bash
    pip install -r requirements.txt.
    ```
   * install dependencies for R
   Rscrip requirements.R
