# fit_timecox.R — upstream estimation step for Figure 14 (Cox time-varying hazard).
#
# This is the ESTIMATION code behind fig14_cox_hazard.py.  It fits the published
# time-varying-coefficient Cox model with R's `timereg::timecox` and writes the
# cumulative regression coefficients (`cum`) that the figure consumes.  The
# figure ships the resulting parquet so the Python pipeline runs without R; run
# THIS script only to regenerate that parquet from the raw survival panel.
#
# Model (exactly as in the paper):
#     timecox(Surv(time / 24, status) ~ log10_size, data, n.sim = 50)
# `timecox` estimates B(t) = int_0^t beta(s) ds for the intercept (= log baseline
# hazard) and for log10_size, via a kernel-smoothed local-linear Newton scheme
# (Nit = 20, bandwidth = 0.5; Martinussen & Scheike 2006, ch. 6).  The pointwise
# beta(t) and baseline lambda_0(t) are recovered from `cum` inside the Python
# figure by cosine-kernel smoothing of the cumulative increments.
#
# NOTE: this estimator lives in compiled C inside timereg (`OStimecox`); there is
# no faithful pure-Python equivalent, so the estimation step stays in R.
# `n.sim` only drives the (unused) resampling confidence bands — set 0 for speed,
# 50 to match the paper byte-for-byte.
#
# Requirements: R (tested 4.5) with packages `timereg`, `survival`, `arrow`:
#     Rscript -e 'install.packages(c("timereg","survival","arrow"), repos="https://cloud.r-project.org")'
# Runtime: single-threaded, ~3 h on the 90,768-event panel; < 1 GB (robust = 0).
# Usage (from the package root):
#     Rscript code/figures/fit_timecox.R
# Output: data/hazard/timecox_cum_may6_12.parquet  (columns: time, intercept, size)

suppressMessages({
  library(timereg)
  library(survival)
  library(arrow)
})

# resolve paths relative to the package root (parent of code/)
args <- commandArgs(trailingOnly = FALSE)
script <- sub("^--file=", "", args[grep("^--file=", args)])
script <- gsub("~+~", " ", script, fixed = TRUE)  # Rscript encodes spaces in --file= as ~+~
pkg_root <- normalizePath(file.path(dirname(script), "..", ".."))
infile  <- file.path(pkg_root, "data", "hazard", "survival_may6_12.parquet")
outfile <- file.path(pkg_root, "data", "hazard", "timecox_cum_may6_12.parquet")

n_sim <- as.integer(Sys.getenv("TIMECOX_NSIM", "0"))  # 0 = point estimate only

d <- as.data.frame(read_parquet(infile))
cat(sprintf("read %s: %d rows, %d events\n", basename(infile), nrow(d), sum(d$status)))

# robust = 0: timecox's robust-variance step stores per-subject influence
# functions sized n_events x n_obs (~100 GB on this 90k-event panel -> OOM) and
# is never used here -- only `cum` (the point estimate) is written below, and it
# is bit-identical with robust = 0.  Keeps the fit under ~0.5 GB.
fit <- timecox(Surv(time / 24, status) ~ log10_size, data = d,
               n.sim = n_sim, robust = 0)

cum <- as.data.frame(fit$cum)
colnames(cum) <- c("time", "intercept", "size")  # time in days from May 6
write_parquet(cum, outfile)
cat(sprintf("wrote %s: %d rows, time %.4f..%.4f days\n",
            basename(outfile), nrow(cum), min(cum$time), max(cum$time)))
