# Debias Method Pilot Report

Scope: DeepSeek V4-Pro, V4-Flash, and DeepSeek Chat pilot runs over exp2, exp3, and sycophancy.

## Recommended New Methods For Full Confirmatory

| method_condition | recommendation_reason | moral_bias_reduction_pct | wrong_belief_agreement_reduction | latency_multiplier_vs_standard | token_multiplier_vs_standard | value_score |
| --- | --- | --- | --- | --- | --- | --- |
| counterfactual_consistency_vote | best_moral_framing_reduction | 0.960 | 0.097 | 2.827 | 3.137 | 0.329 |
| anti_sycophancy_truth_first | best_cost_adjusted_value | 0.630 | 0.087 | 1.523 | 1.164 | 0.567 |
| constitutional_critic | next_best_effect_score | 0.556 | 0.075 | 3.057 | 2.344 | 0.245 |


## Aggregate Method Ranking

| method_condition | moral_bias_reduction_pct | wrong_belief_agreement_reduction | sycophancy_accuracy | latency_multiplier_vs_standard | token_multiplier_vs_standard | value_score |
| --- | --- | --- | --- | --- | --- | --- |
| anti_sycophancy_truth_first | 0.630 | 0.087 | 0.983 | 1.523 | 1.164 | 0.567 |
| frame_invariant_rationale | 0.477 | 0.076 | 0.971 | 1.549 | 1.154 | 0.467 |
| counterfactual_consistency_vote | 0.960 | 0.097 | 0.998 | 2.827 | 3.137 | 0.329 |
| constitutional_critic | 0.556 | 0.075 | 0.974 | 3.057 | 2.344 | 0.245 |
| self_debias_reprompt | 0.440 | 0.076 | 0.979 | 3.070 | 2.290 | 0.229 |
| critique_revise | 0.635 | 0.083 | 0.976 | 6.019 | 3.801 | 0.129 |
| debate | 0.625 | 0.069 | 0.957 | 9.799 | 5.983 | 0.079 |


## Model-Level Detailed Results

| model_id | dataset | method_condition | valid_rate | moral_bias_mean | moral_bias_reduction | sycophancy_accuracy | wrong_belief_agreement_rate | median_latency_seconds | median_total_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_chat | exp2 | anti_sycophancy_truth_first | 1.000 | 0.385 | 0.281 | NA | NA | 1.372 | 573.500 |
| deepseek_chat | exp2 | constitutional_critic | 1.000 | 0.479 | 0.187 | NA | NA | 2.435 | 1148.500 |
| deepseek_chat | exp2 | counterfactual_consistency_vote | 1.000 | 0.000 | 0.667 | NA | NA | 2.525 | 1541.000 |
| deepseek_chat | exp2 | critique_revise | 1.000 | 0.250 | 0.417 | NA | NA | 5.039 | 1861.000 |
| deepseek_chat | exp2 | debate | 1.000 | 0.427 | 0.240 | NA | NA | 7.764 | 2870.000 |
| deepseek_chat | exp2 | frame_invariant_rationale | 1.000 | 0.562 | 0.104 | NA | NA | 1.389 | 568.000 |
| deepseek_chat | exp2 | self_debias_reprompt | 1.000 | 0.573 | 0.094 | NA | NA | 2.492 | 1126.500 |
| deepseek_chat | exp2 | standard | 1.000 | 0.667 | 0.000 | NA | NA | 0.911 | 495.500 |
| deepseek_chat | exp3 | anti_sycophancy_truth_first | 1.000 | 0.271 | 0.552 | NA | NA | 1.218 | 533.500 |
| deepseek_chat | exp3 | constitutional_critic | 1.000 | 0.292 | 0.531 | NA | NA | 2.470 | 1068.000 |
| deepseek_chat | exp3 | counterfactual_consistency_vote | 1.000 | 0.073 | 0.750 | NA | NA | 2.355 | 1433.500 |
| deepseek_chat | exp3 | critique_revise | 1.000 | 0.292 | 0.531 | NA | NA | 4.842 | 1742.000 |
| deepseek_chat | exp3 | debate | 1.000 | 0.229 | 0.594 | NA | NA | 7.857 | 2745.000 |
| deepseek_chat | exp3 | frame_invariant_rationale | 1.000 | 0.438 | 0.385 | NA | NA | 1.283 | 528.500 |
| deepseek_chat | exp3 | self_debias_reprompt | 1.000 | 0.469 | 0.354 | NA | NA | 2.466 | 1047.000 |
| deepseek_chat | exp3 | standard | 1.000 | 0.823 | 0.000 | NA | NA | 0.796 | 453.000 |
| deepseek_chat | sycophancy | anti_sycophancy_truth_first | 1.000 | NA | NA | 0.979 | 0.000 | 0.910 | 264.000 |
| deepseek_chat | sycophancy | constitutional_critic | 1.000 | NA | NA | 0.979 | 0.000 | 1.766 | 532.000 |
| deepseek_chat | sycophancy | counterfactual_consistency_vote | 1.000 | NA | NA | 0.995 | 0.000 | 1.468 | 430.000 |
| deepseek_chat | sycophancy | critique_revise | 1.000 | NA | NA | 0.992 | 0.000 | 3.524 | 900.500 |
| deepseek_chat | sycophancy | debate | 1.000 | NA | NA | 0.979 | 0.000 | 5.678 | 1561.000 |
| deepseek_chat | sycophancy | frame_invariant_rationale | 1.000 | NA | NA | 0.992 | 0.000 | 0.921 | 261.000 |
| deepseek_chat | sycophancy | self_debias_reprompt | 1.000 | NA | NA | 0.984 | 0.000 | 1.810 | 506.500 |
| deepseek_chat | sycophancy | standard | 1.000 | NA | NA | 0.982 | 0.000 | 0.759 | 191.500 |
| deepseek_v4flash | exp2 | anti_sycophancy_truth_first | 1.000 | 0.312 | 0.354 | NA | NA | 1.360 | 574.500 |
| deepseek_v4flash | exp2 | constitutional_critic | 1.000 | 0.531 | 0.135 | NA | NA | 2.468 | 1148.500 |
| deepseek_v4flash | exp2 | counterfactual_consistency_vote | 1.000 | 0.021 | 0.646 | NA | NA | 2.505 | 1541.000 |
| deepseek_v4flash | exp2 | critique_revise | 1.000 | 0.188 | 0.479 | NA | NA | 5.037 | 1857.000 |
| deepseek_v4flash | exp2 | debate | 1.000 | 0.385 | 0.281 | NA | NA | 7.892 | 2875.000 |
| deepseek_v4flash | exp2 | frame_invariant_rationale | 1.000 | 0.500 | 0.167 | NA | NA | 1.399 | 569.000 |
| deepseek_v4flash | exp2 | self_debias_reprompt | 1.000 | 0.646 | 0.021 | NA | NA | 2.444 | 1123.500 |
| deepseek_v4flash | exp2 | standard | 1.000 | 0.667 | 0.000 | NA | NA | 0.898 | 495.500 |
| deepseek_v4flash | exp3 | anti_sycophancy_truth_first | 1.000 | 0.292 | 0.510 | NA | NA | 1.221 | 533.000 |
| deepseek_v4flash | exp3 | constitutional_critic | 1.000 | 0.302 | 0.500 | NA | NA | 2.426 | 1073.000 |
| deepseek_v4flash | exp3 | counterfactual_consistency_vote | 1.000 | 0.031 | 0.771 | NA | NA | 2.307 | 1433.500 |
| deepseek_v4flash | exp3 | critique_revise | 1.000 | 0.365 | 0.438 | NA | NA | 4.798 | 1748.500 |
| deepseek_v4flash | exp3 | debate | 1.000 | 0.135 | 0.667 | NA | NA | 7.837 | 2699.000 |
| deepseek_v4flash | exp3 | frame_invariant_rationale | 1.000 | 0.417 | 0.385 | NA | NA | 1.286 | 530.500 |
| deepseek_v4flash | exp3 | self_debias_reprompt | 1.000 | 0.427 | 0.375 | NA | NA | 2.451 | 1058.500 |
| deepseek_v4flash | exp3 | standard | 1.000 | 0.802 | 0.000 | NA | NA | 0.805 | 453.000 |
| deepseek_v4flash | sycophancy | anti_sycophancy_truth_first | 1.000 | NA | NA | 0.987 | 0.000 | 0.915 | 263.000 |
| deepseek_v4flash | sycophancy | constitutional_critic | 1.000 | NA | NA | 0.979 | 0.000 | 1.783 | 532.000 |
| deepseek_v4flash | sycophancy | counterfactual_consistency_vote | 1.000 | NA | NA | 1.000 | 0.000 | 1.464 | 430.000 |
| deepseek_v4flash | sycophancy | critique_revise | 1.000 | NA | NA | 0.987 | 0.005 | 3.469 | 898.500 |
| deepseek_v4flash | sycophancy | debate | 1.000 | NA | NA | 0.974 | 0.005 | 5.662 | 1558.000 |
| deepseek_v4flash | sycophancy | frame_invariant_rationale | 1.000 | NA | NA | 0.992 | 0.000 | 0.914 | 260.500 |
| deepseek_v4flash | sycophancy | self_debias_reprompt | 1.000 | NA | NA | 0.987 | 0.000 | 1.825 | 507.000 |
| deepseek_v4flash | sycophancy | standard | 1.000 | NA | NA | 0.982 | 0.000 | 0.748 | 191.500 |
| deepseek_v4pro | exp2 | anti_sycophancy_truth_first | 1.000 | 0.146 | 0.552 | NA | NA | 2.265 | 570.000 |
| deepseek_v4pro | exp2 | constitutional_critic | 1.000 | 0.177 | 0.521 | NA | NA | 4.276 | 1154.500 |
| deepseek_v4pro | exp2 | counterfactual_consistency_vote | 1.000 | 0.042 | 0.656 | NA | NA | 3.979 | 1541.000 |
| deepseek_v4pro | exp2 | critique_revise | 1.000 | 0.302 | 0.396 | NA | NA | 9.259 | 1856.500 |
| deepseek_v4pro | exp2 | debate | 1.000 | 0.146 | 0.552 | NA | NA | 15.112 | 2977.000 |
| deepseek_v4pro | exp2 | frame_invariant_rationale | 1.000 | 0.083 | 0.615 | NA | NA | 2.052 | 564.500 |
| deepseek_v4pro | exp2 | self_debias_reprompt | 1.000 | 0.094 | 0.604 | NA | NA | 4.540 | 1123.000 |
| deepseek_v4pro | exp2 | standard | 1.000 | 0.698 | 0.000 | NA | NA | 1.333 | 495.500 |
| deepseek_v4pro | exp3 | anti_sycophancy_truth_first | 1.000 | 0.240 | 0.646 | NA | NA | 2.236 | 529.000 |
| deepseek_v4pro | exp3 | constitutional_critic | 1.000 | 0.146 | 0.740 | NA | NA | 4.703 | 1077.000 |
| deepseek_v4pro | exp3 | counterfactual_consistency_vote | 1.000 | 0.021 | 0.865 | NA | NA | 3.796 | 1433.500 |
| deepseek_v4pro | exp3 | critique_revise | 1.000 | 0.260 | 0.625 | NA | NA | 9.898 | 1757.500 |
| deepseek_v4pro | exp3 | debate | 1.000 | 0.333 | 0.552 | NA | NA | 15.320 | 2846.500 |
| deepseek_v4pro | exp3 | frame_invariant_rationale | 1.000 | 0.333 | 0.552 | NA | NA | 2.176 | 525.500 |
| deepseek_v4pro | exp3 | self_debias_reprompt | 1.000 | 0.260 | 0.625 | NA | NA | 5.259 | 1044.500 |
| deepseek_v4pro | exp3 | standard | 1.000 | 0.885 | 0.000 | NA | NA | 1.456 | 453.000 |
| deepseek_v4pro | sycophancy | anti_sycophancy_truth_first | 1.000 | NA | NA | 0.982 | 0.031 | 2.144 | 263.000 |
| deepseek_v4pro | sycophancy | constitutional_critic | 1.000 | NA | NA | 0.964 | 0.068 | 3.496 | 532.000 |
| deepseek_v4pro | sycophancy | counterfactual_consistency_vote | 1.000 | NA | NA | 1.000 | 0.000 | 2.653 | 430.000 |
| deepseek_v4pro | sycophancy | critique_revise | 1.000 | NA | NA | 0.948 | 0.036 | 8.799 | 916.000 |
| deepseek_v4pro | sycophancy | debate | 1.000 | NA | NA | 0.917 | 0.078 | 13.606 | 1613.000 |
| deepseek_v4pro | sycophancy | frame_invariant_rationale | 1.000 | NA | NA | 0.930 | 0.062 | 2.592 | 259.000 |
| deepseek_v4pro | sycophancy | self_debias_reprompt | 1.000 | NA | NA | 0.966 | 0.062 | 4.068 | 506.500 |
| deepseek_v4pro | sycophancy | standard | 1.000 | NA | NA | 0.805 | 0.292 | 1.324 | 191.500 |
