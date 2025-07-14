library(dplyr)
library(SLOPE)
library(readxl)
library(caret)
library(pROC)
library(here)
library(glmnet)
library(MLmetrics)

fig_name <- function(name) {
  here::here("images", paste0(name, ".pdf"))
}

opar <- par(no.readonly = TRUE)

dat <- readxl::read_excel("./code/41598_2023_38243_MOESM2_ESM.xlsx")[, -1]
colnames(dat)[1] <- "group"
metabolites <- colnames(dat)[-1]

glioma_dat <- dat %>%
  filter(group != "Meningioma") %>%
  mutate(group = ifelse(group == "Healthy control", 0, 1))

x <- glioma_dat[, -1]
y <- glioma_dat[, 1][[1]]

# pattern
fit_pat <- SLOPE(x, y, q = 0.1, pattern = TRUE, family = "binomial")

pattern <- fit_pat$patterns[[20]]
pattern

width <- 17
height <- 10
ps <- 8

patterns_glioma <- fig_name("glioma-clusters")
pdf(patterns_glioma, width = width, height = height, pointsize = ps)
SLOPE::plotClusters(fit_pat, include_zeroes = F)
dev.off()


####### SLOPE and Lasso - classification

set.seed(222)

dat <- readxl::read_excel("./code/41598_2023_38243_MOESM2_ESM.xlsx")[, -1]
colnames(dat)[1] <- "group"
metabolites <- colnames(dat)[-1]

glioma_dat <- dat %>%
  filter(group != "Meningioma")

X <- scale(glioma_dat[, -1])
Y <- glioma_dat[, 1][[1]]

train_index <- createDataPartition(Y, p = 0.7, list = FALSE)
X_train <- X[train_index, ]
Y_train <- ifelse(Y[train_index] == "Healthy control", 0, 1)
X_test <- X[-train_index, ]
Y_test <- ifelse(Y[-train_index] == "Healthy control", 0, 1)

# CV SLOPE

slope_cv <- cvSLOPE(
  X_train,
  Y_train,
  q = 0.1,
  family = "binomial",
  measure = "auc",
  n_folds = 10
)
alpha_cv <- slope_cv$optima$alpha
slope_model <- SLOPE(
  X_train,
  Y_train,
  q = 0.1,
  family = "binomial",
  alpha = alpha_cv
)

# CV Lasso

lambda_cv <- cv.glmnet(
  as.matrix(X_train),
  Y_train,
  nfolds = 10,
  type.measure = "auc",
  family = "binomial"
)
lasso_model <- glmnet(
  as.matrix(X_train),
  Y_train,
  lambda = lambda_cv$lambda.min,
  family = "binomial"
)


### results

# slope

pred_prob_slope <- predict(slope_model, X_test, type = "response")

roc_obj_slope <- roc(Y_test, pred_prob_slope)
auc_val_slope <- auc(roc_obj_slope)

pred_class_slope <- ifelse(pred_prob_slope > 0.5, 1, 0)
f1_slope <- MLmetrics::F1_Score(y_true = Y_test, y_pred = pred_class_slope)


# lasso

pred_prob_lasso <- as.vector(predict(
  lasso_model,
  as.matrix(X_test),
  type = "response"
))

roc_obj_lasso <- roc(Y_test, pred_prob_lasso)
auc_val_lasso <- auc(roc_obj_lasso)

pred_class_lasso <- ifelse(pred_prob_lasso > 0.5, 1, 0)
f1_lasso <- MLmetrics::F1_Score(y_true = Y_test, y_pred = pred_class_lasso)


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


####

slope_model_path <- SLOPE(
  X_train,
  Y_train,
  q = 0.1,
  family = "binomial",
  patterns = TRUE
)


# chosen variables lasso / slope
cbind(coefficients(lasso_model), as.vector(coefficients(slope_model)))

# patterns
pat_slope <- slope_model_path$patterns[[which(
  slope_cv$summary$alpha == alpha_cv
)]]
rownames(pat_slope) <- metabolites
pat_slope[rowSums(pat_slope) != 0, ]
