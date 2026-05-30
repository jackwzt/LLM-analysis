# Qwen3 Moral Bias Evaluation

This project reproduces the model-level framing-bias workflow from the OSF archive in this workspace and adapts it to a local `Qwen/Qwen3-32B` experiment with multiple inference-time debiasing methods.

Supported method conditions:

- `standard`
- `debate`
- `checklist`
- `critique_revise`
- `invariance_vote`

Supported datasets:

- `exp2`
- `exp3`
- `sycophancy`

The implementation is designed for local NVIDIA GPUs and API-backed models, while preserving the original `Exp2` and `Exp3` model-level materials from the archive.

## What This Project Includes

- Extraction of `Exp2` and `Exp3` participant prompts and framing-manipulated vignettes from the OSF zip files.
- A local Qwen runner that supports:
  - `Qwen/Qwen3-32B-AWQ`
  - fallback to `Qwen/Qwen3-32B` with 4-bit `bitsandbytes`
- Sequential four-role debate orchestration:
  - `Rational Analyst`
  - `Intuitive Humanist`
  - `Devil's Advocate`
  - `Moderator`
- Additional inference-time methods:
  - `checklist`
  - `critique_revise`
  - `invariance_vote`
- A built-in `sycophancy` benchmark with aligned vs. belief-conflict factual questions.
- Trial-level logging with parsed answers, validity flags, and framing-invariant choice recoding.
- An R analysis script that recreates the archive-style summaries, adds sycophancy metrics, and writes a composite method ranking.

## Project Layout

```text
qwen3-moral-bias/
  configs/
  data/
    derived/
  logs/
  results/
  scripts/
  src/
```

## Setup

Run the Windows bootstrap script from PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap_windows.ps1
```

The bootstrap script will:

1. Install Python 3.12 if missing.
2. Create `.venv312`.
3. Install Python dependencies.
4. Try to install R if `Rscript` is unavailable.
5. Install required R packages once `Rscript` is available.

## Extract Stimuli

```powershell
.\.venv312\Scripts\python.exe .\scripts\extract_stimuli.py
```

This writes `data\derived\stimuli.csv`.

## Run the Experiment

Smoke test:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase smoke
```

Smoke test with all methods on moral + sycophancy tasks:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase smoke --datasets exp2 exp3 sycophancy --methods standard debate checklist critique_revise invariance_vote
```

Pilot:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase pilot
```

Full `Exp2` run:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase full --datasets exp2
```

Full `Exp2 + Exp3` run:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase full --datasets exp2 exp3
```

API-first pilot across moral framing and sycophancy:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase pilot --datasets exp2 exp3 sycophancy --methods standard debate checklist critique_revise invariance_vote --provider openai_compatible --api-base-url https://dashscope.aliyuncs.com/compatible-mode/v1 --api-model-id qwen3.6-plus --api-disable-thinking --output-name pilot_api_debias_suite
```

Local Gemma 4 31B 4-bit run:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase smoke --datasets exp2 --provider gemma
```

OpenAI-compatible API run:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase full --datasets exp3 --provider openai_compatible --api-base-url https://dashscope.aliyuncs.com/compatible-mode/v1 --api-model-id qwen3.6-plus --api-disable-thinking
```

The OpenAI-compatible provider supports conservative retry and throttling settings from `configs/experiment.default.json`. For rate-limited providers, the default configuration now uses:

- `max_retries = 6`
- `retry_base_delay_seconds = 2`
- `retry_max_delay_seconds = 60`
- `min_request_interval_seconds = 1.5`

For Zhipu or other aggressively rate-limited providers, use the stricter preset:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --config .\configs\experiment.zhipu.json --phase full --datasets exp2 --provider openai_compatible --api-base-url https://open.bigmodel.cn/api/paas/v4/ --api-model-id glm-5.1 --api-extra-body-file .\configs\zhipu.disable_thinking.json --output-name full_exp2_zhipu_glm51 --resume
```

For Gemini 2.5 Flash, use the Gemini preset so the OpenAI-compatible client omits unsupported fields such as `seed`:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --config .\configs\experiment.gemini.json --phase smoke --datasets exp2 --provider openai_compatible --api-base-url https://generativelanguage.googleapis.com/v1beta/openai/ --api-model-id gemini-2.5-flash --api-extra-body-file .\configs\gemini.disable_thinking.json --output-name smoke_exp2_gemini25flash
```

For NVIDIA-hosted KIMI K2.5, use the NVIDIA preset and disable KIMI thinking through `chat_template_kwargs`; otherwise the model may spend the completion budget on hidden reasoning and return `content=null`:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --config .\configs\experiment.nvidia_kimi25.json --phase smoke --datasets exp2 --methods standard --provider openai_compatible --api-base-url https://integrate.api.nvidia.com/v1 --api-model-id moonshotai/kimi-k2.5 --api-extra-body-file .\configs\nvidia.kimi25.instant.json --output-name smoke_exp2_nvidia_kimi25
```

Export `critique_revise` teacher outputs to SFT JSONL for distillation:

```powershell
.\.venv312\Scripts\python.exe .\scripts\export_distillation_jsonl.py --input .\results\<run_name>\raw_trials.csv --output-dir .\data\distillation\<dataset_name> --method critique_revise
```

Resume an interrupted run:

```powershell
.\.venv312\Scripts\python.exe .\scripts\run_experiment.py --phase full --datasets exp2 --output-name full_exp2_qwen --resume
```

Each run directory also writes `progress.json` alongside `raw_trials.csv`.

Report progress only when a new `200`-trial milestone is reached:

```powershell
.\.venv312\Scripts\python.exe .\scripts\check_progress.py --run-name full_exp3_deepseek --milestone-size 200
```

Print the current progress even when no new milestone was reached:

```powershell
.\.venv312\Scripts\python.exe .\scripts\check_progress.py --run-name full_exp3_deepseek --milestone-size 200 --print-current
```

The script stores the last reported milestone in `results\<run_name>\milestone_state.json`.

## Analyze Results

```powershell
Rscript .\scripts\analyze_results.R .\results\<run_name>\raw_trials.csv .\results\<run_name>\analysis
```

The analysis directory now includes:

- `bias_summary.csv`
- `sycophancy_summary.csv`
- `composite_ranking.csv`
- `winner_report.md`

## Notes

- Qwen3 runs with `enable_thinking=False` in both conditions so that the treatment effect comes from the debate intervention rather than Qwen's native thinking mode.
- For `Exp2`, the framing-invariant outcome follows the archive logic and tracks endorsement of the consequentialist / CBR-consistent option.
- For `Exp3`, the framing-invariant outcome tracks endorsement of the original action across `original`, `yesno`, and `omission` variants.

## Clean Local Analysis Packages

This repository now includes two local-only analysis layers that read existing outputs and write derived files without modifying raw `results/` data.

Confirmatory package:

```powershell
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\01_inventory_results.py
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\02_build_confirmatory_dataset.py
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\03_confirmatory_analysis.py
.\.venv312\Scripts\python.exe .\confirmatory_package\scripts\04_make_figures.py
```

The confirmatory package focuses on `standard`, `counterfactual_consistency_vote`, `anti_sycophancy_truth_first`, and `debate`.

Exploratory fingerprint package:

```powershell
.\.venv312\Scripts\python.exe .\fingerprint_package\scripts\01_build_fingerprint_matrix.py
.\.venv312\Scripts\python.exe .\fingerprint_package\scripts\02_cluster_fingerprints.py
.\.venv312\Scripts\python.exe .\fingerprint_package\scripts\03_plot_fingerprints.py
```

The fingerprint package is exploratory and should not be used alone for confirmatory model-family claims.
