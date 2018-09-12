# Author: Youssef Hmamouche

# Use compiler and jit for this file (when processing multiple files this improves performance)
require(compiler)
enableJIT(3)

library(tsDyn)
library(lmtest)
library(vars)
library(parallel)

source("src/tools/read_meta_data.R")
# Adaptation of the VECM model to make nb_preds predictions on a multivariate time series ts
vecm <- function (ts, p, nb_preds, horizon, type = "cross_validation")
{
    pred = data.frame()

    for (ind in 1:nb_preds)
    {
        if (type == "cross_validation")
            df = ts[1:(nrow(ts) - (nb_preds-ind) - horizon),]
            
        else if (type == "rolling")
            df = ts[ind:(nrow(ts) - (nb_preds-ind) - horizon),]
        
        ####### Apply the model
        tryCatch({
            model = VECM (data.frame(df), p, include = c("both"), estim = c("ML"))
        }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})
        
        y = predict(model,n.ahead = horizon)

        for (inh in 1 : horizon)
            pred[ind,inh] = y[inh,1]
    }
    return (pred)
}

# Make predictions on a given input selection file when the target is in the first column
predictbase <- function (method_name, prefix_out, reset = 0){

    data_name = strsplit(method_name, "/")
    print ("Processinf file: ")
    print (method_name)
    if (reset == 0)
    
    output_dir = paste0(prefix_out,"Vecm_",data_name[[1]][length(data_name[[1]])])
    if(file.exists(output_dir))
    {
        print ("file already exists!!")
        # stop("file already exists!!")
    }
    command = paste0 ('awk \' BEGIN{printf("# predict_model; Vecm\\n");}/^#/ \' ',method_name)
    meta_data = read_meta_data(method_name)

    ### normalisation
    fs_method      = read.csv (paste0(method_name), comment.char = "#", header=TRUE, sep=";")

    # determine the lag parameter
    
    if (meta_data$lag_p == 0)
        lagMax = as.integer ((nrow(fs_method)  - 1)  / (2 * (ncol(fs_method) + 1)))
    
    else lagMax = meta_data$lag_p

    var = VARselect(fs_method,lag.max=lagMax)
    p = var$selection[1] ## AIC criteria

    ###  Prediction
    preds = data.frame()
    if (meta_data$nbre_predictions == 0)
        nbrePreds = as.integer(nrow(fs_method) * 10 / 100) # 10% predictions of the size of the data
    else nbrePreds = meta_data$nbre_predictions
    

    preds = vecm (fs_method, p, nbrePreds, meta_data$horizon, meta_data$prediction_type)

    if (nrow (preds) > 0){
        #output_dir = paste0(prefix_out,"Vecm_",data_name[[1]][length(data_name[[1]])])
        system(paste0(command,' > ', output_dir))
        write.table(preds, file = output_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";",append = TRUE)
    }
}


args = commandArgs(trailingOnly=TRUE)

print (args)
selection_files = list.files(path = args[1], all.files = FALSE)
output_directory = args[2]

#print (selection_files[1])
#stop ()

# Number of files from selection step
nbre_files = length (selection_files)

# The numbre of cores
no_cores <- detectCores() -1

# Run comutations on parallel
mclapply(1:nbre_files, function(i) try(predictbase(paste0 (args[1],selection_files[i]), 
                                                  output_directory,
                                                   reset = 0)),
                        mc.cores=no_cores, 
                        mc.preschedule = FALSE)



