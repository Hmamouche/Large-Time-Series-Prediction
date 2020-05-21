# Author: Youssef Hmamouche

#library(lmtest)
library(vars)
library (NlinTS)

source("src/tools/read_meta_data.R")

### arguments
args = commandArgs(trailingOnly=TRUE)

if (length(args) < 2 || length(args) > 4){
    print ("Error: number of arguments incorrect.")
    quit()
}

# dataset directory and output directory
data_dir = args[1]
output_dir = args[2]

is_roling = FALSE
if(length(args) == 3)
    is_roling = TRUE

if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
    output_dir = paste0(output_dir,'/')

# read data
data = read.csv(data_dir, header=TRUE,check.names=FALSE,dec='.',sep=";",comment.char = "#")
data = data[colSums(!is.na(data)) > 0]
#print (tail (data, 2));


# read  metadata
command = paste0 ('awk /^#/ ',data_dir)
meta_data = read_meta_data(data_dir)

if(is.na(meta_data$lag_p))
    meta_data$lag_p = 1

if(is.na(meta_data$horizon))
    meta_data$horizon = 1

if (meta_data$nbre_predictions == 0)
    meta_data$nbre_predictions = as.integer(nrow(data) * 10 / 100)

# construct the output directory
output_dir = paste0(output_dir,"nlin_gc.csv")

system(paste0(command,' > ', output_dir))

# Delete the last rows on which the forecast evaluations will be done
data = data[1:(nrow(data)-meta_data$nbre_predictions),]

#### calculate the matrix
gMat = data.frame(nrow=ncol(data), ncol=ncol(data))

for (i in 1:ncol(data))
{
    for (j in 1:ncol(data))
    {

        if (j != i) {
            tryCatch(
                     {

       		 test =   nlin_causality.test (data[,j], data [,i], meta_data$lag_p, c(meta_data$lag_p), c(2*meta_data$lag_p), 50)
       		 gMat[i,j] = test$gci

			#tryCatch ({
			 #test =   causality.test (data[,j], data [,i], meta_data$lag_p)
			 #gMat[i,j] = 1 - test$pvalue},
   			 #finally = {
                          #   gMat[i,j] = 0
			  #})

                     }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")}
            )
            #gMat[i,j] = test$
        }
        else
            gMat[i,j] = 0
    }
}
gMat = data.frame(c(colnames(data)),gMat)
colnames(gMat) <- c(' ', colnames(data))
write.table(gMat, output_dir, sep = ";",row.names =FALSE, append = TRUE)
