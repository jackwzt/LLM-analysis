# Data Requirements

## Ideal Trial-Level Dataset

The ideal table for strong confirmatory analysis has one row per model response:

- `model_id`
- `model_family`
- `provider`
- `dataset`
- `item_id`
- `item_family_id`
- `framing_condition`
- `bias_type`
- `method_condition`
- `run_tier`
- `raw_final_output`
- `parsed_answer`
- `valid_response`
- `invariant_target`
- `answer_matches_invariant_target`
- `moral_bias_indicator`
- `sycophancy_indicator`
- `wrong_belief_agreement`
- `latency_seconds`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `run_id`
- `timestamp`
- `bundle_id`

## Essential Columns for Main Moral-Framing Analysis

- `model_id`
- `dataset`
- `item_id` or `item_family_id`
- `framing_condition`
- `method_condition`
- `parsed_answer`
- `valid_response`
- `invariant_target` or an equivalent bias label such as `endorse_original_action`
- `latency_seconds` if cost analysis is included
- `total_tokens` if cost analysis is included

## Essential Columns for Sycophancy Analysis

- `model_id`
- `dataset`
- `item_id` or `item_family_id`
- `framing_condition`
- `method_condition`
- `parsed_answer`
- `valid_response`
- `correct_answer` or `model_correct`
- `user_belief_answer`
- `agrees_with_user_belief` or equivalent
- `belief_matches_truth` if aligned/conflict splits are required

## Optional but Useful Columns

- `model_family`
- `provider`
- `run_tier`
- `analysis_tier`
- `source_run`
- `run_completion_rate`
- `prompt_tokens`
- `completion_tokens`
- `timestamp`
- `raw_final_output`
- `method_trace_json`

## Upload Exclusions

Do not upload:

- `.env`
- API keys
- raw credentials
- payment information
- private API logs
- unredacted sensitive provider traces
- model checkpoints unless intentionally released
- temporary cache files
- personal files

Raw trial-level outputs should be redacted or aggregated before upload if they contain sensitive prompts, private logs, raw provider payloads, or credentials.
