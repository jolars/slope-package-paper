source_paper_example <- function(path) {
  example_env <- new.env(parent = globalenv())
  suppressPackageStartupMessages(source(path, local = example_env))
  example_env
}

run_paper_command <- function(command, args = character()) {
  if (!nzchar(command)) {
    stop("A program needed to render the paper is missing from PATH.")
  }
  output <- system2(command, shQuote(args), stdout = TRUE, stderr = TRUE)
  status <- attr(output, "status")
  if (!is.null(status) && status != 0L) {
    stop(paste(c(sprintf("%s failed with exit status %d:", command, status), output),
      collapse = "\n"
    ))
  }
  output
}

paper_figure <- function(name) {
  extension <- if (knitr::is_html_output()) "svg" else "pdf"
  path <- file.path("images", paste0(name, ".", extension))
  if (!file.exists(path)) {
    stop("Missing paper figure: ", path)
  }
  path
}

Sys.setenv(MPLBACKEND = "Agg", GKSwstype = "100", PYTHONHASHSEED = "0")

paper_examples <- list(
  diabetes = source_paper_example("code/example.R"),
  glioma = source_paper_example("code/real-data.R")
)

python <- Sys.getenv("QUARTO_PYTHON", unset = Sys.which("python"))
julia <- Sys.getenv("QUARTO_JULIA", unset = Sys.which("julia"))
cpp <- Sys.getenv("SLOPE_CPP_EXAMPLE", unset = Sys.which("slope-example"))

python_scripts <- c(
  "code/example.py", "code/plot_thresholding.py", "code/plot_benchmark_real.py",
  "code/plot_benchmark_simul.py", "code/plot_benchmark_path.py"
)
for (script in python_scripts) {
  run_paper_command(python, script)
}
run_paper_command(julia, c("--project=.", "code/example.jl"))
cpp_output <- run_paper_command(cpp)

paper_results <- list(
  diabetes = list(cv_text = capture.output(print(paper_examples$diabetes$fit_cv))),
  glioma = paper_examples$glioma$glioma_results,
  cpp = list(output = cpp_output)
)
