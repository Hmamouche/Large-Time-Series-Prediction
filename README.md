# Introduction
This repository contain an implementation of a framework for large time series prediction. The approach includes computing the  graphs of dependencies between time series, feature selection, then prediction using different algorithms.
The system takes as input a multivariate time series with metadata specifying the lag parameter and the variables to predict (see examples of input time series in the folder data).

It is based on the following steps:
  * Computing causality graphs with two measures: the Granger causality test and the Transfer entropy.
  * Reducing the number of predictors: a new feature selection algorithm is available (src/selection/pehar.py), in addition to other existing methods.
  * Prediction: several prediction models can be used (ARIMA, VECM, LSTM, VAR+shrinkage methods)

# Requirements
  * R >= 3.6
  * Python >= 3.6
  * Installing dependencies
    ```bash
      Rscript requirements.R
      pip install -r requirements.txt
    ```
# Usage
### Input data
The data must be a multivariate time series stored as a csv file with semi-colon as separator, and with columns-names specifying the name of each variable. In addition, other information are required as metadata in the top of the file as comments with \# as prefix (see examples in the folder data). A description of these information is as follows:
 * name_prefix: prefix name of the data
 * description: description of data (optional)
 * lag_parameter: the number of lags, i.e., the number of previous observations to consider to make future predictions.
 * predict: the names of target variables (time series to predict).
 * number_predictions: number of observations of the test set.
 * horizon: 1
 * prediction_type: training strategy (in choices ["cross-validation", or "rolling"]). The first one is self-explanatory, and the second means rolling-windows training way.
 * max_attributes: the max number of variables to select during the feature selection step.

### Evaluation mode:
The aim of these steps is to make evaluations on a train-test split of the data of type cross validation or rolling window (specified in meta-data of the input data). It consists first in computing causality graphs, applying reduction methods, then applying prediction models, and finally  finding the best feature selection method and prediction model for each target variable. The results of these steps will be stored in the folder _results_. Example:
```bash
	python process.py  data/us_diff.csv -t pre_selection
	python process.py  data/us_diff.csv -t selection
	python process.py  data/us_diff.csv -t prediction
	python process.py  data/us_diff.csv -t pre_evaluation
	python process.py  data/us_diff.csv -t evaluation
```
if you may want to make just one processing with a specific script, an example is as follows:
```bash
	python process.py  data/us_diff.csv -t selection -s src/slection/pehar_fselection.py
```

### Forecasting mode:
The goal here is making future predictions based on results of the evaluation step. The results will be stored in the folder _Processed_. This folder will contain also the best predictors and reduction method of each target variable. Exampe:

```bash
	python prediction.py  -d data/us_diff.csv -m eval
```
Or if you want to make forecasts without evaluation results, i.e., with a given reduction method and prediction model, you have to use "direct" prediction mode:. For more detail, see the following arguments:
```bash
--data, -d  file of data to process
--mode {eval,direct}, -m {eval,direct}
                      prediction mode
--pred_model {VECM,ARIMA}, -pr {VECM,ARIMA}
                      prediction model
--fs_method {PEHAR_te,PEHAR_gc}, -fsm {PEHAR_te,PEHAR_gc}
                      feature selection method
--nb_predictors NB_PREDICTORS, -nbp NB_PREDICTORS
                      number of variables to select
--graph_type {gc,te}, -g {gc,te}
                      Causality graph to use, ganger causality (gc), or
                      transfer entropy (te)
```


## Citation
```bibtex
@article{hmamouche2021scalable,
  title={A scalable framework for large time series prediction},
  author={Hmamouche, Youssef and Lakhal, Lotfi and Casali, Alain},
  journal={Knowledge and Information Systems},
  volume={63},
  pages={1093--1116},
  year={2021},
  publisher={Springer}
}
```


