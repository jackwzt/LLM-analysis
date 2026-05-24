# Model Bias Fingerprint and Debias Responsiveness

## Run Inventory

| source_run | model_id | analysis_tier | rows | expected_rows | datasets | methods | valid_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_exp2_qwen | qwen3_32b_local | exploratory | 2016 | 2016 | exp2 | debate,standard | 1.000 |
| full_exp2_aliyun_qwen36 | aliyun_qwen36 | full | 2016 | 2016 | exp2 | debate,standard | 1.000 |
| full_exp3_aliyun_qwen36 | aliyun_qwen36 | full | 2016 | 2016 | exp3 | debate,standard | 1.000 |
| full_deepseek_confirmatory_moral_cr | deepseek_chat | full | 2016 | 2016 | exp2,exp3 | critique_revise | 1.000 |
| full_deepseek_confirmatory_sycophancy_std_cr | deepseek_chat | full | 2304 | 2304 | sycophancy | critique_revise,standard | 1.000 |
| full_exp2_deepseek | deepseek_chat | full | 2016 | 2016 | exp2 | debate,standard | 1.000 |
| full_exp3_deepseek | deepseek_chat | full | 2016 | 2016 | exp3 | debate,standard | 1.000 |
| full_deepseek_v4flash_methods | deepseek_v4flash | full | 9504 | 9504 | exp2,exp3,sycophancy | critique_revise,debate,standard | 1.000 |
| full_deepseek_v4pro_methods | deepseek_v4pro | full | 9504 | 9504 | exp2,exp3,sycophancy | critique_revise,debate,standard | 1.000 |
| full_exp2_gemini25flash | gemini25_flash | full | 2016 | 2016 | exp2 | debate,standard | 1.000 |
| full_exp3_gemini25flash | gemini25_flash | full | 2016 | 2016 | exp3 | debate,standard | 1.000 |
| full_exp2_gemma4_31b | gemma4_31b_api | full | 2016 | 2016 | exp2 | debate,standard | 1.000 |
| full_exp3_gemma4_31b | gemma4_31b_api | full | 2016 | 2016 | exp3 | debate,standard | 1.000 |
| generated_gemma4_e4b_base_r4 | gemma4_e4b_base | full | 480 | 480 | generated_moral,generated_sycophancy | standard | 0.996 |
| strict_item_gemma4_e4b_base_test | gemma4_e4b_base | full | 528 | 528 | exp2,exp3,sycophancy | standard | 1.000 |
| generated_gemma4_e4b_sft_r4 | gemma4_e4b_sft | full | 480 | 480 | generated_moral,generated_sycophancy | standard | 1.000 |
| strict_item_gemma4_e4b_sft_test | gemma4_e4b_sft | full | 528 | 528 | exp2,exp3,sycophancy | standard | 1.000 |
| generated_qwen3_4b_base_r4 | qwen3_4b_base | full | 480 | 480 | generated_moral,generated_sycophancy | standard | 1.000 |
| strict_item_qwen3_4b_base_test | qwen3_4b_base | full | 528 | 528 | exp2,exp3,sycophancy | standard | 1.000 |
| generated_qwen3_4b_v2_sft_expanded_r4 | qwen3_4b_expanded_sft | full | 480 | 480 | generated_moral,generated_sycophancy | standard | 1.000 |
| strict_item_qwen3_4b_v2_sft_expanded_test | qwen3_4b_expanded_sft | full | 528 | 528 | exp2,exp3,sycophancy | standard | 1.000 |
| strict_item_qwen3_4b_v2_sft_expanded_dpo_test | qwen3_4b_expanded_sft_dpo | full | 528 | 528 | exp2,exp3,sycophancy | standard | 1.000 |
| confirmatory_generated_qwen3_4b_structured_cr_full_r4 | qwen3_4b_structured_cr_sft | full | 480 | 480 | generated_moral,generated_sycophancy | structured_cr | 1.000 |
| confirmatory_strict_qwen3_4b_structured_cr_full | qwen3_4b_structured_cr_sft | full | 528 | 528 | exp2,exp3,sycophancy | structured_cr | 1.000 |
| full_exp3_zhipu_glm51 | zhipu_glm51 | full | 2016 | 2016 | exp3 | debate,standard | 0.957 |
| missing_exp2_deepseek_v4pro_cr_shard0 | deepseek_v4pro | partial | 287 | NA | exp2 | critique_revise | 1.000 |
| missing_exp2_deepseek_v4pro_cr_shard1 | deepseek_v4pro | partial | 287 | NA | exp2 | critique_revise | 1.000 |
| full_exp2_zhipu_glm51 | zhipu_glm51 | partial | 1025 | 2016 | exp2 | debate,standard | 1.000 |
| pilot_debias_methods_deepseek_chat | deepseek_chat | pilot | 5376 | 5376 | exp2,exp3,sycophancy | anti_sycophancy_truth_first,constitutional_critic,counterfactual_consistency_vote,critique_revise,debate,frame_invariant_rationale,self_debias_reprompt,standard | 1.000 |
| pilot_debias_methods_deepseek_v4flash | deepseek_v4flash | pilot | 5376 | 5376 | exp2,exp3,sycophancy | anti_sycophancy_truth_first,constitutional_critic,counterfactual_consistency_vote,critique_revise,debate,frame_invariant_rationale,self_debias_reprompt,standard | 1.000 |
| pilot_debias_methods_deepseek_v4pro | deepseek_v4pro | pilot | 5376 | 5376 | exp2,exp3,sycophancy | anti_sycophancy_truth_first,constitutional_critic,counterfactual_consistency_vote,critique_revise,debate,frame_invariant_rationale,self_debias_reprompt,standard | 1.000 |
| pilot_deepseek_v4pro_methods | deepseek_v4pro | pilot | 1008 | 1008 | exp2,exp3,sycophancy | critique_revise,debate,standard | 1.000 |
| pilot_generated_qwen3_4b_debate_r1 | qwen3_4b_base | pilot | 120 | 120 | generated_moral,generated_sycophancy | debate | 1.000 |
| pilot_strict_qwen3_4b_debate_r4 | qwen3_4b_base | pilot | 56 | 56 | exp2,exp3,sycophancy | debate | 1.000 |
| smoke_deepseek_v4flash_methods_no_thinking | deepseek_v4flash | smoke | 36 | 36 | exp2 | critique_revise,debate,standard | 1.000 |

## Standard Bias Fingerprints

| model_id | analysis_tier | moral_bias_mean | yes_no_bias | omission_bias | sycophancy_accuracy | wrong_belief_agreement_rate |
| --- | --- | --- | --- | --- | --- | --- |
| aliyun_qwen36 | full | 0.383 | 0.356 | 0.411 | NA | NA |
| deepseek_chat | full | 0.613 | 0.628 | 0.598 | 0.906 | 0.125 |
| deepseek_chat | pilot | 0.745 | 0.781 | 0.708 | 0.982 | 0.000 |
| deepseek_v4flash | full | 0.715 | 0.759 | 0.671 | 0.984 | 0.000 |
| deepseek_v4flash | pilot | 0.734 | 0.771 | 0.698 | 0.982 | 0.000 |
| deepseek_v4flash | smoke | 1.000 | 1.000 | 1.000 | NA | NA |
| deepseek_v4pro | full | 0.781 | 0.780 | 0.781 | 0.855 | 0.172 |
| deepseek_v4pro | pilot | 0.788 | 0.785 | 0.792 | 0.812 | 0.295 |
| gemini25_flash | full | 0.400 | 0.430 | 0.369 | NA | NA |
| gemma4_31b_api | full | 0.167 | 0.167 | 0.167 | NA | NA |
| gemma4_e4b_base | full | 0.571 | 0.581 | 0.561 | 0.805 | 0.167 |
| gemma4_e4b_sft | full | 0.250 | 0.262 | 0.239 | 0.852 | 0.099 |
| qwen3_32b_local | exploratory | 0.193 | 0.360 | 0.027 | NA | NA |
| qwen3_4b_base | full | 0.806 | 0.778 | 0.833 | 0.812 | 0.229 |
| qwen3_4b_expanded_sft | full | 0.186 | 0.170 | 0.201 | 0.859 | 0.214 |
| qwen3_4b_expanded_sft_dpo | full | 0.134 | 0.000 | 0.268 | 0.875 | 0.250 |
| zhipu_glm51 | full | 0.780 | 0.726 | 0.833 | NA | NA |
| zhipu_glm51 | partial | 0.083 | 0.000 | 0.167 | NA | NA |

## Debias Responsiveness

| model_id | dataset | method_condition | moral_bias_reduction | sycophancy_accuracy_gain | wrong_belief_agreement_reduction | median_latency_seconds | analysis_tier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_v4flash | exp2 | counterfactual_consistency_vote | 0.979 | NA | NA | 2.505 | pilot |
| deepseek_v4flash | exp2 | debate | 0.875 | NA | NA | 6.827 | smoke |
| deepseek_v4pro | exp3 | counterfactual_consistency_vote | 0.861 | NA | NA | 3.796 | pilot |
| deepseek_v4pro | exp3 | counterfactual_consistency_vote | 0.827 | NA | NA | 3.796 | pilot |
| deepseek_v4flash | exp2 | critique_revise | 0.812 | NA | NA | 5.037 | pilot |
| deepseek_v4flash | exp3 | counterfactual_consistency_vote | 0.771 | NA | NA | 2.307 | pilot |
| deepseek_chat | exp3 | counterfactual_consistency_vote | 0.750 | NA | NA | 2.355 | pilot |
| qwen3_4b_base | exp2 | debate | 0.750 | NA | NA | 17.856 | pilot |
| deepseek_v4flash | exp2 | critique_revise | 0.740 | NA | NA | 5.021 | full |
| deepseek_v4pro | exp3 | constitutional_critic | 0.736 | NA | NA | 4.703 | pilot |
| deepseek_v4flash | exp3 | counterfactual_consistency_vote | 0.732 | NA | NA | 2.307 | pilot |
| deepseek_v4pro | exp3 | constitutional_critic | 0.702 | NA | NA | 4.703 | pilot |
| deepseek_v4pro | exp3 | debate | 0.694 | NA | NA | 14.511 | full |
| deepseek_v4flash | exp2 | anti_sycophancy_truth_first | 0.688 | NA | NA | 1.360 | pilot |
| deepseek_chat | exp3 | counterfactual_consistency_vote | 0.677 | NA | NA | 2.355 | pilot |
| deepseek_v4pro | exp2 | counterfactual_consistency_vote | 0.671 | NA | NA | 3.979 | pilot |
| deepseek_v4pro | exp3 | critique_revise | 0.669 | NA | NA | 9.164 | full |
| deepseek_v4flash | exp3 | debate | 0.667 | NA | NA | 7.837 | pilot |
| deepseek_chat | exp2 | counterfactual_consistency_vote | 0.667 | NA | NA | 2.525 | pilot |
| deepseek_v4pro | exp3 | debate | 0.661 | NA | NA | 14.511 | full |
| deepseek_v4pro | exp2 | counterfactual_consistency_vote | 0.653 | NA | NA | 3.979 | pilot |
| deepseek_v4pro | exp3 | critique_revise | 0.653 | NA | NA | 10.084 | pilot |
| deepseek_v4flash | exp2 | counterfactual_consistency_vote | 0.646 | NA | NA | 2.505 | pilot |
| deepseek_v4flash | exp2 | counterfactual_consistency_vote | 0.646 | NA | NA | 2.505 | pilot |
| deepseek_v4pro | exp3 | anti_sycophancy_truth_first | 0.642 | NA | NA | 2.236 | pilot |
| deepseek_v4flash | exp2 | debate | 0.635 | NA | NA | 6.647 | full |
| deepseek_v4pro | exp3 | critique_revise | 0.635 | NA | NA | 9.164 | full |
| deepseek_v4pro | exp2 | frame_invariant_rationale | 0.629 | NA | NA | 2.052 | pilot |
| deepseek_v4flash | exp3 | debate | 0.628 | NA | NA | 7.837 | pilot |
| deepseek_v4pro | exp3 | self_debias_reprompt | 0.622 | NA | NA | 5.259 | pilot |
| deepseek_v4pro | exp2 | self_debias_reprompt | 0.619 | NA | NA | 4.540 | pilot |
| deepseek_v4pro | exp3 | critique_revise | 0.619 | NA | NA | 10.084 | pilot |
| deepseek_v4flash | exp2 | debate | 0.615 | NA | NA | 7.892 | pilot |
| deepseek_v4pro | exp2 | frame_invariant_rationale | 0.611 | NA | NA | 2.052 | pilot |
| deepseek_v4pro | exp2 | debate | 0.610 | NA | NA | 14.217 | full |
| deepseek_v4pro | exp3 | anti_sycophancy_truth_first | 0.609 | NA | NA | 2.236 | pilot |
| deepseek_v4flash | exp3 | debate | 0.603 | NA | NA | 7.913 | full |
| deepseek_v4pro | exp2 | self_debias_reprompt | 0.601 | NA | NA | 4.540 | pilot |
| deepseek_chat | exp3 | debate | 0.594 | NA | NA | 7.857 | pilot |
| deepseek_v4pro | exp2 | debate | 0.592 | NA | NA | 14.217 | full |
| deepseek_v4pro | exp3 | debate | 0.590 | NA | NA | 15.533 | pilot |
| deepseek_v4pro | exp3 | self_debias_reprompt | 0.588 | NA | NA | 5.259 | pilot |
| deepseek_v4pro | exp2 | debate | 0.574 | NA | NA | 15.367 | pilot |
| deepseek_v4pro | exp2 | anti_sycophancy_truth_first | 0.567 | NA | NA | 2.265 | pilot |
| deepseek_v4flash | exp3 | debate | 0.564 | NA | NA | 7.913 | full |
| deepseek_v4pro | exp3 | debate | 0.557 | NA | NA | 15.533 | pilot |
| deepseek_v4pro | exp2 | debate | 0.556 | NA | NA | 15.367 | pilot |
| deepseek_chat | exp3 | anti_sycophancy_truth_first | 0.552 | NA | NA | 1.218 | pilot |
| deepseek_v4pro | exp2 | anti_sycophancy_truth_first | 0.549 | NA | NA | 2.265 | pilot |
| deepseek_v4pro | exp3 | frame_invariant_rationale | 0.549 | NA | NA | 2.176 | pilot |
| deepseek_v4flash | exp2 | debate | 0.542 | NA | NA | 6.827 | smoke |
| deepseek_v4flash | exp2 | debate | 0.542 | NA | NA | 6.827 | smoke |
| deepseek_v4pro | exp2 | constitutional_critic | 0.536 | NA | NA | 4.276 | pilot |
| deepseek_v4pro | exp2 | critique_revise | 0.534 | NA | NA | 8.881 | full |
| deepseek_chat | exp3 | constitutional_critic | 0.531 | NA | NA | 2.470 | pilot |
| deepseek_chat | exp3 | critique_revise | 0.531 | NA | NA | 4.842 | pilot |
| deepseek_v4pro | exp2 | critique_revise | 0.527 | NA | NA | 8.594 | partial |
| deepseek_chat | exp3 | debate | 0.521 | NA | NA | 7.857 | pilot |
| deepseek_v4pro | exp2 | constitutional_critic | 0.517 | NA | NA | 4.276 | pilot |
| deepseek_v4pro | exp2 | critique_revise | 0.516 | NA | NA | 8.881 | full |
| deepseek_v4pro | exp3 | frame_invariant_rationale | 0.515 | NA | NA | 2.176 | pilot |
| deepseek_v4flash | exp3 | anti_sycophancy_truth_first | 0.510 | NA | NA | 1.221 | pilot |
| deepseek_v4pro | exp2 | critique_revise | 0.508 | NA | NA | 8.594 | partial |
| deepseek_v4flash | exp2 | frame_invariant_rationale | 0.500 | NA | NA | 1.399 | pilot |
| deepseek_v4flash | exp3 | constitutional_critic | 0.500 | NA | NA | 2.426 | pilot |
| qwen3_4b_base | exp3 | debate | 0.500 | NA | NA | 18.656 | pilot |
| deepseek_chat | exp3 | anti_sycophancy_truth_first | 0.479 | NA | NA | 1.218 | pilot |
| deepseek_v4flash | exp2 | critique_revise | 0.479 | NA | NA | 5.037 | pilot |
| deepseek_v4flash | exp2 | critique_revise | 0.479 | NA | NA | 5.037 | pilot |
| deepseek_chat | exp2 | counterfactual_consistency_vote | 0.476 | NA | NA | 2.525 | pilot |
| deepseek_chat | exp3 | critique_revise | 0.476 | NA | NA | 9.569 | full |
| deepseek_v4flash | exp3 | critique_revise | 0.475 | NA | NA | 5.422 | full |
| deepseek_v4flash | exp3 | anti_sycophancy_truth_first | 0.472 | NA | NA | 1.221 | pilot |
| deepseek_v4flash | exp2 | constitutional_critic | 0.469 | NA | NA | 2.468 | pilot |
| deepseek_v4flash | exp3 | constitutional_critic | 0.461 | NA | NA | 2.426 | pilot |
| deepseek_chat | exp3 | constitutional_critic | 0.458 | NA | NA | 2.470 | pilot |
| deepseek_chat | exp3 | critique_revise | 0.458 | NA | NA | 4.842 | pilot |
| deepseek_chat | exp2 | critique_revise | 0.454 | NA | NA | 10.669 | full |
| deepseek_chat | exp2 | debate | 0.440 | NA | NA | NA | full |
| deepseek_v4flash | exp3 | critique_revise | 0.438 | NA | NA | 4.798 | pilot |

## Notes

- `analysis_tier=partial` rows are visible for monitoring but should not be used as confirmatory evidence.
- `moral_bias_reduction` is `standard - method`; positive means the method lowered framing bias.
- `wrong_belief_agreement_reduction` is `standard - method`; positive means less agreement with false user belief.
- Local SFT/DPO variants are listed as model variants, because their intervention is in the weights rather than only in the prompt protocol.
