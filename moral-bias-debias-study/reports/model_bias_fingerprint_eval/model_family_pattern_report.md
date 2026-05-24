# Model Family Bias Pattern Report

Generated: 2026-04-28T10:48:58

## Interpretation Rules

- `moral_bias_mean` is lower when the model is less framing-sensitive under standard prompting.
- `moral_bias_reduction` is `standard - method`; higher means stronger debiasing.
- `cost_adjusted_reduction_per_second` is only computed when latency is available.
- Current coverage is interim: DeepSeek V4 results are Exp2-complete; some older models cover Exp2+Exp3.

## Family-Level Standard Fingerprints

| provider_family | model_count | completed_dataset_cells | moral_bias_mean | yes_no_bias | omission_bias |
| --- | --- | --- | --- | --- | --- |
| deepseek | 3 | 4 | 0.664 | 0.667 | 0.662 |
| glm | 1 | 2 | 0.432 | 0.363 | 0.500 |
| gemini | 1 | 2 | 0.400 | 0.430 | 0.369 |
| qwen | 2 | 3 | 0.288 | 0.358 | 0.219 |
| gemma | 1 | 1 | 0.167 | 0.167 | 0.167 |

## Training-State Fingerprints

| deployment | training_state | model_count | moral_bias_mean | yes_no_bias | omission_bias |
| --- | --- | --- | --- | --- | --- |
| api | api_aligned | 7 | 0.482 | 0.474 | 0.490 |
| local | base_or_instruct | 1 | 0.193 | 0.360 | 0.027 |

## Method Responsiveness By Family

| provider_family | method_condition | cells | moral_bias_reduction | yes_no_bias_reduction | omission_bias_reduction | median_latency_seconds | cost_adjusted_reduction_per_second |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek | critique_revise | 4 | 0.402 | 0.417 | 0.386 | 9.078 | 0.052 |
| deepseek | debate | 4 | 0.372 | 0.400 | 0.345 | 10.432 | 0.044 |
| gemini | debate | 2 | 0.194 | 0.197 | 0.190 | NA | NA |
| qwen | debate | 3 | 0.096 | 0.152 | 0.040 | NA | NA |
| gemma | debate | 1 | 0.054 | 0.155 | -0.048 | NA | NA |

## Best Method By Effect

| model_id | dataset | method_condition | standard_moral_bias_mean | moral_bias_mean | moral_bias_reduction | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek_chat | exp2 | critique_revise | 0.476 | 0.213 | 0.263 | 10.669 |
| deepseek_chat | exp3 | critique_revise | 0.750 | 0.347 | 0.403 | 9.569 |
| deepseek_v4flash | exp2 | critique_revise | 0.667 | 0.260 | 0.406 | 5.021 |
| deepseek_v4pro | exp2 | debate | 0.713 | 0.103 | 0.610 | 14.217 |
| gemini25_flash | exp2 | debate | 0.119 | 0.143 | -0.024 | NA |
| gemini25_flash | exp3 | debate | 0.680 | 0.269 | 0.411 | NA |
| gemma4_31b_api | exp2 | debate | 0.167 | 0.113 | 0.054 | NA |
| aliyun_qwen36 | exp2 | debate | 0.238 | 0.165 | 0.073 | NA |
| aliyun_qwen36 | exp3 | debate | 0.528 | 0.232 | 0.296 | NA |
| qwen3_32b_local | exp2 | debate | 0.193 | 0.275 | -0.082 | NA |

## Best Method By Cost-Adjusted Effect

| model_id | dataset | method_condition | moral_bias_reduction | median_latency_seconds | cost_adjusted_reduction_per_second |
| --- | --- | --- | --- | --- | --- |
| deepseek_chat | exp2 | critique_revise | 0.263 | 10.669 | 0.025 |
| deepseek_chat | exp3 | critique_revise | 0.403 | 9.569 | 0.042 |
| deepseek_v4flash | exp2 | critique_revise | 0.406 | 5.021 | 0.081 |
| deepseek_v4pro | exp2 | critique_revise | 0.534 | 8.588 | 0.062 |

## DeepSeek V4 Variant Pattern

| model_id | method_condition | standard_moral_bias_mean | moral_bias_mean | moral_bias_reduction | median_latency_seconds | cost_adjusted_reduction_per_second |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4flash | critique_revise | 0.667 | 0.260 | 0.406 | 5.021 | 0.081 |
| deepseek_v4flash | debate | 0.667 | 0.366 | 0.301 | 6.647 | 0.045 |
| deepseek_v4pro | debate | 0.713 | 0.103 | 0.610 | 14.217 | 0.043 |
| deepseek_v4pro | critique_revise | 0.713 | 0.179 | 0.534 | 8.588 | 0.062 |

## Draft Regularities

1. High baseline bias does not imply a fixed best intervention: DeepSeek V4-Pro and V4-Flash both have high Exp2 standard bias, but their strongest method differs.
2. Debate appears strongest for DeepSeek V4-Pro by raw effect, while critique-revise is the cost-adjusted winner and the raw-effect winner for V4-Flash.
3. Model family is informative but insufficient: provider-level averages hide variant-level differences between Pro and Flash.
4. Low baseline-bias models have less room for improvement and can even worsen under debate, as seen in Gemini Exp2 and Qwen3-32B local Exp2.
5. Method selection should be fingerprint-conditioned rather than globally fixed.
