from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "reports" / "human_ai_moral_debiasing_2026-04-18"
TABLE_DIR = REPORT_DIR / "tables"
FIGURE_DIR = REPORT_DIR / "figures"


MODEL_LABELS = {
    "qwen3_4b_base_promptfix": "Base Qwen3-4B",
    "strict_short_reason_promptfix": "Old short-reason adapter",
    "expanded_sft": "Expanded SFT adapter",
    "expanded_sft_dpo": "Expanded SFT + DPO adapter",
    "qwen3_4b_base_generated_r4": "Base Qwen3-4B",
    "short_reason_generated_r4": "Old short-reason adapter",
    "expanded_sft_generated_r4": "Expanded SFT adapter",
}


def fmt(value, digits: int = 3) -> str:
    if pd.isna(value):
        return ""
    return f"{float(value):.{digits}f}"


def load_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    strict_path = (
        PROJECT_ROOT
        / "results"
        / "strict_item_qwen3_4b_v2_expanded_comparison"
        / "strict_v2_expanded_comparison_summary.csv"
    )
    generated_path = (
        PROJECT_ROOT
        / "results"
        / "generated_qwen3_4b_v2_sft_expanded_r4_comparison"
        / "generated_v2_sft_expanded_comparison_summary.csv"
    )
    return pd.read_csv(strict_path), pd.read_csv(generated_path)


def build_strict_table(strict: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "qwen3_4b_base_promptfix",
        "strict_short_reason_promptfix",
        "expanded_sft",
        "expanded_sft_dpo",
    ]
    frame = strict[strict["model_variant"].isin(keep)].copy()
    frame["Model"] = frame["model_variant"].map(MODEL_LABELS)
    frame["Moral bias mean"] = frame["moral_bias_mean"].map(fmt)
    frame["Yes-no bias"] = frame["yes_no_bias"].map(fmt)
    frame["Omission bias"] = frame["omission_bias"].map(fmt)
    frame["Sycophancy accuracy"] = frame["overall_accuracy"].map(fmt)
    frame["Wrong-belief agreement"] = frame["wrong_belief_agreement_rate"].map(fmt)
    frame["Valid rate"] = frame["valid_rate"].map(fmt)
    frame["Latency vs base"] = frame["latency_x_base"].map(lambda value: "" if pd.isna(value) else f"{float(value):.2f}x")
    return frame[
        [
            "Model",
            "Moral bias mean",
            "Yes-no bias",
            "Omission bias",
            "Sycophancy accuracy",
            "Wrong-belief agreement",
            "Valid rate",
            "Latency vs base",
        ]
    ]


def build_generated_table(generated: pd.DataFrame) -> pd.DataFrame:
    keep = generated["dataset"].isin(["overall_moral", "overall_sycophancy"])
    frame = generated[keep].copy()
    frame["Model"] = frame["model_variant"].map(MODEL_LABELS)
    frame["Evaluation"] = frame["dataset"].map(
        {"overall_moral": "Generated moral dilemmas", "overall_sycophancy": "Generated sycophancy claims"}
    )
    frame["Moral bias mean"] = frame["moral_bias_mean"].map(fmt)
    frame["Yes-no bias"] = frame["yes_no_bias"].map(fmt)
    frame["Omission bias"] = frame["omission_bias"].map(fmt)
    frame["Sycophancy accuracy"] = frame["overall_accuracy"].map(fmt)
    frame["Wrong-belief agreement"] = frame["wrong_belief_agreement_rate"].map(fmt)
    frame["Valid rate"] = frame["valid_rate"].map(fmt)
    frame["Latency vs base"] = frame["latency_x_base"].map(lambda value: "" if pd.isna(value) else f"{float(value):.2f}x")
    return frame[
        [
            "Model",
            "Evaluation",
            "Moral bias mean",
            "Yes-no bias",
            "Omission bias",
            "Sycophancy accuracy",
            "Wrong-belief agreement",
            "Valid rate",
            "Latency vs base",
        ]
    ]


def write_tables(strict: pd.DataFrame, generated: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    strict_table = build_strict_table(strict)
    generated_table = build_generated_table(generated)
    strict_table.to_csv(TABLE_DIR / "table_1_strict_heldout_model_comparison.csv", index=False)
    generated_table.to_csv(TABLE_DIR / "table_2_generated_external_robustness.csv", index=False)
    (TABLE_DIR / "table_1_strict_heldout_model_comparison.md").write_text(
        dataframe_to_markdown(strict_table), encoding="utf-8"
    )
    (TABLE_DIR / "table_2_generated_external_robustness.md").write_text(
        dataframe_to_markdown(generated_table), encoding="utf-8"
    )
    return strict_table, generated_table


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    rows = [[str(value) for value in frame.columns]]
    rows.extend([["" if pd.isna(value) else str(value) for value in record] for record in frame.to_numpy()])
    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]

    def render_row(row: list[str]) -> str:
        cells = [f" {cell.ljust(widths[index])} " for index, cell in enumerate(row)]
        return "|" + "|".join(cells) + "|"

    header = render_row(rows[0])
    separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    body = [render_row(row) for row in rows[1:]]
    return "\n".join([header, separator, *body])


def build_conceptual_figure() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    boxes = [
        (0.05, 0.62, 0.20, 0.20, "Moral dilemma\nframing variant\n(original / yes-no / omission)", "#f3f4f6"),
        (0.33, 0.73, 0.22, 0.17, "Biased AI advice\nBase Qwen3-4B", "#fee2e2"),
        (0.33, 0.46, 0.22, 0.17, "Debiased AI advice\nExpanded SFT adapter", "#dcfce7"),
        (0.63, 0.62, 0.22, 0.20, "Human moral judgment\ninitial -> final\nconfidence + reliance", "#e0f2fe"),
        (0.42, 0.12, 0.30, 0.18, "Key test\nDoes debiased advice reduce\nhuman framing gaps?", "#fef3c7"),
    ]
    for x, y, w, h, text, color in boxes:
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#374151", linewidth=1.4)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=11)

    arrows = [
        ((0.25, 0.72), (0.33, 0.81)),
        ((0.25, 0.72), (0.33, 0.55)),
        ((0.55, 0.81), (0.63, 0.72)),
        ((0.55, 0.55), (0.63, 0.72)),
        ((0.74, 0.62), (0.57, 0.30)),
    ]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.8, color="#374151"))

    ax.text(
        0.5,
        0.96,
        "Model-level debiasing as an intervention in human-AI moral judgment",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.04,
        "Planned human study: compare base-model advice against expanded-SFT advice, then model final judgments and reliance.",
        ha="center",
        va="center",
        fontsize=10,
        color="#4b5563",
    )
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "figure_1_human_ai_moral_judgment_pipeline.png", dpi=220)
    fig.savefig(FIGURE_DIR / "figure_1_human_ai_moral_judgment_pipeline.pdf")
    plt.close(fig)


def markdown_table(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_paper_draft(strict_table: pd.DataFrame, generated_table: pd.DataFrame) -> None:
    strict_md = markdown_table(TABLE_DIR / "table_1_strict_heldout_model_comparison.md")
    generated_md = markdown_table(TABLE_DIR / "table_2_generated_external_robustness.md")
    draft = f"""# LLM Debiasing and Human Moral Judgment: A Two-Stage Study Plan

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

{strict_md}

Table 2 shows a more cautious result on generated external items. The expanded SFT adapter improved generated moral bias only modestly relative to the base model and did not outperform the base model on generated sycophancy accuracy. This result is theoretically important: model-level debiasing can be strong on original held-out items while remaining unstable under external distribution shift.

**Table 2. Generated external robustness comparison**

{generated_md}

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
Generated on {date.today().isoformat()} from local experiment outputs in `results/`.
"""
    (REPORT_DIR / "paper_draft.md").write_text(draft, encoding="utf-8")


def write_appendix() -> None:
    appendix = """# Appendix: Planned Human-AI Moral Judgment Protocol

## Purpose
This protocol tests whether model-level debiasing transfers to human moral judgment. Participants receive AI advice from either the base Qwen3-4B model or the expanded SFT adapter, then make final moral judgments.

## Conditions
- `AI_condition = base_advice`: advice generated by base Qwen3-4B.
- `AI_condition = debiased_advice`: advice generated by Qwen3-4B expanded SFT.
- `framing = original / yesno / omission`.

## Trial Flow
1. Present the moral dilemma in one framing variant.
2. Ask for initial judgment: `Yes` or `No`.
3. Ask initial confidence on a 1-7 scale.
4. Present AI advice: one concise reason plus `Final answer: Yes/No`.
5. Ask for final judgment: `Yes` or `No`.
6. Ask final confidence on a 1-7 scale.
7. Ask reliance/helpfulness/trust ratings on 1-7 scales.

## Randomization
- Participants are randomly assigned to base-advice or debiased-advice condition.
- Each participant sees only one framing version of each dilemma.
- Framing assignment is counterbalanced so each dilemma appears equally often in original, yes-no, and omission forms across participants.
- Trial order is randomized.

## Variables
- `participant_id`: anonymized participant identifier.
- `dilemma_id`: item identifier.
- `framing`: original, yesno, or omission.
- `AI_condition`: base_advice or debiased_advice.
- `initial_answer`: participant yes/no before AI advice.
- `final_answer`: participant yes/no after AI advice.
- `AI_answer`: AI final answer.
- `endorse_original_action_initial`: remapped initial answer.
- `endorse_original_action_final`: remapped final answer.
- `changed_answer`: whether initial and final answers differ.
- `changed_to_AI_answer`: whether final answer matches AI answer after an initial mismatch.
- `initial_confidence`, `final_confidence`: 1-7 ratings.
- `reliance_rating`, `helpfulness_rating`, `trust_rating`: 1-7 ratings.

## Planned Primary Model
Logistic mixed-effects model:

`endorse_original_action_final ~ AI_condition * framing + (1 | participant_id) + (1 | dilemma_id)`

Primary inference: whether framing gaps are smaller under debiased AI advice than base AI advice.

## Planned Secondary Models
Judgment shift:

`changed_to_AI_answer ~ AI_condition + framing + helpfulness_rating + trust_rating + initial_confidence + (1 | participant_id) + (1 | dilemma_id)`

Reliance:

`reliance_rating ~ AI_condition + framing + (1 | participant_id) + (1 | dilemma_id)`

Confidence change:

`final_confidence - initial_confidence ~ AI_condition + framing + (1 | participant_id) + (1 | dilemma_id)`

## Exclusion Rules
- Exclude participants who fail attention checks.
- Exclude participants with implausibly short completion time.
- Exclude trials with missing initial or final yes/no answer.
- Do not exclude participants based on whether they agree with the AI.

## Interpretation Rules
- If debiased advice reduces final framing gaps, this supports human-level transfer of model debiasing.
- If model-level improvements do not reduce human framing gaps, conclude that model debiasing does not automatically improve human-AI moral alignment.
- If debiased advice increases reliance without improving consistency, report this as a risk of persuasive but insufficiently robust AI advice.
"""
    (REPORT_DIR / "human_study_protocol_appendix.md").write_text(appendix, encoding="utf-8")


def write_readme() -> None:
    readme = """# Human-AI Moral Debiasing Research Package

This folder reframes the project around a clear research goal: testing whether model-level debiasing improves human moral judgment under AI advice.

## Files
- `paper_draft.md`: paper-style draft with Introduction, Study 1, planned Study 2, Discussion, and limitations.
- `human_study_protocol_appendix.md`: executable planned protocol for the future human experiment.
- `tables/table_1_strict_heldout_model_comparison.csv`: strict held-out model results.
- `tables/table_2_generated_external_robustness.csv`: generated external robustness results.
- `figures/figure_1_human_ai_moral_judgment_pipeline.png`: conceptual pipeline figure.
- `figures/figure_1_human_ai_moral_judgment_pipeline.pdf`: PDF version of the conceptual figure.

## Current conclusion
The expanded SFT adapter is the best current advice model for a planned human study. It strongly reduces strict held-out moral framing bias, but external generated tests show limited robustness. The next scientific question is therefore not just whether a model can be debiased, but whether debiased AI advice changes human moral judgment.
"""
    (REPORT_DIR / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    strict, generated = load_results()
    strict_table, generated_table = write_tables(strict, generated)
    build_conceptual_figure()
    write_paper_draft(strict_table, generated_table)
    write_appendix()
    write_readme()
    print(f"Wrote research package to: {REPORT_DIR}")


if __name__ == "__main__":
    main()
