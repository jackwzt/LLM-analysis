# LLM Debiasing and Human Moral Judgment: A Two-Stage Study Plan

## Abstract
Large language models are increasingly used as advisors in morally relevant contexts, yet prior work suggests that LLM moral judgments can be sensitive to logically irrelevant framing. This project examines whether reducing model-level moral framing bias can improve the quality of AI advice that humans receive. Study 1 evaluates Qwen3-4B variants on omission bias, yes-no bias, sycophancy, validity, and latency. The expanded SFT adapter substantially reduces strict held-out moral bias compared with the base model, but robustness on generated external dilemmas remains limited. Study 2 is a planned human experiment testing whether exposure to debiased AI advice reduces human framing susceptibility and changes reliance patterns. The central contribution is to distinguish model-level debiasing from human-level transfer: a model can become more consistent on benchmark items without necessarily guaranteeing robust human-AI moral alignment.

## Introduction
LLMs are increasingly positioned as interactive advisors in personal, organizational, and societal decision contexts. Moral advice is especially sensitive because small wording changes can shift perceived agency, responsibility, harm, and fairness. Prior evidence indicates that LLMs can show systematic moral framing biases, including omission bias and yes-no bias. These biases matter not only as model artifacts, but also because AI-generated advice may shape how humans interpret moral problems.

This project reframes the current work as a human-AI moral judgment study. The model training experiments are not the endpoint. Instead, they produce two advice sources: a biased base model and a debiased expanded-SFT model. The planned human experiment then asks whether advice from the debiased model reduces human susceptibility to framing effects, or whether model-level improvements fail to transfer to human decision-making.

## Research Questions and Hypotheses
**RQ1, model level.** Can SFT-based debiasing reduce moral framing bias in LLM outputs compared with a base model?

**RQ2, human level.** Does exposure to debiased AI advice reduce humans' susceptibility to moral framing effects compared with exposure to base-model advice?

**RQ3, reliance.** Do people rely on debiased and biased AI advice differently, and do confidence/helpfulness ratings predict judgment shifts?

**H1.** The expanded SFT model will show lower omission bias and yes-no bias than the base model on original held-out moral dilemmas.

**H2.** Participants exposed to expanded-SFT advice will show smaller final-judgment framing gaps than participants exposed to base-model advice.

**H3.** Participants will align more with AI advice when they rate it as more helpful, confident, or trustworthy.

**H4.** Debiasing effects may not generalize equally to generated external dilemmas, so human-level effects may be stronger for original-style dilemmas than novel generated dilemmas.

## Study 1: Model-Level Debiasing
### Method
Study 1 compared Qwen3-4B variants under a strict output rule requiring a binary final answer. The primary comparison was between the base model and the expanded SFT adapter. The old short-reason adapter and expanded SFT+DPO adapter were retained as secondary comparisons.

The strict held-out evaluation used Exp2 Medicine, Exp3 Family Dog, and sycophancy items S05/S11/S17/S23. These items were held out from training. Moral framing bias was computed as the average of yes-no bias and omission bias:

`yes-no bias = |P(endorse original action | original) - P(endorse original action | yesno)|`

`omission bias = |P(endorse original action | original) - P(endorse original action | omission)|`

The generated external evaluation used generated moral dilemmas and generated sycophancy claims as a robustness check.

### Results
Table 1 shows that the expanded SFT adapter produced the strongest strict held-out moral-bias reduction. It reduced moral bias from 1.000 in the base model to 0.080, while keeping valid response rate at 1.000. The expanded SFT+DPO adapter was not selected as the human-study model because it worsened omission robustness and restored wrong-belief agreement to the base-model level.

**Table 1. Strict held-out model comparison**

| Model                      | Moral bias mean | Yes-no bias | Omission bias | Sycophancy accuracy | Wrong-belief agreement | Valid rate | Latency vs base |
|----------------------------|-----------------|-------------|---------------|---------------------|------------------------|------------|-----------------|
| Base Qwen3-4B              | 1.000           | 1.000       | 1.000         | 0.750               | 0.250                  | 1.000      | 1.00x           |
| Old short-reason adapter   | 0.219           | 0.107       | 0.330         | 0.922               | 0.156                  | 1.000      | 1.75x           |
| Expanded SFT adapter       | 0.080           | 0.062       | 0.098         | 0.896               | 0.156                  | 1.000      | 1.85x           |
| Expanded SFT + DPO adapter | 0.134           | 0.000       | 0.268         | 0.875               | 0.250                  | 1.000      | 1.92x           |

Table 2 shows a more cautious result on generated external items. The expanded SFT adapter improved generated moral bias only modestly relative to the base model and did not outperform the base model on generated sycophancy accuracy. This result is theoretically important: model-level debiasing can be strong on original held-out items while remaining unstable under external distribution shift.

**Table 2. Generated external robustness comparison**

| Model                    | Evaluation                  | Moral bias mean | Yes-no bias | Omission bias | Sycophancy accuracy | Wrong-belief agreement | Valid rate | Latency vs base |
|--------------------------|-----------------------------|-----------------|-------------|---------------|---------------------|------------------------|------------|-----------------|
| Base Qwen3-4B            | Generated moral dilemmas    | 0.417           | 0.333       | 0.500         |                     |                        |            | 1.00x           |
| Old short-reason adapter | Generated moral dilemmas    | 0.385           | 0.385       | 0.385         |                     |                        |            | 1.61x           |
| Base Qwen3-4B            | Generated sycophancy claims |                 |             |               | 0.875               | 0.208                  |            | 1.00x           |
| Old short-reason adapter | Generated sycophancy claims |                 |             |               | 0.760               | 0.365                  |            | 1.61x           |
| Expanded SFT adapter     | Generated moral dilemmas    | 0.396           | 0.385       | 0.406         |                     |                        | 1.000      | 1.70x           |
| Expanded SFT adapter     | Generated sycophancy claims |                 |             |               | 0.823               | 0.271                  | 1.000      | 1.70x           |

### Study 1 Interpretation
The expanded SFT adapter is the best current model-layer candidate for human-study advice because it substantially reduces strict held-out moral framing bias. However, external robustness remains incomplete. This supports a cautious theoretical claim: model-level debiasing is possible, but benchmark improvements do not automatically guarantee robust human-AI moral alignment.

## Study 2: Planned Human-AI Moral Judgment Experiment
### Design
Study 2 is a planned online experiment, not yet recruiting participants. Participants will be assigned to one of two AI advice conditions: base-model advice or expanded-SFT advice. Each participant will see one framing version of each dilemma, with framing randomized and counterbalanced across participants. The within-material framing factor has three levels: original, yes-no, and omission.

### Trial Flow
Each trial will present a moral dilemma, collect an initial yes/no judgment, show AI advice with a concise reason and final answer, collect a final yes/no judgment, and then ask participants to rate confidence, helpfulness, trust, and reliance.

### Outcomes
The primary dependent variable is final `endorse_original_action`. Secondary outcomes are initial judgment consistency, judgment shift toward AI advice, confidence change, reliance rating, and perceived AI helpfulness.

### Planned Analysis
The main model will be a logistic mixed-effects model:

`endorse_original_action ~ AI_condition * framing + (1 | participant) + (1 | dilemma)`

The key test is whether the AI condition by framing interaction is smaller in the debiased-advice condition than in the base-advice condition. Secondary models will examine judgment shifts toward AI advice and reliance ratings.

## Discussion
The current results motivate a human-AI framing study rather than a purely technical adapter-training study. Expanded SFT reduces strict model-level moral bias, but external generated tests show that debiasing is not universally stable. This creates a substantive research question: when AI advice is less biased at the model level, does that actually improve human moral judgment, or do humans still exhibit framing susceptibility and selective reliance?

The planned human experiment directly tests this transfer question. If debiased advice reduces final human framing gaps, the study would support the practical value of model-level debiasing for human-AI decision support. If it does not, the study would show that model-layer improvements are insufficient by themselves and that human-AI interaction needs separate evaluation.

## Limitations
The human study is currently planned but not yet collected. The generated external test indicates limited robustness, so the debiased model should be treated as a selected advice condition rather than a solved alignment method. The current model set is also limited to Qwen3-4B variants and does not establish generality across all LLM families.

## Next Steps
The next stage is to preregister the planned human experiment, prepare survey materials, run a small pilot to check comprehension and reliance scales, and then estimate the sample size required for a full mixed-effects analysis.

## Artifact Metadata
Generated on 2026-04-18 from local experiment outputs in `results/`.
