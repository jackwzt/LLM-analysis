# Public Summary Build Report

Status: generated GitHub-safe public summary tables from aggregate outputs.

Excluded by design:

- raw model outputs
- scenario text
- participant prompts
- method traces
- provider metadata
- raw API responses
- API keys or credentials
- local private paths

Generated files:

- `public_moral_model_dataset_method_summary.csv`: 38 rows
- `public_sycophancy_model_dataset_method_summary.csv`: 4 rows
- `public_fingerprint_matrix.csv`: 21 rows
- `public_figure_manifest.csv`: 16 rows

Notes:

- `confirmatory_trial_level.csv` is intentionally not copied into the public summary folder.
- Public tables are aggregate/model-level only.
- Manual review is still recommended before GitHub upload.