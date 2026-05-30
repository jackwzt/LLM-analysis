# Method Definitions

## Primary Methods

### `standard`

The direct-answer baseline condition. The model receives the participant-style prompt and scenario, then must produce a binary final answer in the required format.

### `counterfactual_consistency_vote`

A multi-variant consistency procedure. The method queries the model on counterfactual framing variants of the same underlying item, maps each answer to the invariant underlying judgment, and returns the majority invariant judgment. If the probes do not yield a clear majority, a resolution prompt asks the model to apply one invariant principle and produce a final answer.

Important interpretation: this method can mechanically reduce measured framing gaps because it enforces cross-framing aggregation at inference time. It should be interpreted as a consistency-control procedure, not as proof that the base model has no internal bias.

### `anti_sycophancy_truth_first`

A single-call instruction that prioritizes evidence, stable principles, and disagreement with false user beliefs over social agreement, user confidence, or rhetorical framing. It is designed as a low-cost practical intervention.

### `debate`

A multi-role deliberative prompting procedure. The standard role sequence is:

- Rational Analyst: logical consistency, invariance, and normative reasoning.
- Intuitive Humanist: harm, fairness, emotional salience, and human-like moral concern.
- Devil's Advocate: challenges assumptions and exposes framing-dependent inconsistencies.
- Moderator: synthesizes the prior roles and produces the final decision.

## Secondary Methods

### `constitutional_critic`

Uses a fixed principle list, such as truth over agreement and same moral facts imply same answer, to critique an initial response before returning a final answer.

### `critique_revise`

Generates an initial answer, critiques possible bias or inconsistency, and revises the final answer.

### `self_debias_reprompt`

Asks the model to diagnose whether its own answer may be biased by framing or user belief, then reprompts it to answer again.

### `frame_invariant_rationale`

Requires a concise invariant rule before the final answer. It tests whether a short principle-level rationale is enough to improve consistency.

### `checklist`

Uses a compact checklist of bias risks before final answering.

### `invariance_vote`

Uses repeated or variant-based answers to select a stable invariant judgment.
