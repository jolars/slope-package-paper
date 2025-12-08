using SLOPE
using CSV
using ProjectRoot
using DataFrames
using Statistics

file = @projectroot "data/diabetes.csv"
df = CSV.read(file, DataFrame)

x = Matrix(df[:, 2:end])
y = df[:, 1]

# Standardize features
x_means = mean(x, dims = 1)
x_std = std(x, dims = 1)
x = (x .- x_means) ./ x_std


# TODO: update once new SLOPE version is released
fit_lasso = slope(x, y)
fit_slope = slope(x, y)

fit_cv = cv_slope(x, y)
