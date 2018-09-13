# Author: Youssef Hmamouche

# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

## Prediction using the auto.arima model


library(tsDyn)
library(lmtest)
library(vars)
library(forecast)

source("src/tools/read_meta_data.R")

auto_arima_prediction <- function (target, max_p, nb_preds, horizon, type = "cross_validation")
{
    # ts: multivariate time series to predict the first attribut
    # max_p: max lag parameter
    # nb_preds: number points to predict
    
    results = data.frame()
    for (ind in 1:nb_preds)
    {
        if (type == "cross_validation")
            training_data = target[1:(length(target) - (nb_preds - ind)  - horizon)]
        
        else if (type == "rolling")
            training_data = target[ind:(length(target) - (nb_preds - ind)  - horizon)]
        
        tryCatch({
            model = auto.arima (training_data,  max.p=max_p, max.q=2)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        
        y = forecast(model, h = horizon)[[4]]

        for (j in 1:horizon)
            results[ind,j] = y[j]
    }
    return (results)
}


predictbase <- function (method_name, prefix_out){
    data_name = strsplit(method_name, "/")
    command = paste0 ('awk \'BEGIN{printf("# predict_model;AUTO_ARIMA\\n");} /^#/\' ', method_name)
    meta_data = read_meta_data(method_name)

    print (meta_data)

    if(is.na(meta_data$horizon))
    meta_data$horizon = 1

    if(is.na(meta_data$lag_p))
    meta_data$lag_p = 0

    if(is.na(meta_data$nbre_predictions))
    meta_data$nbre_predictions = 0


    # read data
    data      = read.csv (method_name, comment.char = "#", header=TRUE, sep=";")
    colnames = colnames(data)

    for (target_name in meta_data$target_names)
    {
        for(j in 1:length(colnames))
            if (colnames[j] == target_name) {
                target_index = j
                break;
            }
        output_dir = paste0(prefix_out,"Auto.Arima_",target_name,"_",data_name[[1]][length(data_name[[1]])])
        #system(paste0(command,' > ', output_dir))
        # Bref description of the file
        command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',method_name)
        system(paste0(command,' > ', output_dir))
        cat ("# predict;", file=output_dir,append=TRUE)
        cat (target_name, file=output_dir,append=TRUE, sep='\n')
        cat ("# method; Univariate_model()",file=output_dir,append=TRUE, sep='\n')
        cat ("# predict_model; Auto_Arima",file=output_dir,append=TRUE, sep='\n')

        ### normalisation
        #max = max(data[,target_index])
        #min = min(data[,target_index])


        # determine the lag parameter
        if (meta_data$lag_p == 0){
            lagMax = as.integer ((nrow(data)  - 1)  / 4)
        }
        else lagMax = meta_data$lag_p

        ## determmine the number of predictions
        if (meta_data$nbre_predictions == 0)
            nbrePreds = as.integer(nrow(data) * 10 / 100) # 10% predictions of the size of the data
        else nbrePreds = meta_data$nbre_predictions

        ## compute predictions
        tryCatch({
        preds = auto_arima_prediction (data[,target_index],lagMax, nbrePreds,meta_data$horizon)
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})

        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
    }
}

args = commandArgs(trailingOnly=TRUE)
largs = length(args)
print(args[largs])
try(predictbase(args[1],args[2]))

