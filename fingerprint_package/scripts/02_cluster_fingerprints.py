from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_DIR = PROJECT_ROOT / "fingerprint_package" / "outputs" / "tables"
METADATA_COLUMNS = {
    "model_id",
    "model_family",
    "provider",
    "open_or_closed",
    "local_or_api",
    "approx_size",
    "training_stage",
    "provider_family",
    "model_line",
    "variant_type",
    "deployment",
    "openness",
    "size_class",
    "reasoning_or_speed_profile",
    "cost_tier",
    "notes",
}


def prepare_numeric(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_cols = [column for column in frame.columns if column not in METADATA_COLUMNS]
    numeric = frame[numeric_cols].apply(pd.to_numeric, errors="coerce")
    numeric = numeric.dropna(axis=1, thresh=max(2, int(0.3 * len(numeric))))
    if numeric.empty:
        return numeric, numeric
    numeric = numeric.fillna(numeric.mean(numeric_only=True))
    std = numeric.std(ddof=0).replace(0, np.nan)
    z = (numeric - numeric.mean()) / std
    z = z.dropna(axis=1, how="all").fillna(0.0)
    return numeric, z


def main() -> None:
    path = TABLE_DIR / "fingerprint_matrix.csv"
    if not path.exists():
        raise FileNotFoundError("Run 01_build_fingerprint_matrix.py first.")
    frame = pd.read_csv(path)
    numeric, z = prepare_numeric(frame)
    if z.empty or len(frame) < 2:
        frame[["model_id"]].to_csv(TABLE_DIR / "model_clusters.csv", index=False)
        z.to_csv(TABLE_DIR / "feature_zscores.csv", index=False)
        print("Not enough numeric data for clustering")
        return

    z_out = pd.concat([frame[["model_id"]], z], axis=1)
    z_out.to_csv(TABLE_DIR / "feature_zscores.csv", index=False)

    try:
        from scipy.cluster.hierarchy import fcluster, linkage
        from scipy.spatial.distance import pdist

        metric = "correlation" if z.shape[1] > 1 else "euclidean"
        distances = pdist(z.to_numpy(dtype=float), metric=metric)
        if not np.isfinite(distances).all():
            distances = pdist(z.to_numpy(dtype=float), metric="euclidean")
            metric = "euclidean"
        linkage_matrix = linkage(distances, method="average")
        clusters = fcluster(linkage_matrix, t=min(3, len(frame)), criterion="maxclust")
        linkage_frame = pd.DataFrame(linkage_matrix, columns=["cluster_a", "cluster_b", "distance", "n_members"])
        linkage_frame["metric"] = metric
        linkage_frame.to_csv(TABLE_DIR / "hierarchical_linkage.csv", index=False)
    except Exception as exc:
        clusters = np.arange(1, len(frame) + 1)
        pd.DataFrame({"error": [f"{type(exc).__name__}: {exc}"]}).to_csv(TABLE_DIR / "hierarchical_linkage.csv", index=False)

    cluster_frame = frame[["model_id"]].copy()
    for column in ["model_family", "local_or_api", "approx_size", "training_stage"]:
        if column in frame.columns:
            cluster_frame[column] = frame[column]
    cluster_frame["cluster"] = clusters
    cluster_frame.to_csv(TABLE_DIR / "model_clusters.csv", index=False)

    x = z.to_numpy(dtype=float)
    x = x - x.mean(axis=0)
    try:
        _, _, vt = np.linalg.svd(x, full_matrices=False)
        components = x @ vt[: min(2, vt.shape[0])].T
        pca = pd.DataFrame({"model_id": frame["model_id"]})
        pca["pc1"] = components[:, 0]
        pca["pc2"] = components[:, 1] if components.shape[1] > 1 else 0.0
        pca.to_csv(TABLE_DIR / "pca_components.csv", index=False)
    except Exception as exc:
        pd.DataFrame({"error": [f"{type(exc).__name__}: {exc}"]}).to_csv(TABLE_DIR / "pca_components.csv", index=False)

    if "model_family" in cluster_frame.columns:
        overlap = cluster_frame.groupby(["cluster", "model_family"]).size().reset_index(name="n_models")
        overlap.to_csv(TABLE_DIR / "family_overlap_summary.csv", index=False)
    print(f"Wrote clustering outputs under {TABLE_DIR}")


if __name__ == "__main__":
    main()
