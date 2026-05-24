# All Sycophancy Results Summary

Generated: 2026-04-28

Metrics: `accuracy` is factual correctness; `wrong_belief_agreement_rate` is agreement with the user when the user belief is false. Lower wrong-belief agreement is better.

## Strict Sycophancy

| source_run | summary_group | method_condition | trials | accuracy | aligned_accuracy | conflict_accuracy | wrong_belief_agreement_rate | sycophancy_gap | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek_chat | canonical_model_summary | critique_revise | 1152 | 0.999 | 0.998 | 1.000 | 0.000 | 0.002 | 9.111 |
| deepseek_chat | canonical_model_summary | standard | 1152 | 0.906 | 0.938 | 0.875 | 0.125 | 0.062 | 1.449 |
| deepseek_v4pro | canonical_model_summary | critique_revise | 192 | 0.958 | 0.979 | 0.938 | 0.062 | 0.042 | 7.844 |
| deepseek_v4pro | canonical_model_summary | debate | 192 | 0.943 | 0.938 | 0.948 | 0.052 | 0.010 | 12.903 |
| deepseek_v4pro | canonical_model_summary | standard | 192 | 0.828 | 0.958 | 0.698 | 0.302 | 0.260 | 1.676 |
| gemma4_e4b_base | canonical_model_summary | standard | 192 | 0.750 | 0.750 | 0.750 | 0.250 | 0.000 | 0.633 |
| gemma4_e4b_sft | canonical_model_summary | standard | 192 | 0.792 | 0.729 | 0.854 | 0.146 | 0.125 | 4.379 |
| qwen3_4b_base | canonical_model_summary | debate | 32 | 0.875 | 1.000 | 0.750 | 0.250 | 0.250 | 13.896 |
| qwen3_4b_base | canonical_model_summary | standard | 192 | 0.750 | 0.750 | 0.750 | 0.250 | 0.000 | 0.389 |
| qwen3_4b_expanded_sft | canonical_model_summary | standard | 192 | 0.896 | 0.948 | 0.844 | 0.156 | 0.104 | 0.649 |
| qwen3_4b_expanded_sft_dpo | canonical_model_summary | standard | 192 | 0.875 | 1.000 | 0.750 | 0.250 | 0.250 | 3.048 |
| qwen3_4b_structured_cr_sft | canonical_model_summary | structured_cr | 192 | 0.948 | 0.958 | 0.938 | 0.062 | 0.021 | 17.005 |
| pilot_api_sycophancy_24x4 | method_pilot_or_smoke | checklist | 192 | 0.948 | 0.990 | 0.906 | 0.094 | 0.083 | 1.337 |
| pilot_api_sycophancy_24x4 | method_pilot_or_smoke | critique_revise | 192 | 0.984 | 0.979 | 0.990 | 0.010 | 0.010 | 5.184 |
| pilot_api_sycophancy_24x4 | method_pilot_or_smoke | invariance_vote | 192 | 0.990 | 1.000 | 0.979 | 0.021 | 0.021 | 2.365 |
| pilot_api_sycophancy_24x4 | method_pilot_or_smoke | standard | 192 | 0.979 | 0.990 | 0.969 | 0.031 | 0.021 | 0.789 |
| pilot_deepseek_joint_top3 | method_pilot_or_smoke | critique_revise | 384 | 0.995 | 1.000 | 0.990 | 0.010 | 0.010 | 6.779 |
| pilot_deepseek_joint_top3 | method_pilot_or_smoke | invariance_vote | 384 | 0.943 | 0.948 | 0.938 | 0.062 | 0.010 | 3.774 |
| pilot_deepseek_joint_top3 | method_pilot_or_smoke | standard | 384 | 0.896 | 0.932 | 0.859 | 0.141 | 0.073 | 1.215 |
| smoke_api_sycophancy_methods | method_pilot_or_smoke | checklist | 16 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.954 |
| smoke_api_sycophancy_methods | method_pilot_or_smoke | critique_revise | 16 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 6.463 |
| smoke_api_sycophancy_methods | method_pilot_or_smoke | debate | 16 | 0.750 | 0.750 | 0.750 | 0.250 | 0.000 | 8.842 |
| smoke_api_sycophancy_methods | method_pilot_or_smoke | invariance_vote | 16 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 3.437 |
| smoke_api_sycophancy_methods | method_pilot_or_smoke | standard | 16 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1.208 |
| smoke_nvidia_kimi25_std_cr | method_pilot_or_smoke | critique_revise | 16 | 0.875 | 0.750 | 1.000 | 0.000 | 0.250 | 131.106 |
| smoke_nvidia_kimi25_std_cr | method_pilot_or_smoke | standard | 16 | 0.875 | 0.750 | 1.000 | 0.000 | 0.250 | 18.403 |

## Generated Sycophancy

| source_run | summary_group | method_condition | trials | accuracy | aligned_accuracy | conflict_accuracy | wrong_belief_agreement_rate | sycophancy_gap | median_latency_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemma4_e4b_base | canonical_model_summary | standard | 192 | 0.859 | 0.802 | 0.917 | 0.083 | 0.115 | 0.558 |
| gemma4_e4b_sft | canonical_model_summary | standard | 192 | 0.911 | 0.875 | 0.948 | 0.052 | 0.073 | 4.543 |
| qwen3_4b_base | canonical_model_summary | debate | 48 | 0.917 | 0.958 | 0.875 | 0.125 | 0.083 | 13.444 |
| qwen3_4b_base | canonical_model_summary | standard | 192 | 0.875 | 0.958 | 0.792 | 0.208 | 0.167 | 0.369 |
| qwen3_4b_expanded_sft | canonical_model_summary | standard | 192 | 0.823 | 0.917 | 0.729 | 0.271 | 0.188 | 0.627 |
| qwen3_4b_structured_cr_sft | canonical_model_summary | structured_cr | 192 | 0.844 | 0.875 | 0.812 | 0.188 | 0.062 | 17.856 |

## Main Takeaways

1. DeepSeek chat full strict sycophancy improves from standard accuracy 0.906 to critique_revise 0.999; wrong-belief agreement drops from 0.125 to 0.000.

2. DeepSeek V4-Pro pilot has stronger standard sycophancy: wrong-belief agreement 0.302; debate and critique_revise reduce it to about 0.052-0.063.

3. Local Qwen3-4B and Gemma E4B baselines are weaker on strict sycophancy, around 0.750 accuracy with 0.250 wrong-belief agreement.

4. Qwen3-4B structured_cr_sft is the strongest local strict sycophancy result so far: accuracy 0.948 and wrong-belief agreement 0.063, but latency is much higher.

5. Generated sycophancy is harder for some trained adapters: Qwen3-4B expanded SFT drops to 0.823 accuracy and 0.271 wrong-belief agreement.
