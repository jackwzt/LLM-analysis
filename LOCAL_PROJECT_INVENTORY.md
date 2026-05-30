# Local Project Inventory

Generated for the local `qwen3-moral-bias` working directory. This inventory is descriptive and does not move, delete, or overwrite raw data.

## Project Root

The active local research project is:

`<LOCAL_PROJECT_ROOT>`

A separate cleaned Git repository also exists at:

`<GIT_REPO_ROOT>`

The active working directory contains the raw and derived experiment outputs needed for local confirmatory analysis, so the new analysis packages are created here first.

## Top-Level Structure

- `configs/`: model and provider configuration files, including local Qwen/Gemma configs and API-compatible provider presets.
- `data/`: derived stimuli, benchmark items, generated benchmark batches, and distillation datasets.
- `logs/`: local run logs. Treat as local-only because logs may contain provider traces or private paths.
- `models/`: local adapters/checkpoints and training artifacts. Treat as local-only unless intentionally releasing a model.
- `reports/`: aggregate reports, CSV summaries, model-family fingerprint outputs, and presentation/report artifacts.
- `results/`: trial-level run outputs, including `raw_trials.csv` and `progress.json` for individual runs.
- `scripts/`: experiment runners, analysis scripts, distillation utilities, and progress helpers.
- `src/`: reusable implementation for stimuli, generation backends, prompts, and debiasing methods.

## Available Datasets

- `exp2`: classic moral dilemmas with `original`, `yesno`, and `omission` framings.
- `exp3`: AITA-style moral dilemmas with the same framing structure.
- `sycophancy`: factual belief-aligned and belief-conflict items.
- `generated_moral`: generated external moral items.
- `generated_sycophancy`: generated external sycophancy items.
- `polarity_bias_items`: polarity/negation bias items used in exploratory fingerprint work.

## Available Trial-Level Results

The repository contains multiple `results/*/raw_trials.csv` files. Important examples include:

- `results/full_qwen3_4b_counterfactual_stability_20260530/raw_trials.csv`
- `results/full_gemma4_e4b_counterfactual_stability_20260530/raw_trials.csv`
- `results/full_qwen3_8b_counterfactual_stability_20260530/raw_trials.csv`
- `results/full_deepseek_v4flash_methods_recovered_20260530/raw_trials.csv`
- `results/repair_deepseek_v4flash_methods_valid_only_20260530/raw_trials.csv`
- earlier API/local pilot, smoke, and partial runs under `results/`

Some historical result directories are incomplete, exploratory, or damaged. For example, some DeepSeek V4 full raw files include NUL-byte corruption or low-valid rows caused by hidden thinking output consuming the token budget. These should be inventoried and clearly marked rather than silently used as confirmatory evidence.

## Available Aggregate Reports

Important aggregate outputs include:

- `reports/debias_method_pilot/`: pilot method comparison tables and recommended methods.
- `reports/model_bias_fingerprint_eval/`: earlier multi-model fingerprint and responsiveness summaries.
- `reports/deep_bias_regularities/`: long-format bias table, fingerprint matrix, clustering, variance, metadata regression, and cross-bias prediction outputs.
- `reports/gemma4_e4b_eval/`: Gemma E4B base vs SFT summary.
- `reports/structured_cr_confirmatory_eval/` and `reports/structured_cr_sft_eval/`: structured critique/revise analysis summaries.
- `reports/human_ai_moral_debiasing_2026-04-18/`: draft-style report and presentation materials.

## Available Scripts

- `scripts/run_experiment.py`: primary local/API experiment runner.
- `scripts/run_missing_trials.py`: missing-trial repair runner, now with `--target-valid-only`.
- `scripts/merge_repaired_trials.py`: merges valid base trials with valid repair trials.
- `scripts/analyze_debias_method_pilot.py`: pilot method comparison.
- `scripts/analyze_debias_method_confirmatory.py`: confirmatory-style method comparison.
- `scripts/analyze_deep_bias_regularities.py`: exploratory model-family/fingerprint analysis.
- `scripts/analyze_model_bias_fingerprints.py`: earlier fingerprint analysis workflow.
- `scripts/run_polarity_bias.py`: polarity-bias experiment runner.
- training/distillation scripts for Qwen/Gemma proof-of-concept adapters.

## Missing or Weak Pieces for Strong Confirmatory Analysis

- A fully clean, complete DeepSeek V4-Flash six-method matrix still needs the repair run to finish before it can be used as confirmatory.
- DeepSeek V4-Pro full rerun is partial and should remain exploratory unless completed cleanly.
- Several model-method combinations exist only as pilot/smoke/partial runs and should not be mixed into primary confirmatory claims.
- Some local stability runs compare only `standard` and `counterfactual_consistency_vote`, so they support a narrower method comparison than the API six-method matrix.
- Trial-level data include moral endorsements but not objective moral correctness labels; moral analysis should focus on framing invariance and bias gaps, not correctness.
- Sycophancy analysis is stronger where factual correctness labels and user-belief agreement columns are present.
- Logs, raw provider traces, credentials, API keys, and model checkpoints should remain local unless explicitly sanitized and intentionally released.

## New Clean Analysis Layers

This pass adds:

- `confirmatory_package/`: narrowed confirmatory analysis package.
- `fingerprint_package/`: exploratory model-family fingerprint package.

These folders are designed to read existing local outputs and write cleaned derived tables, figures, and documentation without modifying raw data.
