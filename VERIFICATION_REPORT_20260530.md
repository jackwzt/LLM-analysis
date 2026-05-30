# Verification Report 2026-05-30

## Summary Verdict

Status: `PASS_WITH_NOTE`

The local repair and rebuild are confirmed. The DeepSeek V4-Flash `anti_sycophancy_truth_first` repair run exists, completed `2,881 / 2,881`, and the repaired rows are `100%` valid. The rebuilt confirmatory outputs and fingerprint outputs are present, and the expected DeepSeek V4-Flash numerical results match the current summary tables.

Main note: after the repair, the main confirmatory full-cell subset is now `42,912` rows rather than the earlier expected `39,744` rows. This is expected because the repaired `anti_sycophancy_truth_first` full cells for `exp2`, `exp3`, and `sycophancy` are now included. The moral summary now has `38` rows rather than `36` rows for the same reason.

No external APIs were called during this verification. No experiments were rerun. No raw data were deleted, overwritten, or repaired.

## Files and Folders Checked

Status: `PASS`

Checked project root files and folders:

| Path | Status | Type | Last modified |
|---|---:|---|---|
| `LOCAL_PROJECT_INVENTORY.md` | `PASS` | file | 2026-05-30 16:37:13 |
| `confirmatory_package/` | `PASS` | directory | 2026-05-30 16:37:13 |
| `fingerprint_package/` | `PASS` | directory | 2026-05-30 16:37:13 |
| `GITHUB_UPLOAD_PLAN.md` | `PASS` | file | 2026-05-30 16:37:13 |
| `.gitignore` | `PASS` | file | 2026-05-30 16:37:13 |
| `README.md` | `PASS` | file | 2026-05-30 16:42:31 |

Expected rebuilt output locations also exist:

- `confirmatory_package/outputs/confirmatory_trial_level.csv`
- `confirmatory_package/outputs/tables/`
- `confirmatory_package/outputs/figures/`
- `fingerprint_package/outputs/tables/`
- `fingerprint_package/outputs/figures/`

## Repair Verification

Status: `PASS`

Repair run path:

`results/repair_deepseek_v4flash_anti_sycophancy_valid_only_20260530`

Key files:

| File | Status | Size | Last modified |
|---|---:|---:|---|
| `progress.json` | `PASS` | 159 bytes | 2026-05-30 18:33:46 |
| `raw_trials.csv` | `PASS` | 10,988,683 bytes | 2026-05-30 18:33:46 |

`progress.json` shows:

```json
{
  "completed_trials": 2881,
  "expected_trials": 2881,
  "completion_rate": 1.0,
  "last_note": "run complete",
  "updated_at": "2026-05-30T18:33:46"
}
```

Repair raw row validity:

| Dataset | Method | Rows | Valid | Valid rate |
|---|---|---:|---:|---:|
| `exp2` | `anti_sycophancy_truth_first` | 1008 | 1008 | 1.000 |
| `exp3` | `anti_sycophancy_truth_first` | 1008 | 1008 | 1.000 |
| `sycophancy` | `anti_sycophancy_truth_first` | 865 | 865 | 1.000 |

Note: the repair raw file contains `865` sycophancy rows because `287` valid sycophancy rows already existed in the base run. After merging/rebuilding, the confirmatory dataset contains the full `1152 / 1152` sycophancy cell.

## Confirmatory Dataset Verification

Status: `PASS_WITH_NOTE`

Dataset path:

`confirmatory_package/outputs/confirmatory_trial_level.csv`

Observed table structure:

- Pandas row count: `48,130`
- Column count: `63`
- Unique models: `aliyun_qwen36`, `deepseek_chat`, `deepseek_v4flash`, `deepseek_v4pro`, `gemini25_flash`, `gemma4_31b`, `gemma4_e4b_base`, `qwen3_32b_awq`, `qwen3_4b_base`, `qwen3_8b_base`, `zhipu_glm51`
- Unique datasets: `exp2`, `exp3`, `sycophancy`
- Unique method conditions: `anti_sycophancy_truth_first`, `counterfactual_consistency_vote`, `debate`, `standard`
- `anti_sycophancy_truth_first` appears: yes
- DeepSeek V4-Flash appears as `deepseek_v4flash`: yes
- `exp2`, `exp3`, and `sycophancy` appear: yes
- Full-cell indicator exists: `analysis_tier`

Main confirmatory full-cell subset:

- Observed: `42,912` rows
- Expected earlier: approximately `39,744` rows
- Status: `PASS_WITH_NOTE`
- Explanation: the full-cell subset increased after the repaired `anti_sycophancy_truth_first` cells were included.

Raw output columns are present:

- `raw_final_output`
- `final_raw_output`
- `method_trace_json`
- `scenario_text`
- `participant_prompt`

GitHub safety status for this file: `WARNING`

This file is not safe for routine GitHub upload. It contains raw model outputs, full scenario text, participant prompts, and method traces with provider response metadata. Keep it local unless a separate redaction/export step is performed.

## DeepSeek V4-Flash Anti Full-Cell Verification

Status: `PASS`

Filter:

- `model_id = deepseek_v4flash`
- `method_condition = anti_sycophancy_truth_first`
- datasets: `exp2`, `exp3`, `sycophancy`

Observed confirmatory dataset cells:

| Dataset | Rows | Valid | Valid rate | Analysis tier | Full cell? |
|---|---:|---:|---:|---|---|
| `exp2` | 1008 | 1008 | 1.000 | `confirmatory_full_cell` | yes |
| `exp3` | 1008 | 1008 | 1.000 | `confirmatory_full_cell` | yes |
| `sycophancy` | 1152 | 1152 | 1.000 | `confirmatory_full_cell` | yes |

This confirms that `anti_sycophancy_truth_first` is now included in the DeepSeek V4-Flash full-valid confirmatory cells.

## Moral Summary Verification

Status: `PASS_WITH_NOTE`

Moral summary path:

`confirmatory_package/outputs/tables/moral_bias_summary.csv`

Observed:

- Row count: `38`
- Expected earlier: `36`
- Status: `PASS_WITH_NOTE`
- Explanation: two new rows were added for DeepSeek V4-Flash `anti_sycophancy_truth_first` on `exp2` and `exp3`.
- Models covered: `aliyun_qwen36`, `deepseek_chat`, `deepseek_v4flash`, `gemini25_flash`, `gemma4_31b`, `gemma4_e4b_base`, `qwen3_32b_awq`, `qwen3_4b_base`, `qwen3_8b_base`, `zhipu_glm51`
- Methods covered: `anti_sycophancy_truth_first`, `counterfactual_consistency_vote`, `debate`, `standard`
- Datasets covered: `exp2`, `exp3`
- Includes `anti_sycophancy_truth_first`: yes
- Includes DeepSeek V4-Flash: yes
- Includes standard baseline rows: yes

DeepSeek V4-Flash moral results:

| Dataset | Method | Observed moral bias mean | Expected |
|---|---|---:|---:|
| `exp2` | `standard` | 0.666667 | approx. 0.667 |
| `exp2` | `anti_sycophancy_truth_first` | 0.366071 | approx. 0.366 |
| `exp3` | `standard` | 0.763393 | approx. 0.763 |
| `exp3` | `anti_sycophancy_truth_first` | 0.275298 | approx. 0.275 |

Reduction table path:

`confirmatory_package/outputs/tables/moral_bias_reductions.csv`

DeepSeek V4-Flash reductions:

| Dataset | Standard | Anti | Absolute reduction | Percent reduction | Expected |
|---|---:|---:|---:|---:|---:|
| `exp2` | 0.666667 | 0.366071 | 0.300595 | 45.089% | approx. 45.1% |
| `exp3` | 0.763393 | 0.275298 | 0.488095 | 63.938% | approx. 63.9% |

The expected numerical results match within rounding.

## Sycophancy Summary Verification

Status: `PASS`

Sycophancy summary path:

`confirmatory_package/outputs/tables/sycophancy_summary.csv`

Observed:

- Row count: `4`
- Models covered: `deepseek_chat`, `deepseek_v4flash`
- Methods covered: `anti_sycophancy_truth_first`, `debate`, `standard`
- Includes `anti_sycophancy_truth_first`: yes
- Includes DeepSeek V4-Flash: yes

DeepSeek V4-Flash sycophancy results:

| Method | Trials | Accuracy | Conflict accuracy | Aligned accuracy | Wrong-belief agreement |
|---|---:|---:|---:|---:|---:|
| `standard` | 1152 | 0.984375 | 1.000 | 0.968750 | 0.000 |
| `anti_sycophancy_truth_first` | 1152 | 0.989583 | 1.000 | 0.979167 | 0.000 |
| `debate` | 1152 | 0.981771 | 1.000 | 0.963542 | 0.000 |

Expected values match:

- Standard wrong-belief agreement: observed `0.000`, expected approx. `0.000`
- Anti wrong-belief agreement: observed `0.000`, expected approx. `0.000`
- Standard accuracy: observed `0.984375`, expected approx. `0.984`
- Anti accuracy: observed `0.989583`, expected approx. `0.990`

Interpretation status: `PASS_WITH_NOTE`

This indicates a floor effect for DeepSeek V4-Flash wrong-belief agreement on this sycophancy set: the baseline is already `0.000`, so `anti_sycophancy_truth_first` cannot reduce it further on this metric. The small accuracy increase is still visible.

## Cost Summary Verification

Status: `PASS`

Cost summary path:

`confirmatory_package/outputs/tables/cost_summary.csv`

Value ranking path:

`confirmatory_package/outputs/tables/method_value_ranking.csv`

Observed DeepSeek V4-Flash `anti_sycophancy_truth_first` cost multipliers:

| Dataset | Latency multiplier vs standard | Expected | Token multiplier vs standard | Expected |
|---|---:|---:|---:|---:|
| `exp2` | 2.398560 | approx. 2.40x | 1.160444 | approx. 1.16x |
| `exp3` | 2.006972 | approx. 2.01x | 1.176600 | approx. 1.18x |

Expected values match within rounding.

## Figure Verification

Status: `PASS`

Confirmatory figures present:

| Figure | Type covered | Last modified |
|---|---|---|
| `baseline_model_bias.png` / `.pdf` | baseline bias | 2026-05-30 19:02:27 |
| `method_moral_bias_reduction.png` / `.pdf` | method reduction | 2026-05-30 19:02:28 |
| `cost_effectiveness_scatter.png` / `.pdf` | cost-effectiveness | 2026-05-30 19:02:28 |
| `model_method_heatmap.png` / `.pdf` | model-method heatmap | 2026-05-30 19:02:28 |
| `method_value_score_ranking.png` / `.pdf` | value-score ranking | 2026-05-30 19:02:28 |

Fingerprint figures present:

| Figure | Type covered | Last modified |
|---|---|---|
| `model_feature_heatmap.png` / `.pdf` | fingerprint heatmap | 2026-05-30 19:02:32 |
| `model_fingerprint_dendrogram.png` / `.pdf` | dendrogram | 2026-05-30 19:02:32 |
| `model_fingerprint_pca.png` / `.pdf` | PCA | 2026-05-30 19:02:33 |

## Fingerprint Matrix Verification

Status: `PASS_WITH_NOTE`

Fingerprint matrix path:

`fingerprint_package/outputs/tables/fingerprint_matrix.csv`

Observed:

- Row count: `21`
- Number of models: `21`
- Numeric feature count: `26`
- Expected: approximately `21 models x 24 numeric features`
- Status: `PASS_WITH_NOTE`

The model count matches. The numeric feature count is higher than expected because the rebuilt matrix now includes additional derived features, including `anti_sycophancy_truth_first_reduction` and value/cost-related numeric fields.

Model families present:

- `DeepSeek`
- `GLM`
- `Gemini/Gemma`
- `Qwen`
- `unknown`

This is sufficient for exploratory fingerprinting, but model-family conclusions should remain cautious because some families still have few models or mixed local/API provenance.

## GitHub Upload Safety Check

Status: `WARNING`

`.gitignore` currently excludes:

- `.env` and `.env.*`
- `*.key`
- `*.pem`
- `secrets*`
- `credentials*`
- token-like filename patterns
- virtual environments
- Python caches
- `logs/` and `*.log`
- raw API log folders
- `models/`
- common model checkpoint extensions
- cache and temp folders

Remaining risks:

- `results/` is not globally ignored.
- `confirmatory_package/outputs/confirmatory_trial_level.csv` is not ignored.
- repair raw files such as `results/repair_deepseek_v4flash_anti_sycophancy_valid_only_20260530/raw_trials.csv` are not ignored.
- `confirmatory_trial_level.csv` contains raw model outputs, scenario text, participant prompts, and `method_trace_json`.
- `method_trace_json` contains raw provider metadata such as response IDs, usage details, and system fingerprints.
- The output CSV is large, about `199 MB`.

Credential scan status: `PASS_WITH_NOTE`

A simple pattern scan over the docs/packages did not show an obvious API key in the inspected outputs, but raw model-output CSVs triggered false-positive text matches because they contain words like `risk-averse` and extensive raw traces. This reinforces the recommendation not to upload raw trial-level CSVs.

Recommendation:

- Keep `confirmatory_trial_level.csv` local.
- Keep all `results/*/raw_trials.csv` and repair raw files local.
- Upload scripts, docs, compact summary tables, and figures only after a final manual review.

## Remaining Issues or Inconsistencies

Status: `PASS_WITH_NOTE`

- The expected main confirmatory full-cell subset was approximately `39,744`; observed is `42,912` after anti repair inclusion. This is not a failure.
- The expected moral summary was `36` rows; observed is `38` rows after adding DeepSeek V4-Flash anti rows. This is not a failure.
- The expected fingerprint numeric feature count was around `24`; observed is `26`. This is not a failure, but should be documented if reporting matrix shape.
- DeepSeek V4-Flash `counterfactual_consistency_vote` remains low-valid/partial in the current confirmatory dataset and is not treated as a full-cell confirmatory result for V4-Flash.
- DeepSeek V4-Pro remains partial/low-valid in this package and should not be treated as confirmatory.
- Sycophancy wrong-belief agreement for V4-Flash has a floor effect at baseline.

## Recommended Next Step

Status: `PASS_WITH_NOTE`

For GitHub-safe release preparation:

1. Keep raw trial-level and repair CSV files local.
2. Upload only docs, scripts, compact summary tables, and figures.
3. Consider adding explicit ignore patterns for `results/`, `confirmatory_package/outputs/confirmatory_trial_level.csv`, and other large raw CSV files before staging anything.
4. If a public trial-level sample is needed, create a separate redacted export that drops `raw_final_output`, `final_raw_output`, `method_trace_json`, `scenario_text`, and `participant_prompt`.
5. Do not make strong family-level fingerprint claims without labeling them exploratory.

## Final Concise Status

- Repair confirmed: `PASS`
- `anti_sycophancy_truth_first` included in DeepSeek V4-Flash confirmatory full cells: `PASS`
- Rebuilt confirmatory outputs present: `PASS`
- Expected numerical results match: `PASS`
- Figures regenerated: `PASS`
- Fingerprint outputs present: `PASS_WITH_NOTE`
- GitHub-safe release ready: `WARNING`; scripts/docs/figures/summary tables are close, but raw trial-level CSVs require manual exclusion or redaction.
