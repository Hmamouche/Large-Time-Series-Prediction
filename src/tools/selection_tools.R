
# Author: Youssef Hmamouche

library (stats)
library(cluster)
library (kernlab)

############### Hierarchical gsm ###########################
hgfsm <- function (F,gmat, targetIndex,threshold, clus, nk)
{
    gsmCluster = c()
    mincaus = 0
    #### eliminate variables that not cause the target
    delet = c()
    n = 1
    m = 1
    for (i in 1:ncol(gmat))
    {
        if (i == targetIndex)
        target = m
        if (i != targetIndex)
        if (gmat[i,targetIndex] < threshold)
        {
            delet[n] = i
            n = n + 1
        }
        else {
            m = m + 1
        }
    }
    
    ### Applying the PAM methode
    if ((length(delet) + 1) == ncol(F))
    return (data.frame())
    
    if (length(delet) > 0)
    {
        gmat = gmat[-delet, -delet]
        F = F[,-delet]
    }
    x = gmat[-target, -target]
    ## determine the optimal number of cluster
    if(clus == TRUE)
    {
        kmax = nrow(x)-1
        if (kmax < 2)
        return (F[,-target])
        
        a=fviz_nbclust(as.dist(x), pam, method = "silhouette",k.max = kmax)
        #a=fviz_nbclust(x, pam, method = "silhouette",k.max = kmax)
        k = which.max(a$data[,2])
    }
    else
    k = nk
    ######
    #print ("#################")
    #print (ncol (x))
    if (k < ncol(x))
    {
        for (l in 2:ncol(x))
        for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - mean(x[l,m], x[m,l])
        
        clusters = hclust (as.dist (x))
        #print (clusters)
        clusteringVector = cutree(clusters, k)
        #print (clusteringVector)
        #clusteringVector = clusters$cluster
        #clusteringVector = clusters (clusters)
        
        classes = data.frame()
        for (j in 1:k)
        {
            l = 1
            for ( i in 1:ncol(x))
            if (clusteringVector[i] == j)
            {
                classes[l,j] = i
                if (classes[l,j] >= target)
                {
                    classes[l,j] = classes[l,j] + 1
                }
                l = l + 1
            }
        }
        ### buildind the gsm cluster from the PAM clusters
        for (j in 1:k)
        {
            bestInGroup = 1;
            if (ncol(classes) >= j)
            {
                caus = gmat[classes[1,j],target];
                for (l in 2:length(classes[,j]))
                {
                    if(is.na(classes[l,j]) == FALSE)
                    {
                        if (gmat[classes[l,j],target] > caus)
                        {
                            caus = gmat[classes[l,j],target];
                            bestInGroup = l;
                        }
                    }
                    gsmCluster[j] = classes[bestInGroup,j];
                }
            }
        }
        GSM = data.frame()
        GSM = F [,gsmCluster]
        return (GSM)
    }
    else
    return (F[,-target])
}




#########################################################
gfsm <- function (F,gmat, targetIndex,threshold, clus, nk)
{
  gsmCluster = c()
  mincaus = 0
  #### eliminate variables that not cause the target
  delet = c()
  n = 1
  m = 1
  for (i in 1:ncol(gmat))
  {
    if (i == targetIndex)
      target = m
    if (i != targetIndex)
      if (gmat[i,targetIndex] < threshold)
      {
        delet[n] = i
        n = n + 1
      }
    else {
      m = m + 1
    }
  }

  ### Applying the PAM methode
  if ((length(delet) + 1) == ncol(F))
    return (data.frame())
  
  if (length(delet) > 0)
  {
    gmat = gmat[-delet, -delet]
    F = F[,-delet]
  } 
  x = gmat[-target, -target]
  ## determine the optimal number of cluster
  if(clus == TRUE)
  {
  kmax = nrow(x)-1
  if (kmax < 2)
    return (F[,-target])
  
  a=fviz_nbclust(as.dist(x), pam, method = "silhouette",k.max = kmax)
  #a=fviz_nbclust(x, pam, method = "silhouette",k.max = kmax)
  k = which.max(a$data[,2])
  }
  else
    k = nk
  ######
  if (k < ncol(x))
  {
    for (l in 2:ncol(x))
      for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - mean(x[l,m], x[m,l])

#clusters = pam (as.dist(x),k)
      clusters = pam (as.dist (x), diss = TRUE, k)
      clusteringVector = clusters$cluster
      #clusteringVector = clusters (clusters)

      classes = data.frame()
      for (j in 1:k)
      {
        l = 1
        for ( i in 1:ncol(x))
          if (clusteringVector[i] == j)
          {
            classes[l,j] = i
            if (classes[l,j] >= target)
            {
              classes[l,j] = classes[l,j] + 1
            }
            l = l + 1
          }
      }
      ### buildind the gsm cluster from the PAM clusters
      for (j in 1:k)
      {
        bestInGroup = 1;
        if (ncol(classes) >= j)
        {
          caus = gmat[classes[1,j],target];
          for (l in 2:length(classes[,j]))
          {
            if(is.na(classes[l,j]) == FALSE)
            {
              if (gmat[classes[l,j],target] > caus)
              {
                caus = gmat[classes[l,j],target];
                bestInGroup = l;
              }
            }
            gsmCluster[j] = classes[bestInGroup,j];
          }
        }
      }
      GSM = data.frame()
      GSM = F [,gsmCluster]
      return (GSM)
  }
  else
    return (F[,-target])
}

##### gsm with PCA method
gsmPCA <- function (F,gmat, targetIndex,threshold, clus, nk)
{
  gsmCluster = data.frame()
  mincaus = 0
  #### eliminate variables that not cause the target
  delet = c()
  n = 1
  m = 1
  for (i in 1:ncol(gmat))
  {
    if (i == targetIndex)
      target = m
    if (i != targetIndex)
      if (gmat[i,targetIndex] < threshold)
      {
        delet[n] = i
        n = n + 1
      }
    else {
      m = m + 1
    }
  }
  ###########
  ### Applying the PAM methode
  if ((length(delet) + 1) == ncol(F))
    return (data.frame())
  
  if (length(delet) > 0)
  {
    gmat = gmat[-delet, -delet]
    F = F[,-delet]
  } 
  x = gmat[-target, -target]
  ## determine the optimal number of cluster
  if(clus == TRUE)
  {
    kmax = nrow(x)-1
    if (kmax < 2)
      return (F[,-target])
    
    a=fviz_nbclust(as.dist(x), pam, method = "silhouette",k.max = kmax)
    k = which.max(a$data[,2])
  }
  else
    k = nk
  ######
  if (k < ncol(x))
  {

    for (l in 2:ncol(x))
      for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - max(x[l,m], x[m,l])


      #km = kcca(x, k, family = kccaFamily ("kmeans"), weights=NULL, group=NULL, control=NULL, simple=FALSE)
      #symmetrize(x, rule="strong")
      clusters = pam (as.dist(x), k)
      clusteringVector = clusters$cluster
      #clusteringVector = clusters (km)

      classes = data.frame()
      for (j in 1:k)
      {
        l = 1
        for ( i in 1:ncol(x))
          if (clusteringVector[i] == j)
          {
            classes[l,j] = i
            if (classes[l,j] >= target)
            {
              classes[l,j] = classes[l,j] + 1
            }
            l = l + 1
          }
      }

      ### buildind the gsm cluster from the PAM clusters
      for (j in 1:k)
      {
          vect = classes[,j]
          vect <- vect[!is.na(vect)]
          if (length(vect) > 1) {
              #prinComp = kpca(~.,data=F[,vect], kernel="rbfdot",sigma=0.2,features=1)
              fit = princomp (~.,data=F[,vect])
              variables = fit$scores
              for (l in 1:nrow(variables))
                gsmCluster[l,j] = variables[l,1]
          }
          if (length(vect) == 1)
            for(h in 1:nrow(F))
              gsmCluster[h,j] = F[h,vect[1]]
      }
      return (gsmCluster)
  }
  else
    return (F[,-target])
}

#### GFSM + dimension reduction methods
gfsm_dms_reduction <- function (F,gmat, targetIndex,threshold, clus, nk, methode_name)
{
  gsmCluster = data.frame()
  mincaus = 0
  #### eliminate variables that not cause the target
  delet = c()
  n = 1
  m = 1
  for (i in 1:ncol(gmat))
  {
    if (i == targetIndex)
      target = m
    if (i != targetIndex)
      if (gmat[i,targetIndex] < threshold)
      {
        delet[n] = i
        n = n + 1
      }
    else {
      m = m + 1
    }
  }
  ###########
  ### Applying the PAM methode
  if ((length(delet) + 1) == ncol(F))
    return (data.frame())
  
  if (length(delet) > 0)
  {
    gmat = gmat[-delet, -delet]
    F = F[,-delet]
  } 
  x = gmat[-target, -target]

  # Symmetrize x
  for (l in 2:ncol(x))
    for(m in 1: (l-1))
        x[l,m] = x[m,l] = 1 - max(x[l,m], x[m,l])
  ## determine the optimal number of cluster
  if(clus == TRUE)
  {
    kmax = nrow(x)-1
    if (kmax < 2)
      return (F[,-target])

     asw = c()
     #silouhette methode
    for (km in 1:kmax)
  		asw[k] <- (pam(as.dist(x),diss=TRUE,km)$silinfo)$avg.width
	k <- which.max(asw)
	print (k)
    
  }
  else
    k = nk
  ######
  if (k < ncol(x))
  {   
      clusters = pam (as.dist (x), diss = TRUE, k)
      clusteringVector = clusters$cluster

      classes = data.frame()
      for (j in 1:k)
      {
        l = 1
        for ( i in 1:ncol(x))
          if (clusteringVector[i] == j)
          {
            classes[l,j] = i
            if (classes[l,j] >= target)
            {
              classes[l,j] = classes[l,j] + 1
            }
            l = l + 1
          }
      }

      ### buildind the gsm cluster from the PAM clusters
      for (j in 1:k)
      {
          vect = classes[,j]
          vect <- vect[!is.na(vect)]
          if (length(vect) > 1) {
          	if (methode_name == "KPCA") {
          		print ("KPCA method")
              prinComp = kpca(~.,data=F[,vect], kernel="rbfdot",sigma=0.2,features=1)
              variables = pcv(prinComp)
          	}
          	if (methode_name == "FACT"){
          		print ("Factor analysis method")
              fit = factanal(F[,vect], factors=1)
              model = factor.scores(F[,vect],fit)
              variables = model$scores
          	}
          	if (methode_name == "PCA"){
          		print ("PCA method")
          		#the functions prcomp() use the singular value decomposition (SVD).
                fit = princomp (~.,data=F[,vect])
                variables = fit$scores

          	}
            for (l in 1:nrow(variables))
                gsmCluster[l,j] = variables[l,1]
          }
          if (length(vect) == 1)
            for(h in 1:nrow(F))
              gsmCluster[h,j] = F[h,vect[1]]
      }
      return (gsmCluster)
  }
  else
    return (F[,-target])
}

#### SELECTKBEST based on causality
naiveSelection <- function (gmat, targetIndex, threshold)
{
  naiveClasse = c()
  ##F = data.frame ()
  ind  = 1
  index = c()

  for (i in 1:ncol(gmat))
  {
    if (i != targetIndex)
    {
      #F[ind,1] = i;
      if (gmat[i,targetIndex] >= threshold && gmat[targetIndex,i] < threshold)
      {
        index[ind] = i
        ind = ind + 1
      }
    }
  }
  return (index)
}
### Normalize a dataframe
normalize <- function (F)
{
  for (i in 1 : ncol(F))
  {
    max = max(F[,i])
    min = min(F[,i])
    for(j in 1:nrow(F))
      F[j,i] = (F[j,i] - min) / (max - min)
  }
  return (F)
}

#### neural network function
disc <- function (F,p, dec, cible)
{

  G = F[1:(nrow(F) - (dec + 1)),]
  hiddenLayers = c((ncol(G) * p* 2 / 3), (ncol(G) * p * 2 / 3),(ncol(G) * p * 2 / 3))
  module = varnnet(G, p, 1, hiddenLayers, 1000)
  result = data.frame()
  ts = data.frame()
  for (ind in 1:dec)
  {
    ts = F[1:(nrow(F) - (dec - ind + 1)),]

    y = module$forecast(ts)

    for (ij in 1:ncol(y))
      result[ind,ij] = y[nrow(y),ij]

    iter = 1

    while (iter < 2)
    {
      module$learn (F[1:(nrow(F) - (dec - ind)),])
      iter = iter + 1
    }
  }
  return (result)
}



