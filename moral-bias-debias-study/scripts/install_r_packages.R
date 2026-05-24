suppressPackageStartupMessages({
  required <- c(
    "tidyverse",
    "afex",
    "emmeans",
    "lme4",
    "broom.mixed",
    "ggplot2"
  )
})

repos <- c(CRAN = "https://cloud.r-project.org")
user_lib <- Sys.getenv("R_LIBS_USER")
if (!nzchar(user_lib)) {
  user_lib <- file.path(path.expand("~"), "R", "win-library", paste(R.version$major, sub("\\..*$", "", R.version$minor), sep = "."))
}
dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))

installed <- rownames(installed.packages())
missing <- setdiff(required, installed)

if (length(missing) > 0) {
  install.packages(missing, repos = repos, lib = user_lib)
}

cat("R packages ready.\n")
