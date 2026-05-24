from __future__ import annotations

from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "reports" / "human_ai_moral_debiasing_2026-04-18" / "poster"

BG = "#f7f3ea"
INK = "#17212b"
MUTED = "#53606c"
BLUE = "#1f5f8b"
TEAL = "#0f766e"
ORANGE = "#c76a1a"
RED = "#b42318"
GREEN = "#15803d"
CARD = "#fffdf8"
LINE = "#d6cfc2"


TITLE = "From Model-Level Debiasing to Human-AI Moral Judgment"
SUBTITLE = "Testing whether less biased AI advice reduces human moral framing effects"
AUTHOR_LINE = "Summer school poster based on completed model-level experiments and a planned human-AI transfer study"

ABSTRACT = (
    "Large language models (LLMs) are increasingly used as advisors in morally consequential situations, yet their "
    "judgments can shift across logically equivalent action-omission and yes-no framings. This project first tests "
    "whether model-level interventions reduce these moral framing biases, then asks whether less biased AI advice "
    "transfers to human moral judgment. In the completed computational study, I evaluated standard responses, "
    "structured multi-persona debate prompts, supervised fine-tuning (SFT), and DPO across Qwen3-4B and API models. "
    "Debate prompts reduced bias in several API models but were model-dependent. The expanded SFT adapter produced "
    "the strongest strict held-out reduction, lowering moral bias from 1.000 to 0.080, while external generated "
    "dilemmas showed limited generalisation. The planned human study will compare no-AI, base-model advice, and "
    "debiased-adapter advice to test effects on framing sensitivity, confidence, trust, and reliance."
)


def add_card(ax, x, y, w, h, title: str | None = None, title_color: str = BLUE) -> None:
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.015",
            linewidth=1.5,
            edgecolor=LINE,
            facecolor=CARD,
            zorder=0,
        )
    )
    if title:
        ax.text(x + 0.022, y + h - 0.045, title, fontsize=26, fontweight="bold", color=title_color, va="top")


def add_wrapped(ax, x, y, text: str, width: int, fontsize: int = 18, color: str = INK, line_gap: float = 0.025, weight: str = "normal") -> float:
    current = y
    for paragraph in text.split("\n"):
        lines = wrap(paragraph, width=width) if paragraph else [""]
        for line in lines:
            ax.text(x, current, line, fontsize=fontsize, color=color, va="top", fontweight=weight)
            current -= line_gap
        current -= line_gap * 0.45
    return current


def add_bullets(ax, x, y, bullets: list[str], width: int = 58, fontsize: int = 18, line_gap: float = 0.024) -> float:
    current = y
    for bullet in bullets:
        wrapped = wrap(bullet, width=width)
        ax.text(x, current, "-", fontsize=fontsize + 2, color=TEAL, va="top", fontweight="bold")
        for i, line in enumerate(wrapped):
            ax.text(x + 0.018, current, line, fontsize=fontsize, color=INK, va="top")
            current -= line_gap
        current -= line_gap * 0.35
    return current


def draw_table(ax, x, y, w, row_h, headers: list[str], rows: list[list[str]], col_widths: list[float], fontsize: int = 15) -> None:
    assert abs(sum(col_widths) - 1.0) < 1e-6
    total_rows = len(rows) + 1
    h = row_h * total_rows
    ax.add_patch(Rectangle((x, y - h), w, h, facecolor="white", edgecolor=LINE, linewidth=1.0))
    ax.add_patch(Rectangle((x, y - row_h), w, row_h, facecolor="#e8f1f8", edgecolor=LINE, linewidth=1.0))
    col_x = [x]
    for cw in col_widths[:-1]:
        col_x.append(col_x[-1] + w * cw)
    for idx, header in enumerate(headers):
        ax.text(col_x[idx] + 0.006, y - row_h * 0.62, header, fontsize=fontsize, fontweight="bold", color=INK, va="center")
    for r_idx, row in enumerate(rows):
        ry = y - row_h * (r_idx + 2)
        if r_idx % 2 == 1:
            ax.add_patch(Rectangle((x, ry), w, row_h, facecolor="#faf7ef", edgecolor="none"))
        for c_idx, cell in enumerate(row):
            ax.text(col_x[c_idx] + 0.006, ry + row_h * 0.46, cell, fontsize=fontsize, color=INK, va="center")
    for cx in col_x[1:]:
        ax.plot([cx, cx], [y, y - h], color=LINE, linewidth=0.8)
    for i in range(total_rows + 1):
        yy = y - row_h * i
        ax.plot([x, x + w], [yy, yy], color=LINE, linewidth=0.8)


def load_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    strict = pd.read_csv(PROJECT_ROOT / "results" / "strict_item_qwen3_4b_v2_expanded_comparison" / "strict_v2_expanded_comparison_summary.csv")
    generated = pd.read_csv(
        PROJECT_ROOT
        / "results"
        / "generated_qwen3_4b_v2_sft_expanded_r4_comparison"
        / "generated_v2_sft_expanded_comparison_summary.csv"
    )
    return strict, generated


def debate_rows() -> list[list[str]]:
    specs = [
        ("DeepSeek", "Exp2", "results/full_exp2_deepseek/analysis/bias_summary.csv"),
        ("DeepSeek", "Exp3", "results/full_exp3_deepseek/analysis/bias_summary.csv"),
        ("Alibaba Qwen3.6", "Exp2", "results/full_exp2_aliyun_qwen36/analysis/bias_summary.csv"),
        ("Alibaba Qwen3.6", "Exp3", "results/full_exp3_aliyun_qwen36/analysis/bias_summary.csv"),
    ]
    rows = []
    for model, dataset, rel_path in specs:
        df = pd.read_csv(PROJECT_ROOT / rel_path)
        grouped = df.groupby("prompt_condition")[["yes_no_bias", "omission_bias"]].mean()
        standard = grouped.loc["standard"].mean()
        debate = grouped.loc["debate"].mean()
        reduction = (standard - debate) / standard * 100 if standard else 0
        rows.append([model, dataset, f"{standard:.3f}", f"{debate:.3f}", f"{reduction:.0f}%"])
    return rows


def strict_rows(strict: pd.DataFrame) -> list[list[str]]:
    labels = {
        "qwen3_4b_base_promptfix": "Base",
        "strict_short_reason_promptfix": "Old SFT",
        "expanded_sft": "Expanded SFT",
        "expanded_sft_dpo": "SFT + DPO",
    }
    rows = []
    for key in labels:
        row = strict[strict["model_variant"] == key].iloc[0]
        rows.append(
            [
                labels[key],
                f"{row['moral_bias_mean']:.3f}",
                f"{row['overall_accuracy']:.3f}",
                f"{row['wrong_belief_agreement_rate']:.3f}",
                f"{row['latency_x_base']:.2f}x",
            ]
        )
    return rows


def generated_rows(generated: pd.DataFrame) -> list[list[str]]:
    rows = []
    for model_key, label in [
        ("qwen3_4b_base_generated_r4", "Base"),
        ("short_reason_generated_r4", "Old SFT"),
        ("expanded_sft_generated_r4", "Expanded SFT"),
    ]:
        moral = generated[(generated["model_variant"] == model_key) & (generated["dataset"] == "overall_moral")].iloc[0]
        syc = generated[(generated["model_variant"] == model_key) & (generated["dataset"] == "overall_sycophancy")].iloc[0]
        rows.append(
            [
                label,
                f"{moral['moral_bias_mean']:.3f}",
                f"{syc['overall_accuracy']:.3f}",
                f"{syc['wrong_belief_agreement_rate']:.3f}",
            ]
        )
    return rows


def external_rows(generated: pd.DataFrame) -> list[list[str]]:
    rows = []
    for model_key, label in [
        ("qwen3_4b_base_generated_r4", "Base"),
        ("short_reason_generated_r4", "Old SFT"),
        ("expanded_sft_generated_r4", "Expanded SFT"),
    ]:
        moral = generated[(generated["model_variant"] == model_key) & (generated["dataset"] == "overall_moral")].iloc[0]
        syc = generated[(generated["model_variant"] == model_key) & (generated["dataset"] == "overall_sycophancy")].iloc[0]
        rows.append(
            [
                label,
                f"{moral['moral_bias_mean']:.3f}",
                f"{syc['overall_accuracy']:.3f}",
                f"{syc['wrong_belief_agreement_rate']:.3f}",
            ]
        )
    return rows


def draw_bar_chart(ax, strict: pd.DataFrame, generated: pd.DataFrame, x: float, y: float, w: float, h: float) -> None:
    chart = ax.inset_axes([x, y, w, h])
    labels = ["Base", "Old SFT", "Expanded\nSFT", "SFT+DPO"]
    values = [
        float(strict[strict["model_variant"] == "qwen3_4b_base_promptfix"]["moral_bias_mean"].iloc[0]),
        float(strict[strict["model_variant"] == "strict_short_reason_promptfix"]["moral_bias_mean"].iloc[0]),
        float(strict[strict["model_variant"] == "expanded_sft"]["moral_bias_mean"].iloc[0]),
        float(strict[strict["model_variant"] == "expanded_sft_dpo"]["moral_bias_mean"].iloc[0]),
    ]
    colors = [RED, ORANGE, GREEN, "#64748b"]
    xpos = list(range(len(labels)))
    chart.bar(xpos, values, color=colors, width=0.62)
    chart.set_xticks(xpos)
    chart.set_xticklabels(labels)
    chart.set_ylim(0, 1.05)
    chart.set_ylabel("Strict moral bias mean", fontsize=13)
    chart.tick_params(axis="both", labelsize=12)
    chart.spines[["top", "right"]].set_visible(False)
    chart.grid(axis="y", color="#d8d2c8", linewidth=0.8, alpha=0.8)
    for idx, value in enumerate(values):
        chart.text(idx, value + 0.035, f"{value:.3f}", ha="center", fontsize=12, fontweight="bold")

    chart2 = ax.inset_axes([x + w * 0.57, y + 0.04, w * 0.40, h * 0.48])
    chart2.clear()
    gen_vals = [
        float(generated[(generated["model_variant"] == "qwen3_4b_base_generated_r4") & (generated["dataset"] == "overall_moral")]["moral_bias_mean"].iloc[0]),
        float(generated[(generated["model_variant"] == "expanded_sft_generated_r4") & (generated["dataset"] == "overall_moral")]["moral_bias_mean"].iloc[0]),
    ]
    xpos2 = [0, 1]
    chart2.bar(xpos2, gen_vals, color=[RED, GREEN], width=0.55)
    chart2.set_xticks(xpos2)
    chart2.set_xticklabels(["Base", "Expanded\nSFT"])
    chart2.set_ylim(0, 0.5)
    chart2.set_title("External generated moral", fontsize=12, pad=4)
    chart2.tick_params(axis="both", labelsize=10)
    chart2.spines[["top", "right"]].set_visible(False)
    chart2.grid(axis="y", color="#d8d2c8", linewidth=0.7, alpha=0.8)
    for idx, value in enumerate(gen_vals):
        chart2.text(idx, value + 0.018, f"{value:.3f}", ha="center", fontsize=10, fontweight="bold")


def draw_pipeline(ax, x: float, y: float, w: float, h: float) -> None:
    boxes = [
        (x, y + h * 0.54, w * 0.20, h * 0.26, "Framed\nmoral dilemma", "#e8f1f8"),
        (x + w * 0.27, y + h * 0.72, w * 0.22, h * 0.18, "No-AI\ncontrol", "#f1f5f9"),
        (x + w * 0.27, y + h * 0.51, w * 0.22, h * 0.18, "Base-model\nadvice", "#fee2e2"),
        (x + w * 0.27, y + h * 0.30, w * 0.22, h * 0.18, "Debiased\nadapter advice", "#dcfce7"),
        (x + w * 0.65, y + h * 0.52, w * 0.28, h * 0.28, "Human judgment\ninitial -> final\ntrust + reliance", "#fef3c7"),
    ]
    for bx, by, bw, bh, text, color in boxes:
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.008,rounding_size=0.012", facecolor=color, edgecolor=LINE))
        ax.text(bx + bw / 2, by + bh / 2, text, ha="center", va="center", fontsize=17, color=INK, fontweight="bold")

    arrows = [
        ((x + w * 0.20, y + h * 0.67), (x + w * 0.27, y + h * 0.81)),
        ((x + w * 0.20, y + h * 0.67), (x + w * 0.27, y + h * 0.60)),
        ((x + w * 0.20, y + h * 0.67), (x + w * 0.27, y + h * 0.39)),
        ((x + w * 0.49, y + h * 0.81), (x + w * 0.65, y + h * 0.66)),
        ((x + w * 0.49, y + h * 0.60), (x + w * 0.65, y + h * 0.66)),
        ((x + w * 0.49, y + h * 0.39), (x + w * 0.65, y + h * 0.66)),
    ]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18, linewidth=2, color=MUTED))
    ax.text(
        x + w * 0.5,
        y + h * 0.18,
        "Primary human-level test: does debiased advice reduce final framing gaps?",
        ha="center",
        fontsize=17,
        color=BLUE,
        fontweight="bold",
    )


def make_poster() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    strict, generated = load_results()

    fig = plt.figure(figsize=(33.11, 46.81), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=BG, edgecolor="none"))

    ax.text(0.04, 0.965, TITLE, fontsize=56, fontweight="heavy", color=INK, va="top")
    ax.text(0.04, 0.922, SUBTITLE, fontsize=31, color=BLUE, va="top", fontweight="bold")
    ax.text(0.04, 0.895, AUTHOR_LINE, fontsize=18, color=MUTED, va="top")
    ax.add_patch(Rectangle((0.04, 0.878), 0.92, 0.004, facecolor=BLUE, edgecolor="none"))

    add_card(ax, 0.04, 0.710, 0.92, 0.153, "Summer school abstract", TEAL)
    add_wrapped(ax, 0.065, 0.795, ABSTRACT, width=140, fontsize=18, line_gap=0.020)

    add_card(ax, 0.04, 0.495, 0.28, 0.190, "Background", BLUE)
    add_bullets(
        ax,
        0.062,
        0.625,
        [
            "LLM moral judgments can change across logically equivalent action-omission and yes-no framings.",
            "These biases matter because LLMs are increasingly used as advisors in morally consequential contexts.",
            "This project treats moral bias as a bounded, strategy-dependent response shaped by prompting and training.",
        ],
        width=44,
        fontsize=17,
    )

    add_card(ax, 0.36, 0.495, 0.28, 0.190, "Completed model-level study", ORANGE)
    add_bullets(
        ax,
        0.382,
        0.625,
        [
            "Compared standard single-response outputs, structured debate prompts, SFT, and DPO.",
            "Used moral dilemmas with original, yes-no, and omission framings plus sycophancy-style tasks.",
            "Debate roles: Rational Analyst, Intuitive Humanist, Devil's Advocate, and Moderator.",
        ],
        width=44,
        fontsize=17,
    )

    add_card(ax, 0.68, 0.495, 0.28, 0.190, "Why human transfer matters", TEAL)
    add_bullets(
        ax,
        0.702,
        0.625,
        [
            "Strict held-out gains do not guarantee robustness on generated external dilemmas.",
            "Humans may selectively follow advice depending on trust, confidence, and perceived helpfulness.",
            "The next test is whether less biased AI advice changes human final judgments.",
        ],
        width=44,
        fontsize=17,
    )

    add_card(ax, 0.04, 0.295, 0.43, 0.175, "Key result 1: debate prompts", ORANGE)
    draw_table(
        ax,
        0.062,
        0.405,
        0.386,
        0.025,
        ["Model", "Data", "Std", "Debate", "Drop"],
        debate_rows(),
        [0.33, 0.15, 0.15, 0.18, 0.19],
        fontsize=14,
    )
    add_wrapped(
        ax,
        0.062,
        0.305,
        "Interpretation: debate often reduced both bias types, especially in DeepSeek and Alibaba Qwen3.6, but gains were model-dependent rather than universal.",
        width=72,
        fontsize=15,
        color=MUTED,
        line_gap=0.018,
    )

    add_card(ax, 0.53, 0.295, 0.43, 0.175, "Key result 2: trained adapter", GREEN)
    draw_table(
        ax,
        0.552,
        0.405,
        0.386,
        0.025,
        ["Model", "Bias", "Syc Acc", "Wrong Belief", "Cost"],
        strict_rows(strict),
        [0.26, 0.15, 0.18, 0.25, 0.16],
        fontsize=14,
    )
    add_wrapped(
        ax,
        0.552,
        0.305,
        "Best strict held-out candidate: expanded SFT. DPO lowered training loss but worsened robustness, so it is excluded from the planned human study.",
        width=72,
        fontsize=15,
        color=MUTED,
        line_gap=0.018,
    )

    add_card(ax, 0.04, 0.065, 0.28, 0.205, "Model result summary", BLUE)
    draw_bar_chart(ax, strict, generated, 0.062, 0.150, 0.225, 0.065)
    draw_table(
        ax,
        0.062,
        0.132,
        0.225,
        0.013,
        ["External", "Moral bias", "Syc acc", "Wrong belief"],
        external_rows(generated),
        [0.30, 0.23, 0.22, 0.25],
        fontsize=8,
    )
    add_wrapped(
        ax,
        0.062,
        0.083,
        "Strict held-out moral bias fell from 1.000 to 0.080 with expanded SFT. External generated moral bias remained around 0.396.",
        width=43,
        fontsize=14,
        color=MUTED,
        line_gap=0.016,
    )

    add_card(ax, 0.36, 0.065, 0.28, 0.205, "Planned human experiment", TEAL)
    draw_pipeline(ax, 0.382, 0.115, 0.235, 0.115)
    add_wrapped(
        ax,
        0.382,
        0.086,
        "Participants will make initial and final moral judgments, then rate confidence, trust, helpfulness, and reliance after no-AI, base-model, or debiased-adapter advice.",
        width=43,
        fontsize=15,
        color=MUTED,
        line_gap=0.018,
    )

    add_card(ax, 0.68, 0.065, 0.28, 0.205, "Analysis plan", RED)
    add_bullets(
        ax,
        0.702,
        0.205,
        [
            "Primary outcome: final endorsement of the original action.",
            "Main model: endorse_original_action ~ AI_condition * framing + (1 | participant) + (1 | dilemma).",
            "Secondary outcomes: judgment shift toward AI, confidence change, perceived trust, helpfulness, and reliance.",
            "Success criterion: smaller framing gap in the debiased-advice group than in the base-advice group.",
        ],
        width=43,
        fontsize=15,
        line_gap=0.021,
    )

    ax.add_patch(Rectangle((0.04, 0.025), 0.92, 0.004, facecolor=BLUE, edgecolor="none", alpha=0.9))
    ax.text(
        0.04,
        0.018,
        "Takeaway: model-level debiasing is promising but not sufficient; human-AI moral alignment requires testing whether less biased advice changes human judgments.",
        fontsize=19,
        color=INK,
        fontweight="bold",
        va="top",
    )
    ax.text(
        0.96,
        0.018,
        "A0 portrait poster",
        fontsize=13,
        color=MUTED,
        ha="right",
        va="top",
    )

    pdf_path = OUT_DIR / "a0_poster_human_ai_moral_debiasing.pdf"
    png_path = OUT_DIR / "a0_poster_human_ai_moral_debiasing.png"
    # Keep the exact A0 portrait canvas size instead of tight-cropping.
    fig.savefig(pdf_path, format="pdf", facecolor=BG)
    fig.savefig(png_path, format="png", dpi=150, facecolor=BG)
    plt.close(fig)

    content_path = OUT_DIR / "poster_text_content.md"
    content_path.write_text(
        (
            f"# {TITLE}\n\n"
            f"## Subtitle\n{SUBTITLE}\n\n"
            f"## Abstract\n{ABSTRACT}\n\n"
            "## Main Message\n"
            "Model-level debiasing is promising but not sufficient. The next scientific step is to test whether less biased AI advice changes human moral judgment.\n\n"
            "## Completed Model-Level Study\n"
            "- Standard single-response outputs were compared with structured debate prompts, SFT, and DPO.\n"
            "- Debate reduced bias in several API models but was model-dependent.\n"
            "- Expanded SFT reduced strict held-out moral bias from 1.000 to 0.080.\n"
            "- Generated external dilemmas showed limited generalisation, with expanded SFT moral bias around 0.396.\n\n"
            "## Planned Human Study\n"
            "- Conditions: no-AI control, base-model advice, debiased-adapter advice.\n"
            "- Outcomes: final moral judgment, framing sensitivity, confidence, trust, helpfulness, and reliance.\n"
            "- Main model: endorse_original_action ~ AI_condition * framing + (1 | participant) + (1 | dilemma).\n"
        ),
        encoding="utf-8",
    )
    print(f"Wrote {pdf_path}")
    print(f"Wrote {png_path}")
    print(f"Wrote {content_path}")


if __name__ == "__main__":
    make_poster()
