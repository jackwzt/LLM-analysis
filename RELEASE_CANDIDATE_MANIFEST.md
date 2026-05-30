# Release Candidate Manifest

## Scope

This folder is a GitHub-safe release candidate assembled from the local project after the 2026-05-30 verification and results freeze.

It is intended for manual review before copying into the Git repository. It does not include raw experiment result directories, repair raw outputs, API logs, model checkpoints, or `confirmatory_trial_level.csv`.

## Included Root Files

- `.gitignore`
- `README.md`
- `requirements.txt`
- `LOCAL_PROJECT_INVENTORY.md`
- `VERIFICATION_REPORT_20260530.md`
- `RESULTS_FREEZE_20260530.md`
- `GITHUB_UPLOAD_PLAN.md`
- `NEXT_COMMANDS.md`
- `RELEASE_CANDIDATE_MANIFEST.md`
- `RELEASE_SAFETY_REPORT.md`

## Included Confirmatory Package Files

Docs:

- `confirmatory_package/docs/analysis_plan.md`
- `confirmatory_package/docs/data_requirements.md`
- `confirmatory_package/docs/method_definitions.md`
- `confirmatory_package/docs/results_narrative.md`

Scripts:

- `confirmatory_package/scripts/01_inventory_results.py`
- `confirmatory_package/scripts/02_build_confirmatory_dataset.py`
- `confirmatory_package/scripts/03_confirmatory_analysis.py`
- `confirmatory_package/scripts/04_make_figures.py`
- `confirmatory_package/scripts/05_make_public_summary_tables.py`
- `confirmatory_package/scripts/06_make_heterogeneity_summary.py`

Public summaries:

- `confirmatory_package/outputs/public_summary/public_moral_model_dataset_method_summary.csv`
- `confirmatory_package/outputs/public_summary/public_sycophancy_model_dataset_method_summary.csv`
- `confirmatory_package/outputs/public_summary/public_fingerprint_matrix.csv`
- `confirmatory_package/outputs/public_summary/public_figure_manifest.csv`
- `confirmatory_package/outputs/public_summary/public_summary_build_report.md`

Compact confirmatory tables:

- `confirmatory_package/outputs/tables/confirmatory_dataset_cell_summary.csv`
- `confirmatory_package/outputs/tables/cost_summary.csv`
- `confirmatory_package/outputs/tables/method_value_ranking.csv`
- `confirmatory_package/outputs/tables/model_dataset_method_heterogeneity_summary.csv`
- `confirmatory_package/outputs/tables/moral_bias_reductions.csv`
- `confirmatory_package/outputs/tables/moral_bias_summary.csv`
- `confirmatory_package/outputs/tables/sycophancy_summary.csv`

Figures:

- `confirmatory_package/outputs/figures/baseline_model_bias.png`
- `confirmatory_package/outputs/figures/baseline_model_bias.pdf`
- `confirmatory_package/outputs/figures/method_moral_bias_reduction.png`
- `confirmatory_package/outputs/figures/method_moral_bias_reduction.pdf`
- `confirmatory_package/outputs/figures/cost_effectiveness_scatter.png`
- `confirmatory_package/outputs/figures/cost_effectiveness_scatter.pdf`
- `confirmatory_package/outputs/figures/model_method_heatmap.png`
- `confirmatory_package/outputs/figures/model_method_heatmap.pdf`
- `confirmatory_package/outputs/figures/method_value_score_ranking.png`
- `confirmatory_package/outputs/figures/method_value_score_ranking.pdf`

## Included Fingerprint Package Files

Docs:

- `fingerprint_package/docs/fingerprint_plan.md`

Scripts:

- `fingerprint_package/scripts/01_build_fingerprint_matrix.py`
- `fingerprint_package/scripts/02_cluster_fingerprints.py`
- `fingerprint_package/scripts/03_plot_fingerprints.py`

Tables:

- `fingerprint_package/outputs/tables/fingerprint_matrix.csv`
- `fingerprint_package/outputs/tables/model_clusters.csv`
- `fingerprint_package/outputs/tables/model_metadata.csv`
- `fingerprint_package/outputs/tables/feature_zscores.csv`
- `fingerprint_package/outputs/tables/hierarchical_linkage.csv`
- `fingerprint_package/outputs/tables/pca_components.csv`
- `fingerprint_package/outputs/tables/family_overlap_summary.csv`

Figures:

- `fingerprint_package/outputs/figures/model_feature_heatmap.png`
- `fingerprint_package/outputs/figures/model_feature_heatmap.pdf`
- `fingerprint_package/outputs/figures/model_fingerprint_dendrogram.png`
- `fingerprint_package/outputs/figures/model_fingerprint_dendrogram.pdf`
- `fingerprint_package/outputs/figures/model_fingerprint_pca.png`
- `fingerprint_package/outputs/figures/model_fingerprint_pca.pdf`

## Explicitly Excluded Categories

- `confirmatory_package/outputs/confirmatory_trial_level.csv`
- raw `results/*/raw_trials.csv`
- repair raw outputs
- raw logs
- raw API traces
- raw model outputs
- scenario text tables
- participant prompt tables
- method trace tables
- provider metadata tables
- `.env`
- credentials
- API keys
- private local paths
- large cache files
- model checkpoints

## Cache Cleanup

Python cache files and cache folders were removed from this release candidate after assembly:

- `__pycache__/`
- `*.pyc`
- `*.pyo`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.ipynb_checkpoints/`
