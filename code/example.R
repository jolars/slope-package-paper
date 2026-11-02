library(SLOPE)
library(here)

source(here::here("code", "plot-utils.R"), local = TRUE)

data("diabetes", package = "lars")

x <- scale(diabetes$x)
y <- diabetes$y

# Basic Use
fit_slope <- SLOPE(x, y, q = 0.4)
fit_lasso <- SLOPE(x, y, lambda = "lasso")

width <- 6.4
height <- 4.1
ps <- 8

save_paper_plot("diabetes-slope-lasso", width, height, ps, {
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
})

# Relaxed SLOPE
fit_relaxed <- SLOPE(x, y, q = 0.1, gamma = 0)
fit_semirelaxed <- SLOPE(x, y, q = 0.1, gamma = 0.5)
fit_standard <- SLOPE(x, y, q = 0.1, gamma = 1)

save_paper_plot("slope-relaxed", width, height, ps, {
  par(
    mfrow = c(1, 3),
    cex = 1,
    mar = c(4, 0.5, 2, 0.1),
    oma = c(0.1, 4.5, 0.1, 0.1)
  )
  plot(fit_relaxed, type = "S", main = expression(paste(gamma, " = 0")))
  mtext(expression(hat(beta)), side = 2, line = 2, outer = TRUE)
  plot(
    fit_semirelaxed,
    ylab = "",
    type = "S",
    main = expression(paste(gamma, " = 0.5")),
    yaxt = "n"
  )
  plot(
    fit_standard,
    ylab = "",
    main = expression(paste(gamma, " = 1")),
    type = "S",
    yaxt = "n"
  )
})

# Cross-Validation
set.seed(48)
fit_cv <- cvSLOPE(x, y, q = c(0.1, 0.2))

save_paper_plot("slope-cv", width, 3, ps, {
  par(
    mfrow = c(1, 2),
    cex = 1,
    mar = c(4, 0.7, 2, 0.1),
    oma = c(0.1, 4.5, 0.1, 0.1)
  )
  plot(fit_cv, index = 1)
  plot(fit_cv, plot_args = list(ylab = "", yaxt = "n"), index = 2)
  mtext("MSE", side = 2, line = 2, outer = TRUE)
})
