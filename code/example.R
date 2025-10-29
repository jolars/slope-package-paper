library(SLOPE)
library(here)

fig_name <- function(name) {
  here::here("images", paste0(name, ".pdf"))
}

data("diabetes", package = "lars")

x <- scale(diabetes$x)
y <- diabetes$y

# Basic Use
fit_slope <- SLOPE(x, y, q = 0.4)
fit_lasso <- SLOPE(x, y, lambda = "lasso")

width <- 6
height <- 4.2
ps <- 8

slope_lasso_file <- fig_name("diabetes-slope-lasso")
pdf(slope_lasso_file, width = width, height = height, pointsize = ps)
par(
  mfrow = c(1, 2),
  cex = 1,
  mar = c(4, 0.5, 2, 0.1),
  oma = c(0.1, 4.5, 0.1, 0.1)
)
plot(
  fit_slope,
  main = "SLOPE",
  ylab = "",
  add_labels = TRUE,
  xlim = c(18, 0.005)
)
mtext(expression(hat(beta)), side = 2, line = 2, outer = TRUE)
plot(
  fit_lasso,
  main = "Lasso",
  yaxt = "n",
  ylab = "",
  add_labels = TRUE,
  xlim = c(51, 0.009)
)
dev.off()

# Cross-Validation
set.seed(48)
fit_cv <- cvSLOPE(x, y, q = c(0.1, 0.2))

cv_file <- fig_name("slope-cv")
pdf(cv_file, width = 5.8, height = 3, pointsize = ps)
par(
  mfrow = c(1, 2),
  cex = 1,
  mar = c(4, 0.7, 2, 0.1),
  oma = c(0.1, 4.5, 0.1, 0.1)
)
plot(fit_cv, index = 1)
plot(
  fit_cv,
  plot_args = list(
    ylab = "",
    yaxt = "n"
  ),
  index = 2
)
mtext("MSE", side = 2, line = 2, outer = TRUE)
dev.off()
knitr::plot_crop(cv_file)
