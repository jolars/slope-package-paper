using SLOPE
using CSV
using ProjectRoot
using DataFrames
using Statistics
using Plots
using Measures

Plots.resetfontsizes()
Plots.scalefontsizes(0.6)

imgdir = @projectroot "images/"

file = @projectroot "data/diabetes.csv"
df = CSV.read(file, DataFrame)

x = Matrix(df[:, 2:end])
y = df[:, 1]

# Standardize features
x_means = mean(x, dims = 1)
x_std = std(x, dims = 1)
x = (x .- x_means) ./ x_std

fit_lasso = slope(x, y, λ = :lasso)
fit_slope = slope(x, y, λ = :bh)

p1 = plot(fit_lasso)
p2 = plot(fit_slope)

p_comb = plot(
    p1,
    p2,
    layout = (1, 2),
    size = (400, 200),
    title = ["Lasso" "SLOPE"],
    bottom_margin = 5pt,
    left_margin = 5pt,
)

savefig(p_comb, imgdir * "diabetes-slope-lasso-julia.pdf")

fit_cv = slopecv(x, y)

pcv = plot(fit_cv, size = (300, 200))

savefig(pcv, imgdir * "slope-cv-julia.pdf")
