import glob
import sys

file_name = sys.argv[1]
data_name = file_name.split('/')[-1].split('.')[0]

print (10 * "*" + " COUNTING SELECTION FILES" + 10 * "*")
hits = glob.glob ("results/selection/" + data_name + "/*Hits*")
fcbf = glob.glob ("results/selection/" + data_name + "/*fcbf*")
KernelPCA = glob.glob ("results/selection/" + data_name+ "/*KernelPCA*")
PCA = glob.glob ("results/selection/" + data_name + "/*_PCA*")
Fact = glob.glob ("results/selection/" + data_name + "/*_Fact*")
GFSM = glob.glob ("results/selection/" + data_name + "/*_GFSM*")

print (1* '\t' + "Hits: %s" % (len (hits)/2))
print (1* '\t' + "fcbf: %s" % len (fcbf))
print (1* '\t' + "KernelPCA: %s" % len (KernelPCA))
print (1* '\t' + "PCA: %s" % len (PCA))
print (1* '\t' + "Fact: %s" % len (Fact))
print (1* '\t' + "GFSM: %s" % (len (GFSM)/2))

print (10 * "*" + " COUNTING PREDICTION FILES" + 10 * "*")
hits = glob.glob ("results/prediction/" + data_name + "/*Hits*")
fcbf = glob.glob ("results/prediction/" + data_name + "/*fcbf*")
KernelPCA = glob.glob ("results/prediction/" + data_name + "/*KernelPCA*")
PCA = glob.glob ("results/prediction/" + data_name + "/*_PCA*")
Fact = glob.glob ("results/prediction/" + data_name + "/*_Fact*")
GFSM = glob.glob ("results/prediction/" + data_name + "/*_GFSM*")
Arima = glob.glob ("results/prediction/" + data_name + "/*Arima*")
LSTM = glob.glob ("results/prediction/" + data_name + "/*lstm*")
VECM = glob.glob ("results/prediction/" + data_name + "/*Vecm*")
LASSO = glob.glob ("results/prediction/" + data_name + "/*Lasso*")
RIDGE = glob.glob ("results/prediction/" + data_name + "/*Ridge*")

print (1* '\t' + "Hits: %s"% (len (hits)/2))
print (1* '\t' + "fcbf: %s"%len (fcbf))
print (1* '\t' + "KernelPCA: %s"%len (KernelPCA))
print (1* '\t' + "PCA: %s"%len (PCA))
print (1* '\t' + "Fact: %s"%len (Fact))
print (1* '\t' + "GFSM: %s"% (len (GFSM)/2))
print (1* '\t' + "Arima: %s"% len (Arima))
print (1* '\t' + "Lstm: %s"% len (LSTM))
print (1* '\t' + "Vecm: %s"% len (VECM))
print (1* '\t' + "Lasso: %s"% len (LASSO))
print (1* '\t' + "Lasso: %s"% len (RIDGE))
#print (1* '\t' + "SUM: %s"% str ((len (hits)/2) + len (fcbf) + len (KernelPCA) + len (PCA) +  (len (GFSM)/2)))

print (30 * "*")
