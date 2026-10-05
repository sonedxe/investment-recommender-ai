"""Figures for the experiments (requires matplotlib, see requirements-experiments.txt)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from experiments.ablation import (  # noqa: E402
    ARCHETYPES,
    CALIBRATION_ARCHETYPES,
    CALIBRATION_GRID,
    CATEGORIES,
    CONFIGURATIONS,
    GENE_LAMBDAS,
    MACRO_LEVELS,
    POLITICAL_LEVELS,
    WEIGHT_COLUMNS,
)

# Validated categorical palette (fixed order, one hue per category).
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
ARCHETYPE_COLORS = {"moderado": "#2a78d6", "agresivo": "#eb6834", "estres_baja_absorcion": "#1baf7a"}
SURFACE, TEXT, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CATEGORY_LABELS = {"stocks": "Acciones", "mixed": "Mixtos", "debt": "Deuda", "bonds": "Bonos", "term": "Plazo fijo"}
CONFIG_LABELS = {"base": "Base", "solo_difuso": "Solo difuso", "solo_contexto": "Solo contexto",
                 "completo": "Completo"}
PARAMETER_LABELS = {"kappa": "κ", "phi": "φ", "max_weight": "tope"}
DPI = 110

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED, "text.color": TEXT,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 9, "axes.titlesize": 10, "legend.frameon": False,
})


def _stacked(ax: Any, labels: Sequence[str], rows: Sequence[dict[str, Any]]) -> None:
    bottom = np.zeros(len(rows))
    x = np.arange(len(rows))
    for column, color, category in zip(WEIGHT_COLUMNS, SERIES, CATEGORIES):
        values = np.array([100 * r[f"{column}_mean"] for r in rows])
        ax.bar(x, values, 0.62, bottom=bottom, color=color, edgecolor=SURFACE, linewidth=2,
               label=CATEGORY_LABELS[category])
        for xi, (v, b) in enumerate(zip(values, bottom)):
            if v >= 8:
                ax.text(xi, b + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=8, color=TEXT)
        bottom += values
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 100)
    ax.grid(axis="x", visible=False)


def _legend(fig: Any, ax: Any) -> None:
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), bbox_to_anchor=(0.5, -0.01))


def ablation_weights(out: Path, summary: Sequence[dict[str, Any]]) -> str:
    fig, axes = plt.subplots(1, len(ARCHETYPES), figsize=(11, 3.8), sharey=True)
    for ax, arch in zip(axes, ARCHETYPES):
        rows = [next(r for r in summary if r["archetype"] == arch.name and r["config"] == c) for c in CONFIGURATIONS]
        _stacked(ax, [CONFIG_LABELS[c] for c in CONFIGURATIONS], rows)
        ax.set_title(f"{arch.name.capitalize()} (λ_base {arch.lambda_base:g}, H {arch.horizon_years:g} años)")
        ax.tick_params(axis="x", labelsize=8)
    axes[0].set_ylabel("Peso medio (%)")
    _legend(fig, axes[0])
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    return _save(fig, out, "fig_ablation_weights.png")


def context_shift(out: Path, summary: Sequence[dict[str, Any]]) -> str:
    fig, axes = plt.subplots(1, len(MACRO_LEVELS), figsize=(10, 3.8), sharey=True)
    for ax, macro in zip(axes, MACRO_LEVELS):
        rows = [next(r for r in summary if r["political"] == p and r["macro"] == macro) for p in POLITICAL_LEVELS]
        _stacked(ax, [f"Político {p:+.0f}" for p in POLITICAL_LEVELS], rows)
        ax.set_title(f"Macroeconómico {macro:+.0f}")
    axes[0].set_ylabel("Peso medio (%)")
    _legend(fig, axes[0])
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    return _save(fig, out, "fig_context_shift.png")


def gene_c(out: Path, summary: Sequence[dict[str, Any]]) -> str:
    levels = list(dict.fromkeys(r["absorption"] for r in summary))
    fig, axes = plt.subplots(2, len(levels), figsize=(11, 6), sharex=True, sharey="row")
    x = np.array(GENE_LAMBDAS)
    for col, level in enumerate(levels):
        rows = [next(r for r in summary if r["absorption"] == level and r["lambda_base"] == lam) for lam in x]
        top, bottom = axes[0][col], axes[1][col]
        c_mean = np.array([r["c_mean"] for r in rows])
        c_sd = np.array([r["c_sd"] for r in rows])
        top.fill_between(x, c_mean - c_sd, c_mean + c_sd, color=SERIES[0], alpha=0.15, linewidth=0)
        top.plot(x, c_mean, color=SERIES[0], lw=2, marker="o", ms=6, label="c evolucionado")
        top.axhline(rows[0]["centroid_mean"], color=SERIES[1], lw=2, ls="--", label="Centroide")
        top.axhline(rows[0]["mode_mean"], color=MUTED, lw=1.2, ls=":", label="Moda del conjunto")
        top.set_ylim(0, 1)
        top.set_title(f"Absorción {level}")
        sigma = np.array([100 * r["sigma_mean"] for r in rows])
        sigma_max = np.array([100 * r["sigma_max_c_mean"] for r in rows])
        sigma_free = np.array([100 * r["sigma_free_mean"] for r in rows])
        bottom.plot(x, sigma_free, color=MUTED, lw=1.5, ls=":", marker="s", ms=5, label="σ sin penalización")
        bottom.plot(x, sigma_max, color=SERIES[1], lw=2, ls="--", marker="^", ms=6, label="σ_max(c)")
        bottom.plot(x, sigma, color=SERIES[0], lw=2, marker="o", ms=6, label="σ del portafolio")
        bottom.set_xscale("log")
        bottom.set_xticks(x, [f"{v:g}" for v in x])
        bottom.minorticks_off()
        bottom.set_xlabel("λ_base")
    axes[0][0].set_ylabel("c (capacidad)")
    axes[1][0].set_ylabel("Volatilidad (%)")
    axes[0][1].legend(loc="lower left", fontsize=8)
    axes[1][0].legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    return _save(fig, out, "fig_gene_c.png")


def convergence(out: Path, histories: dict[str, Any]) -> str:
    fig, axes = plt.subplots(1, len(ARCHETYPES), figsize=(11, 3.4))
    for ax, arch in zip(axes, ARCHETYPES):
        curves = histories[f"{arch.name}/completo"]
        generations = np.arange(len(curves["best"]))
        ax.plot(generations, curves["mean"], color=MUTED, lw=1.5, label="Fitness medio")
        ax.plot(generations, curves["best"], color=SERIES[0], lw=2, label="Mejor fitness")
        ax.set_title(f"{arch.name.capitalize()} (completo, semilla 0)")
        ax.set_xlabel("Generación")
        top = max(curves["best"])
        span = top - float(np.percentile(curves["mean"], 10))
        ax.set_ylim(top - 1.3 * span, top + 0.1 * span)
    axes[0].set_ylabel("Fitness")
    axes[0].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    return _save(fig, out, "fig_convergence.png")


def calibration(out: Path, summary: Sequence[dict[str, Any]]) -> str:
    parameters = list(CALIBRATION_GRID)
    fig, axes = plt.subplots(2, len(parameters), figsize=(11, 5.6))
    for col, parameter in enumerate(parameters):
        values = np.array(CALIBRATION_GRID[parameter])
        for name in CALIBRATION_ARCHETYPES:
            rows = [next(r for r in summary if r["archetype"] == name and r["parameter"] == parameter
                         and r["value"] == v) for v in values]
            color = ARCHETYPE_COLORS[name]
            axes[0][col].plot(values, [100 * r["sigma_mean"] for r in rows], color=color, lw=2, marker="o", ms=6,
                              label=f"{name}")
            axes[1][col].plot(values, [r["c_mean"] for r in rows], color=color, lw=2, marker="o", ms=6,
                              label=f"{name}")
            axes[1][col].axhline(rows[0]["centroid_mean"], color=color, lw=1.2, ls=":")
        for ax in (axes[0][col], axes[1][col]):
            ax.set_xticks(values, [f"{v:g}" for v in values])
            ax.axvline(_default(parameter), color=GRID, lw=6, zorder=0)
        if parameter == "phi":
            for ax in (axes[0][col], axes[1][col]):
                ax.set_xscale("log")
                ax.set_xticks(values, [f"{v:g}" for v in values])
                ax.minorticks_off()
        axes[0][col].set_title(f"Barrido de {PARAMETER_LABELS[parameter]} (banda gris: valor por defecto)")
        axes[1][col].set_xlabel(PARAMETER_LABELS[parameter])
        axes[1][col].set_ylim(0, 1)
    axes[0][0].set_ylabel("σ del portafolio (%)")
    axes[1][0].set_ylabel("c (punteado: centroide)")
    axes[1][0].legend(loc="center right", fontsize=8)
    fig.tight_layout()
    return _save(fig, out, "fig_calibration.png")


def _default(parameter: str) -> float:
    return {"kappa": 0.03, "phi": 50.0, "max_weight": 0.40}[parameter]


def _save(fig: Any, out: Path, name: str) -> str:
    fig.savefig(out / name, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return name


def draw_all(out: Path, summaries: dict[str, Any], histories: dict[str, Any]) -> list[str]:
    return [
        ablation_weights(out, summaries["ablation"]),
        context_shift(out, summaries["context"]),
        gene_c(out, summaries["gene"]),
        convergence(out, histories),
        calibration(out, summaries["calibration"]),
    ]
