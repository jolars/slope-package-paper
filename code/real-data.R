library(SLOPE)
library(caret)
library(pROC)
library(here)
library(glmnet)

source(here::here("code", "plot-utils.R"), local = TRUE)

####### SLOPE and Lasso - classification
set.seed(222)

x <- scale(glioma$x)
y <- glioma$y

train_index <- createDataPartition(y, p = 0.7, list = FALSE)
x_train <- x[train_index, ]
y_train <- y[train_index]
x_test <- x[-train_index, ]
y_test <- y[-train_index]

# CV SLOPE

slope_cv <- cvSLOPE(
  x_train,
  y_train,
  q = 0.1,
  family = "binomial",
  measure = "auc",
  n_folds = 10
)

alpha_cv <- slope_cv$optima$alpha
slope_model <- SLOPE(
  x_train,
  y_train,
  q = 0.1,
  family = "binomial",
  alpha = alpha_cv
)

# CV Lasso

lambda_cv <- cv.glmnet(
  as.matrix(x_train),
  y_train,
  nfolds = 10,
  type.measure = "auc",
  family = "binomial"
)
lasso_model <- glmnet(
  as.matrix(x_train),
  y_train,
  lambda = lambda_cv$lambda.min,
  family = "binomial"
)

### results

# slope

pred_prob_slope <- predict(slope_model, x_test, type = "response")

roc_obj_slope <- roc(y_test, pred_prob_slope)
auc_val_slope <- auc(roc_obj_slope)

# lasso

pred_prob_lasso <- as.vector(predict(
  lasso_model,
  as.matrix(x_test),
  type = "response"
))

roc_obj_lasso <- roc(y_test, pred_prob_lasso)
auc_val_lasso <- auc(roc_obj_lasso)

# plot

width <- 7
height <- 3
ps <- 8

save_paper_plot("glioma-roc", width, height, ps, {
  par(
    mfrow = c(1, 2),
    cex = 1,
    mar = c(4, 0.5, 2, 0.1),
    oma = c(0.1, 4.5, 0.1, 0.1)
  )
  plot(
    roc_obj_slope,
    main = sprintf("ROC Curve for SLOPE with AUC = %g", round(auc_val_slope, 3)),
    lwd = 2,
    xlim = c(1, 0),
    ylim = c(0, 1)
  )

  plot(
    roc_obj_lasso,
    main = sprintf("ROC Curve for Lasso with AUC: %g", round(auc_val_lasso, 3)),
    lwd = 2,
    xlim = c(1, 0),
    ylim = c(0, 1)
  )
})

slope_model_path <- SLOPE(
  x_train,
  y_train,
  q = 0.1,
  family = "binomial",
  patterns = TRUE
)

# chosen variables lasso / slope
cbind(coefficients(lasso_model), as.vector(coefficients(slope_model)))

colSums(
  cbind(coefficients(lasso_model), as.vector(coefficients(slope_model))) != 0
)

# patterns
pat_slope <- slope_model_path$patterns[[
  which.min(abs(slope_model_path$alpha - alpha_cv))
]]
rownames(pat_slope) <- colnames(x)
pat_slope[rowSums(pat_slope) != 0, ]

selected_step <- which.min(abs(slope_model_path$alpha - alpha_cv))
stopifnot(isTRUE(all.equal(slope_model_path$alpha[selected_step], alpha_cv)))

save_paper_plot("glioma-clusters", 4.5, 4.2, 8, {
  SLOPE::plotClusters(slope_model_path, include_zeroes = FALSE)
  abline(
    v = (selected_step - 1) / (length(slope_model_path$alpha) - 1),
    col = "firebrick", lty = 2, lwd = 1.5
  )
  mtext(sprintf("Selected step %d", selected_step), side = 3, line = 0.5)
})

selected_pattern <- as.matrix(pat_slope)
groups <- lapply(seq_len(ncol(selected_pattern)), function(index) {
  rownames(selected_pattern)[selected_pattern[, index] != 0]
})
groups <- Filter(length, groups)

# The intercept is unpenalized, so selection counts refer only to metabolites.
glioma_results <- list(
  auc_slope = as.numeric(auc_val_slope),
  auc_lasso = as.numeric(auc_val_lasso),
  n_selected_slope = sum(as.vector(coef(slope_model))[-1] != 0),
  n_selected_lasso = sum(as.vector(coef(lasso_model))[-1] != 0),
  n_clusters_slope = length(groups),
  groups = groups,
  alpha = alpha_cv,
  selected_step = selected_step
)
