# Model-Dataset-Method Heterogeneity Summary

Status: derived from confirmatory aggregate tables.

The current main full-cell subset is 42,912 rows. `anti_sycophancy_truth_first` is now included after the valid-only repair of DeepSeek V4-Flash full cells.

Effects should be interpreted by model and dataset, not as universal LLM claims.

## DeepSeek V4-Flash Anti-Sycophancy Truth-First

Observed reductions:

- `exp2`: moral bias mean = 0.366; reduction vs standard = 45.1%.
- `exp3`: moral bias mean = 0.275; reduction vs standard = 63.9%.

Required interpretation notes:

- DeepSeek V4-Flash `exp2` reduction is 45.1%.
- DeepSeek V4-Flash `exp3` reduction is 63.9%.
- Sycophancy wrong-belief agreement has a floor effect for DeepSeek V4-Flash because the standard condition is already 0.000.
- `counterfactual_consistency_vote` is a consistency-enforcement procedure; it should not be interpreted as eliminating internal model bias.
- Moral tasks do not have objective correctness labels, so the analysis uses framing-gap reduction rather than moral accuracy.

## Table Preview

```text
        model_id model_family dataset                method_condition          analysis_tier  n_trials  n_valid  valid_rate  moral_bias_mean  reduction_vs_standard  moral_bias_reduction_pct  bootstrap_ci_low  bootstrap_ci_high  latency_multiplier_vs_standard  token_multiplier_vs_standard  value_score
   aliyun_qwen36         Qwen    exp2                          debate confirmatory_full_cell      1008     1008    1.000000         0.165179               0.072917                  0.306250          0.002976           0.328869                             NaN                           NaN          NaN
   aliyun_qwen36         Qwen    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.238095               0.000000                  0.000000          0.000000           0.547619                             NaN                           NaN          NaN
   aliyun_qwen36         Qwen    exp3                          debate confirmatory_full_cell      1008     1008    1.000000         0.232143               0.296131                  0.560563          0.102679           0.361756                             NaN                           NaN          NaN
   aliyun_qwen36         Qwen    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.528274               0.000000                  0.000000          0.223214           0.833333                             NaN                           NaN          NaN
   deepseek_chat     DeepSeek    exp2                          debate confirmatory_full_cell      1008     1008    1.000000         0.226190               0.250000                  0.525000          0.122024           0.321429                             NaN                           NaN          NaN
   deepseek_chat     DeepSeek    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.476190               0.000000                  0.000000          0.166667           0.760417                             NaN                           NaN          NaN
   deepseek_chat     DeepSeek    exp3                          debate confirmatory_full_cell      1008     1008    1.000000         0.421131               0.328869                  0.438492          0.239583           0.602679                             NaN                           NaN          NaN
   deepseek_chat     DeepSeek    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.750000               0.000000                  0.000000          0.416667           1.000000                             NaN                           NaN          NaN
deepseek_v4flash     DeepSeek    exp2     anti_sycophancy_truth_first confirmatory_full_cell      1008     1008    1.000000         0.366071               0.300595                  0.450893          0.074405           0.680097                        2.398560                      1.160444     0.168921
deepseek_v4flash     DeepSeek    exp2                          debate confirmatory_full_cell      1008     1008    1.000000         0.364583               0.302083                  0.453125          0.229018           0.497061                        9.990497                      5.790111     0.038285
deepseek_v4flash     DeepSeek    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.666667               0.000000                  0.000000          0.333333           1.000000                        1.000000                      1.000000     0.000000
deepseek_v4flash     DeepSeek    exp3     anti_sycophancy_truth_first confirmatory_full_cell      1008     1008    1.000000         0.275298               0.488095                  0.639376          0.071429           0.574405                        2.006972                      1.176600     0.306634
deepseek_v4flash     DeepSeek    exp3                          debate confirmatory_full_cell      1008     1008    1.000000         0.199405               0.563988                  0.738791          0.116071           0.323103                        9.911612                      6.019868     0.070802
deepseek_v4flash     DeepSeek    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.763393               0.000000                  0.000000          0.684524           0.870573                        1.000000                      1.000000     0.000000
  gemini25_flash Gemini/Gemma    exp2                          debate confirmatory_full_cell      1008     1007    0.999008         0.142722              -0.023674                 -0.198864          0.020833           0.291569                             NaN                           NaN          NaN
  gemini25_flash Gemini/Gemma    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.119048               0.000000                  0.000000          0.017857           0.267857                             NaN                           NaN          NaN
  gemini25_flash Gemini/Gemma    exp3                          debate confirmatory_full_cell      1008     1008    1.000000         0.269345               0.410714                  0.603939          0.066964           0.480655                             NaN                           NaN          NaN
  gemini25_flash Gemini/Gemma    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.680060               0.000000                  0.000000          0.492374           0.848214                             NaN                           NaN          NaN
      gemma4_31b Gemini/Gemma    exp2                          debate confirmatory_full_cell      1008     1008    1.000000         0.113095               0.053571                  0.321429          0.010417           0.266369                             NaN                           NaN          NaN
      gemma4_31b Gemini/Gemma    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.166667               0.000000                  0.000000          0.000000           0.333333                             NaN                           NaN          NaN
      gemma4_31b Gemini/Gemma    exp3                          debate confirmatory_full_cell      1008     1008    1.000000         0.339286              -0.005952                 -0.017857          0.092188           0.666667                             NaN                           NaN          NaN
      gemma4_31b Gemini/Gemma    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.333333               0.000000                  0.000000          0.083333           0.666667                             NaN                           NaN          NaN
 gemma4_e4b_base Gemini/Gemma    exp2 counterfactual_consistency_vote confirmatory_full_cell      1008     1008    1.000000         0.000000               0.776786                  1.000000          0.000000           0.000000                        2.977777                      3.082613     0.256348
 gemma4_e4b_base Gemini/Gemma    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.776786               0.000000                  0.000000          0.497024           1.000000                        1.000000                      1.000000     0.000000
 gemma4_e4b_base Gemini/Gemma    exp3 counterfactual_consistency_vote confirmatory_full_cell      1008     1008    1.000000         0.000000               0.714286                  1.000000          0.000000           0.000000                        2.964966                      3.160638     0.233213
 gemma4_e4b_base Gemini/Gemma    exp3                        standard confirmatory_full_cell      1008     1008    1.000000         0.714286               0.000000                  0.000000          0.475893           0.916667                        1.000000                      1.000000     0.000000
   qwen3_32b_awq         Qwen    exp2                          debate confirmatory_full_cell      1008     1007    0.999008         0.275298              -0.081845                 -0.423077          0.129464           0.434524                             NaN                           NaN          NaN
   qwen3_32b_awq         Qwen    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         0.193452               0.000000                  0.000000          0.026786           0.386905                             NaN                           NaN          NaN
   qwen3_4b_base         Qwen    exp2 counterfactual_consistency_vote confirmatory_full_cell      1008     1008    1.000000         0.000000               1.000000                  1.000000          0.000000           0.000000                        3.180617                      3.100195     0.318430
   qwen3_4b_base         Qwen    exp2                        standard confirmatory_full_cell      1008     1008    1.000000         1.000000               0.000000                  0.000000          1.000000           1.000000                        1.000000                      1.000000     0.000000
```