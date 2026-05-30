from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "fingerprint_package" / "outputs" / "tables"
FIGURE_DIR = PROJECT_ROOT / "fingerprint_package" / "outputs" / "figures"


def save(name: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf"]:
        plt.savefig(FIGURE_DIR / f"{name}.{suffix}", bbox_inches="tight", dpi=180)
    plt.close()


def heatmap() -> None:
    path = TABLE_DIR / "feature_zscores.csv"
    if not path.exists():
        return
    frame = pd.read_csv(path)
    if "model_id" not in frame.columns or len(frame.columns) <= 1:
        return
    data = frame.set_index("model_id")
    matrix = data.to_numpy(dtype=float)
    plt.figure(figsize=(max(8, 0.45 * len(data.columns)), max(4, 0.42 * len(data))))
    vmax = np.nanmax(np.abs(matrix)) if np.isfinite(matrix).any() else 1.0
    plt.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    plt.colorbar(label="z-score")
    plt.xticks(range(len(data.columns)), data.columns, rotation=45, ha="right")
    plt.yticks(range(len(data.index)), data.index)
    plt.title("Model Bias Fingerprint Heatmap")
    save("model_feature_heatmap")


def dendrogram() -> None:
    linkage_path = TABLE_DIR / "hierarchical_linkage.csv"
    z_path = TABLE_DIR / "feature_zscores.csv"
    if not linkage_path.exists() or not z_path.exists():
        return
    linkage_frame = pd.read_csv(linkage_path)
    if {"cluster_a", "cluster_b", "distance", "n_members"} - set(linkage_frame.columns):
        return
    labels = pd.read_csv(z_path)["model_id"].astype(str).tolist()
    try:
        from scipy.cluster.hierarchy import dendrogram as scipy_dendrogram

        linkage_matrix = linkage_frame[["cluster_a", "cluster_b", "distance", "n_members"]].to_numpy(dtype=float)
        plt.figure(figsize=(max(8, 0.6 * len(labels)), 5))
        scipy_dendrogram(linkage_matrix, labels=labels, leaf_rotation=45)
        plt.title("Hierarchical Clustering of Model Fingerprints")
        plt.ylabel("Distance")
        save("model_fingerprint_dendrogram")
    except Exception:
        return


def pca_plot() -> None:
    path = TABLE_DIR / "pca_components.csv"
    cluster_path = TABLE_DIR / "model_clusters.csv"
    if not path.exists():
        return
    pca = pd.read_csv(path)
    if {"pc1", "pc2", "model_id"} - set(pca.columns):
        return
    if cluster_path.exists():
        clusters = pd.read_csv(cluster_path)
        pca = pca.merge(clusters[["model_id", "cluster"]], on="model_id", how="left")
    else:
        pca["cluster"] = 1
    plt.figure(figsize=(7, 5))
    for cluster, group in pca.groupby("cluster"):
        plt.scatter(group["pc1"], group["pc2"], label=f"cluster {cluster}", s=65)
        for _, row in group.iterrows():
            plt.text(row["pc1"], row["pc2"], str(row["model_id"]), fontsize=8, ha="left", va="bottom")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Exploratory PCA of Bias Fingerprints")
    plt.legend(fontsize=8)
    save("model_fingerprint_pca")


def main() -> None:
    heatmap()
    dendrogram()
    pca_plot()
    print(f"Wrote fingerprint figures under {FIGURE_DIR}")


if __name__ == "__main__":
    main()
