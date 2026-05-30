# Confirmatory Analysis Plan

## Narrowed Research Question

Do selected inference-time interventions reliably reduce moral framing bias in large language models, and are these reductions cost-effective when latency and token cost are considered?

## Primary Methods

- `standard`: direct-answer baseline.
- `counterfactual_consistency_vote`: expected strongest moral-framing intervention because it explicitly queries framing variants and aggregates the invariant judgment.
- `anti_sycophancy_truth_first`: expected best low-cost practical intervention, especially for user-belief and sycophancy settings.
- `debate`: high-cost deliberative comparator using multi-role reasoning.

## Secondary Methods

The following methods are supplementary unless available data make a stronger comparison possible:

- `constitutional_critic`
- `critique_revise`
- `self_debias_reprompt`
- `frame_invariant_rationale`
- `checklist`
- `invariance_vote`

## Primary Hypotheses

- H1: `counterfactual_consistency_vote` reduces moral framing bias relative to `standard`.
- H2: `anti_sycophancy_truth_first` provides the best cost-adjusted value among the primary intervention methods.
- H3: `debate` reduces moral framing bias relative to `standard`, but is less cost-effective because of higher latency and token cost.
- H4: Debiasing effectiveness varies by model, producing a method-by-model interaction.

## Secondary Hypotheses

- Methods that explicitly compare counterfactual framings will reduce yes-no and omission gaps more than single-call instruction methods.
- Truth-first instruction will reduce wrong-belief agreement more cost-effectively than multi-role debate.
- Method rankings will differ across model families and deployment types.

## Model Inclusion Criteria

Primary confirmatory tables should include model-method-dataset cells that meet all of the following:

- Trial-level rows exist locally.
- The run tier is `full` or otherwise clearly marked as confirmatory.
- Required columns for framing analysis are present.
- Valid response rate is high enough for the intended comparison, ideally at least 95%.
- The model and method cell has enough item-family coverage to estimate framing gaps.

Smoke, pilot, partial, and repair-in-progress cells may be kept in candidate datasets but must be marked exploratory.

## Dataset Inclusion Criteria

Primary moral-framing analysis uses:

- `exp2`
- `exp3`

Sycophancy analysis uses:

- `sycophancy`

Generated and polarity datasets are secondary or exploratory unless a complete and clean confirmatory matrix is available.

## Outcome Variables

Primary moral outcomes:

- yes-no bias gap: absolute difference between original and yes-no endorsement of the invariant/original action.
- omission bias gap: absolute difference between original and omission endorsement of the invariant/original action.
- moral bias mean: mean of yes-no and omission gaps.

Sycophancy outcomes:

- factual accuracy.
- wrong-belief agreement rate.
- aligned and conflict accuracy when labels are available.

Cost outcomes:

- median latency.
- median prompt tokens.
- median completion tokens.
- median total tokens.
- method cost multiplier relative to `standard`.
- value score combining bias reduction and token or latency multiplier.

## Invalid-Response Handling

Only unambiguous `Final answer: Yes` or `Final answer: No` rows are treated as valid. Invalid rows remain in the candidate dataset for audit but are excluded from primary effect estimates. If repair runs exist, valid repair rows can replace invalid base rows only in a derived clean dataset; raw files must not be overwritten.

## Statistical Models

Preferred trial-level model, if item-level binary targets are available:

`answer_matches_invariant_target ~ method_condition * model_id + dataset + random intercept for item_family_id or item_id`

For moral framing, objective correctness is not available, so the confirmatory fallback is item-family bootstrap over framing-gap metrics:

- compute endorsement rate per model, dataset, item family, method, and framing.
- compute yes-no and omission gaps per item family.
- aggregate gaps by model, dataset, and method.
- bootstrap item families to estimate uncertainty intervals.

If only aggregate data are available, the analysis must be labeled aggregate-level and limited.

## Planned Plots

- Baseline model-bias comparison plot.
- Method-level moral-bias reduction plot.
- Cost-effectiveness scatter plot.
- Model-by-method heatmap.
- Method value-score ranking plot.

## Limitations

- Moral tasks measure framing invariance, not moral correctness.
- `counterfactual_consistency_vote` enforces consistency by design, so its effect should be interpreted as an inference-time consistency procedure, not proof that the base model internally became unbiased.
- Some models may have incomplete or repaired data; those cells must be labeled.
- Token and latency costs can vary by provider, time, rate limits, and hidden reasoning settings.
- Model-family claims require enough models per family; otherwise they remain exploratory.
