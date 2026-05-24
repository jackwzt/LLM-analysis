from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager


STANDARD_COLOR = "#1f4e79"
DEBATE_COLOR = "#d97706"
CONNECTOR_COLOR = "#bdbdbd"
GRID_COLOR = "#dddddd"


@dataclass(frozen=True)
class RunSpec:
    model: str
    dataset: str
    run_name: str
    takeaway_cn: str
    takeaway_en: str
    status_cn: str
    status_en: str


RUN_SPECS = [
    RunSpec(
        model="DeepSeek",
        dataset="Exp2",
        run_name="full_exp2_deepseek",
        takeaway_cn="强支持",
        takeaway_en="Strong support",
        status_cn="两类 bias 均明显下降。",
        status_en="Both bias types decreased clearly.",
    ),
    RunSpec(
        model="DeepSeek",
        dataset="Exp3",
        run_name="full_exp3_deepseek",
        takeaway_cn="强支持",
        takeaway_en="Strong support",
        status_cn="两类 bias 均下降，但题目异质性更高。",
        status_en="Both bias types decreased, with stronger item heterogeneity.",
    ),
    RunSpec(
        model="Alibaba Qwen3.6",
        dataset="Exp2",
        run_name="full_exp2_aliyun_qwen36",
        takeaway_cn="强支持",
        takeaway_en="Strong support",
        status_cn="yes-no 改善最明显，omission 小幅下降。",
        status_en="The largest gain was on yes-no bias, with a smaller omission gain.",
    ),
    RunSpec(
        model="Alibaba Qwen3.6",
        dataset="Exp3",
        run_name="full_exp3_aliyun_qwen36",
        takeaway_cn="强支持",
        takeaway_en="Strong support",
        status_cn="两类 bias 均稳定下降。",
        status_en="Both bias types decreased consistently.",
    ),
    RunSpec(
        model="Zhipu GLM-5.1",
        dataset="Exp3",
        run_name="full_exp3_zhipu_glm51",
        takeaway_cn="有前景但稳健性较弱",
        takeaway_en="Promising but less robust",
        status_cn="平均 bias 下降，但 debate 有效率偏低。",
        status_en="Average bias decreased, but debate validity was lower.",
    ),
    RunSpec(
        model="Qwen local",
        dataset="Exp2",
        run_name="full_exp2_qwen",
        takeaway_cn="混合结果",
        takeaway_en="Partial / mixed",
        status_cn="yes-no 小幅下降，但 omission 上升。",
        status_en="Yes-no bias decreased slightly, but omission bias increased.",
    ),
    RunSpec(
        model="Gemma 4 31B",
        dataset="Exp2",
        run_name="full_exp2_gemma4_31b",
        takeaway_cn="混合结果",
        takeaway_en="Partial / mixed",
        status_cn="yes-no 明显下降，但 omission 上升。",
        status_en="Yes-no bias dropped sharply, but omission bias increased.",
    ),
    RunSpec(
        model="Gemini 2.5 Flash",
        dataset="Exp2",
        run_name="full_exp2_gemini25flash",
        takeaway_cn="混合结果",
        takeaway_en="Partial / mixed",
        status_cn="omission 下降，但 yes-no 上升。",
        status_en="Omission bias decreased, but yes-no bias increased.",
    ),
]


def choose_font_path(lang: str) -> Path:
    candidates = {
        "cn": [
            Path(r"C:\Windows\Fonts\msyh.ttc"),
            Path(r"C:\Windows\Fonts\simhei.ttf"),
            Path(r"C:\Windows\Fonts\simsun.ttc"),
        ],
        "en": [
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path(r"C:\Windows\Fonts\calibri.ttf"),
        ],
    }
    for path in candidates[lang]:
        if path.exists():
            return path
    raise FileNotFoundError(f"No suitable font found for language: {lang}")


def configure_fonts() -> tuple[font_manager.FontProperties, font_manager.FontProperties]:
    cn_font_path = choose_font_path("cn")
    en_font_path = choose_font_path("en")

    font_manager.fontManager.addfont(str(cn_font_path))
    font_manager.fontManager.addfont(str(en_font_path))

    cn_font = font_manager.FontProperties(fname=str(cn_font_path))
    en_font = font_manager.FontProperties(fname=str(en_font_path))
    plt.rcParams["axes.unicode_minus"] = False
    return cn_font, en_font


def load_run_summary(project_root: Path, spec: RunSpec) -> dict[str, object]:
    analysis_dir = project_root / "results" / spec.run_name / "analysis"
    bias = pd.read_csv(analysis_dir / "bias_summary.csv")
    valid = pd.read_csv(analysis_dir / "valid_response_counts.csv")
    anova = pd.read_csv(analysis_dir / "anova_table.csv")

    def mean_for(condition: str, column: str) -> float:
        subset = bias.loc[bias["prompt_condition"] == condition, column]
        return float(subset.mean())

    def valid_rate_for(condition: str) -> float:
        subset = valid.loc[valid["prompt_condition"] == condition, ["valid_count", "total_trials"]]
        return float(subset["valid_count"].sum() / subset["total_trials"].sum())

    anova_row = anova.loc[anova["term"] == "framing_condition:prompt_condition"]
    anova_p = anova_row.iloc[0]["Pr(>F)"] if not anova_row.empty else "NA"

    return {
        "model": spec.model,
        "dataset": spec.dataset,
        "valid_standard": valid_rate_for("standard"),
        "valid_debate": valid_rate_for("debate"),
        "yesno_standard": mean_for("standard", "yes_no_bias"),
        "yesno_debate": mean_for("debate", "yes_no_bias"),
        "omission_standard": mean_for("standard", "omission_bias"),
        "omission_debate": mean_for("debate", "omission_bias"),
        "anova_p": str(anova_p),
        "takeaway_cn": spec.takeaway_cn,
        "takeaway_en": spec.takeaway_en,
        "status_cn": spec.status_cn,
        "status_en": spec.status_en,
    }


def build_summary_frame(project_root: Path) -> pd.DataFrame:
    rows = [load_run_summary(project_root, spec) for spec in RUN_SPECS]
    return pd.DataFrame(rows)


def format_decimal(value: float) -> str:
    return f"{value:.3f}"


def p_label(value: str) -> str:
    try:
        numeric = float(value)
    except ValueError:
        return value
    if numeric < 0.001:
        return "p < .001"
    return f"p = {numeric:.3f}"


def make_table_frame(frame: pd.DataFrame, lang: str) -> pd.DataFrame:
    out = frame.copy()
    out["valid_pair"] = out.apply(
        lambda row: f"{format_decimal(row['valid_standard'])} / {format_decimal(row['valid_debate'])}",
        axis=1,
    )
    out["yesno_pair"] = out.apply(
        lambda row: f"{format_decimal(row['yesno_standard'])} -> {format_decimal(row['yesno_debate'])}",
        axis=1,
    )
    out["omission_pair"] = out.apply(
        lambda row: f"{format_decimal(row['omission_standard'])} -> {format_decimal(row['omission_debate'])}",
        axis=1,
    )
    takeaway_col = "takeaway_cn" if lang == "cn" else "takeaway_en"
    columns = ["model", "dataset", "valid_pair", "yesno_pair", "omission_pair", takeaway_col]
    renamed = {
        "cn": ["模型", "数据集", "有效率 Std / Deb", "Yes-no Std -> Deb", "Omission Std -> Deb", "结论"],
        "en": ["Model", "Dataset", "Valid Std / Deb", "Yes-no Std -> Deb", "Omission Std -> Deb", "Takeaway"],
    }
    table = out[columns].copy()
    table.columns = renamed[lang]
    return table


def draw_wrapped_lines(fig, x: float, y: float, width: int, lines: list[str], font_prop, size: int, line_gap: float):
    current_y = y
    for line in lines:
        wrapped = wrap(line, width=width) or [line]
        for piece in wrapped:
            fig.text(x, current_y, piece, fontproperties=font_prop, fontsize=size, va="top")
            current_y -= line_gap
    return current_y


def build_report_pdf(frame: pd.DataFrame, output_path: Path, lang: str, font_prop) -> None:
    fig = plt.figure(figsize=(8.27, 11.69), dpi=160)
    fig.patch.set_facecolor("white")

    if lang == "cn":
        title = "Structured Debate 是否降低大语言模型中的道德偏差？"
        aim_header = "研究目标"
        aim_text = (
            "比较 standard single-response 与 structured debate 是否降低模型层 moral framing bias。"
            "核心指标为 yes-no bias 与 omission bias，数值越低越好。"
        )
        takeaway_header = "核心结论"
        takeaways = [
            "1. DeepSeek 与 Alibaba Qwen3.6 的结果最稳定，在已完成的 Exp2 与 Exp3 中，debate 均降低了两类 bias。",
            "2. Qwen local、Gemma 4 31B 与 Gemini 2.5 Flash 呈现混合结果，说明 debate 的收益具有明显模型依赖性。",
            "3. Zhipu GLM-5.1 在 Exp3 中平均 bias 有所下降，但 debate 有效率较低，因此证据强度弱于 DeepSeek 与 Alibaba。",
        ]
        note_header = "方法说明"
        notes = [
            "使用原 OSF Exp2/Exp3 刺激材料。",
            "每个 题目 x framing x 条件 使用 56 次重复采样。",
            "仅纳入已完成且已分析的 model-level 结果。",
        ]
        stats_header = "统计摘要"
        stats = [
            "所有已纳入 run 的 framing x prompt ANOVA 交互项均达到显著。",
            "DeepSeek 与 Alibaba Qwen3.6 的统计证据最强，均为 p < .001。",
            "Zhipu GLM-5.1 / Exp3 也达到显著，但 debate 有效率仅为 0.914。",
        ]
    else:
        title = "Does Structured Debate Reduce Moral Bias in Large Language Models?"
        aim_header = "Aim"
        aim_text = (
            "We compare standard single-response against structured debate at the model level. "
            "The two core outcomes are yes-no bias and omission bias, where lower values indicate smaller framing gaps."
        )
        takeaway_header = "Key Takeaways"
        takeaways = [
            "1. DeepSeek and Alibaba Qwen3.6 show the most stable support: debate reduced both bias types in completed Exp2 and Exp3 runs.",
            "2. Qwen local, Gemma 4 31B, and Gemini 2.5 Flash show mixed outcomes, indicating that debate gains are strongly model-dependent.",
            "3. Zhipu GLM-5.1 improved on average in Exp3, but the lower debate validity rate weakens the robustness of that result.",
        ]
        note_header = "Methods Note"
        notes = [
            "We used the original OSF Exp2/Exp3 stimuli.",
            "Each dilemma x framing x condition cell used 56 repeated samples.",
            "Only completed and analyzed model-level runs are included.",
        ]
        stats_header = "Statistical Note"
        stats = [
            "The framing x prompt ANOVA interaction is significant for every included run.",
            "The strongest evidence appears in DeepSeek and Alibaba Qwen3.6, both with p < .001.",
            "Zhipu GLM-5.1 / Exp3 is also significant, but the debate valid-response rate is only 0.914.",
        ]

    fig.text(0.06, 0.965, title, fontproperties=font_prop, fontsize=18, weight="bold", va="top")

    fig.text(0.06, 0.925, aim_header, fontproperties=font_prop, fontsize=13, weight="bold", va="top")
    y = draw_wrapped_lines(fig, 0.06, 0.902, 74, [aim_text], font_prop, 11, 0.020)

    fig.text(0.06, y - 0.01, takeaway_header, fontproperties=font_prop, fontsize=13, weight="bold", va="top")
    y = draw_wrapped_lines(fig, 0.06, y - 0.032, 74, takeaways, font_prop, 11, 0.020)

    fig.text(0.06, y - 0.01, stats_header, fontproperties=font_prop, fontsize=13, weight="bold", va="top")
    y = draw_wrapped_lines(fig, 0.06, y - 0.032, 74, stats, font_prop, 10, 0.018)

    fig.text(0.06, y - 0.01, note_header, fontproperties=font_prop, fontsize=13, weight="bold", va="top")
    y = draw_wrapped_lines(fig, 0.06, y - 0.032, 74, notes, font_prop, 10, 0.018)

    table_frame = make_table_frame(frame, lang)
    ax_table = fig.add_axes([0.05, 0.06, 0.90, 0.33])
    ax_table.axis("off")
    table = ax_table.table(
        cellText=table_frame.values,
        colLabels=table_frame.columns,
        cellLoc="center",
        colLoc="center",
        loc="upper center",
        colWidths=[0.22, 0.09, 0.17, 0.16, 0.16, 0.20],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.8 if lang == "en" else 8.4)
    table.scale(1, 1.55)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#c7c7c7")
        text = cell.get_text()
        text.set_fontproperties(font_prop)
        if row == 0:
            cell.set_facecolor("#edf2f7")
            text.set_weight("bold")
        else:
            cell.set_facecolor("white")

    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def build_plot(frame: pd.DataFrame, png_path: Path, pdf_path: Path, font_prop) -> None:
    plot_df = frame.copy()
    plot_df["label"] = plot_df.apply(
        lambda row: f"{row['model']} / {row['dataset']}" + (" *" if row["valid_debate"] < 0.95 else ""),
        axis=1,
    )
    order = list(plot_df["label"])
    y_positions = list(range(len(order)))[::-1]
    label_to_y = {label: y for label, y in zip(order, y_positions)}

    fig, axes = plt.subplots(ncols=2, figsize=(14, 8), sharey=True)
    plt.subplots_adjust(wspace=0.18, left=0.28, right=0.97, top=0.88, bottom=0.12)

    configs = [
        ("yesno_standard", "yesno_debate", "Yes-no bias"),
        ("omission_standard", "omission_debate", "Omission bias"),
    ]

    for ax, (std_col, deb_col, title) in zip(axes, configs):
        for _, row in plot_df.iterrows():
            y = label_to_y[row["label"]]
            ax.plot([row[std_col], row[deb_col]], [y, y], color=CONNECTOR_COLOR, linewidth=2.0, zorder=1)
            ax.scatter(
                row[std_col],
                y,
                color=STANDARD_COLOR,
                s=70,
                zorder=2,
                label="Standard" if y == y_positions[0] else None,
            )
            ax.scatter(
                row[deb_col],
                y,
                color=DEBATE_COLOR,
                s=70,
                zorder=3,
                marker="D",
                label="Debate" if y == y_positions[0] else None,
            )

        ax.set_title(title, fontsize=12, weight="bold")
        ax.set_xlabel("Absolute framing gap (lower is better)")
        ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
        ax.set_axisbelow(True)

    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels(order, fontsize=10, fontproperties=font_prop)
    axes[1].tick_params(axis="y", labelleft=False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, prop=font_prop)
    fig.suptitle("Structured debate effect across completed model runs", fontsize=14, weight="bold")
    fig.text(0.5, 0.04, "* debate valid-response rate < 95%", ha="center", fontsize=10)
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "reports" / "briefing_2026-04-14"
    output_dir.mkdir(parents=True, exist_ok=True)

    cn_font, en_font = configure_fonts()
    frame = build_summary_frame(project_root)
    frame.to_csv(output_dir / "summary_metrics.csv", index=False, encoding="utf-8-sig")

    build_report_pdf(frame, output_dir / "model_bias_briefing_cn.pdf", "cn", cn_font)
    build_report_pdf(frame, output_dir / "model_bias_briefing_en.pdf", "en", en_font)
    build_plot(
        frame,
        output_dir / "model_bias_effect_comparison.png",
        output_dir / "model_bias_effect_comparison.pdf",
        en_font,
    )


if __name__ == "__main__":
    main()
