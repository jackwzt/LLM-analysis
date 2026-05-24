# Deep Bias Regularities Report

Generated: 2026-05-06

This report applies the paper's machine-individuality logic to the current bias project: separate global response tendency, stimulus/item effects, and model-specific item/bias fingerprints.

## Data Coverage

| bias_type | dataset | method_condition | models | trial_rows | score_rows |
| --- | --- | --- | --- | --- | --- |
| moral_omission_bias | exp2 | critique_revise | 3 | 4236.000 | 46.000 |
| moral_omission_bias | exp2 | debate | 9 | 6179.000 | 77.000 |
| moral_omission_bias | exp2 | standard | 13 | 7392.000 | 81.000 |
| moral_omission_bias | exp2 | structured_cr | 1 | 112.000 | 1.000 |
| moral_omission_bias | exp3 | critique_revise | 3 | 2784.000 | 36.000 |
| moral_omission_bias | exp3 | debate | 8 | 5063.000 | 61.000 |
| moral_omission_bias | exp3 | standard | 11 | 5360.000 | 59.000 |
| moral_omission_bias | exp3 | structured_cr | 1 | 112.000 | 1.000 |
| moral_omission_bias | generated_moral | debate | 1 | 48.000 | 24.000 |
| moral_omission_bias | generated_moral | standard | 4 | 766.000 | 96.000 |
| moral_omission_bias | generated_moral | structured_cr | 1 | 192.000 | 24.000 |
| moral_yes_no_bias | exp2 | critique_revise | 3 | 4238.000 | 46.000 |
| moral_yes_no_bias | exp2 | debate | 9 | 6177.000 | 76.000 |
| moral_yes_no_bias | exp2 | standard | 13 | 7392.000 | 81.000 |
| moral_yes_no_bias | exp2 | structured_cr | 1 | 112.000 | 1.000 |
| moral_yes_no_bias | exp3 | critique_revise | 3 | 2784.000 | 36.000 |
| moral_yes_no_bias | exp3 | debate | 8 | 5090.000 | 61.000 |
| moral_yes_no_bias | exp3 | standard | 11 | 5360.000 | 59.000 |
| moral_yes_no_bias | exp3 | structured_cr | 1 | 112.000 | 1.000 |
| moral_yes_no_bias | generated_moral | debate | 1 | 48.000 | 24.000 |
| moral_yes_no_bias | generated_moral | standard | 4 | 768.000 | 96.000 |
| moral_yes_no_bias | generated_moral | structured_cr | 1 | 192.000 | 24.000 |
| polarity_negation_gap | polarity_bias | standard | 5 | 5757.000 | 10.000 |
| sycophancy_wrong_belief_agreement | generated_sycophancy | debate | 1 | 24.000 | 1.000 |
| sycophancy_wrong_belief_agreement | generated_sycophancy | standard | 4 | 384.000 | 4.000 |
| sycophancy_wrong_belief_agreement | generated_sycophancy | structured_cr | 1 | 96.000 | 1.000 |
| sycophancy_wrong_belief_agreement | sycophancy | checklist | 2 | 0.000 | 2.000 |
| sycophancy_wrong_belief_agreement | sycophancy | critique_revise | 7 | 1824.000 | 7.000 |
| sycophancy_wrong_belief_agreement | sycophancy | debate | 4 | 1264.000 | 4.000 |
| sycophancy_wrong_belief_agreement | sycophancy | invariance_vote | 3 | 0.000 | 3.000 |
| sycophancy_wrong_belief_agreement | sycophancy | standard | 12 | 2304.000 | 12.000 |
| sycophancy_wrong_belief_agreement | sycophancy | structured_cr | 1 | 96.000 | 1.000 |

## Fingerprint Matrix

| model_id | provider_family | deployment | training_state | yes_no_gap | omission_gap | sycophancy_wrong_belief | polarity_gap_abs | debate_reduction | critique_revise_reduction | feature_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4pro | deepseek | api | api_aligned | 0.780 | 0.781 | 0.302 | 0.000 | 0.610 | 0.534 | 0.900 |
| deepseek_chat | deepseek | api | api_aligned | 0.628 | 0.598 | 0.125 | NA | 0.289 | 0.333 | 0.800 |
| deepseek_v4flash | deepseek | api | api_aligned | 0.759 | 0.671 | NA | 0.000 | 0.301 | 0.406 | 0.800 |
| gemma4_e4b_base | gemma | local | base_or_instruct | 0.581 | 0.561 | 0.250 | 0.000 | NA | NA | 0.700 |
| qwen3_4b_base | qwen | local | base_or_instruct | 0.778 | 0.833 | 0.250 | 0.333 | NA | NA | 0.700 |
| aliyun_qwen36 | qwen | api | api_aligned | 0.356 | 0.411 | NA | NA | 0.185 | NA | 0.600 |
| gemma4_e4b_sft | gemma | local | sft_debiased | 0.262 | 0.239 | 0.146 | NA | NA | NA | 0.600 |
| qwen3_4b_expanded_sft | qwen | local | sft_debiased | 0.170 | 0.201 | 0.156 | NA | NA | NA | 0.600 |
| qwen3_32b_local | qwen | local | base_or_instruct | 0.360 | 0.027 | NA | 0.083 | -0.082 | NA | 0.600 |
| gemini25_flash | gemini | api | api_aligned | 0.430 | 0.369 | NA | NA | 0.194 | NA | 0.600 |
| qwen3_4b_expanded_sft_dpo | qwen | local | sft_dpo_debiased | 0.000 | 0.268 | 0.250 | NA | NA | NA | 0.600 |
| zhipu_glm51 | glm | api | api_aligned | 0.363 | 0.500 | NA | NA | NA | NA | 0.500 |
| gemma4_31b_api | gemma | api | api_aligned | 0.167 | 0.167 | NA | NA | 0.054 | NA | 0.500 |
| pilot_api_sycophancy_24x4 | NA | NA | NA | NA | NA | 0.031 | NA | NA | NA | 0.100 |
| pilot_deepseek_joint_top3 | NA | NA | NA | NA | NA | 0.141 | NA | NA | NA | 0.100 |
| qwen3_4b_structured_cr_sft | qwen | local | sft_structured_cr | NA | NA | NA | NA | NA | NA | 0.100 |
| smoke_api_sycophancy_methods | NA | NA | NA | NA | NA | 0.000 | NA | NA | NA | 0.100 |
| smoke_nvidia_kimi25_std_cr | NA | NA | NA | NA | NA | 0.000 | NA | NA | NA | 0.100 |

## Variance Decomposition

The mixed model is the closest analogue to the reference paper. The crossed-mean proxy is included as a robust fallback because the data are unbalanced across models and methods.

| status |
| --- |
| mixedlm_failed: LinAlgError: Singular matrix |

| method | component | variance | share | n_rows | n_models | n_items |
| --- | --- | --- | --- | --- | --- | --- |
| crossed_mean_variance_proxy | model_global_response_bias | 0.008 | 0.046 | 587 | 14 | 50 |
| crossed_mean_variance_proxy | stimulus_item_effect | 0.042 | 0.246 | 587 | 14 | 50 |
| crossed_mean_variance_proxy | bias_type_fixed_effect | 0.003 | 0.016 | 587 | 14 | 50 |
| crossed_mean_variance_proxy | method_fixed_effect | 0.006 | 0.036 | 587 | 14 | 50 |
| crossed_mean_variance_proxy | model_specific_item_fingerprint | 0.053 | 0.313 | 587 | 14 | 50 |
| crossed_mean_variance_proxy | residual_noise | 0.058 | 0.343 | 587 | 14 | 50 |

## Model Clusters

| model_id | provider_family | model_line | variant_type | deployment | cluster_k3 | pca1 | pca2 | feature_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aliyun_qwen36 | qwen | qwen3.6 | flash_api | api | 1 | -0.538 | 0.082 | 0.667 |
| gemini25_flash | gemini | gemini-2.5 | flash_api | api | 1 | -0.369 | -0.048 | 0.667 |
| gemma4_31b_api | gemma | gemma-4 | large_api | api | 1 | -2.009 | 0.112 | 0.556 |
| gemma4_e4b_sft | gemma | gemma-4 | e4b_local_sft | local | 1 | -2.133 | 0.039 | 0.667 |
| qwen3_32b_local | qwen | qwen3 | 32b_local | local | 1 | -2.133 | -0.258 | 0.667 |
| qwen3_4b_expanded_sft | qwen | qwen3 | 4b_local_sft | local | 1 | -2.566 | 0.318 | 0.667 |
| qwen3_4b_expanded_sft_dpo | qwen | qwen3 | 4b_local_sft_dpo | local | 1 | -2.194 | 1.246 | 0.667 |
| zhipu_glm51 | glm | glm-5.1 | chat_api | api | 1 | -0.038 | -0.093 | 0.556 |
| deepseek_v4flash | deepseek | deepseek-v4 | flash_api | api | 2 | 2.150 | -0.362 | 0.889 |
| deepseek_v4pro | deepseek | deepseek-v4 | pro_api | api | 2 | 4.269 | 3.003 | 1.000 |
| gemma4_e4b_base | gemma | gemma-4 | e4b_local | local | 2 | 1.225 | 0.718 | 0.778 |
| qwen3_4b_base | qwen | qwen3 | 4b_local | local | 2 | 3.657 | -2.135 | 0.778 |
| deepseek_chat | deepseek | deepseek-chat | chat_api | api | 3 | 0.679 | -2.620 | 0.889 |

## Cross-Bias Prediction

| test | n | pearson_r | pearson_p | slope | loo_rmse | r_squared |
| --- | --- | --- | --- | --- | --- | --- |
| Exp2 moral predicts Exp3 moral | 11 | 0.484 | 0.131 | 0.360 | 0.325 | 0.234 |
| Moral framing predicts strict sycophancy | 7 | 0.433 | 0.332 | 0.103 | 0.079 | 0.187 |
| Moral framing predicts polarity gap | 5 | 0.201 | 0.746 | 0.115 | 0.276 | 0.040 |
| Yes-no framing predicts polarity gap | 5 | 0.168 | 0.787 | 0.133 | 0.211 | 0.028 |
| Debate response predicts critique-revise response | 3 | 0.944 | 0.213 | 0.528 | 1.053 | 0.892 |

## Metadata Meta-Regression

These are exploratory OLS models over aggregated bias scores; model count is still too small for causal interpretation.

| model | term | coef | std_err | p_value | r_squared | n_rows |
| --- | --- | --- | --- | --- | --- | --- |
| training_state_plus_bias_type | Intercept | 0.381 | 0.028 | 0.000 | 0.028 | 587 |
| deployment_plus_bias_type | Intercept | 0.380 | 0.028 | 0.000 | 0.020 | 587 |
| provider_family_plus_bias_type | Intercept | 0.425 | 0.033 | 0.000 | 0.038 | 587 |
| provider_method_bias_type | Intercept | 0.298 | 0.035 | 0.000 | 0.106 | 587 |
| method_plus_bias_type | Intercept | 0.298 | 0.035 | 0.000 | 0.063 | 587 |
| method_plus_bias_type | C(bias_type)[T.sycophancy_wrong_belief_agreement] | -0.282 | 0.034 | 0.000 | 0.063 | 587 |
| deployment_plus_bias_type | C(bias_type)[T.sycophancy_wrong_belief_agreement] | -0.258 | 0.037 | 0.000 | 0.020 | 587 |
| provider_method_bias_type | C(bias_type)[T.sycophancy_wrong_belief_agreement] | -0.266 | 0.040 | 0.000 | 0.106 | 587 |
| method_plus_bias_type | C(bias_type)[T.polarity_negation_gap] | -0.386 | 0.062 | 0.000 | 0.063 | 587 |
| provider_family_plus_bias_type | C(bias_type)[T.sycophancy_wrong_belief_agreement] | -0.234 | 0.039 | 0.000 | 0.038 | 587 |
| training_state_plus_bias_type | C(bias_type)[T.polarity_negation_gap] | -0.348 | 0.059 | 0.000 | 0.028 | 587 |
| provider_method_bias_type | C(method_condition)[T.standard] | 0.311 | 0.054 | 0.000 | 0.106 | 587 |
| deployment_plus_bias_type | C(bias_type)[T.polarity_negation_gap] | -0.322 | 0.057 | 0.000 | 0.020 | 587 |
| training_state_plus_bias_type | C(bias_type)[T.sycophancy_wrong_belief_agreement] | -0.245 | 0.044 | 0.000 | 0.028 | 587 |
| provider_method_bias_type | C(bias_type)[T.polarity_negation_gap] | -0.419 | 0.080 | 0.000 | 0.106 | 587 |
| provider_family_plus_bias_type | C(bias_type)[T.polarity_negation_gap] | -0.317 | 0.064 | 0.000 | 0.038 | 587 |
| method_plus_bias_type | C(method_condition)[T.standard] | 0.172 | 0.039 | 0.000 | 0.063 | 587 |
| provider_method_bias_type | C(provider_family)[T.qwen] | -0.181 | 0.051 | 0.000 | 0.106 | 587 |
| provider_method_bias_type | C(provider_family)[T.gemma] | -0.171 | 0.052 | 0.001 | 0.106 | 587 |
| provider_method_bias_type | C(method_condition)[T.structured_cr] | 0.238 | 0.073 | 0.001 | 0.106 | 587 |
| provider_method_bias_type | C(provider_family)[T.gemini] | -0.170 | 0.062 | 0.006 | 0.106 | 587 |
| provider_family_plus_bias_type | C(provider_family)[T.glm] | 0.207 | 0.083 | 0.013 | 0.038 | 587 |
| provider_method_bias_type | C(provider_family)[T.glm] | 0.147 | 0.079 | 0.062 | 0.106 | 587 |
| provider_family_plus_bias_type | C(provider_family)[T.gemini] | -0.110 | 0.061 | 0.069 | 0.038 | 587 |
| training_state_plus_bias_type | C(training_state)[T.base_or_instruct] | 0.084 | 0.050 | 0.092 | 0.028 | 587 |

## Method Specificity

| model_id | dataset | bias_type | method_condition | standard_bias | method_bias | bias_reduction |
| --- | --- | --- | --- | --- | --- | --- |
| qwen3_4b_base | exp2 | moral_omission_bias | debate | 1.000 | 0.250 | 0.750 |
| qwen3_4b_base | exp2 | moral_yes_no_bias | debate | 1.000 | 0.250 | 0.750 |
| deepseek_v4pro | exp3 | moral_yes_no_bias | critique_revise | 0.885 | 0.152 | 0.734 |
| deepseek_v4pro | exp2 | moral_omission_bias | debate | 0.714 | 0.060 | 0.655 |
| deepseek_v4flash | exp3 | moral_yes_no_bias | debate | 0.851 | 0.235 | 0.616 |
| deepseek_v4pro | exp3 | moral_yes_no_bias | debate | 0.885 | 0.281 | 0.604 |
| deepseek_v4pro | exp3 | moral_omission_bias | debate | 0.838 | 0.240 | 0.598 |
| deepseek_v4pro | exp2 | moral_omission_bias | critique_revise | 0.714 | 0.141 | 0.573 |
| gemini25_flash | exp3 | moral_yes_no_bias | debate | 0.824 | 0.289 | 0.536 |
| deepseek_v4flash | exp3 | moral_yes_no_bias | critique_revise | 0.851 | 0.318 | 0.533 |
| deepseek_v4pro | exp3 | moral_omission_bias | critique_revise | 0.838 | 0.311 | 0.527 |
| deepseek_chat | exp3 | moral_yes_no_bias | critique_revise | 0.833 | 0.312 | 0.521 |
| deepseek_v4pro | exp2 | moral_yes_no_bias | debate | 0.728 | 0.210 | 0.518 |
| deepseek_v4flash | exp3 | moral_omission_bias | debate | 0.676 | 0.164 | 0.512 |
| deepseek_v4flash | exp2 | moral_yes_no_bias | debate | 0.750 | 0.246 | 0.504 |
| qwen3_4b_base | exp3 | moral_omission_bias | debate | 1.000 | 0.500 | 0.500 |
| qwen3_4b_base | exp3 | moral_yes_no_bias | debate | 1.000 | 0.500 | 0.500 |
| deepseek_chat | exp3 | moral_yes_no_bias | debate | 0.833 | 0.375 | 0.458 |
| deepseek_v4flash | exp2 | moral_omission_bias | critique_revise | 0.750 | 0.297 | 0.453 |
| deepseek_v4pro | exp2 | moral_yes_no_bias | critique_revise | 0.728 | 0.307 | 0.421 |
| zhipu_glm51 | exp3 | moral_omission_bias | debate | 0.833 | 0.417 | 0.416 |
| deepseek_v4flash | exp2 | moral_omission_bias | debate | 0.750 | 0.364 | 0.386 |
| deepseek_v4flash | exp2 | moral_yes_no_bias | critique_revise | 0.750 | 0.406 | 0.344 |
| deepseek_v4flash | exp3 | moral_omission_bias | critique_revise | 0.676 | 0.336 | 0.339 |
| aliyun_qwen36 | exp3 | moral_yes_no_bias | debate | 0.557 | 0.244 | 0.312 |
| deepseek_chat | exp2 | moral_omission_bias | critique_revise | 0.530 | 0.244 | 0.286 |
| gemini25_flash | exp3 | moral_omission_bias | debate | 0.536 | 0.250 | 0.286 |
| deepseek_chat | exp3 | moral_omission_bias | critique_revise | 0.667 | 0.381 | 0.286 |
| aliyun_qwen36 | exp3 | moral_omission_bias | debate | 0.500 | 0.220 | 0.280 |
| deepseek_chat | exp2 | moral_omission_bias | debate | 0.530 | 0.256 | 0.274 |

## Main Findings

1. Model-specific item/bias fingerprint explains about 31.3% of decomposed aggregate-bias variance under the available model, so there is evidence beyond simple global response bias.

2. Bias is multidimensional: moral framing, sycophancy, and polarity do not collapse into one universally high-or-low model score.

3. DeepSeek variants show strong moral framing sensitivity but current polarity results are near zero, supporting the idea that moral yes-no bias is not merely negation failure.

4. Method response is model-specific: debate is strongest for DeepSeek V4-Pro by raw moral effect, while critique-revise is stronger or more cost-efficient for DeepSeek chat and V4-Flash.

5. Metadata effects should be treated as exploratory because API model counts are small and deployment/training-state variables are confounded with model family.

## Limitations

- DeepSeek V4 full runs remain partial outside completed Exp2 cells; those rows are marked exploratory rather than confirmatory.

- Some local strict tests cover held-out items rather than the full Exp2/Exp3 grid, so cross-model comparisons should use the sample-size audit.

- The first implementation uses aggregate bias scores for stable variance decomposition; raw binary crossed-logistic modeling should be added only after the design matrix is balanced enough.
