from sklearn.metrics import\
        mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score
import numpy as np

def MASE(testing_series, prediction_series):
    training_len = len(testing_series)
    differences = np.abs(np.diff(testing_series.T)).sum() / (training_len - 1)
    errors = np.abs(testing_series - prediction_series)
    return errors.mean() / differences

def MASE2(training_series, testing_series, prediction_series):
    """
    Computes the MEAN-ABSOLUTE SCALED ERROR forcast error for univariate time series prediction.

    See "Another look at measures of forecast accuracy", Rob J Hyndman

    parameters:
        training_series: the series used to train the model, 1d numpy array
        testing_series: the test series to predict, 1d numpy array or float
        prediction_series: the prediction of testing_series, 1d numpy array (same size as testing_series) or float
        absolute: "squares" to use sum of squares and root the result, "absolute" to use absolute values.

    """
    n = len(training_series)
    d = np.abs(  np.diff( training_series) ).sum()/(n-1)

    errors = np.abs(testing_series.T - prediction_series )
    return errors.mean()/d

# All used measures
GLOBAL_MEASURES = {
        'rmse': lambda x,y: np.sqrt(mean_squared_error(x,y)),
        'mse': mean_squared_error,
        'mae': mean_absolute_error,
        'medae': median_absolute_error,
        'MASE': None,
        # 'evc': explained_variance_score,
        # 'r2': r2_score,
        # 'R': lambda x,y: 1, # placeholder
        }
