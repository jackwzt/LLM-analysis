# Human-AI Moral Debiasing Research Package

This folder reframes the project around a clear research goal: testing whether model-level debiasing improves human moral judgment under AI advice.

## Files
- `paper_draft.md`: paper-style draft with Introduction, Study 1, planned Study 2, Discussion, and limitations.
- `summer_school_abstract_150w.md`: revised short abstract for summer school submission.
- `human_study_protocol_appendix.md`: executable planned protocol for the future human experiment.
- `tables/table_1_strict_heldout_model_comparison.csv`: strict held-out model results.
- `tables/table_2_generated_external_robustness.csv`: generated external robustness results.
- `figures/figure_1_human_ai_moral_judgment_pipeline.png`: conceptual pipeline figure.
- `figures/figure_1_human_ai_moral_judgment_pipeline.pdf`: PDF version of the conceptual figure.
- `poster/a0_poster_human_ai_moral_debiasing.pdf`: English A0 summer school poster focused on human-AI transfer.
- `poster/a0_poster_human_ai_moral_debiasing.png`: PNG preview of the A0 summer school poster.

## Current conclusion
The expanded SFT adapter is the best current advice model for a planned human study. It strongly reduces strict held-out moral framing bias, but external generated tests show limited robustness. The next scientific question is therefore not just whether a model can be debiased, but whether debiased AI advice changes human moral judgment.
