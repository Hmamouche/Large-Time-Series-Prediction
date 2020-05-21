# Some of these packages may can not be installed, but can be installed manually, like rJava and TransferEntropy

packages = c ("NlinTS")

for (package in packages)
{
  if (!require(package))
    try(install.packages (package, repos='http://cran.us.r-project.org'))
}


