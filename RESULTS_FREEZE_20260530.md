# Results Freeze 2026-05-30

## Freeze Metadata

- Freeze date: 2026-05-30
- Verification report: `VERIFICATION_REPORT_20260530.md`
- Project root: `<LOCAL_PROJECT_ROOT>`
- Freeze status: verified local state after DeepSeek V4-Flash `anti_sycophancy_truth_first` repair and analysis rebuild.

## Repair Status

- Repair run path: `results/repair_deepseek_v4flash_anti_sycophancy_valid_only_20260530`
- Repair target: DeepSeek V4-Flash `anti_sycophancy_truth_first` for `exp2`, `exp3`, and `sycophancy`
- Completion: `2,881 / 2,881`
- Repair valid rate: `100%`

Full-cell inclusion after repair:

| Dataset | Rows | Valid | Valid rate | Analysis tier |
|---|---:|---:|---:|---|
| `exp2` | 1008 | 1008 | 1.000 | `confirmatory_full_cell` |
| `exp3` | 1008 | 1008 | 1.000 | `confirmatory_full_cell` |
| `sycophancy` | 1152 | 1152 | 1.000 | `confirmatory_full_cell` |

## Frozen Dataset and Output Counts

- Confirmatory candidate dataset: approximately `48,130` rows.
- Current main confirmatory full-cell subset: `42,912` rows.
- Moral summary: `38` rows across `10` models.
- Fingerprint matrix: `21` models with `26` numeric features.

Note: earlier documents may mention `39,744` full-cell rows and `36` moral summary rows. Those values are superseded by this freeze because repaired `anti_sycophancy_truth_first` cells are now included.

## Method Sets

Primary method set:

- `standard`
- `counterfactual_consistency_vote`
- `anti_sycophancy_truth_first`
- `debate`

Secondary or supplementary methods:

- `constitutional_critic`
- `critique_revise`
- `self_debias_reprompt`
- `frame_invariant_rationale`
- `checklist`
- `invariance_vote`

## Key DeepSeek V4-Flash Results

Moral framing:

| Dataset | Standard moral bias mean | Anti-sycophancy truth-first moral bias mean | Reduction |
|---|---:|---:|---:|
| `exp2` | 0.667 | 0.366 | 45.1% |
| `exp3` | 0.763 | 0.275 | 63.9% |

Sycophancy:

| Metric | Standard | Anti-sycophancy truth-first |
|---|---:|---:|
| Wrong-belief agreement | 0.000 | 0.000 |
| Accuracy | 0.984 | 0.990 |

Cost:

| Dataset | Latency multiplier | Token multiplier |
|---|---:|---:|
| `exp2` | 2.40x | 1.16x |
| `exp3` | 2.01x | 1.18x |

## Interpretation Notes

- Sycophancy wrong-belief agreement has a floor effect for DeepSeek V4-Flash: the standard condition is already `0.000`, so the anti-sycophancy method cannot reduce it further on this metric.
- `counterfactual_consistency_vote` should be interpreted as output-level consistency enforcement. It can eliminate measured framing gaps by construction and should not be described as eliminating internal model bias.
- Moral tasks do not provide objective correctness labels; the confirmatory moral analysis uses framing-gap reduction, not moral accuracy.
- Fingerprint clustering is exploratory and does not yet justify strong model-family claims without more balanced model-family coverage.

## GitHub Upload Warning

Do not upload:

- `confirmatory_package/outputs/confirmatory_trial_level.csv`
- `results/*/raw_trials.csv`
- repair raw outputs
- logs
- raw API traces
- raw model outputs
- scenario-text or participant-prompt tables
- method trace tables
- provider metadata tables
- `.env`, credentials, API keys, or private tokens
- model checkpoints or local caches

`confirmatory_trial_level.csv` must remain local because it contains raw outputs, scenario text, participant prompts, method traces, and provider metadata.

## Recommended Public Upload Contents

Recommended for GitHub after manual review:

- source scripts
- `confirmatory_package/scripts/`
- `confirmatory_package/docs/`
- `confirmatory_package/outputs/public_summary/`
- compact summary tables from `confirmatory_package/outputs/tables/`
- safe figures from `confirmatory_package/outputs/figures/`
- `fingerprint_package/scripts/`
- `fingerprint_package/docs/`
- cleaned fingerprint summary tables
- safe fingerprint figures
- `LOCAL_PROJECT_INVENTORY.md`
- `VERIFICATION_REPORT_20260530.md`
- `RESULTS_FREEZE_20260530.md`
- `GITHUB_UPLOAD_PLAN.md`
- `README.md`
- `.gitignore`
- `requirements.txt`
