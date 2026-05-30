# Results Narrative

## Overview of Analysis Set

The candidate confirmatory dataset contains approximately 48,130 rows. The current main full-cell subset contains 42,912 rows after the valid-only repair of DeepSeek V4-Flash `anti_sycophancy_truth_first` cells. The main confirmatory package focuses on `standard`, `counterfactual_consistency_vote`, `anti_sycophancy_truth_first`, and `debate`.

Moral tasks do not have objective correctness labels. Therefore, the moral analysis estimates framing-gap reduction rather than moral accuracy. The central outcome is whether endorsement of the same underlying moral action changes across logically related framings.

## Validity and Repair Procedure

DeepSeek V4-Flash `anti_sycophancy_truth_first` initially had low-valid cells because the provider returned hidden reasoning rather than parseable final answers. A valid-only repair was completed under `results/repair_deepseek_v4flash_anti_sycophancy_valid_only_20260530`. The repair completed `2,881 / 2,881` assigned trials with `100%` validity.

After rebuilding, `anti_sycophancy_truth_first` enters full confirmatory analysis for DeepSeek V4-Flash on `exp2`, `exp3`, and `sycophancy`.

## Moral Framing Bias Results

The repaired DeepSeek V4-Flash results show that `anti_sycophancy_truth_first` reduces moral framing bias relative to `standard`.

For `exp2`, moral bias mean decreases from `0.667` under `standard` to `0.366` under `anti_sycophancy_truth_first`, a reduction of `45.1%`.

For `exp3`, moral bias mean decreases from `0.763` under `standard` to `0.275` under `anti_sycophancy_truth_first`, a reduction of `63.9%`.

These effects should be interpreted by model and dataset. They do not establish a universal effect across all LLMs.

## Anti-Sycophancy Truth-First Results

`anti_sycophancy_truth_first` is a low-cost single-call intervention that instructs the model to prioritize truth, stable principles, and disagreement with false user beliefs over social agreement. In DeepSeek V4-Flash, it produced substantial reductions in moral framing bias while maintaining high sycophancy accuracy.

On the sycophancy benchmark, wrong-belief agreement remained `0.000` for both `standard` and `anti_sycophancy_truth_first`. This is a floor effect: the baseline model already shows no wrong-belief agreement on this benchmark, so there is no room for improvement on that metric. Accuracy increased slightly from `0.984` to `0.990`.

## Counterfactual Consistency Vote Results

`counterfactual_consistency_vote` should be interpreted as output-level consistency enforcement. It queries multiple framing variants, maps answers to an invariant underlying judgment, and returns the majority invariant judgment or a resolution answer.

Because this method explicitly aggregates across framings, it can mechanically reduce measured framing gaps. It should not be described as eliminating internal model bias. It is best understood as an inference-time consistency-control procedure.

## Debate and Cost-Efficiency Results

`debate` remains a high-cost deliberative comparator. It can reduce moral framing bias for some models and datasets, including DeepSeek V4-Flash, but it generally has larger latency and token costs than single-call methods.

For DeepSeek V4-Flash, `anti_sycophancy_truth_first` is more cost-efficient than debate in the repaired cells. Its latency multiplier is approximately `2.40x` standard on `exp2` and `2.01x` standard on `exp3`, while token multipliers are approximately `1.16x` and `1.18x`.

## Sycophancy Results and Floor Effects

DeepSeek V4-Flash has a floor effect for wrong-belief agreement on the current sycophancy set. Both `standard` and `anti_sycophancy_truth_first` produce `0.000` wrong-belief agreement, while accuracy is already high. This means sycophancy conclusions for this model should emphasize maintenance of accuracy and lack of degradation, not further reduction in wrong-belief agreement.

## Cost Analysis

Cost analysis uses latency and token multipliers relative to `standard`. These are practical deployment metrics, not model-intrinsic properties. They can vary by provider load, caching, hidden reasoning settings, and API implementation.

The repaired DeepSeek V4-Flash `anti_sycophancy_truth_first` cells show moderate cost overhead and substantial moral-bias reductions, especially on `exp3`.

## Fingerprint Clustering Results

The fingerprint package contains an exploratory model-level fingerprint matrix and clustering outputs. These results are hypothesis-generating. They can suggest whether models differ by bias-response profile, but they do not yet justify strong model-family claims unless each family has enough models and comparable full-cell coverage.

## Limitations

- Moral tasks measure framing-gap reduction, not objective moral correctness.
- `counterfactual_consistency_vote` enforces consistency at inference time and should not be interpreted as internal debiasing.
- Some model-method cells remain partial or low-valid and should not be treated as confirmatory.
- Sycophancy wrong-belief agreement for DeepSeek V4-Flash is at floor.
- Cost metrics are provider- and run-condition-dependent.
- Fingerprint clustering remains exploratory.

## Interpretive Summary

The repaired analysis supports a cautious conclusion: selected inference-time interventions can reduce measured moral framing bias, but effects vary by model, dataset, and method. For DeepSeek V4-Flash, `anti_sycophancy_truth_first` now has full-valid confirmatory cells and shows meaningful moral-bias reduction with modest token overhead. `counterfactual_consistency_vote` remains powerful but should be framed as consistency enforcement rather than evidence of internal model-level debiasing.
