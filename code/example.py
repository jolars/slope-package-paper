from matplotlib import pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.preprocessing import StandardScaler
from sortedl1 import Slope

x, y = load_diabetes(return_X_y=True)
scaler = StandardScaler()
x = scaler.fit_transform(x)

model_lasso = Slope(lambda_type="lasso")
model_slope = Slope(lambda_type="bh", q=0.4)

fit_lasso = model_lasso.path(x, y)
fit_slope = model_slope.path(x, y)

plt.rcParams["savefig.bbox"] = "tight"

figsize = (2.8, 2.5)

fit_lasso.plot(figsize=figsize)
plt.title("Lasso")
plt.savefig("images/diabetes-slope-python.pdf")

fit_slope.plot(figsize=figsize)
plt.title("SLOPE")
plt.savefig("images/diabetes-lasso-python.pdf")

fit_cv = model_slope.cv(x, y, q=[0.1, 0.2])

fit_cv.plot()

plt.savefig("images/slope-cv-python.pdf")
