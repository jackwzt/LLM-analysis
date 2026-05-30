# Exploratory Model-Family Fingerprint Plan

## Goal

This package explores whether models cluster by bias-response profile and whether those clusters align with model family, training stage, provider, or local/API status.

This analysis is exploratory. It should generate hypotheses rather than make strong confirmatory claims.

## Model Families of Interest

- Qwen
- Gemini / Gemma
- GLM
- DeepSeek
- local small models

The scripts inspect which models actually exist in the local data. Missing metadata are marked as `unknown`.

## Candidate Features

- `baseline_moral_bias_mean`
- `yes_no_gap`
- `omission_gap`
- `sycophancy_wrong_belief_rate`
- `sycophancy_accuracy`
- `polarity_gap_abs`
- `counterfactual_consistency_vote_reduction`
- `anti_sycophancy_truth_first_reduction`
- `debate_reduction`
- `critique_revise_reduction`
- `latency_multiplier_counterfactual`
- `token_multiplier_counterfactual`
- `latency_multiplier_debate`
- `token_multiplier_debate`
- `best_value_score`
- `method_sensitivity_sd`
- `cross_dataset_stability`

## Planned Analyses

- z-score standardization of available features.
- hierarchical clustering with correlation or cosine distance where possible.
- PCA if enough models and features exist.
- model-by-feature heatmap.
- dendrogram.
- PCA scatter plot.
- cluster summary table.
- family-overlap summary when there are enough models per family.

## Limitations

Do not make strong model-family claims if each family has only one or two models. In that case, clustering is hypothesis-generating only.
