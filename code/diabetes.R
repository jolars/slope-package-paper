library(SLOPE)
library(here)

data("diabetes", package = "lars")

x <- scale(diabetes$x)
y <- diabetes$y

q <- 0.05

fit_slope <- SLOPE(x, y, q = 0.1)
fit_lasso <- SLOPE(x, y, lambda = "lasso")

width <- 2.9
height <- 4.2
ps <- 8

slope_file <- here("images", "diabetes-slope.pdf")
pdf(slope_file, width = width, height = height, pointsize = ps)
plot(fit_slope)
dev.off()

lasso_file <- here("images", "diabetes-lasso.pdf")
pdf(lasso_file, width = width, height = height, pointsize = ps)
plot(fit_lasso)
dev.off()

knitr::plot_crop(lasso_file)
knitr::plot_crop(slope_file)
