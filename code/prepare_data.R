library(dplyr)
library(readxl)

dat <- readxl::read_excel(here::here(
  "code",
  "41598_2023_38243_MOESM2_ESM.xlsx"
))[, -1]
colnames(dat)[1] <- "group"
metabolites <- colnames(dat)[-1]

glioma_dat <- dat %>%
  filter(group != "Meningioma") %>%
  mutate(group = ifelse(group == "Healthy control", 0, 1))

saveRDS(glioma_dat, "code/glioma_dat.RDS")
