"""Figure 14 — Cox model of Anchor withdrawals (time-varying hazard).

Reproduces ``paper/figures/Run22-Cox-hazard.png``.
Left  — the time-varying coefficient on trader size beta(t) (blue) and the
        baseline withdrawal hazard lambda_0(t) (black, right axis).
Right — the UST discount (blue) and the baseline hazard (black, right axis).

METHOD (faithful port of the published R fit).  The published exhibit is a
**time-varying-coefficient Cox model** estimated in R with ``timereg::timecox``:

    timecox(Surv(time / 24, status) ~ log10_size, data = wdtime, n.sim = 50)

``timecox`` estimates *cumulative* regression coefficients B(t) = int_0^t beta(s) ds
(one path for the intercept, one for ``log10_size``) on the May 6-13 window.
The pointwise effect beta(t) and the baseline hazard are recovered from B(t) by
cosine-kernel smoothing of the cumulative increments (Martinussen & Scheike,
*Dynamic Regression Models for Survival Data*, eq. 6.35, p. 207):

    beta(t) = int b^{-1} K((s - t) / b) dB(s),   K = cosine ("Tukey") kernel, b = 1 h

(evaluated via integration by parts so only B(s) — not its noisy increments — is
interpolated).  The baseline hazard is lambda_0(t) = exp(beta_intercept(t)),
expressed per hour and in percent (``exp(.)/24*100``); the size coefficient is
beta_size(t).

PROVENANCE.  ``timecox``'s estimator is kernel-smoothed local-linear with 20
Newton iterations and lives in compiled C inside the R package (``OStimecox``),
so there is no faithful pure-Python equivalent — the estimation step stays in R.
It is packaged as ``code/figures/fit_timecox.R``, which reads the shipped
survival panel, runs the exact published ``timecox`` call, and writes the
``cum`` parquet below.  That parquet is shipped so THIS figure (and the rest of
the package) runs without R; rerun the R script only to regenerate it.
    # cum columns: time (days since May 6), intercept (= log baseline hazard), size

Inputs (shippable):
    data/hazard/timecox_cum_may6_12.parquet   time (days), intercept, size  [R timecox cum]
    data/hazard/ust_discount_may6_12.parquet  hours_from_may6, ust_discount_bp

Output: output/figures/Run22-Cox-hazard.png
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.integrate import quad
from scipy.interpolate import interp1d

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm  # noqa: E402

PAGE_W_CM, PAGE_H_CM = 15.5, 5.5   # true on-page size; included at textwidth
MAY6 = pd.Timestamp("2022-05-06")  # cum time is measured in days from May 6
KERNEL_B = 1.0 / 24.0              # cosine-kernel half-width: 1 hour (cum time is in days)
PLOT_POINTS = 2000                 # grid on which beta(t) is recovered
PLOT_START = pd.Timestamp("2022-05-06 23:00:00")
PLOT_END = pd.Timestamp("2022-05-13 01:00:00")
BLUE = "#5B9BD5"                   # lighter blue for the series and its axis labels


# ---- cosine ("Tukey") kernel and its derivative -------------------------------
def _cosine_kernel(s):
    return ((np.cos(np.pi * s) + 1) / 2) * (np.abs(s) < 1)


def _cosine_kernel_prime(s):
    return -np.pi * np.sin(np.pi * s) / 2 * (np.abs(s) < 1)


def _beta_point(t, B, b):
    """Pointwise coefficient at t from cumulative path B via int b^-1 K((s-t)/b) dB(s),
    computed by integration by parts so only B (not dB) is interpolated."""
    def integrand(s):
        return _cosine_kernel_prime((s - t) / b) / b / b * B(s)

    def boundary(s):
        return B(s) / b * _cosine_kernel((s - t) / b)

    a, c = t - b, t + b
    term3 = quad(integrand, a, c, epsabs=1e-4, full_output=True)[0]
    return boundary(c) - boundary(a) - term3


def _recover_beta(cum):
    """Recover beta_intercept(t) and beta_size(t) from the timecox cumulative paths.
    Returns a DataFrame indexed by datetime (days-from-May-6 mapped to wall clock)."""
    cum = cum[cum["time"] > 0]
    B = {k: interp1d(cum["time"].values, cum[k].values, kind="linear",
                     fill_value="extrapolate")
         for k in ("intercept", "size")}
    times = np.linspace(cum["time"].min(), cum["time"].max(), PLOT_POINTS)
    beta = pd.DataFrame({k: [_beta_point(t, B[k], KERNEL_B) for t in times]
                         for k in ("intercept", "size")})
    beta.index = MAY6 + pd.to_timedelta(times, unit="D")
    return beta


def main() -> Path:
    cum = pd.read_parquet(datadir("hazard", "timecox_cum_may6_12.parquet"))

    beta = _recover_beta(cum).resample("15min").mean().loc[PLOT_START:PLOT_END]
    beta_size = beta["size"]
    # baseline hazard lambda_0(t) = exp(beta_intercept(t)), per hour, in percent
    lam0 = np.exp(beta["intercept"]) / 24 * 100

    disc = pd.read_parquet(datadir("hazard", "ust_discount_may6_12.parquet"))
    disc_t = MAY6 + pd.to_timedelta(disc["hours_from_may6"].values, unit="h")
    disc_frac = disc["ust_discount_bp"].values / 10_000.0   # basis points -> fraction

    fmt = mdates.DateFormatter("%-m/%d")
    out = figpath("Run22-Cox-hazard.png")
    with plt.rc_context(caption_rc()):
        fig, (axL, axR) = plt.subplots(1, 2, figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))

        # left: size coefficient beta(t) (blue) + baseline hazard (black, right axis)
        axL.plot(beta_size.index, beta_size.to_numpy(), color=BLUE, lw=1.4)
        axL.set_ylabel("Coef of log10 size", color=BLUE)
        axL.set_ylim(0.2, 1.0)
        axL.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        axL.tick_params(axis="y", labelcolor=BLUE)
        axL.grid(alpha=0.3)
        axL.set_xlim(PLOT_START, PLOT_END)   # late May 6 -> early May 13; gridlines at 12AM 5/7..5/13
        axL.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        axL.xaxis.set_major_formatter(fmt)
        axLb = axL.twinx()
        axLb.plot(lam0.index, lam0.to_numpy(), color="black", lw=1.1)
        axLb.set_ylabel("Baseline hazard", color="black")
        axLb.set_ylim(0, 1.6)
        axLb.set_yticks([0.0, 0.4, 0.8, 1.2, 1.6])

        # right: UST discount (blue) + baseline hazard (black, right axis)
        axR.plot(disc_t, disc_frac, color=BLUE, lw=1.2)
        axR.set_ylabel("UST discount", color=BLUE)
        axR.set_ylim(0, 0.9)
        axR.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
        axR.tick_params(axis="y", labelcolor=BLUE)
        axR.grid(alpha=0.3)
        axR.set_xlim(PLOT_START, PLOT_END)   # late May 6 -> early May 13; gridlines at 12AM 5/7..5/13
        axR.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        axR.xaxis.set_major_formatter(fmt)
        axRb = axR.twinx()
        axRb.plot(lam0.index, lam0.to_numpy(), color="black", lw=1.1)
        axRb.set_ylabel("Baseline hazard", color="black")
        axRb.set_ylim(0, 1.6)
        axRb.set_yticks([0.0, 0.4, 0.8, 1.2, 1.6])

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}  (size coef {beta_size.iloc[0]:.2f}->{beta_size.iloc[-1]:.2f}, "
          f"lambda0 peak {lam0.max():.2f}%)")
    return out


if __name__ == "__main__":
    main()
