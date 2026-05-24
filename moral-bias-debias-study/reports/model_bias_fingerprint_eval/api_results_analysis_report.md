# API Results Analysis

Generated: 2026-04-28

Scope: API models only. Local open-weight baselines and adapters are excluded except where used as context in separate reports.

## Run Coverage

| run | model_id | analysis_tier | rows | expected_rows | datasets | methods | valid_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_exp2_aliyun_qwen36 | aliyun_qwen36 | full | 2016 | 2016.000 | exp2 | debate,standard | 1.000 |
| full_exp3_aliyun_qwen36 | aliyun_qwen36 | full | 2016 | 2016.000 | exp3 | debate,standard | 1.000 |
| full_deepseek_confirmatory_moral_cr | deepseek_chat | full | 2016 | 2016.000 | exp2,exp3 | critique_revise | 1.000 |
| full_deepseek_confirmatory_sycophancy_std_cr | deepseek_chat | full | 2304 | 2304.000 | sycophancy | critique_revise,standard | 1.000 |
| full_exp2_deepseek | deepseek_chat | full | 2016 | 2016.000 | exp2 | debate,standard | 1.000 |
| full_exp3_deepseek | deepseek_chat | full | 2016 | 2016.000 | exp3 | debate,standard | 1.000 |
| full_deepseek_v4flash_methods | deepseek_v4flash | partial | 3025 | 9504.000 | exp2,exp3 | critique_revise,debate,standard | 1.000 |
| smoke_deepseek_v4flash_methods_no_thinking | deepseek_v4flash | smoke | 36 | 36.000 | exp2 | critique_revise,debate,standard | 1.000 |
| full_deepseek_v4pro_methods | deepseek_v4pro | partial | 2450 | 9504.000 | exp2 | critique_revise,debate,standard | 1.000 |
| missing_exp2_deepseek_v4pro_cr_shard0 | deepseek_v4pro | partial | 287 | NA | exp2 | critique_revise | 1.000 |
| missing_exp2_deepseek_v4pro_cr_shard1 | deepseek_v4pro | partial | 287 | NA | exp2 | critique_revise | 1.000 |
| pilot_deepseek_v4pro_methods | deepseek_v4pro | pilot | 1008 | 1008.000 | exp2,exp3,sycophancy | critique_revise,debate,standard | 1.000 |
| full_exp2_gemini25flash | gemini25_flash | full | 2016 | 2016.000 | exp2 | debate,standard | 1.000 |
| full_exp3_gemini25flash | gemini25_flash | full | 2016 | 2016.000 | exp3 | debate,standard | 1.000 |
| full_exp2_gemma4_31b | gemma4_31b_api | full | 2016 | 2016.000 | exp2 | debate,standard | 1.000 |
| full_exp3_gemma4_31b | gemma4_31b_api | full | 2016 | 2016.000 | exp3 | debate,standard | 1.000 |
| full_exp2_zhipu_glm51 | zhipu_glm51 | partial | 1025 | 2016.000 | exp2 | debate,standard | 1.000 |
| full_exp3_zhipu_glm51 | zhipu_glm51 | full | 2016 | 2016.000 | exp3 | debate,standard | 0.957 |

## Standard Moral Framing Fingerprint

Lower `moral_bias_mean` is better. These are standard-prompt results only.

| model_id | provider_family | datasets | moral_bias_mean | yes_no_bias | omission_bias | valid_rate |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | deepseek | exp2 | 0.713 | 0.705 | 0.720 | 1.000 |
| deepseek_v4flash | deepseek | exp2 | 0.667 | 0.667 | 0.667 | 1.000 |
| deepseek_chat | deepseek | exp2,exp3 | 0.613 | 0.628 | 0.598 | 1.000 |
| zhipu_glm51 | glm | exp2,exp3 | 0.432 | 0.363 | 0.500 | 1.000 |
| gemini25_flash | gemini | exp2,exp3 | 0.400 | 0.430 | 0.369 | 1.000 |
| aliyun_qwen36 | qwen | exp2,exp3 | 0.383 | 0.356 | 0.411 | 1.000 |
| gemma4_31b_api | gemma | exp2 | 0.167 | 0.167 | 0.167 | 1.000 |

## Dataset-Level Moral Fingerprints

| model_id | dataset | analysis_tier | trials | valid_rate | moral_bias_mean | yes_no_bias | omission_bias | yes_no_bias_signed | omission_bias_signed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | exp2 | partial | 1008 | 1.000 | 0.713 | 0.705 | 0.720 | 0.271 | 0.274 |
| deepseek_v4flash | exp2 | partial | 1008 | 1.000 | 0.667 | 0.667 | 0.667 | 0.333 | 0.333 |
| deepseek_chat | exp2 | full | 1008 | 1.000 | 0.476 | 0.423 | 0.530 | 0.244 | 0.262 |
| aliyun_qwen36 | exp2 | full | 1008 | 1.000 | 0.238 | 0.155 | 0.321 | -0.155 | -0.321 |
| gemma4_31b_api | exp2 | full | 1008 | 1.000 | 0.167 | 0.167 | 0.167 | 0.167 | -0.167 |
| gemini25_flash | exp2 | full | 1008 | 1.000 | 0.119 | 0.036 | 0.202 | 0.036 | -0.131 |
| zhipu_glm51 | exp2 | partial | 1008 | 1.000 | 0.083 | 0.000 | 0.167 | 0.000 | -0.167 |
| zhipu_glm51 | exp3 | full | 1008 | 1.000 | 0.780 | 0.726 | 0.833 | -0.060 | -0.167 |
| deepseek_chat | exp3 | full | 1008 | 1.000 | 0.750 | 0.833 | 0.667 | -0.833 | -0.667 |
| gemini25_flash | exp3 | full | 1008 | 1.000 | 0.680 | 0.824 | 0.536 | -0.568 | -0.536 |
| aliyun_qwen36 | exp3 | full | 1008 | 1.000 | 0.528 | 0.557 | 0.500 | -0.557 | -0.500 |

## Debias Responsiveness

Higher `moral_bias_reduction` is better. Negative values mean the method worsened framing bias.

| model_id | dataset | method_condition | standard_moral_bias_mean | moral_bias_mean | moral_bias_reduction | yes_no_bias_reduction | omission_bias_reduction | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | exp2 | debate | 0.713 | 0.103 | 0.610 | 0.577 | 0.643 | 14.217 |
| deepseek_v4pro | exp2 | critique_revise | 0.713 | 0.179 | 0.534 | 0.533 | 0.536 | 8.588 |
| gemini25_flash | exp3 | debate | 0.680 | 0.269 | 0.411 | 0.536 | 0.286 | NA |
| deepseek_v4flash | exp2 | critique_revise | 0.667 | 0.260 | 0.406 | 0.375 | 0.438 | 5.021 |
| deepseek_chat | exp3 | critique_revise | 0.750 | 0.347 | 0.403 | 0.521 | 0.286 | 9.569 |
| deepseek_chat | exp3 | debate | 0.750 | 0.421 | 0.329 | 0.458 | 0.199 | NA |
| deepseek_v4flash | exp2 | debate | 0.667 | 0.366 | 0.301 | 0.339 | 0.263 | 6.647 |
| aliyun_qwen36 | exp3 | debate | 0.528 | 0.232 | 0.296 | 0.312 | 0.280 | NA |
| deepseek_chat | exp2 | critique_revise | 0.476 | 0.213 | 0.263 | 0.241 | 0.286 | 10.669 |
| deepseek_chat | exp2 | debate | 0.476 | 0.226 | 0.250 | 0.226 | 0.274 | NA |
| aliyun_qwen36 | exp2 | debate | 0.238 | 0.165 | 0.073 | 0.110 | 0.036 | NA |
| gemma4_31b_api | exp2 | debate | 0.167 | 0.113 | 0.054 | 0.155 | -0.048 | NA |
| gemini25_flash | exp2 | debate | 0.119 | 0.143 | -0.024 | -0.143 | 0.095 | NA |

## Method Response By API Family

| provider_family | method_condition | cells | moral_bias_reduction | yes_no_bias_reduction | omission_bias_reduction | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek | critique_revise | 4 | 0.402 | 0.417 | 0.386 | 9.078 |
| deepseek | debate | 4 | 0.372 | 0.400 | 0.345 | 10.432 |
| gemini | debate | 2 | 0.194 | 0.197 | 0.190 | NA |
| qwen | debate | 2 | 0.185 | 0.211 | 0.158 | NA |
| gemma | debate | 1 | 0.054 | 0.155 | -0.048 | NA |

## Sycophancy

| model_id | method_condition | analysis_tier | sycophancy_trials | sycophancy_accuracy | aligned_accuracy | conflict_accuracy | wrong_belief_agreement_rate | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_chat | critique_revise | full | 1152.000 | 0.999 | 0.998 | 1.000 | 0.000 | 9.111 |
| deepseek_chat | standard | full | 1152.000 | 0.906 | 0.938 | 0.875 | 0.125 | 1.449 |
| deepseek_v4pro | critique_revise | pilot | 192.000 | 0.958 | 0.979 | 0.938 | 0.062 | 7.844 |
| deepseek_v4pro | debate | pilot | 192.000 | 0.943 | 0.938 | 0.948 | 0.052 | 12.903 |
| deepseek_v4pro | standard | pilot | 192.000 | 0.828 | 0.958 | 0.698 | 0.302 | 1.676 |

## Polarity / Negation Bias

DeepSeek V4 polarity rows are currently partial because full API runs were paused.

| model_id | provider_family | method_condition | task_families | polarity_gap_abs | accuracy_mean |
| --- | --- | --- | --- | --- | --- |
| deepseek_v4flash | deepseek | standard | factual,moral | 0.000 | 1.000 |
| deepseek_v4pro | deepseek | standard | factual,moral | 0.000 | 1.000 |

## Main Findings

1. DeepSeek-family API models show the largest raw moral framing bias under standard prompting, especially V4-Pro and V4-Flash on Exp2.

2. Debate has the strongest raw effect on DeepSeek V4-Pro, but critique-revise is the better cost-adjusted choice because it is faster and still removes most of the bias.

3. V4-Flash responds better to critique-revise than debate, so even within one model family the best debias method is variant-specific.

4. Gemini 2.5 Flash is dataset-sensitive: low Exp2 standard bias but high Exp3 standard bias, and debate helps Exp3 while slightly worsening Exp2.

5. Aliyun Qwen3.6 is medium-bias overall; debate helps more on Exp3 than Exp2.

6. GLM-5.1 Exp3 shows high standard bias and lower valid rate under debate, so its debate results should be treated cautiously.

7. DeepSeek chat sycophancy is strongly improved by critique-revise, reducing wrong-belief agreement from 0.125 to 0.000.

8. Current partial polarity results suggest DeepSeek V4-Pro/Flash do not fail simple positive/negative question equivalence, meaning their moral yes-no bias is not just a simple negation-comprehension bug.

## Recommended Next Analyses

1. Complete DeepSeek V4-Pro/V4-Flash polarity full runs to verify the partial zero-gap finding.

2. Run sycophancy full for V4-Pro/V4-Flash because pilot V4-Pro standard had high wrong-belief agreement.

3. Fit a model-level meta-regression where outcome is `bias_reduction` and predictors are `provider_family`, `method_condition`, `bias_type`, and baseline bias.

4. Separate conclusions by dataset: Exp2 and Exp3 often differ enough that pooled averages hide the mechanism.
