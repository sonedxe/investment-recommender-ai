"""Figures of the technical report computed with the real code (docs/informe/img/*.png).

Usage (from the repository root, project virtualenv with matplotlib):
    PYTHONPATH=. .venv/bin/python docs/informe/build_figures.py

- fig-horizonte.png: horizon membership functions with the worked example H = 2.5.
- fig-absorcion.png: aggregated absorption set mu_CA for r = 0.25, E = 3 and its centroid.
- fig-convergencia.png: GA convergence of the moderate example (seed 42, neutral context).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ai.shared.parameters import load_parameters  # noqa: E402
from ai.shared.types import RiskProfile, UserProfile  # noqa: E402
from ai.uncertainty.fuzzy.absorption import evaluate_absorption  # noqa: E402
from ai.uncertainty.fuzzy.membership import membership  # noqa: E402
from backend.app.services.recommendation import recommend  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, GRID = "#111111", "#555555", "#d0d0d0"
STYLES = ["-", "--", ":"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
})


def horizon_figure(params) -> None:
    sets = params.fuzzy.horizon.sets
    x = np.linspace(0, 15, 601)
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    labels = {"corto": "Corto Trap(0, 0, 1, 3)", "mediano": "Mediano Tri(2, 5, 8)", "largo": "Largo Trap(6, 10, 30, 30)"}
    for style, (name, spec) in zip(STYLES, sets.items()):
        ax.plot(x, membership(spec, x), style, color=INK, lw=1.6, label=labels[name])
    h = 2.5
    ax.axvline(h, color=MUTED, lw=1)
    for name in ("corto", "mediano"):
        y = float(membership(sets[name], h))
        ax.plot([h], [y], "o", color=INK, ms=5)
        ax.annotate(rf"$\mu_{{\mathrm{{{name}}}}}$ = {y:.2f}", (h, y), xytext=(8, 4 if name == "corto" else -12),
                    textcoords="offset points", fontsize=9, color=INK)
    ax.set_xlabel("Horizonte H (años; universo [0, 30], se muestra hasta 15)")
    ax.set_ylabel("Pertenencia")
    ax.set_ylim(-0.02, 1.08)
    ax.legend(loc="center right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig-horizonte.png", dpi=200)
    plt.close(fig)


def absorption_figure(params) -> None:
    ap = params.fuzzy.absorption
    result = evaluate_absorption(ap, 5000, 20000, 3)
    u = result.universe
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    names = {"baja": "Baja", "media": "Media", "alta": "Alta"}
    for style, (name, spec) in zip(STYLES, ap.output_sets.items()):
        ax.plot(u, membership(spec, u), style, color=MUTED, lw=1, label=f"Consecuente {names[name]}")
    ax.fill_between(u, result.mu_ca, color="#bdbdbd", lw=0)
    ax.plot(u, result.mu_ca, color=INK, lw=2, label=r"$\mu_{CA}$ agregado (recorte min, unión max)")
    ax.axvline(result.centroid, color=INK, lw=1, ls="-.")
    ax.annotate(f"centroide = {result.centroid:.4f}", (result.centroid, 0.62), xytext=(6, 0),
                textcoords="offset points", fontsize=9)
    ax.set_xlabel("Capacidad de absorción CA (universo [0, 1])")
    ax.set_ylabel("Pertenencia")
    ax.set_ylim(-0.02, 1.08)
    ax.set_ylim(-0.02, 1.08)
    fig.legend(loc="lower center", fontsize=8, ncol=4, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / "fig-absorcion.png", dpi=200)
    plt.close(fig)


def convergence_figure() -> None:
    profile = UserProfile(amount=10000, risk_profile=RiskProfile("moderado"), horizon_years=5.0,
                          horizon_label=None, total_savings=40000, emergency_months=4)
    conv = recommend(profile, None, seed=42)["technical"]["convergence"]
    gens = np.arange(len(conv["best"]))
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ax.plot(gens, conv["best"], "-", color=INK, lw=2, label="Mejor aptitud de la generación")
    ax.plot(gens, conv["mean"], "--", color=MUTED, lw=1.4, label="Aptitud media de la población")
    ax.set_xlabel(f"Generación (convergió en la generación {conv['generations']}: 25 sin mejora)")
    ax.set_ylabel("Aptitud")
    ax.legend(loc="lower right", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig-convergencia.png", dpi=200)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    params = load_parameters()
    horizon_figure(params)
    absorption_figure(params)
    convergence_figure()
    print(f"figures written to {OUT}")


if __name__ == "__main__":
    main()
