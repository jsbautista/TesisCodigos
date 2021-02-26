import seaborn as sns
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import scipy.stats as stats

### Carga de resultados
#resultados = pd.read_excel('formato_resultados.xlsx', index_col=0) 
resultados = pd.read_csv('resultados.csv')

### Grafica de resultados

metricas = ["FO_Global", "FO_Ordenes", "FO_Costo", "FO_ANS", "FO_Fairness", "FO_Prioridad", "FO_Distancia", "Tiempo"]

for metrica in metricas:
    plt.figure()
    ax_global = sns.boxplot(x="Tamano", y=metrica, hue="Modelo", 
                             order=["Small", "Medium", "Large"],
                             data=resultados).set_title(metrica)
    #plt.savefig('ex1.pdf') para guardar

### ANOVA

# Two Way ANOVA
model = ols('FO_Global ~ C(Tamano) + C(Modelo) + C(Tamano):C(Modelo)', data=resultados).fit()
modelResults = sm.stats.anova_lm(model, typ=2)

# One Way ANOVA
model = ols('FO_Global ~ C(Modelo)', data=resultados).fit()
modelResults = sm.stats.anova_lm(model, typ=1)
residuals = model.resid

print(modelResults, '\n')

### Validacion supuestos ANOVA 

### Residuals (experimental error) are normally distributed (Shapiro-Wilks Test)

#QQ-Plot
sm.qqplot(residuals, line='45')
plt.title("Residuals QQ-Plot")
plt.xlabel("Theoretical Quantiles")
plt.ylabel("Standardized Residuals")
plt.show()

# Histogram
plt.hist(residuals, bins='auto', histtype='bar', ec='k') 
plt.title("Residuals Histogram")
plt.xlabel("Residuals")
plt.ylabel('Frequency')
plt.show()

# Shapiro-Wilk test
w, pvalue = stats.shapiro(residuals)
print("Shapiro-Wilk Test ---", "w:", w, "p-value:", pvalue)

### Homogeneity of variances (variances are equal between treatment groups) (Levene’s or Bartlett’s Test)

# Bartlett's test
datosFOGlobalDEAP = resultados.loc[resultados['Modelo'] == 'DEAP', 'FO_Global'].values
datosFOGlobalGurobi = resultados.loc[resultados['Modelo'] == 'Gurobi', 'FO_Global'].values
datosFOGlobalPyomo = resultados.loc[resultados['Modelo'] == 'Pyomo', 'FO_Global'].values
w, pvalue = stats.bartlett(datosFOGlobalDEAP, datosFOGlobalGurobi, datosFOGlobalPyomo)
print("Bartlett's Test ---", "w:", w, "p-value:", pvalue)