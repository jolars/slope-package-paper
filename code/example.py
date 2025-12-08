from matplotlib import pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.preprocessing import StandardScaler
from sortedl1 import Slope

x, y = load_diabetes(return_X_y=True)
scaler = StandardScaler()
x = scaler.fit_transform(x)

model_lasso = Slope(lambda_type="lasso")
model_slope = Slope(q=0.4)

fit_lasso = model_lasso.path(x, y)
fit_slope = model_slope.path(x, y)

fit_lasso.plot()
plt.savefig("images/diabetes-slope-python.pdf")

fit_slope.plot()
plt.savefig("images/diabetes-lasso-python.pdf")

fit_cv = model_slope.cv(x, y, q=[0.1, 0.2])

fit_cv.plot()
