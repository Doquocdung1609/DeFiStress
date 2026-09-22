# TerraUSD/LUNA May 2022 Case Study

## Question and design

Can models frozen at `T0 = 2022-05-06 23:59:59 UTC` reproduce or provide useful early-warning signals for the subsequent death spiral? The default evaluation window is 7–13 May 2022 UTC. All dates are configurable.

Terra Classic is the primary mechanism chain. Ethereum Curve, wrapped assets, and bridges are secondary contagion venues. External price feeds are reference series, not silent replacements for chain state.

## Workflow

`source observations → versioned dataset → pre-T0 calibration view → frozen model → replay → isolated ground truth → validation → benchmark → ablation/counterfactual`

The bundled dataset is a synthetic `FIXTURE`. It demonstrates the workflow but is not evidence about May 2022. A historical claim requires an imported dataset with a defensible manifest.

## Interpretation

`OUT_OF_SAMPLE_REPLAY` is retrospective evaluation under an information cutoff. `EARLY_WARNING` is a decomposable model-implied risk signal. Neither is a live prospective price prediction.
