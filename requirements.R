# Some of these packages should not be installed, but can be installed manually, like rJava and TransferEntropy

packages = c ("kernlab",
              "TransferEntropy",
              "forecast",
              "cluster",
              "lmtest",
              "fpc",
              "vars",
              "Biocomb",
              "rJava",
              "stats",
              "parallel",
              "tsDyn",
              "factoextra",
              "NbClust",
              "psych")

for (package in packages)
{
  if (!require(package))
    try(install.packages (package, repos='http://cran.us.r-project.org'))
}


