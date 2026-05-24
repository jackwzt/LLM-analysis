# Moral Bias and Inference-Time Debiasing Study

## Summary

This package evaluates whether inference-time interventions reduce moral framing bias and sycophancy in large language models. It builds on an OSF moral-framing replication workflow and extends it with multi-model API/local experiments, bias fingerprint analysis, and new debiasing methods.

Primary evaluated bias types:

- Moral yes-no framing bias
- Moral omission bias
- Sycophancy / wrong-belief agreement
- Polarity / negation sensitivity
- Debias responsiveness across model families

## Main Debiasing Methods

Baseline and previously tested methods:

- `standard`
- `debate`
- `critique_revise`
- `structured_cr`
- `checklist`
- `invariance_vote`

New inference-time methods from the latest pilot:

- `self_debias_reprompt`
- `counterfactual_consistency_vote`
- `constitutional_critic`
- `anti_sycophancy_truth_first`
- `frame_invariant_rationale`

The latest pilot selected three new methods for full confirmatory testing:

| Method | Main Role | Pilot Result |
| --- | --- | --- |
| `counterfactual_consistency_vote` | Strongest moral framing reduction | About 96% mean moral-bias reduction |
| `anti_sycophancy_truth_first` | Best cost-adjusted value | Low latency/token cost with strong sycophancy improvement |
| `constitutional_critic` | Stable general-purpose debiasing | Stronger effect than short rationale methods |

## Key Results

Important reports:

- [`reports/debias_method_pilot/debias_method_pilot_report.md`](reports/debias_method_pilot/debias_method_pilot_report.md)
- [`reports/deep_bias_regularities/deep_bias_regularities_report.md`](reports/deep_bias_regularities/deep_bias_regularities_report.md)
- [`reports/model_bias_fingerprint_eval/model_bias_fingerprint_report.md`](reports/model_bias_fingerprint_eval/model_bias_fingerprint_report.md)

High-level findings:

- DeepSeek V4-Pro and V4-Flash show strong moral framing sensitivity under standard prompting.
- `counterfactual_consistency_vote` was the strongest new method for moral framing.
- `anti_sycophancy_truth_first` had the best cost-adjusted score.
- Bias is multidimensional: moral framing, sycophancy, and polarity do not collapse into one universal model bias score.
- Model-specific item/bias fingerprints remain visible after accounting for global response bias and stimulus effects.

## Reproduction

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
```

Run a smoke test with dry outputs:

```powershell
.\.venv\Scripts\python.exe scripts\run_experiment.py --phase smoke --datasets exp2 sycophancy --methods standard counterfactual_consistency_vote --dry-run --output-name smoke_dryrun
```

Run an API pilot with an OpenAI-compatible provider:

```powershell
$env:OPENAI_COMPATIBLE_API_KEY = "<your-api-key>"
.\.venv\Scripts\python.exe scripts\run_experiment.py `
  --phase pilot `
  --datasets exp2 exp3 sycophancy `
  --methods standard debate critique_revise counterfactual_consistency_vote anti_sycophancy_truth_first constitutional_critic `
  --provider openai_compatible `
  --api-base-url https://api.deepseek.com `
  --api-model-id deepseek-v4-flash `
  --api-extra-body-file configs\deepseek_v4_non_thinking.json `
  --output-name pilot_deepseek_v4flash_confirmatory `
  --resume
```

Analyze the latest debias method pilot:

```powershell
.\.venv\Scripts\python.exe scripts\analyze_debias_method_pilot.py
```

Analyze model fingerprints:

```powershell
.\.venv\Scripts\python.exe scripts\analyze_model_bias_fingerprints.py
.\.venv\Scripts\python.exe scripts\analyze_deep_bias_regularities.py
```

## Data Policy

This public package includes benchmark stimuli, method code, configs without secrets, and aggregate reports. It excludes:

- API keys
- `logs/`
- raw run directories
- large trial-level exports
- model checkpoints and adapters

See `PACKAGE_NOTE.txt` for the local source path used when this package was prepared.

