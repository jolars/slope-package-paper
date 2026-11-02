save_paper_plot <- function(name, width, height, pointsize, code) {
  plot_code <- substitute(code)
  plot_env <- parent.frame()
  dir.create(here::here("images"), showWarnings = FALSE, recursive = TRUE)

  for (extension in c("pdf", "svg")) {
    path <- here::here("images", paste0(name, ".", extension))
    if (extension == "pdf") {
      grDevices::pdf(path, width = width, height = height, pointsize = pointsize)
    } else {
      grDevices::svg(path, width = width, height = height, pointsize = pointsize)
    }
    tryCatch(eval(plot_code, envir = plot_env), finally = grDevices::dev.off())
  }

  invisible(NULL)
}
