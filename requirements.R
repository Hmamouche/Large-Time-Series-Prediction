# Some of these packages should not be installed, but can be installed manually, like rJava and TransferEntropy
# for rJava, see: https://zhiyzuo.github.io/installation-rJava/


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
install.packages (packages, repos='http://cran.us.r-project.org')

