"""Reproduire le lab de régression sur les données synthétiques fournies."""

from pathlib import Path
import json
import platform
import os
from datetime import datetime, timezone

# Un seul thread de calcul suffit pour ce petit jeu pédagogique.
for variable in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]:
    os.environ.setdefault(variable, "1")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
import scipy
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]


def main():
    df = pd.read_csv(ROOT / "data" / "trafic_synthetique.csv")
    X = df[["utilisateurs"]]
    y = df["trafic_mbps"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    model = LinearRegression().fit(X_train, y_train)
    predictions = model.predict(X_test)
    results = pd.DataFrame({
        "source_row_0based": X_test.index,
        "utilisateurs": X_test["utilisateurs"].to_numpy(),
        "trafic_observe_mbps": y_test.to_numpy(),
        "trafic_predit_mbps": predictions,
        "residu_mbps": y_test.to_numpy() - predictions,
    })
    baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)
    baseline_pred = baseline.predict(X_test)
    expected = float(model.predict(pd.DataFrame({"utilisateurs": [110]}))[0])
    scenarios = pd.DataFrame({
        "utilisateurs": [110] * 4,
        "trafic_observe_mbps": [160, 180, 220, 120],
        "provenance": ["extension_reproduction", "extension_reproduction",
                       "cas_documente_source", "extension_reproduction"],
    })
    scenarios["trafic_predit_mbps"] = expected
    scenarios["residu_mbps"] = scenarios["trafic_observe_mbps"] - expected
    scenarios["seuil_absolu_mbps"] = 40
    scenarios["a_investiguer"] = scenarios["residu_mbps"].abs() > 40
    worst = results.loc[results["residu_mbps"].abs().idxmax()]
    summary = {
        "project": "ai-network-traffic-lab",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "reconstructed_from_source_and_executed",
        "data_origin": "20 synthetic educational pairs from the supplied lab PDF",
        "split": {"train_size": len(X_train), "test_size": len(X_test),
                  "random_state": 42, "shuffle": True,
                  "train_rows_0based": X_train.index.tolist(),
                  "test_rows_0based": X_test.index.tolist()},
        "model": {"intercept_mbps": float(model.intercept_),
                  "slope_mbps_per_user": float(model.coef_[0])},
        "test_metrics": {"mae_mbps": float(mean_absolute_error(y_test, predictions)),
                         "mse_mbps_squared": float(mean_squared_error(y_test, predictions)),
                         "r2": float(r2_score(y_test, predictions))},
        "mean_baseline_test_metrics": {
            "constant_mbps": float(y_train.mean()),
            "mae_mbps": float(mean_absolute_error(y_test, baseline_pred)),
            "mse_mbps_squared": float(mean_squared_error(y_test, baseline_pred)),
            "r2": float(r2_score(y_test, baseline_pred)),
            "provenance": "extension_reproduction"},
        "largest_test_residual": {"utilisateurs": int(worst["utilisateurs"]),
                                 "residu_mbps": float(worst["residu_mbps"])},
        "source_scenario": {"utilisateurs": 110, "observed_mbps": 220,
                            "predicted_mbps": expected, "residual_mbps": 220 - expected,
                            "arbitrary_threshold_mbps": 40, "rule": "abs(residual) > threshold",
                            "investigate": abs(220 - expected) > 40,
                            "confirmed_attack": None,
                            "attack_status": "not_established"},
        "limitations": ["synthetic data", "four test observations", "no attack labels",
                        "110 users is outside the observed 10-105 range",
                        "uncalibrated threshold", "no production validation"],
        "execution_versions": {"python": platform.python_version(),
                               "numpy": np.__version__, "pandas": pd.__version__,
                               "scikit_learn": sklearn.__version__,
                               "scipy": scipy.__version__,
                               "matplotlib": matplotlib.__version__},
    }
    for directory in [ROOT / "results", ROOT / "assets"]:
        directory.mkdir(parents=True, exist_ok=True)
    results.to_csv(ROOT / "results" / "predictions-test.csv", index=False)
    scenarios.to_csv(ROOT / "results" / "scenarios.csv", index=False)
    (ROOT / "results" / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "figure.facecolor": "white"})
    fig, ax = plt.subplots(figsize=(10.8, 5.5), layout="constrained")
    ax.scatter(X_train["utilisateurs"], y_train, color="#237a91", s=45,
               label="Entraînement (16 points)", zorder=3)
    ax.scatter(X_test["utilisateurs"], y_test, color="#e19b27", edgecolor="#79510d",
               s=85, marker="s", label="Test (4 points)", zorder=4)
    grid = pd.DataFrame({"utilisateurs": np.linspace(10, 105, 100)})
    ax.plot(grid["utilisateurs"], model.predict(grid), color="#24364b", lw=1.8,
            label="Modèle ajusté sur l'entraînement")
    ax.set(xlabel="Nombre d'utilisateurs", ylabel="Trafic réseau (Mbps)",
           title="Régression linéaire sur les données synthétiques du lab")
    ax.grid(alpha=.16); ax.legend(loc="upper left", fontsize=10)
    fig.savefig(ROOT / "assets" / "regression.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.8, 4.6), layout="constrained")
    sorted_results = results.sort_values("utilisateurs")
    bars = ax.bar(sorted_results["utilisateurs"].astype(str),
                  sorted_results["residu_mbps"], width=.5,
                  color=["#e19b27" if u == 95 else "#237a91"
                         for u in sorted_results["utilisateurs"]])
    ax.axhline(0, color="#24364b", lw=1)
    ax.bar_label(bars, fmt="%.3f", padding=4)
    ax.set(xlabel="Nombre d'utilisateurs (jeu de test)",
           ylabel="Résidu observé - prédit (Mbps)", ylim=(-.53, 1.04),
           title="Erreurs du modèle sur les quatre observations de test")
    ax.grid(axis="y", alpha=.16); ax.set_axisbelow(True)
    fig.savefig(ROOT / "assets" / "residus.png", dpi=180)
    plt.close(fig)

    print(f"Modèle : trafic = {model.intercept_:.6f} + {model.coef_[0]:.6f} x utilisateurs")
    print(f"MAE : {summary['test_metrics']['mae_mbps']:.6f} Mbps")
    print(f"MSE : {summary['test_metrics']['mse_mbps_squared']:.6f} (Mbps)^2")
    print(f"R2 : {summary['test_metrics']['r2']:.8f}")
    print(f"Cas source : attendu {expected:.2f} Mbps ; résidu {220-expected:.2f} Mbps.")
    print("Un écart à investiguer ne confirme pas une cyberattaque.")


if __name__ == "__main__":
    main()
