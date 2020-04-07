# Author: Youssef Hmamouche

require(compiler)
enableJIT(3)


library(tsDyn)
library(lmtest)
library(vars)
library(cluster)
library (factoextra)
library(parallel)

source("src/tools/read_meta_data.R")


#' GFSM method using the PAM clustering technique
#' @details select variables of a given multivariate time series with a target variable.
#' @param F Numerical dataframe
#' @param gmat Numerical dataframe, the matrix of pairwise causalities of variables of F
#' @param targetIndex Integer, the position of the target variable in the dataframe F (e.g., 1 if it is in the first column)
#' @param threshold a threshold of causality, 0.9 by default
#' @param clus Logical, False by default for selecting k variables where k is an input, and True for selecting a natural number of variables
#' @param k the reduction size, i.e., the number of variables to select

#' @return a dataFrame of selected variables

gfsm <- function (F,gmat, targetIndex,threshold = 0.0, clus = FALSE, nbre_vars) {
    
    # in case of nbre_vars = 1, we return just one variable based on causality to the target
    if (nbre_vars == 1){
        max_caus = 1
        for (i in 2:nrow (gmat))
            if (gmat[i, targetIndex] > gmat[max_caus, targetIndex])
                max_caus = i
        GSM = data.frame (F[,max_caus])
        colnames (GSM) = colnames (F)[max_caus]
        return (GSM)
    }
    
    #### First, we eliminate variables that do not cause the target according to the threshold
    gsmCluster = c()
    delet = c()
    n = 1
    m = 1
    for (i in 1:ncol(gmat)){
        if (i == targetIndex)
            target = m
        if (i != targetIndex)
            if (gmat[i,targetIndex] < threshold) {
                delet[n] = i
                n = n + 1
            }
        else
            m = m + 1
    }

    ### Applying the PAM methode for the clustering task
    if ((length(delet) + 1) == ncol(F))
        return (data.frame())
  
    if (length(delet) > 0)
    {
        gmat = gmat[-delet, -delet]
        F = F[,-delet]
    } 
    x = gmat[-target, -target]
  
    ## determine the optimal number of cluster in case of clus = TRUE
    if(clus == TRUE) {
        kmax = nrow(x)-1
        if (kmax < 2)
            return (F[,-target])
  
        a=fviz_nbclust(x, pam, method = "silhouette",k.max = kmax)
        k = which.max(a$data[,2])
    }
    else
        k = nbre_vars

    if (k < ncol(x))
    {
        for (l in 2:ncol(x))
        for(m in 1: (l-1))
            x[l,m] = x[m,l] = 1 - max(x[l,m], x[m,l])

        clusters = pam (as.dist (x), diss = TRUE, k)
        clusteringVector = clusters$cluster

        classes = data.frame()
        for (j in 1:k) {
            l = 1
            for ( i in 1:ncol(x))
                if (clusteringVector[i] == j) {
                    classes[l,j] = i
                if (classes[l,j] >= target)
                {
                    classes[l,j] = classes[l,j] + 1
                }
                l = l + 1
            }
        }
        ### choose the best variable from each cluster
        for (j in 1:k) {
            bestInGroup = 1;
            if (ncol(classes) >= j) {
                caus = gmat[classes[1,j],target];
          
                for (l in 2:length(classes[,j])) {
                    if(is.na(classes[l,j]) == FALSE) {
                        if (gmat[classes[l,j],target] > caus) {
                            caus = gmat[classes[l,j],target];
                            bestInGroup = l;
                        }
                    }
                }
                gsmCluster[j] = classes[bestInGroup,j];
            }
        }
        GSM = F [,gsmCluster]
    }

    else
        GSM =  F[,-target]
  
   return (GSM)
}

# Make selection for one target variable, i.e. one inout file.
gfsm_selection_inner <- function (output_dir, target_name, prediction_type, graph_name, nk, data, matrix, target_index, threshold, data_dir){
    
    print (paste0 ("Processing file: ", target_name, "..."))
    out_dir = paste0(output_dir,target_name,"_",graph_name,"_GFSM_K=",nk,".csv")
    p_gfsm = gfsm (data, matrix, target_index, threshold, clus = FALSE, nbre_vars= nk)

    if (ncol(data.frame(p_gfsm)) > 0)
        p_gfsm = data.frame (data[,target_index],data.frame(p_gfsm))

    else
        p_gfsm = data.frame (data[,target_index])

    colnames(p_gfsm)[1] = target_name
    # Set metadata
    command = paste0 ('awk \'/^#/ && !/^# *predict/\' ', data_dir)
    system(paste0(command,' > ', out_dir))
    cat ("# predict;", file=out_dir, append=TRUE)
    cat (target_name, file=out_dir, append=TRUE, sep='\n')
    cat ("# prediction_type;", file=out_dir, append=TRUE)
    cat (paste0(prediction_type), file=out_dir, append=TRUE, sep='\n')
    cat (paste0("# method; Part-GFS_", graph_name, "(n_components=",nk,")"),file=out_dir, append=TRUE, sep='\n')
    ## Store the selected variables
    write.table(p_gfsm, out_dir, row.names = FALSE, na = "",col.names = TRUE, sep = ";", append = TRUE)
}


# Make selection for all target variables in parallel.
gfsm_selection <- function (args){

    data_dir = args[1]
    output_dir = args[2]
    if( substr(output_dir, nchar(output_dir),nchar(output_dir)) != '/')
        output_dir = paste0(output_dir,'/')

    no_cores <- detectCores () - 1
    no_cores <- 1

    ## read the dataset
    data = read.csv (data_dir,check.names=FALSE, header = TRUE, dec = '.',sep=";", comment.char = "#")
    
    # read meta-data
    meta_data = read_meta_data(data_dir)
    
    ## max number of attributes
    max_features = meta_data$max_attributes

    colnames = colnames(data)

    # Graphs directory
    graph_dir = paste0  ("results/pre_selection/",meta_data$data_name)
    graphs = list.files (path = graph_dir, all.files = FALSE)
    
    for (k in 1:length(graphs))
    {
        graph_name = substr(graphs[[k]], 1, (nchar(graphs[[k]])-4) )
        threshold = 0.01
        if (is.element (graph_name, c("granger_graph")))
        threshold = 0.95

        graph_dir = paste0("results/pre_selection/",meta_data$data_name,"/",graphs[k])

        matrix = read.table(graph_dir,check.names=FALSE, header = TRUE,row.names = 1, dec = '.',sep=";", comment.char = "#")
        
        ############# Execute the method  for each target
        for (target_name in meta_data$target_names)
        {
            for(j in 1:length(colnames))
                if (colnames[j] == target_name) {
                    target_index = j
                    break;
                }

            mclapply (1:max_features, function(i) try (gfsm_selection_inner (output_dir, target_name,meta_data$prediction_type, graph_name, i, data, matrix, target_index, threshold, data_dir)), mc.cores=no_cores, mc.preschedule = FALSE)
        }
    }
}

args = commandArgs (trailingOnly=TRUE)

if (length(args) > 3){
    print ("Error: number of arguments incorrect.")
    quit()
}

gfsm_selection (args)

