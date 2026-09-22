# Anti-Leakage Design

`CalibrationDatasetView` rejects every observation after the cutoff. `EvaluationDatasetView` exposes timestamps, not values, to simulation. Models accept only `ModelInputState`, timestamps, frozen parameters, and seed. They do not import or accept `GroundTruthState`.

`GroundTruthRepository` loads evaluation values only after model execution and passes them only to validation. `test_model_cannot_access_post_cutoff_ground_truth()` locks this boundary.

Every export includes the cutoff/window, dataset hash/version, model version, git commit, seed, parameters, sources, and leakage status. In-sample runs display `IN-SAMPLE — NOT VALID EVIDENCE OF PREDICTIVE PERFORMANCE`.
