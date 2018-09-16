
# Author: Youssef Hmamouche

require(compiler)
enableJIT(3)

library (Biocomb)

library(tsDyn)
library(lmtest)
library(vars)
library(parallel)

#source("src/tools/selection_tools.R")
source("src/tools/read_meta_data.R")

no_cores <- detectCores() - 1


process_one_target <- function (target_name, colnames, data, max_features, meta_data, output_dir, data_dir)
{
    print (paste("Processing:",target_name))
    for(j in 1:length(colnames))
    if (colnames[j] == target_name){
        target_index = j
        break;
    }
    
    y = data[,j]
    X = data[,-j]
    datax = data.frame (X, y)
    colnames (datax) = c (colnames [-j],target_name)
    
    
    # check if files already exist
    test = 0
    for (k in 1:max_features){
        out_dir = paste0(output_dir,target_name,"_","_fcbf_K=",k,".csv")
        if (!file.exists (out_dir)){
            test = 1
            break
        }
    }
    
    if (test == 0){
        print ("already exists")
        #return (0)
    }
    
    # apply the method
    try ({FFS = select.fast.filter (datax ,  disc.method = "MDL", threshold = 0.2, attrs.nominal=numeric())
        
        
        factors = FFS$NumberFeature
        factors_names = as.character(FFS$Biomarker)
        
        
        if (max_features > length (factors))
            max_features = length (factors)
        
        for (k in 1:max_features)
        {
            try ({
                factors_out = data.frame (data[,j], datax[, factors[1:k]])
                colnames (factors_out) = c(target_name, factors_names [1:k])
                #print (head (factors_out,1))
                out_dir = paste0(output_dir,target_name,"_","_fcbf_K=",k,".csv")
                
                # Set metadata
                command = paste0 ('awk \'/^#/ && !/^# *predict/\' ',data_dir)
                system(paste0(command,' > ', out_dir))
                
                cat ("# predict;", file=out_dir,append=TRUE)
                cat (target_name, file=out_dir,append=TRUE, sep='\n')
                cat ("# prediction_type;", file=out_dir, append=TRUE)
                cat (paste0(meta_data$prediction_type), file=out_dir, append=TRUE, sep='\n')
                cat (paste0("# method; FCBF", "(n_components=",k,")"),file=out_dir,append=TRUE, sep='\n')
                
                ## Store the selected variables
                write.table(factors_out, out_dir,row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)
            })
        }
    })
    

}

select_fast_filter <- function (args){

    data_dir = args[1]
    output_dir = args[2]
    if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
        output_dir = paste0(output_dir,'/')

    # read meta-data
    meta_data = read_meta_data(data_dir)
    

    ## read the dataset
    data = read.table(data_dir,check.names=FALSE, header = TRUE, dec = '.',sep=";", comment.char = "#")
    
    data = data[colSums(!is.na(data)) > 0]
    #print (ncol (data))
    colnames = colnames(data)

    # extract the maximum number of attributes
    max_features = meta_data$max_attributes
    
    
    ncol = ncol (data)
        ############# Execute the method  for each target
    mclapply(meta_data$target_names, function(target_name) try(process_one_target (target_name, colnames, data, max_features, meta_data, output_dir, data_dir)), mc.cores=no_cores, mc.preschedule = FALSE)
}

args = commandArgs(trailingOnly=TRUE)

if (length(args) > 3){
    print ("Error: number of arguments incorrect.")
    quit()
}

select_fast_filter (args)

