# Release Safety Report

Status: `WARNING`

Scanned files: 60
Files with warnings: 26

## Warnings

- `.gitignore` (285 bytes): risky text pattern `secret`; risky text pattern `token`; risky text pattern `credentials`
- `confirmatory_package/docs/analysis_plan.md` (5083 bytes): risky text pattern `token`
- `confirmatory_package/docs/data_requirements.md` (1957 bytes): risky text pattern `token`; risky text pattern `credentials`; risky text pattern `method_trace`
- `confirmatory_package/docs/results_narrative.md` (5750 bytes): risky text pattern `token`; risky text pattern `repair_deepseek`
- `confirmatory_package/outputs/model_dataset_method_heterogeneity_summary.md` (10513 bytes): risky text pattern `token`
- `confirmatory_package/outputs/public_summary/public_fingerprint_matrix.csv` (6613 bytes): risky text pattern `token`
- `confirmatory_package/outputs/public_summary/public_moral_model_dataset_method_summary.csv` (6029 bytes): risky text pattern `token`
- `confirmatory_package/outputs/public_summary/public_summary_build_report.md` (749 bytes): risky text pattern `credentials`; risky text pattern `confirmatory_trial_level.csv`
- `confirmatory_package/outputs/public_summary/public_sycophancy_model_dataset_method_summary.csv` (823 bytes): risky text pattern `token`
- `confirmatory_package/outputs/tables/cost_summary.csv` (4329 bytes): risky text pattern `token`
- `confirmatory_package/outputs/tables/method_value_ranking.csv` (10548 bytes): risky text pattern `token`
- `confirmatory_package/outputs/tables/model_dataset_method_heterogeneity_summary.csv` (6382 bytes): risky text pattern `token`
- `confirmatory_package/scripts/02_build_confirmatory_dataset.py` (11227 bytes): risky text pattern `token`; risky text pattern `confirmatory_trial_level.csv`
- `confirmatory_package/scripts/03_confirmatory_analysis.py` (13059 bytes): risky text pattern `token`; risky text pattern `confirmatory_trial_level.csv`
- `confirmatory_package/scripts/04_make_figures.py` (4463 bytes): risky text pattern `token`
- `confirmatory_package/scripts/05_make_public_summary_tables.py` (9649 bytes): risky text pattern `token`; risky text pattern `credentials`; risky text pattern `confirmatory_trial_level.csv`
- `confirmatory_package/scripts/06_make_heterogeneity_summary.py` (5739 bytes): risky text pattern `token`
- `fingerprint_package/docs/fingerprint_plan.md` (1542 bytes): risky text pattern `token`
- `fingerprint_package/outputs/tables/fingerprint_matrix.csv` (7034 bytes): risky text pattern `token`
- `fingerprint_package/scripts/01_build_fingerprint_matrix.py` (6875 bytes): risky text pattern `token`
- `GITHUB_UPLOAD_PLAN.md` (1672 bytes): risky text pattern `token`; risky text pattern `credentials`
- `LOCAL_PROJECT_INVENTORY.md` (5590 bytes): risky text pattern `token`; risky text pattern `credentials`; risky text pattern `repair_deepseek`
- `RELEASE_CANDIDATE_MANIFEST.md` (4725 bytes): risky text pattern `credentials`; risky text pattern `raw output`; risky text pattern `confirmatory_trial_level.csv`
- `RELEASE_SAFETY_REPORT.md` (8702 bytes): risky text pattern `secret`; risky text pattern `token`; risky text pattern `credentials`; risky text pattern `raw output`; risky text pattern `method_trace`; risky text pattern `scenario_text`; risky text pattern `participant_prompt`; risky text pattern `C:/Users/`; risky text pattern `repair_deepseek`; risky text pattern `confirmatory_trial_level.csv`
- `RESULTS_FREEZE_20260530.md` (4059 bytes): risky text pattern `token`; risky text pattern `credentials`; risky text pattern `raw output`; risky text pattern `repair_deepseek`; risky text pattern `confirmatory_trial_level.csv`
- `VERIFICATION_REPORT_20260530.md` (13552 bytes): risky text pattern `secret`; risky text pattern `token`; risky text pattern `credentials`; risky text pattern `method_trace`; risky text pattern `scenario_text`; risky text pattern `participant_prompt`; risky text pattern `repair_deepseek`; risky text pattern `confirmatory_trial_level.csv`

## Scanned Files

| File | Size bytes | Warning count |
|---|---:|---:|
| `.gitignore` | 285 | 3 |
| `confirmatory_package/docs/analysis_plan.md` | 5083 | 1 |
| `confirmatory_package/docs/data_requirements.md` | 1957 | 3 |
| `confirmatory_package/docs/method_definitions.md` | 2446 | 0 |
| `confirmatory_package/docs/results_narrative.md` | 5750 | 2 |
| `confirmatory_package/outputs/figures/baseline_model_bias.pdf` | 15079 | 0 |
| `confirmatory_package/outputs/figures/baseline_model_bias.png` | 56783 | 0 |
| `confirmatory_package/outputs/figures/cost_effectiveness_scatter.pdf` | 16383 | 0 |
| `confirmatory_package/outputs/figures/cost_effectiveness_scatter.png` | 57105 | 0 |
| `confirmatory_package/outputs/figures/method_moral_bias_reduction.pdf` | 12547 | 0 |
| `confirmatory_package/outputs/figures/method_moral_bias_reduction.png` | 59984 | 0 |
| `confirmatory_package/outputs/figures/method_value_score_ranking.pdf` | 13055 | 0 |
| `confirmatory_package/outputs/figures/method_value_score_ranking.png` | 34203 | 0 |
| `confirmatory_package/outputs/figures/model_method_heatmap.pdf` | 21560 | 0 |
| `confirmatory_package/outputs/figures/model_method_heatmap.png` | 93371 | 0 |
| `confirmatory_package/outputs/model_dataset_method_heterogeneity_summary.md` | 10513 | 1 |
| `confirmatory_package/outputs/public_summary/public_figure_manifest.csv` | 2497 | 0 |
| `confirmatory_package/outputs/public_summary/public_fingerprint_matrix.csv` | 6613 | 1 |
| `confirmatory_package/outputs/public_summary/public_moral_model_dataset_method_summary.csv` | 6029 | 1 |
| `confirmatory_package/outputs/public_summary/public_summary_build_report.md` | 749 | 2 |
| `confirmatory_package/outputs/public_summary/public_sycophancy_model_dataset_method_summary.csv` | 823 | 1 |
| `confirmatory_package/outputs/tables/confirmatory_dataset_cell_summary.csv` | 3506 | 0 |
| `confirmatory_package/outputs/tables/cost_summary.csv` | 4329 | 1 |
| `confirmatory_package/outputs/tables/method_value_ranking.csv` | 10548 | 1 |
| `confirmatory_package/outputs/tables/model_dataset_method_heterogeneity_summary.csv` | 6382 | 1 |
| `confirmatory_package/outputs/tables/moral_bias_reductions.csv` | 9417 | 0 |
| `confirmatory_package/outputs/tables/moral_bias_summary.csv` | 6654 | 0 |
| `confirmatory_package/outputs/tables/sycophancy_summary.csv` | 441 | 0 |
| `confirmatory_package/scripts/01_inventory_results.py` | 6868 | 0 |
| `confirmatory_package/scripts/02_build_confirmatory_dataset.py` | 11227 | 2 |
| `confirmatory_package/scripts/03_confirmatory_analysis.py` | 13059 | 2 |
| `confirmatory_package/scripts/04_make_figures.py` | 4463 | 1 |
| `confirmatory_package/scripts/05_make_public_summary_tables.py` | 9649 | 3 |
| `confirmatory_package/scripts/06_make_heterogeneity_summary.py` | 5739 | 1 |
| `fingerprint_package/docs/fingerprint_plan.md` | 1542 | 1 |
| `fingerprint_package/outputs/figures/model_feature_heatmap.pdf` | 27366 | 0 |
| `fingerprint_package/outputs/figures/model_feature_heatmap.png` | 198242 | 0 |
| `fingerprint_package/outputs/figures/model_fingerprint_dendrogram.pdf` | 16602 | 0 |
| `fingerprint_package/outputs/figures/model_fingerprint_dendrogram.png` | 148447 | 0 |
| `fingerprint_package/outputs/figures/model_fingerprint_pca.pdf` | 18773 | 0 |
| `fingerprint_package/outputs/figures/model_fingerprint_pca.png` | 86779 | 0 |
| `fingerprint_package/outputs/tables/family_overlap_summary.csv` | 165 | 0 |
| `fingerprint_package/outputs/tables/feature_zscores.csv` | 5620 | 0 |
| `fingerprint_package/outputs/tables/fingerprint_matrix.csv` | 7034 | 1 |
| `fingerprint_package/outputs/tables/hierarchical_linkage.csv` | 956 | 0 |
| `fingerprint_package/outputs/tables/model_clusters.csv` | 1095 | 0 |
| `fingerprint_package/outputs/tables/model_metadata.csv` | 1451 | 0 |
| `fingerprint_package/outputs/tables/pca_components.csv` | 1238 | 0 |
| `fingerprint_package/scripts/01_build_fingerprint_matrix.py` | 6875 | 1 |
| `fingerprint_package/scripts/02_cluster_fingerprints.py` | 3997 | 0 |
| `fingerprint_package/scripts/03_plot_fingerprints.py` | 3354 | 0 |
| `GITHUB_UPLOAD_PLAN.md` | 1672 | 2 |
| `LOCAL_PROJECT_INVENTORY.md` | 5590 | 3 |
| `NEXT_COMMANDS.md` | 1806 | 0 |
| `README.md` | 8343 | 0 |
| `RELEASE_CANDIDATE_MANIFEST.md` | 4725 | 3 |
| `RELEASE_SAFETY_REPORT.md` | 8702 | 10 |
| `requirements.txt` | 133 | 0 |
| `RESULTS_FREEZE_20260530.md` | 4059 | 5 |
| `VERIFICATION_REPORT_20260530.md` | 13552 | 8 |