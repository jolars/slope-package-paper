import sys
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.preprocessing import StandardScaler
from sortedl1 import Slope

sys.path.append(str(Path(__file__).resolve().parents[1]))

from slopeutils.plot_utils import save_paper_figure

x, y = load_diabetes(return_X_y=True)
scaler = StandardScaler()
x = scaler.fit_transform(x)

model_lasso = Slope(lambda_type="lasso")
model_slope = Slope(lambda_type="bh", q=0.4)

fit_lasso = model_lasso.path(x, y)
fit_slope = model_slope.path(x, y)

plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 9
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["lines.markersize"] = 3
plt.rcParams["lines.linewidth"] = 1
Path("images").mkdir(parents=True, exist_ok=True)

figsize = (2.35, 2.5)

fit_lasso.plot(figsize=figsize)
plt.title("Lasso")
save_paper_figure(plt.gcf(), "images/diabetes-lasso-python.pdf")
plt.close()

fit_slope.plot(figsize=figsize)
plt.title("SLOPE")
save_paper_figure(plt.gcf(), "images/diabetes-slope-python.pdf")
plt.close()

# Explicit folds keep cross-validation reproducible across render processes.
rng = np.random.default_rng(48)
folds = np.array([np.array_split(rng.permutation(len(y)), 10)], dtype=object)
fit_cv = model_slope.cv(x, y, q=[0.1, 0.2], predefined_folds=folds)

fit_cv.plot(figsize=(5.2, 3.9))

save_paper_figure(plt.gcf(), "images/slope-cv-python.pdf")
plt.close()
