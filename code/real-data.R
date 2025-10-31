library(SLOPE)
library(caret)
library(pROC)
library(here)
library(glmnet)
library(MLmetrics)
library(dplyr)
library(readxl)

fig_name <- function(name) {
  here::here("images", paste0(name, ".pdf"))
}

x <- glioma$x
y <- glioma$y

# pattern
fit_pat <- SLOPE(x, y, q = 0.1, pattern = TRUE, family = "binomial")

pattern <- fit_pat$patterns[[20]]
pattern

width <- 4.5
height <- 4.2
ps <- 7

patterns_glioma <- fig_name("glioma-clusters")
pdf(patterns_glioma, width = width, height = height, pointsize = ps)
SLOPE::plotClusters(fit_pat, include_zeroes = FALSE)
dev.off()


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

pred_class_slope <- ifelse(pred_prob_slope > 0.5, 1, 0)
f1_slope <- MLmetrics::F1_Score(y_true = y_test, y_pred = pred_class_slope)


# lasso

pred_prob_lasso <- as.vector(predict(
  lasso_model,
  as.matrix(x_test),
  type = "response"
))

roc_obj_lasso <- roc(y_test, pred_prob_lasso)
auc_val_lasso <- auc(roc_obj_lasso)

pred_class_lasso <- ifelse(pred_prob_lasso > 0.5, 1, 0)
f1_lasso <- MLmetrics::F1_Score(y_true = y_test, y_pred = pred_class_lasso)

# plot

width <- 7
height <- 3
ps <- 8

patterns_glioma <- fig_name("glioma-roc")
pdf(patterns_glioma, width = width, height = height, pointsize = ps)
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
dev.off()

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
pat_slope <- slope_model_path$patterns[[which(
  slope_cv$summary$alpha == alpha_cv
)]]
rownames(pat_slope) <- colnames(x)
pat_slope[rowSums(pat_slope) != 0, ]
